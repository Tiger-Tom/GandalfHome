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
	#echo "Copied files"
	#echo "Checking for missing configuration..."
	#foundConfigs=()
	#for entry in ~/Gandalf/_config/*
	#do
	#	echo "Found entry $entry..."
	#	foundConfigs+=( $entry )
	#done
	#for entry in $source/Gandalf/_config/*
	#do
	#	echo "Found entry $entry in source"
	#	if [[ " ${foundConfigs[@]} " =~ " $entry " ]]; then
	#		echo "$entry exists"
	#	else
	#		echo "$entry does not exist"
	#		cp $entry ~/Gandalf/_config
	#		echo "Copied $entry"
	#	fi
	#done
	cd ~/Gandalf/
else
	echo "No previous installation found. Installing defaults..."
	mkdir ~/Gandalf/
	sudo cp -r "$source/Gandalf" ~/
	cd ~/Gandalf/
fi

pip3 install -r ~/Gandalf/requirements.txt
