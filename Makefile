#install ansible roles this playbook needs
dep:
	@echo "\033[32mInstalling ansible roles...\033[0m"
	@echo "\033[32mInstalling artis3n.tailscale collection...\033[0m"
	@ansible-galaxy collection install artis3n.tailscale
	## install geerlingguy.docker 
	@echo "\033[32mInstalling geerlingguy.docker collection...\033[0m"
	@aansible-galaxy role install geerlingguy.docker