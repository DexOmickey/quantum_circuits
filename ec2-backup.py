#!/usr/bin/python3

#Declarations
import sys
import os
import subprocess
import re
import time

#Functions

#checking CLI arguments to validate volume id and directory to prevent program taking in garbage
#using regular expressions and in built python directory checker
def flags():
  if len(sys.argv)<=2:
    if len(sys.argv)<=1:
      print("Invalid use of tool, use -h for hint on usage")
      sys.exit()
    else:
      if(os.path.isdir(str(sys.argv[1]))==True):
        return "-"
      elif sys.argv[1]=="-h":
        print("Run with directory : ec2-backup /dir/ ")
        print("Use -v flag with volume id followed by directory: ec2-backup -v vol-xxxxxxxxxxxxxx /dir/ ")
        sys.exit()
      elif len(sys.argv)==0:
        print("Invalid use of tool, use -h for hint on usage")
        sys.exit()
      else:
        print("Invalid use of tool, use -h for hint on usage")
        sys.exit()
  elif sys.argv[1]=="-v":
    if len(sys.argv)<4:
      print("Please provide volume id and Directory")
      sys.exit()
    else:
      isDirectory = os.path.isdir(str(sys.argv[3]))
      pattern=re.compile("^vol\-[a-z0-9]{17}$")
      if isDirectory==False:
        print("Not a valid Directory- Please provide a Valid Directory")
        sys.exit()
      elif bool(pattern.match(str(sys.argv[2])))==False:
        print("Not a valid Volume-id")
        sys.exit()
      elif len(sys.argv)<3:
        print("Please provide Volume id and Directory")
        sys.exit()
      elif len(sys.argv)>4:
        print("Tool takes only two arguments after -v flag")
        sys.exit()
      else:
        print("Volume: "+str(sys.argv[2]))
        return str(sys.argv[2]) 
  else:
    print("Invalid use of tool, use -h for hint on usage")
    sys.exit()

#checking user's AWS environment configuration select ami's and validate user usage
#returned value (region) here supports other functions to run and make decisions
def check_config(FLAG_VERBOSE):
  result=subprocess.run("aws configure get region",shell=True,stdout=subprocess.PIPE)
  if result.returncode ==1 or result.returncode==2:
    print("Error occured Restart program")
    sys.exit()
  elif result.returncode ==130:
    print("E2-Backup tool was Interrupted")
    sys.exit()
  elif result.returncode ==255:
    print("Error Occured in E2-Backup tool")
    sys.exit()
  else:
    conf=result.stdout.decode('utf-8').strip()
    if conf == "us-east-1" or conf == "us-east-2" or conf == "us-west-1" or conf == "us-west-2" or conf == "eu-west-2" or conf == "eu-central-1":
      if str(FLAG_VERBOSE)=="1":
        print("Configured Region:"+ conf)
        return conf
      else:
        return conf
    else:
      print("Program does not support your region")
      sys.exit()

#mapping ami's to respective regions to dynamically create instances of supported regions
def ami(reg):
  us_east_1="ami-0036ab7a"
  us_east_2="ami-00fd2a47558af2d5e"
  us_west_1="ami-02caf19519c4c499e"
  us_west_2="ami-00b393dff4b72de45"
  eu_central_1="ami-02794c442da068ce5"
  eu_west_1="ami-0019f18ee3d4157d3"
  eu_west_2="ami-00dfb15d8a057c8b5"  
  eu_west_3="ami-00548e9e2ae95fa4d"   
  if reg=="us-east-1":
    return us_east_1
  elif reg=="us-east-2":
    return us_east_2
  elif reg=="us-west-1":
    return us_west_1
  elif reg=="us-west-2":
    return us_west_2
  elif reg=="eu-central-1":
    return eu_central_1
  elif reg=="eu-west-1":
    return eu_west_1
  elif reg=="eu-west-2":
    return eu_west_2
  elif reg=="eu-west-3":
    return eu_west_3
  else:
    print("Your region:"+reg+" not among supported regions")
    sys.exit()


