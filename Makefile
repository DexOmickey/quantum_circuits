
SHELL := /bin/bash


all: executable ec2-backup config to_path

executable:
	chmod +x ec2-backup.py
ec2-backup: 
	ln -s ./ec2-backup.py ec2-backup
config:
	chmod +x config.sh 
to_path:
	./config.sh	
