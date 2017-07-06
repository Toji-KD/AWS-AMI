#!/usr/bin/python3
import boto3
import datetime
import sys
import requests

##### Retention in days ######
Retention = 4       #Specify retention here #
##############################

#This scipt takes AMI of current instance (Instance of this script configured)
#AMIs and its associated snapshots will be removed accoding to the retention period.
#
##### Server Requirements ####################
# AWS CLI - # pip install awscli , # aws configure
# Python3 -   Default in all servers.
# Pip     - # apt-get install -y python3-pip
# Boto3   - # pip install boto3
##############################################

ID = requests.get('http://169.254.169.254/latest/meta-data/instance-id')
ID = ID.text

#Creating AMI
Time_Now = datetime.datetime.now().strftime("%Y-%m-%d/%H-%M-%S")
ec2 = boto3.resource('ec2')
client = boto3.client('ec2')
Img_info= client.describe_images(Filters=[{'Name': 'name','Values':['AMI of *']}])

try:
	J = client.create_image(Description='AMI of '+ID+' Dated '+Time_Now, InstanceId=ID, Name='AMI of '+ID+' Dated '+Time_Now, NoReboot=True)
	if isinstance(J['ImageId'],str):
		print('AMI '+J['ImageId']+' Taken sucessfully for Instance ',ID)
	else:
		print('Error in taking AMI')
except:
	print('Script couldnt take AMI')

print(' ')

#Retention check
try:
	I1 = Img_info['Images'][0]['ImageId']
except:
	print('No AMIs available in this region. Exiting..')
	sys.exit()
#Img_info= client.describe_images(Filters=[{'Name': 'name','Values':['AMI of *']}])
for Image in Img_info['Images']:
  d2= Image['CreationDate'].split('T')[0]
  D2=datetime.datetime.strptime(d2, "%Y-%m-%d")
  D1=datetime.datetime.now()
  D=D1-D2
  Days=int(D.days)
  if Days > Retention:
    try:
      I2 = client.deregister_image(ImageId= Image['ImageId'])
      if I2['ResponseMetadata']['HTTPStatusCode'] == 200:
        print('Removing AMI ',Image['ImageId'])
      else:
        print('Error in removing AMI')
    except:
      print('Script couldnt remove AMI')
			
    try:
      I3 = client.delete_snapshot(SnapshotId= Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
      if I3['ResponseMetadata']['HTTPStatusCode'] ==200:
        print('Removing SnapShot ',Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
      else:
        print('Error in removing Snapshot')
    except:
      print('Script couldnt remove Snapshot')
			
  else:
    print('Not removing AMI '+Image['ImageId']+' and snapshot '+Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId']+' as they come under retention period')

