#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fstream>
#include <time.h>
#include <sstream>
#include <ctime>

using namespace std;
fstream fscl;
ifstream in;

//declaration of custom functions
void create_key_pair(char ir[100]);
void create_instance(char ir[100]);
void clear_data();
void halt(const int & time);
void get_subnet();
void get_instance();
void get_ip_address();
void get_instance_zone();
void get_volume_zone(char volume[100]);
void get_security_group();
void get_config_region();
void set_ssh_rule(char sg_id[100]);
void nuke(char ir[100]);
void terminate(char instance_id[100],char ir[100]);
void run(char* instr,char* vol_id,char ir[100]);
void initiate_ssh(char ip[100],char ir[100]);
void terminate_instance(char instance_id[100],char ir[100]);


int main(int argc, char** argv){
char* instr = argv[1];
char* vol_id = argv[2];
srand ( time(NULL) );
char ir[100];
int i = 1 + rand() % 79;
stringstream sri;
sri << i;
string str = sri.str();
strcpy(ir,str.c_str());
run(instr,vol_id,ir);
return 0;
}

//function to create dummy key
void create_key_pair(char ir[100]){
char key[250];
char mode[100];
strcpy(key,"aws ec2 create-key-pair --key-name _ec2-backup_");
strcat(key,ir);
strcat(key," --query 'KeyMaterial' --output text > _ec2-backup_");
strcat(key,ir);
strcat(key,".pem");
strcpy(mode,"chmod 400 _ec2-backup_");
strcat(mode,ir);
strcat(mode,".pem");
system(key);
system(mode);
}

//function to get used subnet details
void get_subnet(){
int st;
char subnet[250];
strcpy(subnet,"aws ec2 describe-subnets --filters Name=default-for-az,Values=true --output text | awk '{print $9;exit}' > output.txt");
st=system(subnet);
if(st==-1){
  exit(EXIT_FAILURE);
 }
}

//function to get instance id 
void get_instance(){
int st;
char instances[250];
strcpy(instances,"aws ec2 describe-instances --filters Name=instance-state-name,Values=running  --query 'reverse(sort_by(Reservations[].Instances[], &LaunchTime)[:].[InstanceId,PublicIpAddress])' --output text | awk '{print $1;exit}' >> output.txt");
st=system(instances);
if(st==-1){
  exit(EXIT_FAILURE);
 }
}

//function to get ip address
void get_ip_address(){
int st;
char ip[250];
strcpy(ip,"aws ec2 describe-instances --filters Name=instance-state-name,Values=running  --query 'reverse(sort_by(Reservations[].Instances[], &LaunchTime)[:].[InstanceId,PublicIpAddress])' --output text | awk '{print $2;exit}' >> output.txt");
st=system(ip);
if(st==-1){
  exit(EXIT_FAILURE);
 }
}

//function get availabilty zone
void get_instance_zone(){
int st;
char zone[270];
strcpy(zone,"aws ec2 describe-instances --filters Name=instance-state-name,Values=running  --query 'reverse(sort_by(Reservations[].Instances[], &LaunchTime)[:].[InstanceId,PublicIpAddress,Placement.AvailabilityZone])' --output text | awk '{print $3;exit}' >> output.txt");
st=system(zone);
if(st==-1){
  exit(EXIT_FAILURE);
 }
}

//function get volume zone
void get_volume_zone(char volume[100]){
int st;
char zone[250];
strcpy(zone,"aws ec2 describe-volumes  --filters Name=volume-id,Values=");
strcat(zone,volume);
strcat(zone," --query 'Volumes[*].{zone:AvailabilityZone}' --output text | awk '{print $1;exit}' >> output.txt");
st=system(zone);
if(st==-1){
  exit(EXIT_FAILURE);
 }
}

//function to get security group id
void get_security_group(){
int st;
char group[250];
strcpy(group,"aws ec2 describe-security-groups --filters Name=group-name,Values=default --output text | awk '{print $6;exit}' >> output.txt");
st=system(group);
if(st==-1){
  exit(EXIT_FAILURE);
 }
}

void get_config_region(){
int st;
char region[250];
strcpy(region,"aws configure get region --output text >> output.txt");
st=system(region);
if(st==-1){
  exit(EXIT_FAILURE);
 }
}

//function to create/run dummy netbsd instance
void create_instance(char ir[100]){
int st;
char instance[250];
strcpy(instance,"aws ec2 run-instances --image-id ami-569ed93c --count 1 --instance-type t1.micro --key-name _ec2-backup_");
strcat(instance,ir);
strcat(instance," >> logs.txt");
st=system(instance);
if(st==-1){
  exit(EXIT_FAILURE);
 }
}

//function to attach volume
void attach_volume(char volume_id[100] ,char instance_id[100]){
int st;
char attach[250];
strcpy(attach,"aws ec2 attach-volume --volume-id ");
strcat(attach,volume_id);
strcat(attach," --instance-id ");
strcat(attach,instance_id);
strcat(attach," --device /dev/sda3");
st=system(attach);
if(st==-1){
  exit(EXIT_FAILURE);
 }
}

//function to ssh to instance
void initiate_ssh(char ip[100],char ir[100]){
int st;
char ssh[250];
strcpy(ssh,"ssh -o StrictHostKeyChecking=no -tt -i _ec2-backup_");
strcat(ssh,ir);
strcat(ssh,".pem root@");
strcat(ssh,ip);
strcat(ssh," 'date +%s | dd of=/dev/xbd2d'");
st=system(ssh);
if(st==-1){
  exit(EXIT_FAILURE);
 }
}

