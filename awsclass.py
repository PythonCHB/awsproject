#!/usr/bin/env python3

""" AWS Class Tool by Paul Casey

This program is an AWS class utility that performs the following:

- Create, list, and delete subnets in the VPC
- Create, list, and delete S3 buckets. Also list the files in the buckets
- Create, list, and rename EC2 instances
- Start, stop, and terminate EC2 instances
- Create, list, and delete EC2 keypair
- Create, list and delete Application Load Balancers

"""

# Import Modules

import boto3
from configparser import ConfigParser


class Aws():
    def __init__(self):
        awscfg = ConfigParser()
        awscfg.read("/home/ec2-user/.aws/credentials")
        self.region = awscfg.get("default", "region")
        self.mykey = awscfg.get("default", "key")
        self.mysg = awscfg.get("default", "secgroup")
        self.myami = awscfg.get("default", "ami")
        self.ec2type = awscfg.get("default", "ec2type")
        self.myvpc = awscfg.get("default", "vpc")

        self.ec2r = boto3.resource("ec2")
        self.ec2c = boto3.client("ec2")
        self.s3r = boto3.resource("s3")
        self.s3c = boto3.client("s3")
        self.elbv2c = boto3.client("elbv2")

        self.vpc = self.ec2r.Vpc(self.myvpc)

        self.userdata = """#cloud-config
repo_update: true
repo_upgrade: all

packages:
 - nginx

runcmd:
 - sudo yum update
 - service nginx start
"""

# Create VPC subnet function

    def create_subnet(self, subnetvar, az):
        self.subnetvar = subnetvar
        self.az = az

        try:
            newsub = self.vpc.create_subnet(
                CidrBlock=subnetvar,
                AvailabilityZone=az)
            self.vpc.create_tags(
                Resources=[newsub.id],
                Tags=[{"Key": "Name", "Value": "subnet-{}-{}".format(
                    newsub.availability_zone[-2:],
                    newsub.cidr_block.split(".")[2])}])
            print("\nThe subnet ID created was {}".format(newsub.id))
            return(newsub.id)
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

# Delete VPC subnet function

    def delete_subnet(self, subid):
        self.subid = subid

        try:
            self.ec2c.delete_subnet(SubnetId=subid)
            print("\nThe subnet {} was deleted.".format(subid))
            return(subid)
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

# List VPC subnets function

    def list_subnets_all(self):
        listsub = self.ec2c.describe_subnets()
        lsdict = {}

        for sub in listsub["Subnets"]:
            print(
                "Subnet ID = {SubnetId} with CIDR of {CidrBlock} in AZ "
                "{AvailabilityZone} with {AvailableIpAddressCount} "
                "available IPs".format(**sub))
            lsdict[sub["SubnetId"]] = sub["CidrBlock"]

        return(lsdict)

# List subnets for a particular AZ function

    def list_subnets_az(self, subaz):
        self.subaz = subaz
        lsdict = {}

        listsubaz = self.ec2c.describe_subnets(
            Filters=[{"Name": "availabilityZone", "Values": [self.subaz]}])

        for sub in listsubaz["Subnets"]:
            print(
                "Subnet ID = {SubnetId} with CIDR of {CidrBlock} in AZ "
                "{AvailabilityZone} with {AvailableIpAddressCount} "
                "available IPs".format(**sub))
            lsdict[sub["SubnetId"]] = sub["CidrBlock"]

        return(lsdict)

# Create new EC2 instances function

    def create_inst(self, subid, key, instname):
        self.subid = subid
        self.mykey = key
        self.instname = instname
        # waitrun = self.ec2c.get_waiter("instance_running")

        try:
            newinst = self.ec2c.run_instances(
                ImageId=self.myami, MinCount=1,
                MaxCount=1, KeyName=self.mykey, InstanceType=self.ec2type,
                SecurityGroupIds=[self.mysg], SubnetId=self.subid,
                UserData=self.userdata)
            self.ec2c.create_tags(
                Resources=[newinst["Instances"][0]["InstanceId"]],
                Tags=[{"Key": "Name", "Value": instname}])
            # waitrun.wait(InstanceIds=[newinst["Instances"][0]["InstanceId"]])
            print(
                "\nThe instance ID created was {} and is named {}".format(
                    newinst["Instances"][0]["InstanceId"], self.instname))
            return(newinst["Instances"][0]["InstanceId"])
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

