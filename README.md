# Homelab 

this repository represents a growing list of configurations and scripts i use to manage my homelab infrastructure. I can't promise everything will work 100% out of the box, but you will be able to steal snippets you find useful. 



## Current structure/stack
My homelab currently(as of 2/01/26) consists of three machines(Balrog,chronos and lazarus) 


### Balrog 
is a RaspberryPI that primarily runs homeassistant as a i have a few zigbee devices and prefer not install 4 different apps that all require a cloud service. This might change in the future as i intend to run [pi-hole](https://pi-hole.net/). 

### Chronos
Chronos is my main machine for backups,media and majority of the services i will be running for now.
Its a thinkcenter with 8gigs of memory and an i5, as at time of writing it runs most things well and runs < 15% even under "heavy load". 


### Lazarus 
Although second oldest in the fleet, runs a broken install of nix and is constantly dying on me. Its a playground i might eventually turn into a k8s worker. Only time will tell. 



## Services 

- Grafana/Prometheus(monitoring)
- Media streaming(Jellyfin)
- Glance for dashboard
- Docker for containers(managed through ansible)
- NFS for file share(might move to samba cuz of macos support.)
- Qbittorrent( for "p2p file sharing" )
- prowlarr/sonarr( for indexing p2p files)
- tailscale for remote access 


## IAC 
- Ansible(for bootstrapping/updates)
- NixOS(kinda)




## Networking 
Networking is fairly basic for now, prioritizing uptime before i invest int other networking equipment so all machines are plugged into my ISPs router directly. 


## Misc 
see notes.md for specifics on issues i run into. 





## FAQs(not really)

### 1. Why no k8s
Do that in my main job and side projects. pls no more  

### 2. Why do this? 
IDK don't you like being asked why your home media service is broken ?


