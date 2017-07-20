#!/usr/bin/python3
import boto3
import datetime
import sys
import requests
import logging

##### Retention in days ######
Retention = 4       #Specify retention here #
##############################

#This scipt takes AMI of current instance (Instance of this script configured)
#AMIs and its associated snapshots will be removed accoding to the retention period.
#
##### Server Requirements ####################
# AWS CLI - # pip install awscli , # aws configure
# Python3 -   Default in all servers.
# Pip3     - # apt-get install -y python3-pip
# Boto3   - # pip install boto3
##############################################
# Written by Toji K Dominic 
# tojikdominic@gmail.com +91 9747389586
##############################################

########   Log file   ########################

LOG_FILE = '/var/log/AMI-Backup.log'
logging.basicConfig(filename=LOG_FILE,level=logging.INFO,format="%(asctime)s:%(levelname)s:%(message)s")
logging.info(' ')
logging.info('AMI STARTS FOR THE DAY')
logging.info(' ')

#Get current Instance ID
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
		logging.info('AMI '+J['ImageId']+' Taken sucessfully for Instance '+ID)
	else:
		print('Error in taking AMI for the instance',ID)
		logging.error('Error in taking AMI for the instance '+ID)
except:
	print('Script couldnt take AMI for Instance',ID)
	logging.error('Script couldnt take AMI for Instance '+ID)

print(' ')

#Retention check
try:
	I1 = Img_info['Images'][0]['ImageId']
except:
	print('No AMIs available in this region. Exiting..')
	logging.info('No AMIs available in this region. Exiting..')
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
        print('Deregistering AMI',Image['ImageId'])
        logging.info('Deregistering AMI '+Image['ImageId'])
      else:
        print('Error in removing AMI',Image['ImageId'])
        logging.error('Error in Deregistering AMI '+Image['ImageId'])
    except:
      print('Script couldnt remove AMI',Image['ImageId'])
      logging.info('Script couldnt remove AMI '+Image['ImageId'])
			
    try:
      I3 = client.delete_snapshot(SnapshotId= Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
      if I3['ResponseMetadata']['HTTPStatusCode'] ==200:
        print('Removing SnapShot',Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
        logging.info('Removing SnapShot '+Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
      else:
        print('Error in removing Snapshot',Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
        logging.error('Error in removing Snapshot '+Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
    except:
      print('Script couldnt remove Snapshot',Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
      logging.error('Script couldnt remove Snapshot '+Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
			
  else:
    print('Not removing AMI '+Image['ImageId']+' and snapshot '+Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId']+' as they come under retention period')
    logging.info('Not removing AMI '+Image['ImageId']+' and snapshot '+Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId']+' as they come under retention period')