# Start and stop EC2 instances functions

    def start_inst(self, instid):
        self.instid = instid

        try:
            self.ec2c.start_instances(InstanceIds=[self.instid])
            print("Started instance {}".format(self.instid))
            return(instid)
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

    def stop_inst(self, instid):
        self.instid = instid

        try:
            self.ec2c.stop_instances(InstanceIds=[instid])
            print("Stopped instance {}".format(instid))
            return(instid)
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

# Terminate EC2 instances function

    def term_inst(self, instid):
        self.instid = instid

        try:
            self.ec2c.terminate_instances(InstanceIds=[instid])
            print("Terminated instance {}".format(instid))
            return(instid)
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

# List EC2 instances function

    def list_inst(self):
        listinst = self.ec2c.describe_instances()
        dcinst = {}
        for res in listinst["Reservations"]:
            for inst in res["Instances"]:
                print(
                    "ID: {InstanceId} Type: {InstanceType} Name: "
                    "{Tags[0][Value]} State: {State[Name]}".format(**inst))
                dcinst.update({inst["Tags"][0]["Value"]:
                    inst["State"]["Name"]})
        return(dcinst)

# Rename an EC2 instance function

    def ren_inst(self, instid, newname):
        self.instid = instid
        self.newname = newname

        try:
            self.ec2c.create_tags(
                Resources=[instid],
                Tags=[{"Key": "Name", "Value": newname}])
            print("The instance was renamed to {}".format(newname))
            return(instid)
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

# Create an Application Load Balancer function

    def create_alb(self, albname, sub1, sub2, sub3, tgarn):
        self.albname = albname
        self.sub1 = sub1
        self.sub2 = sub2
        self.sub3 = sub3
        self.tgarn = tgarn

        # tgarn = self.elbv2c.describe_target_groups(
        # Names=[tgname])["TargetGroups"][0]["TargetGroupArn"]

        try:
            newalb = self.elbv2c.create_load_balancer(
                Name=albname,
                Subnets=[sub1, sub2, sub3], SecurityGroups=[self.mysg],
                Scheme="internet-facing", IpAddressType="ipv4")
            self.elbv2c.create_listener(
                LoadBalancerArn=newalb["LoadBalancers"][0]["LoadBalancerArn"],
                Protocol="HTTP", Port=80,
                DefaultActions=[{"Type": "forward", "TargetGroupArn": tgarn}])
            print(
                "ALB created. The DNS name is {}".format(
                    newalb["LoadBalancers"][0]["DNSName"]))
            return(newalb["LoadBalancers"][0]["DNSName"])
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

# List Application Load Balancers function

    def list_alb(self):
        listalb = self.elbv2c.describe_load_balancers()
        ladict = {}

        for alb in listalb["LoadBalancers"]:
            print(
                "LB Name = {LoadBalancerName}  "
                "DNS Name = {DNSName}".format(**alb))
            ladict[alb["LoadBalancerName"]] = alb["DNSName"]

        return(ladict)

# Delete an Application Load Balancer function

    def delete_alb(self, albname):
        self.albname = albname

        albarn = self.elbv2c.describe_load_balancers(
                 Names=[albname])["LoadBalancers"][0]["LoadBalancerArn"]

        try:
            self.elbv2c.delete_load_balancer(LoadBalancerArn=albarn)
            print("ALB {} deleted.".format(albname))
            return(albarn)
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

