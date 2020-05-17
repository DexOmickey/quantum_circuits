NAME
     ec2-backup -- backup a directory into Elastic Block Storage (EBS)

SYNOPSIS
     ec2-backup [-h] [-v volume-id] dir

DESCRIPTION
     The ec2-backup tool performs a backup of the given directory into Amazon
     Elastic Block Storage (EBS).  This is achieved by creating a volume of
     the appropriate size, attaching it to an EC2 instance and finally copying
     the files from the given directory onto this volume.

OPTIONS
     ec2-backup accepts the following command-line flags:

     -h		   Print a usage statement and exit.

     -v volume-id  Use the given volume instead of creating a new one.

DETAILS
     ec2-backup will perform a backup of the given directory to an ESB volume.
     The backup is done with the help of the tar(1) command on the local host,
     writing the resulting archive directly to the block device.  That is,
     ec2-backup does not create or use a filesystem on the volume.  Instead,
     ec2-backup utilizes the dd(1) command to write out the data to the raw
     volume.
