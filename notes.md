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



 