#create and initiate ec2 instances based on users configured region.
def create_instance(ami,reg,FLAG_VERBOSE):
  resin=subprocess.run("aws ec2 run-instances --image-id "+ami+" --count 1 --instance-type t1.micro --key-name ec2-backup",shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
  if resin.returncode == 1 or resin.returncode==2:
    print("Error occured Restart program")
    sys.exit()
  elif resin.returncode ==130:
    print("E2-Backup tool was Interrupted")
    sys.exit()
  elif resin.returncode ==255:
    print("Error Occured in E2-Backup tool- Could Not Create Instance")
    sys.exit()
  else:
    if str(FLAG_VERBOSE)=="1":
      res=resin.stdout.decode('utf-8').strip()
      print("===========================================")
      print("Creating Instance in "+reg) 

#create ec2 instance with EC2_BACKUP_FLAGS_AWS flags, seperated from create_instance() 
#to make it easy for the tool to make a decision when the flag is set.
def flag_create_instance(ami,reg,FLAG_INSTANCE,FLAG_VERBOSE):
  resin=subprocess.run("aws ec2 run-instances --image-id "+ami+" --count 1 --key-name ec2-backup "+str(FLAG_INSTANCE),shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
  if resin.returncode == 1 or resin.returncode==2:
    print("Error occured Restart program")
    sys.exit()
  elif resin.returncode ==130:
    print("E2-Backup tool was Interrupted")
    sys.exit()
  elif resin.returncode ==255:
    print("Error Occured in E2-Backup tool- Could Not Create Instance: Invalid Flag parameters")
    sys.exit()
  else:
    if str(FLAG_VERBOSE)=="1":
      res=resin.stdout.decode('utf-8').strip()
      print("===========================================")
      print("Creating Instance in "+reg)

 

#getting zone of instance to aid in creating a volume in the same zone
#returned value (instance zone) here supports other functions in validation
def instance_zone(instance_id):
  result=subprocess.run("aws ec2 describe-instances --filters Name=instance-id,Values="+instance_id+" --query Reservations[].Instances[].Placement.AvailabilityZone --output text | awk '{print $1;exit}'",shell=True,stdout=subprocess.PIPE)
  if result.returncode == 1 or result.returncode==2:
    print("Error occured Restart program")
    sys.exit()
  elif result.returncode ==130:
    print("E2-Backup tool was Interrupted")
    sys.exit()
  elif result.returncode ==255:
    print("Error Occured in E2-Backup tool")
    sys.exit()
  else:
    return result.stdout.decode('utf-8').strip()


#create a volume if user does not have or provide one
def create_volume(zone):
  result=subprocess.run("aws ec2 create-volume --volume-type standard --size 50 --availability-zone "+zone+" --output text | awk '{print $6}'",shell=True,stdout=subprocess.PIPE)
  if result.returncode !=0:
    print("Error occured Restart program")
    sys.exit()
  else:
    print("Volume :"+result.stdout.decode('utf-8').strip()+" created!")
    return result.stdout.decode('utf-8').strip()


#Get instance id which will be used in attaching a volume 
def get_instance_details(FLAG_VERBOSE):
  result = subprocess.run("aws ec2 describe-instances --filters Name=instance-state-name,Values=running,pending  --query 'reverse(sort_by(Reservations[].Instances[], &LaunchTime)[:].[InstanceId,PublicIpAddress])' --output text | awk '{print $1;exit}'",shell=True,stdout=subprocess.PIPE)
  if result.returncode ==1 or result.returncode==2:
    print("Error occured Restart program")
    sys.exit()
  elif result.returncode ==130:
    print("E2-Backup tool was Interrupted")
    sys.exit()
  elif result.returncode ==255:
    print("Error Occured in E2-Backup tool")
    sys.exit()
  else:
    if str(FLAG_VERBOSE)=="1":
      print("Instance with Instance_Id:"+result.stdout.decode('utf-8').strip()+" Created!")
      print("Fetching additional details please wait....")
    return result.stdout.decode('utf-8').strip()


#Get Instance public DNS which is used by the .ssh file for backup over ssh
def get_ip(FLAG_VERBOSE):
  result = subprocess.run("aws ec2 describe-instances --filters Name=instance-state-name,Values=running  --query 'reverse(sort_by(Reservations[].Instances[], &LaunchTime)[:].[InstanceId,PublicDnsName])' --output text | awk '{print $2;exit}'",shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
  if result.returncode ==1 or result.returncode==2:
    print("Error occured Restart program")
    sys.exit()
  elif result.returncode ==130:
    print("E2-Backup tool was Interrupted")
    sys.exit()
  elif result.returncode ==255:
    print("Error Occured in E2-Backup tool")
    sys.exit()
  else:
    if result.stdout.decode('utf-8').strip()=="":
      print("Could Not Obtain public DNS.. please wait")
      time.sleep(10)
      get_ip(FLAG_VERBOSE)
    else:
      if str(FLAG_VERBOSE)=="1":
        print("Instance has Public DNS:"+result.stdout.decode('utf-8').strip()+"")
    return result.stdout.decode('utf-8').strip()


#Verify location of volume and instance to see if they are in the same zone, if not program stops
def verify_location_instvol(volume_id,instance_id,FLAG_VERBOSE):
  vol_zone = subprocess.run("aws ec2 describe-volumes --filters Name=volume-id,Values="+volume_id+" --query 'Volumes[*].{zone:AvailabilityZone}' --output text | awk '{print $1;exit}'",shell=True,stdout=subprocess.PIPE)
  inst_zone = subprocess.run("aws ec2 describe-instances --filters Name=instance-state-name,Values=running  --query 'reverse(sort_by(Reservations[].Instances[], &LaunchTime)[:].[Placement.AvailabilityZone])' --output text | awk '{print $1;exit}'",shell=True,stdout=subprocess.PIPE)
  if vol_zone.returncode ==1 or inst_zone.returncode ==1 or vol_zone.returncode==2 or inst_zone.returncode==2:
    print("Error occured Restart program")
    sys.exit()
  elif vol_zone.returncode ==130 or inst_zone.returncode ==130:
    print("E2-Backup tool was Interrupted")
    sys.exit()
  elif vol_zone.returncode ==255 or inst_zone.returncode == 255:
    print("Error Occured in E2-Backup tool")
    sys.exit()
  else:
    if vol_zone.stdout.decode('utf-8').strip()!=inst_zone.stdout.decode('utf-8').strip():
      print("Volume and Instance not in the same Availability Zone")
      terminate_instance(instance_id)
      sys.exit()
    else:
      if str(FLAG_VERBOSE)=="1":
        print("Verifying Volume...............")
        time.sleep(5)
        print("Attaching volume to Instance")
        print(volume_id+" Successfully attached to "+instance_id)
        print("===========================================")


#verify volume state to see if it is available available to used or its already in use
def verify_volume_state(volume_id,instance_id):
  result = subprocess.run("aws ec2 describe-volumes  --filters Name=volume-id,Values="+volume_id+" --query 'Volumes[].State' --output text",shell=True,stdout=subprocess.PIPE)
  if result.returncode ==1 or result.returncode==2:
    print("Error occured Restart program")
    sys.exit()
  elif result.returncode ==130:
    print("E2-Backup tool was Interrupted")
    sys.exit()
  elif result.returncode ==255:
    print("Error Occured in E2-Backup tool")
    sys.exit()
  else:
    state=result.stdout.decode('utf-8').strip()
    if state=="in-use":
      print("Volume provided is in use by another instance.") 
      terminate_instance(instance_id)


#Attach volume to instance
def attach_volume(volume_id,instance_id,state):
  if state=="0":
    time.sleep(10)
    verify_instance_running(instance_id)
  elif state=="1":
    FNULL = open(os.devnull, 'w')
    result = subprocess.run("aws ec2 attach-volume --volume-id "+volume_id+" --instance-id "+instance_id+" --device /dev/sdf",shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
    if result.returncode ==1 or result.returncode==2:
      print("Error occured Restart program")
      terminate_instance(instance_id)
      sys.exit()
    elif result.returncode ==130:
      print("E2-Backup tool was Interrupted")
      terminate_instance(instance_id)
      sys.exit()
    elif result.returncode ==255:
      print("Error Occured in E2-Backup tool- Could Not attach Volume to Instance")
      terminate_instance(instance_id)
      sys.exit()
    else:
      time.sleep(8)
  else:
    state=result.stdout.decode('utf-8').strip()
    if state=="in-use":
      print("Volume provided is in use by another instance.") 
      terminate_instance(instance_id)


#verify that state of instance to see if its running. If its not, it loops till the instance gets ready
def verify_instance_running(instance_id):
  result = subprocess.run("aws ec2 describe-instance-status --instance-ids "+instance_id+" --query 'InstanceStatuses[].InstanceState.Name' --output text",shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
  if result.returncode ==1 or result.returncode==2:
    print("Error occured Restart program")
    sys.exit()
  elif result.returncode ==130:
    print("E2-Backup tool was Interrupted")
    sys.exit()
  elif result.returncode ==255:
    print("Error Occured in E2-Backup tool")
    sys.exit()
  else:
    status = result.stdout.decode('utf-8').strip()
    if status=="stopping" or status=="stopped" or status=="shutting-down" or status=="terminated":
      print("Instance not Active")
      sys.exit()
    elif status=="pending":
      print("Instance is initializing please wait as it boots")
      return "0"
    else:
      return "1"

#get size of directory using du command which is used compare if directory backup will fit the volume
def get_directory_size(directory):
  files=str(directory) 
  result = subprocess.run("du -sh "+files+" | awk '{print $1;exit}'" ,shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
  if result.returncode !=0:
    print("Error occured Restart")
    sys.exit()
  else:
    return result.stdout.decode('utf-8').strip()

def non_sudoer_directory_size(directory):
  files=str(directory)
  result = subprocess.run("du -sh "+files+" --exclude='/bin' --exclude='/boot' --exclude='/dev' --exclude='/etc' --exclude='/initrd.img' --exclude='/initrd.img.old' --exclude='/lib' --exclude='/lib32' --exclude='/lib64' --exclude='/libx32' --exclude='/lost+found' --exclude='/media' --exclude='/mnt' --exclude='/proc' --exclude='/projects' --exclude='/root' --exclude='/run' --exclude='/sbin' --exclude='/snap' --exclude='/var' --exclude='/srv' --exclude='/sys' --exclude='/tmp' --exclude='/vmlinuz' --exclude='/vmlinuz.old' | awk '{print $1;exit}'" ,shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
  if result.returncode !=0:
    print("Error occured Restart")
    sys.exit()
  else:
    return result.stdout.decode('utf-8').strip()


#verify data size and volume size
def verify_data_vol_size(volume_id,directory,instance_id,FLAG_VERBOSE):
  result=subprocess.run("aws ec2 describe-volumes --filter Name=volume-id,Values="+volume_id+" --query Volumes[].Size --output text | awk '{print $1;exit}'",shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
  resdir=subprocess.run("du -s "+directory+" | awk '{print $1;exit}'",shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
  if result.returncode!=0 or resdir.returncode!=0:
    print("Error Occured")
    sys.exit()
  else:
    vol_size=(int(result.stdout.decode('utf-8').strip()))*(1024*1024)
    size_d =resdir.stdout.decode('utf-8').strip()
    if(int(size_d) > vol_size):
      print("Error: Backup data larger than Volume")
      terminate_instance(instance_id)
      sys.exit()
    elif(int(size_d)==0):
      print("Error: No data in directory, Backup not required")
      terminate_instance(instance_id)
      sys.exit()
    else:
      if str(FLAG_VERBOSE)=="1":
        print("Commencing Backup .......")


#ssh to instance
def ssh_instance(dns,directory,size,instance_id,sudo,FLAG_VERBOSE):
  files = str(directory)
  if files=="/":
    if sudo=="no":
      sudo_ssh_instance_no_sudoer(dns,directory,instance_id,FLAG_VERBOSE)
      print("Couldn't backup '/bin /boot /dev /etc /lib /var / srv / sys ... - To back up entire root directory you need to be a sudoer")
    else:
      sudo_ssh_instance(dns,directory,size,instance_id,FLAG_VERBOSE)
  else:
    result = subprocess.run("tar cf - "+files+" | ssh centos@"+dns+" -o StrictHostKeyChecking=no 'sudo dd of=/dev/xvdf'",shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
    if result.returncode ==1 or result.returncode==2:
      print("Error occured Restart")
      terminate_instance(instance_id)
      sys.exit()
    elif result.returncode ==130:
      print("E2-Backup tool was Interrupted")
      terminate_instance(instance_id)
      sys.exit()
    elif result.returncode ==255:
      print("Error Occured in E2-Backup tool- Could Not ssh to instance")
      terminate_instance(instance_id)
      sys.exit()
    else:
      if str(FLAG_VERBOSE)=="1":
        print(size+"B of Data Successfully Sent to Volume!") 

#check sudo access
def sudo_check():
  result = subprocess.run("sudo -v ",shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
  if result.returncode !=0:
    return "no"
  else:
    return "yes"

#handle backup if user is no sudoer excepting files that require sudo access.
def sudo_ssh_instance_no_sudoer(dns,directory,instance_id,FLAG_VERBOSE):
  files = str(directory)
  result = subprocess.run("tar cf - "+files+" --exclude='/bin' --exclude='/boot' --exclude='/dev' --exclude='/etc' --exclude='/initrd.img' --exclude='/initrd.img.old' --exclude='/lib' --exclude='/lib32' --exclude='/lib64' --exclude='/libx32' --exclude='/lost+found' --exclude='/media' --exclude='/mnt' --exclude='/proc' --exclude='/projects' --exclude='/root' --exclude='/run' --exclude='/sbin' --exclude='/snap' --exclude='/var' --exclude='/srv' --exclude='/sys' --exclude='/tmp' --exclude='/vmlinuz' --exclude='/vmlinuz.old' | ssh centos@"+dns+" -o StrictHostKeyChecking=no 'sudo dd of=/dev/xvdf'",shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
  if result.returncode ==1 or result.returncode==2:
    print("Error occured Restart")
    terminate_instance(instance_id)
    sys.exit()
  elif result.returncode ==130:
    print("E2-Backup tool was Interrupted")
    terminate_instance(instance_id)
    sys.exit()
  elif result.returncode ==255:
    print("Error Occured in E2-Backup tool- Could Not ssh to instance")
    terminate_instance(instance_id)
    sys.exit()
  else:
    if str(FLAG_VERBOSE)=="1":
      size=non_sudoer_directory_size(directory)
      print(size+"B of Data Successfully Sent to Volume!")  

#handle backup if user if user is a sudoer
def sudo_ssh_instance(dns,directory,size,instance_id,FLAG_VERBOSE):
  files = str(directory)
  result = subprocess.run("sudo tar cf - "+files+" | ssh centos@"+dns+" -o StrictHostKeyChecking=no 'sudo dd of=/dev/xvdf'",shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
  if result.returncode ==1 or result.returncode==2:
    print("Error occured Restart")
    terminate_instance(instance_id)
    sys.exit()
  elif result.returncode ==130:
    print("E2-Backup tool was Interrupted")
    terminate_instance(instance_id)
    sys.exit()
  elif result.returncode ==255:
    print("Error Occured in E2-Backup tool- Could Not ssh to instance")
    terminate_instance(instance_id)
    sys.exit()
  else:
    if str(FLAG_VERBOSE)=="1":
      print(size+"B of Data Successfully Sent to Volume!")

#handles ssh and backup with when EC2_BACKUP_FLAGS_SSH is set
def ssh_with_flag(dns,directory,size,instance_id,sudo,FLAG_SSH,FLAG_VERBOSE):
  files = str(directory)
  if files=="/":
    if sudo=="no":
      sudo_ssh_instance_no_sudoer_flag(dns,directory,instance_id,FLAG_SSH,FLAG_VERBOSE)
      print("Couldn't backup '/bin /boot /dev /etc /lib /var / srv / sys ... - To back up entire root directory you need to be a sudoer")
    else:
      sudo_ssh_instance_flag(dns,directory,size,instance_id,FLAG_SSH,FLAG_VERBOSE)
  else:
    result = subprocess.run("tar cf - "+files+" | ssh "+str(FLAG_SSH)+" centos@"+dns+" -o StrictHostKeyChecking=no 'sudo dd of=/dev/xvdf'",shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
    if result.returncode ==1 or result.returncode==2:
      print("Error occured Restart")
      terminate_instance(instance_id)
      sys.exit()
    elif result.returncode ==130:
      print("E2-Backup tool was Interrupted")
      terminate_instance(instance_id)
      sys.exit()
    elif result.returncode ==255:
      print("Error Occured in E2-Backup tool- Could Not ssh to instance: Check your SSH Flag")
      terminate_instance(instance_id)
      sys.exit()
    else:
      if str(FLAG_VERBOSE)=="1":
        print(size+"B of Data Successfully Sent to Volume!")


#handle ssh and backup with when EC2_BACKUP_FLAGS_SSH is set if user is no sudoer excepting files that require sudo access.
def sudo_ssh_instance_no_sudoer_flag(dns,directory,instance_id,FLAG_SSH,FLAG_VERBOSE):
  files = str(directory)
  result = subprocess.run("tar cf - "+files+" --exclude='/bin' --exclude='/boot' --exclude='/dev' --exclude='/etc' --exclude='/initrd.img' --exclude='/initrd.img.old' --exclude='/lib' --exclude='/lib32' --exclude='/lib64' --exclude='/libx32' --exclude='/lost+found' --exclude='/media' --exclude='/mnt' --exclude='/proc' --exclude='/projects' --exclude='/root' --exclude='/run' --exclude='/sbin' --exclude='/snap' --exclude='/var' --exclude='/srv' --exclude='/sys' --exclude='/tmp' --exclude='/vmlinuz' --exclude='/vmlinuz.old' | ssh "+str(FLAG_SSH)+" centos@"+dns+" -o StrictHostKeyChecking=no 'sudo dd of=/dev/xvdf'",shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
  if result.returncode ==1 or result.returncode==2:
    print("Error occured Restart")
    terminate_instance(instance_id)
    sys.exit()
  elif result.returncode ==130:
    print("E2-Backup tool was Interrupted")
    terminate_instance(instance_id)
    sys.exit()
  elif result.returncode ==255:
    print("Error Occured in E2-Backup tool- Could Not ssh to instance: Check your SSH Flag")
    terminate_instance(instance_id)
    sys.exit()
  else:
    if str(FLAG_VERBOSE)=="1":
      size=non_sudoer_directory_size(directory)
      print(size+"B of Data Successfully Sent to Volume!")


#handle ssh and backup with when EC2_BACKUP_FLAGS_SSH is set if user is a sudoer
def sudo_ssh_instance_flag(dns,directory,size,instance_id,FLAG_SSH,FLAG_VERBOSE):
  files = str(directory)
  result = subprocess.run("sudo tar cf - "+files+" | ssh "+str(FLAG_SSH)+" centos@"+dns+" -o StrictHostKeyChecking=no 'sudo dd of=/dev/xvdf'",shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
  if result.returncode ==1 or result.returncode==2:
    print("Error occured Restart")
    terminate_instance(instance_id)
    sys.exit()
  elif result.returncode ==130:
    print("E2-Backup tool was Interrupted")
    terminate_instance(instance_id)
    sys.exit()
  elif result.returncode ==255:
    print("Error Occured in E2-Backup tool- Could Not ssh to instance: Check your SSH Flag")
    terminate_instance(instance_id)
    sys.exit()
  else:
    if str(FLAG_VERBOSE)=="1":
      print(size+"B of Data Successfully Sent to Volume!")


#terminate instance
def terminate_instance(instance_id):
  result = subprocess.run("aws ec2 terminate-instances --instance-ids "+instance_id,shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull, 'w'))
  if result.returncode !=0:
    print("Error occured while terminating please wait")
    terminate_instance(instance_id)
    sys.exit()
  else:
    if str(FLAG_VERBOSE)=="1":
      print("Terminating :"+instance_id+" !....")
    time.sleep(5)
    sys.exit()


#FLAGS
def check_env_flag(FLAG):
  if FLAG==None or FLAG=="":
    return None
  else:
    result=subprocess.run("sh -c 'echo "+FLAG+"'",shell=True,stdout=subprocess.PIPE,stderr=open(os.devnull,'w'))
    if result.returncode !=0:
      print("Error occured")
    else:
      return result.stdout.decode('utf-8').strip()	

FLAG_SSH = check_env_flag(os.getenv('EC2_BACKUP_FLAGS_SSH'))
FLAG_VERBOSE = check_env_flag(os.getenv('EC2_BACKUP_VERBOSE'))
FLAG_INSTANCE = check_env_flag(os.getenv('EC2_BACKUP_FLAGS_AWS'))

#Implementations
#Handle decision making and logic of the tool from accepting arguments down to backing up and terminating instance
def run_tool():
  volume=flags()
  if len(sys.argv)<=2:
    directory=sys.argv[1]
  else:
    directory=sys.argv[3]
  reg=check_config(FLAG_VERBOSE)
  if FLAG_INSTANCE==None or FLAG_INSTANCE=="" :
    create_instance(ami(reg),reg,FLAG_VERBOSE)
  else:
    flag_create_instance(ami(reg),reg,FLAG_INSTANCE,FLAG_VERBOSE)
  instance_id =get_instance_details(FLAG_VERBOSE)
  zone=instance_zone(instance_id)
  if volume=="-":
    volume=create_volume(zone)
  time.sleep(48)
  state=verify_instance_running(instance_id)
  public_dns=get_ip(FLAG_VERBOSE)
  verify_volume_state(volume,instance_id)
  verify_location_instvol(volume,instance_id,FLAG_VERBOSE)
  attach_volume(volume,instance_id,state)
  size=get_directory_size(directory)
  verify_data_vol_size(volume,directory,instance_id,FLAG_VERBOSE)
  time.sleep(40)
  sudo=sudo_check()
  if FLAG_SSH==None or FLAG_SSH=="" :
    ssh_instance(public_dns,directory,size,instance_id,sudo,FLAG_VERBOSE)
  else:
    ssh_with_flag(public_dns,directory,size,instance_id,sudo,FLAG_SSH,FLAG_VERBOSE)
  terminate_instance(instance_id)

#Execute
run_tool()
