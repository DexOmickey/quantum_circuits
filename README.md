NAME
     ec2-backup-v1 -- backup a directory into Elastic Block Storage (EBS)

SYNOPSIS
     ec2-backup-v1 [-h] -v volume-id

DESCRIPTION
     The ec2-backup(1) tool will eventually perform a backup of the given
     directory into Amazon Elastic Block Storage (EBS).	 This will be achieved
     by creating a volume of the appropriate size, attaching it to an EC2
     instance and finally copying the files from the given directory onto this
     volume.

     The ec2-backup-v1 tool is the first iteration of this program and does
     not actually perform a backup.  This program merely allows the user to
     specify a volume that ec2-backup-v1 will attach to a suitable instance
     and write the current date to the raw device.

OPTIONS
     ec2-backup-v1 accepts the following command-line flags:

     -h		   Print a usage statement and exit.

     -v volume-id  Use the given volume.

DETAILS
     ec2-backup-v1 will create an instance suitable for the specified volume,
     attach the volume to the instance, remotely log in on the instance and
     write the current date to the raw device.
