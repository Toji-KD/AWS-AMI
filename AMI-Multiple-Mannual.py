#!/usr/bin/python3
import boto3
import datetime
import sys

### ID of instance to be Backed-up ###
I = ['i-0f51537da89ac11ab'] #Specify instance ids here. IDs should be comma sepereated with in single quotes.
######################################
##### Retention in days ######
Retention = 0                #
##############################

#This scipt takes AMI of all running instance for the Region configured in AWS cli-tools. 
#AMIs and its associated snapshots will be removed accoding to the retention period.
#
##### Server Requirements ####################
# AWS CLI - # pip install awscli , # aws configure
# Python3 -   Default in all servers.
# Pip3     - # apt-get install -y python3-pip
# Boto3   - # pip3 install boto3
##############################################

#Creating AMI
Time_Now = datetime.datetime.now().strftime("%Y-%m-%d/%H-%M-%S")
ec2 = boto3.resource('ec2')
client = boto3.client('ec2')
Img_info= client.describe_images(Filters=[{'Name': 'name','Values':['AMI of *']}])

for instance in I:
	try:
		J = client.create_image(Description='AMI of '+instance+' Dated '+Time_Now, InstanceId=instance, Name='AMI of '+instance+' Dated '+Time_Now, NoReboot=True)
		if isinstance(J['ImageId'],str):
			print('AMI '+J['ImageId']+' Taken sucessfully for Instance ',instance)
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
  if Days >= Retention:
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

