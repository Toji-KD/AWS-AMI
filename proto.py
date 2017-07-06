#!/usr/bin/python3
import boto3
import datetime
import sys
Retention = 4 #Retention in days

#Creating AMI
Time_Now = datetime.datetime.now().strftime("%Y-%m-%d/%H-%M-%S")
ec2 = boto3.resource('ec2')
client = boto3.client('ec2')
for instance in ec2.instances.all():
	try:
		I = client.create_image(Description='AMI of '+instance.id+' Dated '+Time_Now, InstanceId=instance.id, Name='AMI of '+instance.id+' Dated '+Time_Now, NoReboot=True)
		if I['ImageId'] == str:
			print('AMI '+I['ImageId']+' Taken sucessfully')
		else:
			print('Error in taking AMI')
	except:
		print('Script couldn\'t take AMI')

#Retention check
try:
  Img_info= client.describe_images(Filters=[{'Name': 'name','Values':['AMI of *']}])
  I1 = Img_info['Images'][0]['ImageId']
except:
	print('No AMIs available in this region. Exiting..')
	sys.exit()
Img_info= client.describe_images(Filters=[{'Name': 'name','Values':['AMI of *']}])
for Image in Img_info['Images']:
	d2= Image['CreationDate'].split('T')[0]
	D2=datetime.datetime.strptime(d2, "%Y-%m-%d")
	D1=datetime.datetime.now()
	D=D1-D2
	Days=int(D.days)
	if Days > Retention:
		
		try:
			client.deregister_image(ImageId= Image['ImageId'])
			print('Removing AMI ',Image['ImageId'])
		except:
			print('Error in removing AMI')
		try:
			client.delete_snapshot(SnapshotId= Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
			print('Removing SnapShot ',Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
		except:
			print('Error in removing Snapshot')
	else:
		print('Not removing AMI and snapshot as it come under retention period')
		print('Snapshot ID',Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
		print('AMI ID',Image['ImageId'])
