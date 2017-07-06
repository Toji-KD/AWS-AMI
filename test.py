#!/usr/bin/python3
import datetime
import boto3
Time_Now = datetime.datetime.now().strftime("%Y/%m/%d-%H/%M/%S")
ec2 = boto3.resource('ec2')
client = boto3.client('ec2')
for instance in ec2.instances.all():
        response = client.create_image(Description='AMI of '+instance.id+' Dated '+Time_Now, InstanceId=instance.id, Name='AMI of '+instance.id+' Dated'+Time_Now, NoReboot=True)
