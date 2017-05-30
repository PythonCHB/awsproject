#!/usr/bin/env python3

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

        self.vpc = self.ec2r.Vpc(self.myvpc)

# Create VPC subnet function

    def create_subnet(self, subnetvar, az):
        self.subnetvar = subnetvar
        self.az = az

        try:
            newsub = self.vpc.create_subnet(CidrBlock=subnetvar, AvailabilityZone=az)
            self.vpc.create_tags(Resources=[newsub.id], Tags=[{"Key": "Name", "Value": "subnet-{}-{}".format(newsub.availability_zone[-2:], newsub.cidr_block.split(".")[2])}])
            print("\nThe subnet ID created was {}".format(newsub.id))
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

        return(newsub.id)

# Delete VPC subnet function

    def delete_subnet(self, subid):
        self.subid = subid

        try:
            self.ec2c.delete_subnet(SubnetId=subid)
            print("\nThe subnet {} was deleted.".format(subid))
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

        return(subid)

# List VPC subnets function

    def list_subnets(self):
        listsub = self.ec2c.describe_subnets()
        lsdict = {}

        for sub in listsub["Subnets"]:
            print("Subnet ID = {SubnetId} with CIDR of {CidrBlock} in AZ {AvailabilityZone} with {AvailableIpAddressCount} available IPs".format(**sub))
            lsdict[sub["SubnetId"]] = sub["CidrBlock"]

        return(lsdict)

# Create new EC2 instances function

    def create_inst(self, subid, instname):
        self.subid = subid
        self.instname = instname

        try:
            # newinst = self.ec2r.create_instances(ImageId=self.myami, MinCount=1, MaxCount=1, InstanceType=self.ec2type, SecurityGroupIds=[self.mysg], SubnetId=self.subid)
            # self.ec2c.create_tags(Resources=[newinst[0].id], Tags=[{"Key": "Name", "Value": self.instname}])
            newinst = self.ec2c.run_instances(ImageId=self.myami, MinCount=1, MaxCount=1, KeyName=self.mykey, InstanceType=self.ec2type, SecurityGroupIds=[self.mysg], SubnetId=self.subid)
            self.ec2c.create_tags(Resources=[newinst["Instances"][0]["InstanceId"]], Tags=[{"Key": "Name", "Value": instname}])
            print("\nThe instance ID created was {} and is named {}".format(newinst["Instances"][0]["InstanceId"], self.instname))
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

        return(newinst["Instances"][0]["InstanceId"])

# Start and stop EC2 instances functions

    def start_inst(self, instid):
        self.instid = instid

        try:
            self.ec2c.start_instances(InstanceIds=[self.instid])
            print("Started instance {}".format(self.instid))
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

        return(instid)

    def stop_inst(self, instid):
        self.instid = instid

        try:
            self.ec2c.stop_instances(InstanceIds=[instid])
            print("Stopped instance {}".format(instid))
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

        return(instid)

# Terminate EC2 instances function

    def term_inst(self, instid):
        self.instid = instid

        try:
            self.ec2c.terminate_instances(InstanceIds=[instid])
            print("Terminated instance {}".format(instid))
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

        return(instid)

# List EC2 instances function

    def list_inst(self):
        listinst = self.ec2r.instances.all()
        dcinst = {}
        for i in listinst:
            print("ID: {0}  Name: {1}  Type: {2}  State: {3}".format(i.id, i.tags[0]["Value"], i.instance_type, i.state["Name"]))
            dcinst[i.id] = i.tags[0]["Value"]
        return(dcinst)

# Rename an EC2 instance function

    def ren_inst(self, instid, newname):
        self.instid = instid
        self.newname = newname

        try:
            self.ec2c.create_tags(Resources=[instid], Tags=[{"Key": "Name", "Value": newname}])
            print("The instance was renamed to {}".format(newname))
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

        return(instid)

# Create a key pair

    def create_keypair(self, keyname):
        self.keyname = keyname

        try:
            key = self.ec2c.create_key_pair(KeyName=keyname)
            print("\nKey pair created. The following is the key:\n")
            print(key["KeyMaterial"])
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

        return(key["KeyMaterial"])

# List key pairs

    def list_keypair(self):
        listkey = self.ec2c.describe_key_pairs()
        dckey = {}

        for key in listkey["KeyPairs"]:
            print("Key pair = {KeyName}, fingerprint = {KeyFingerprint}".format(**key))
            dckey[key["KeyName"]] = key["KeyFingerprint"]

        return(dckey)

# Delete a key pair

    def delete_keypair(self, keyname):
        self.keyname = keyname

        try:
            self.ec2c.delete_key_pair(KeyName=keyname)
            print("\nThe key pair {} was deleted.".format(keyname))
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

        return(keyname)

# Create S3 bucket function

    def create_bucket(self, buckname):
        self.buckname = buckname

        try:
            newbuck = self.s3c.create_bucket(Bucket=buckname, CreateBucketConfiguration={"LocationConstraint": self.region})
            print("\nBucket {Location} was created successfully.".format(**newbuck))
        except boto3.exceptions.botocore.exceptions.ParamValidationError as e:
            print(e)
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

        return(newbuck["Location"])

# Delete S3 bucket function

    def delete_bucket(self, buckname):
        self.buckname = buckname

        try:
            self.s3c.delete_bucket(Bucket=buckname)
            print("Bucket {} was deleted successfully.".format(buckname))
        except boto3.exceptions.botocore.exceptions.ParamValidationError as e:
            print(e)
        except boto3.exceptions.botocore.client.ClientError as e:
            print(e.response["Error"]["Message"].strip("\""))

        return(buckname)

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
