#!/usr/bin/python3
import boto3
import datetime
Img_info= client.describe_images(Filters=[{'Name': 'name','Values':['AMI of *']}])
Image_Del = []
Snap_Del = []

for Image in Img_info['Images']:
	d2= Image['CreationDate'].split('T')[0]
	D2=datetime.datetime.strptime(d2, "%Y-%m-%d")
	D1=datetime.datetime.now()
	D=D1-D2
	Days=int(D.days)
	if Days > Retention:
		print('Removing AMI and its snapshot')
		client.deregister_image(ImageId= Image['ImageId'])
		client.delete_snapshot(SnapshotId= Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId']	
	else :
		print('Not removing AMI and snapshot as it come under retention period')
		print('Snapshot ID',Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
		print('AMI ID',Image['ImageId'])

