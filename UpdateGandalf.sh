#!/bin/bash -i
shopt -s extglob
source="/mnt/usb-drive"
echo "Installing from $source"
if [ -d ~/Gandalf ]; then
	sudo chown $USER ~/Gandalf/
	echo "Previous installation found. Installing non-config..."
	cd ~/Gandalf/
	sudo rm -r !(_config)
	cd $source/Gandalf/
	cp -r !(_config) ~/Gandalf/
	cd ~/Gandalf/
else
	echo "No previous installation found. Installing defaults..."
	mkdir ~/Gandalf/
	sudo cp -r "$source/Gandalf" ~/
	cd ~/Gandalf/
fi

pip3 install -r ~/Gandalf/requirements.txt
