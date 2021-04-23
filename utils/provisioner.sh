#! /bin/bash
# Django Server Provisioning

source $HOME/Projects/Publishing_Suite/utils/config.sh

install_packages(){
	echo -e "## Installing system dependencies. ##"
	sudo apt-get update; sudo apt-get upgrade -y; sudo apt-get dist-upgrade -y; sudo apt-get autoremove -y; sudo apt-get autoclean -y
	sudo apt-get install vim tmux python3 python3-dev python3-django python3-pip python3-wheel mono-runtime python3-venv csvkit
}

create_environment(){
	if [ ! -d $VENV ]; then
		echo -e "## Creating/Activating Python environment. ##"
		python3 -m venv $VENV
	fi
	source $VENV/bin/activate
	echo -e "## Installing PyPI dependencies. ##"
	python3 -m pip install -r $CMSDIR/requirements.txt
}	

$1
