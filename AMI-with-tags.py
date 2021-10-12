#!/usr/bin/python3
import boto3
import datetime
import sys

##### Retention in days ##################
#Put 0 if you do not want retention option
Retention = 0                
##########################################


Time_Now = datetime.datetime.now().strftime("%Y-%m-%d/%H-%M-%S")
ec2 = boto3.resource('ec2',region_name='us-east-1')
client = boto3.client('ec2',region_name='us-east-1')
Instance_Id = ec2.instances.filter(Filters=[{'Name': 'tag:role','Values': ['tkd']}])
Img_info= client.describe_images(Filters=[{'Name': 'name','Values':['AMI of *']}])

####   Function to get Instance Name  ###

def get_instance_name(fid):
    # When given an instance ID as str e.g. 'i-1234567', return the instance 'Name' from the name tag.
    ec2 = boto3.resource('ec2',region_name='us-east-1')
    ec2instance = ec2.Instance(fid)
    instancename = ''
    for tags in ec2instance.tags:
        if tags["Key"] == 'Name':
            instancename = tags["Value"]
    return instancename

####  Creating AMI  ###

for instance in Instance_Id:
	try:
		I = client.create_image(Description='AMI of '+instance.id+' Dated '+Time_Now, InstanceId=instance.id, Name='AMI of '+instance.id+' Dated '+Time_Now, NoReboot=True)
		if isinstance(I['ImageId'],str):
			print('AMI '+I['ImageId']+' Taken sucessfully for the instance',instance.id)
			Instance_Name = get_instance_name(instance.id)
			Instance_Name = Instance_Name+' Image backup'
			image = ec2.Image(I['ImageId'])
			image.create_tags(Tags=[{'Key': 'Name','Value': Instance_Name}])

		else:
			print('Error in taking AMI for the instance',instance.id)
			logging.error('Error in taking AMI for the instance '+instance.id)
	except:
		print('Script couldnt take AMI for the instance',instance.id)
		logging.error('Script couldnt take AMI for the instance '+instance.id)
		

####  Retention check  ###

if Retention == 0:
    print('Exiting as Retention option is not enabled in script')
    sys.exit()
else:
    try:
        I1 = Img_info['Images'][0]['ImageId']
    except:
        print('No AMIs available in this region. Exiting..')
        logging.info('No AMIs available in this region. Exiting..')
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
                    print('Deregistering AMI ',Image['ImageId'])
                    
                else:
                    print('Error in deregistering AMI',Image['ImageId'])
                
            except:
                print('Script couldnt deregister AMI',Image['ImageId'])
            
            try:
                I3 = client.delete_snapshot(SnapshotId= Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
                if I3['ResponseMetadata']['HTTPStatusCode'] ==200:
                    print('Removing SnapShot ',Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
                    
                else:
                    print('Error in removing Snapshot',Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
                    
            except:
                print('Script couldnt remove Snapshot',Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId'])
            
                    
        else:
            print('Not removing AMI '+Image['ImageId']+' and snapshot '+Image['BlockDeviceMappings'][0]['Ebs']['SnapshotId']+' as they come under retention period')