# Create an ALB target group function

    def create_target_group(self, tgname, inst1, inst2, inst3):
        self.tgname = tgname
        self.inst1 = inst1
        self.inst2 = inst2
        self.inst3 = inst3

        try:
            print("Waiting for instances to start")
            waitrun = self.ec2c.get_waiter("instance_running")
            waitrun.wait(InstanceIds=[inst1, inst2, inst3])
            newtg = self.elbv2c.create_target_group(
                Name=tgname,
                Protocol="HTTP", Port=80, VpcId=self.myvpc)
            tgarn = newtg["TargetGroups"][0]["TargetGroupArn"]
            self.elbv2c.register_targets(
                TargetGroupArn=tgarn,
                Targets=[{"Id": inst1}, {"Id": inst2}, {"Id": inst3}])
            print(
                "Target group created. The target group name is {}".format(
                    newtg["TargetGroups"][0]["TargetGroupName"]))
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

        return(tgarn)

# List ALB target groups function

    def list_target_groups(self):
        listtg = self.elbv2c.describe_target_groups()

        for tg in listtg["TargetGroups"]:
            print(
                "TG Name = {TargetGroupName}  "
                "ARN = {TargetGroupArn}".format(**tg))

# Delete ALB target group function

    def delete_target_group(self, tgname):
        self.tgname = tgname

        tgarn = self.elbv2c.describe_target_groups(
            Names=[tgname])["TargetGroups"][0]["TargetGroupArn"]

        try:
            self.elbv2c.delete_target_group(TargetGroupArn=tgarn)
            print("Target group {} deleted.".format(tgname))
            return(tgarn)
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

# Create a key pair function

    def create_keypair(self, keyname):
        self.keyname = keyname

        try:
            key = self.ec2c.create_key_pair(KeyName=keyname)
            print("\nKey pair created. The following is the key:\n")
            print(key["KeyMaterial"])
            return(key["KeyName"])
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

# List key pairs function

    def list_keypair(self):
        listkey = self.ec2c.describe_key_pairs()
        dckey = {}

        for key in listkey["KeyPairs"]:
            print(
                "Key pair = {KeyName}, "
                "fingerprint = {KeyFingerprint}".format(**key))
            dckey[key["KeyName"]] = key["KeyFingerprint"]

        return(dckey)

# Delete a key pair

    def delete_keypair(self, keyname):
        self.keyname = keyname

        try:
            self.ec2c.delete_key_pair(KeyName=keyname)
            print("\nThe key pair {} was deleted.".format(keyname))
            return(keyname)
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

# Create S3 bucket function

    def create_bucket(self, buckname):
        self.buckname = buckname

        try:
            newbuck = self.s3c.create_bucket(
                Bucket=buckname,
                CreateBucketConfiguration={"LocationConstraint": self.region})
            print(
                "\nBucket {Location} was created successfully.".format(
                    **newbuck))
            return(newbuck["Location"])
        except boto3.exceptions.botocore.exceptions.ParamValidationError as e:
            print(e)
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

# Delete S3 bucket function

    def delete_bucket(self, buckname):
        self.buckname = buckname

        try:
            self.s3c.delete_bucket(Bucket=buckname)
            print("Bucket {} was deleted successfully.".format(buckname))
            return(buckname)
        except boto3.exceptions.botocore.exceptions.ParamValidationError as e:
            print(e)
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

# List S3 buckets function

    def list_buckets(self):
        listbuck = self.s3r.buckets.all()
        lb = []
        print("\nList of buckets:")
        for b in listbuck:
            print(b.name)
            lb.append(b.name)
        print("\nNumber of buckets: {}".format(len(lb)))
        return(lb)

# List S3 files function

    def list_files(self):
        lsdict = {}
        listfile = self.s3r.buckets.all()
        for buck in listfile:
            for obj in buck.objects.all():
                print("Bucket: {0}  File: {1}".format(buck.name, obj.key))
                lsdict[buck.name] = obj.key
        return(lsdict)
