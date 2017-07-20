#!/usr/bin/python3
import boto3
import datetime
import sys
import logging
##### Retention in days ######
Retention = 4                #
##############################

#This scipt takes AMI of all running instance for the Region configured in AWS cli-tools. 
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

#Creating AMI
Time_Now = datetime.datetime.now().strftime("%Y-%m-%d/%H-%M-%S")
ec2 = boto3.resource('ec2')
client = boto3.client('ec2')
Img_info= client.describe_images(Filters=[{'Name': 'name','Values':['AMI of *']}])

I = client.describe_instance_status()
for instance in I['InstanceStatuses']:
	try:
		J = client.create_image(Description='AMI of '+instance['InstanceId']+' Dated '+Time_Now, InstanceId=instance['InstanceId'], Name='AMI of '+instance['InstanceId']+' Dated '+Time_Now, NoReboot=True)
		if isinstance(J['ImageId'],str):
			print('AMI '+J['ImageId']+' Taken sucessfully for Instance',instance['InstanceId'])
			logging.info('AMI '+J['ImageId']+' Taken sucessfully for Instance '+instance['InstanceId'])
		else:
			print('Error in taking AMI for the instance',instance['InstanceId'])
			logging.error('Error in taking AMI for the instance '+instance['InstanceId'])
	except:
		print('Script couldnt take AMI for the instance',instance['InstanceId'])
		logging.error('Script couldnt take AMI for the instance '+instance['InstanceId'])
print(' ')
#Retention check
try:
	I1 = Img_info['Images'][0]['ImageId']
except:
	print('No AMIs available in this region to check retention. Exiting..')
	logging.info('No AMIs available in this region to check retention. Exiting..')
	sys.exit()
	
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
        print('Error in deregistering AMI',Image['ImageId'])
        logging.error('Error in deregistering AMI '+Image['ImageId'])
    except:
      print('Script couldnt Deregister AMI',Image['ImageId'])
      logging.error('Script couldnt Deregister AMI '+Image['ImageId'])
			
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
