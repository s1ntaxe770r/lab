## Resources 

Below is a growning list of notes and and resources for specific issues i run into. 



## [mounting disk after reboot](https://publish.obsidian.md/janvanderwijktech/9+KB/ICT/NETWORK/PORTNUMBERS#Herb+Jensen+%3CHWJensen%26nfsrv.avionics.itt.com%3E)


## [mount nfs drive on mac](https://www.cyberciti.biz/faq/apple-mac-osx-nfs-mount-command-tutorial/)

```bash
 sudo mount -t nfs -o resvport chronos:/mnt/thomas/media ~/Desktop/nfs
 ```


## Running tailscale
using these extra flags so it does not break my connection. 



By default tailscale will try to route all traffic through the its dns , which is not desireable if you rely on hostnames or a local dns server. 




```bash
tailscale up  --accept-dns=false
```


## Grafana and Jellyfin reporting disk full after SSD replacement

After replacing the internal SSD on chronos, Grafana and Jellyfin kept reporting the disk was full. Jellyfin was throwing:

```
System.InvalidOperationException: The path `/config/data` has insufficient free space.
```

Turned out Ubuntu had installed with LVM but only allocated 100G to the root logical volume — leaving 373G of free space sitting unused on the same drive. The LVM volume group had the space, it just was never extended.

Fixed by extending the logical volume to use all remaining free space and resizing the filesystem live — no reboot needed.

```yaml
- name: Extend logical volume to use all free space
  ansible.builtin.command: lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv
  become: true
  register: lv_extend
  changed_when: "'successfully resized' in lv_extend.stdout"
  failed_when: lv_extend.rc != 0 and 'matches existing size' not in lv_extend.stderr
  tags: extend-lv

- name: Resize filesystem to fill extended volume
  ansible.builtin.command: resize2fs /dev/ubuntu-vg/ubuntu-lv
  become: true
  tags: extend-lv
```

Root partition went from 94G/98G (100% full) to 94G/466G (21% used).