//function to allow ssh connction if not set in security group
void set_ssh_rule(char sg_id[100]){
int st;
char rule[250];
strcpy(rule,"aws ec2 authorize-security-group-ingress --group-id ");
strcat(rule,sg_id);
strcat(rule," --protocol tcp --port 22 --cidr 0.0.0.0/0 -arg 2> /dev/null");
st=system(rule);
if(st==-1){
  exit(EXIT_FAILURE);
 }
}

//function to terminate instance and nuke the dummy key
void terminate_instance(char instance_id[100], char ir[100]){
int st;
char instance[250];
strcpy(instance,"aws ec2 terminate-instances --instance-ids ");
strcat(instance,instance_id);
strcat(instance," >> logs.txt");
st=system(instance);
nuke(ir);
if(st==-1){
  exit(EXIT_FAILURE);
 }
exit(EXIT_SUCCESS);
}

void terminate(char instance_id[100],char ir[100]){
int st;
char instance[250];
strcpy(instance,"aws ec2 terminate-instances --instance-ids ");
strcat(instance,instance_id);
strcat(instance," >> logs.txt");
nuke(ir);
halt(8);
st=system(instance);
if(st==-1){
  exit(EXIT_FAILURE);
 }
exit(EXIT_SUCCESS);
}

//function to run the entire functions of the ec2-backup tool
void run(char* instr,char* vol_id,char ir[100]){

char sg[100];
char subnet[200];
char instance_id[100];
char instance_zone[100];
char ip[100];
char vol[100];
char vol_zone[100];
char reg[100];

if(strcmp(instr,"-h") == 0){
cout<<"Run ec2-backup tool with -v flag and a volume id"<<endl<<"i.e ./ec2-backup -v vol-*********"<<endl;
}
else if(strcmp(instr,"-v") == 0){
strcpy(vol,vol_id); 
create_key_pair(ir);
get_config_region();
in.open("output.txt");
in >>reg;
in.close();
clear_data();
if(strcmp(reg,"us-east-1")!=0){
cout<<"The program requires ami-569ed93c Found in Region:us-east-1"<<endl;
cout<<"Please reconfigure your environment to get the program to ran"<<endl;
cout<<"==========================================================="<<endl;
exit(EXIT_FAILURE);
}

cout<<"Preparing to launch instance in :"<<endl;
cout<<"==========================================================="<<endl;
get_security_group();
in.open("output.txt");
in >> sg;
in.close();
clear_data();
set_ssh_rule(sg);
get_subnet();
in.open("output.txt");
in >> subnet;
in.close();
clear_data();
cout<<"Subnet :"<<subnet<<"\n";
cout<<"Security Group :"<<sg<<"\n";
create_instance(ir);
cout<<"Instance launched fetching instance details...."<<endl;
cout<<"======================================================================="<<endl;
halt(45);
get_instance();
in.open("output.txt");
in >> instance_id;
in.close();
clear_data();
cout<<"Instance Id :"<<instance_id<<"\n";
get_ip_address();
in.open("output.txt");
in >> ip;
in.close();
clear_data();
cout<<"IP address :"<<ip<<"\n";
get_instance_zone();
in.open("output.txt");
in >> instance_zone;
in.close();
clear_data();
cout<<"Instance Zone :"<<instance_zone<<"\n";
get_volume_zone(vol);
in.open("output.txt");
in >> vol_zone;
in.close();
clear_data();

if(strcmp(instance_zone,vol_zone) != 0){
halt(5);
cout<<"======================================================================="<<endl;
cout<<"Availability Zone of Instance does not match Volume"<<endl;
cout<<"Can not attach volume"<<endl;
cout<<"Terminating instance..."<<endl;
halt(5);
terminate(instance_id,ir);
}else{

cout<<"Attaching Volume to Instance..."<<endl;
cout<<"======================================================================="<<endl;
attach_volume(vol,instance_id);
cout<<"Volume id:"<<vol<<endl;
cout<<"Volume zone:"<<vol_zone<<endl;
cout<<"Instance Id :"<<instance_id<<endl;
cout<<"======================================================================="<<endl;
cout<<"Requesting Remote Connection to Instance..."<<endl;
halt(60);
initiate_ssh(ip,ir);
halt(5);
cout<<"Current Date Successfully sent to Volume"<<endl;
halt(10);
cout<<"======================================================================="<<endl;
cout<<"Terminating instance..."<<endl;
terminate_instance(instance_id,ir);
   }
 }
else if(instr==NULL){
cout<<"improper usage of tool, use -h to check usage"<<endl;
}

else{
cout<<"improper usage of tool, use -h to check usage"<<endl;
}

}

//clear data from file storing metadata for the program
void clear_data(){
fscl.open("output.txt", ios::out | ios::trunc);
fscl.close();
}

//pause program for sometime
void halt(const int & time){
timespec delay = {time,0}; 
timespec delayrem;
nanosleep(&delay, &delayrem);
return;
}

//remove dummy key from console and system
void nuke(char ir[100]){
char delK[100];
char chM[100];
char rmK[100];
strcpy(delK,"aws ec2 delete-key-pair --key-name _ec2-backup_");
strcat(delK,ir);
strcat(delK,"  > /dev/null");
system(delK);
strcpy(chM,"chmod 644 _ec2-backup_");
strcat(chM,ir);
strcat(chM,".pem");
system(chM);
strcpy(rmK,"rm _ec2-backup_");
strcat(rmK,ir);
strcat(rmK,".pem");
system(rmK);
}
