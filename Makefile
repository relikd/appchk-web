help:
	@echo ''
	@echo 'Commands available:'
	@echo '  pull:          get newest changes from server (data/ dir only)'
	@echo '  push:          overwrite source files on server (excl. data/ dir)'
	@echo '  push-list:     replace custom lists like "Messengers", etc.'
	@echo '  remote-build:  force-rebuild all remote files (index & html)'
	@echo '  local:         force-rebuild all local files (index & html)'
	@echo ''
	@echo 'Usage:'
	@echo '  make push remote-build SSH=your_ssh_key'
	@echo ''
check_defined_ssh = \
    $(if $(value SSH),, \
      $(error Undefined SSH. Usage: make $1 SSH=your_ssh_key))
pull:
	@:$(call check_defined_ssh,pull)
	rsync -ralptv --delete -e ssh $(SSH):/var/www/de-appchk/data/ "data/"
push:
	@:$(call check_defined_ssh,push)
	rsync -rlptv --delete --exclude=.DS_Store --exclude=.git/ "." --exclude=/{data/,src/{__pycache__,lists}/,error.log} --include=/out/static/ --exclude=/out/* $(SSH):/var/www/de-appchk/
	@# --dry-run && ssh $(SSH) chown -R www-data:www-data /var/www/de-appchk
push-list:
	@:$(call check_defined_ssh,push-list)
	rsync -rlptv --delete --exclude=.DS_Store --exclude=.git/ "data/_lists/" $(SSH):/var/www/de-appchk/data/_lists/
remote-build:
	@:$(call check_defined_ssh,remote-build)
	ssh $(SSH) /var/www/de-appchk/src/main.py run '*'
local:
	src/main.py run '*'
