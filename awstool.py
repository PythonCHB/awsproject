#!/usr/bin/env python3

""" AWS Configuration Tool by Paul Casey

This program is a menu-driven AWS utility that performs the following:

- Create, list, and delete subnets in the VPC
- Create, list, and delete S3 buckets. Also list the files in the buckets
- Create, list, and rename EC2 instances
- Start, stop, and terminate EC2 instances
- Create, list, and delete EC2 keypair
- Create, list and delete Application Load Balancers

"""

# Import modules

import boto3
import sys
from configparser import ConfigParser

# Load the configuration settings from the "credentials" file


awscfg = ConfigParser()
awscfg.read("/home/ec2-user/.aws/credentials")
region = awscfg.get("default", "region")
mykey = awscfg.get("default", "key")
mysg = awscfg.get("default", "secgroup")
myami = awscfg.get("default", "ami")
ec2type = awscfg.get("default", "ec2type")
myvpc = awscfg.get("default", "vpc")

# Set the "resource" and "client" variables for EC2 and S3
# AWS functions are separated between the "client" and "resource"
# variables.


ec2r = boto3.resource("ec2")
ec2c = boto3.client("ec2")
s3r = boto3.resource("s3")
s3c = boto3.client("s3")
elbv2c = boto3.client("elbv2")

vpc = ec2r.Vpc(myvpc)

# Help menu

intro = """
AWS Configuration Tool by Paul Casey

Type 'csub' to create a subnet
Type 'dsub' to delete a subnet
Type 'lsub' to list the subnets
Type 'imake' to create an instance
Type 'istart' to start an instance
Type 'istop' to stop an instance
Type 'iterm' to terminate an instance
Type 'ilist' to list the instances
Type 'iren' to rename an instance
Type 'calb' to create an ALB
Type 'lalb' to list the ALBs
Type 'dalb' to delete an ALB
Type 'ctg' to create a target group
Type 'ltg' to list target groups
Type 'dtg' to delete a target group
Type 'ckey' to create a key pair
Type 'lkey' to list key pairs
Type 'dkey' to delete a key pair
Type 'cbuck' to create an S3 bucket
Type 'dbuck' to delete an S3 buckets
Type 'lbuck' to list the S3 buckets
Type 'ls' to list all S3 files
Type 'x' to exit

"""

# User data for building and instance that automatically installs and runs
# nginx

userdata = """#cloud-config
repo_update: true
repo_upgrade: all

packages:
 - nginx

runcmd:
 - sudo yum update
 - service nginx start
"""

# Main prompt


def action_prompt():
    action = input("==> ")
    return action.strip()


# Print help menu

def help_menu():
    print(intro)

# Create VPC subnet function


def create_subnet():
    subnetvar = input("Enter the subnet (Ex: 192.168.94.0/24): ").strip()
    az = input("Enter the availability zone (Ex: us-west-2a): ").strip()

    try:
        newsub = vpc.create_subnet(CidrBlock=subnetvar, AvailabilityZone=az)
        vpc.create_tags(
            Resources=[newsub.id],
            Tags=[{"Key": "Name", "Value": "subnet-{}-{}".format(
                newsub.availability_zone[-2:],
                newsub.cidr_block.split(".")[2])}])
        print("\nThe subnet ID created was {}".format(newsub.id))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# Delete VPC subnet function


def delete_subnet():
    list_subnets_all()
    subid = input("Enter the subnet ID: ").strip()

    try:
        ec2c.delete_subnet(SubnetId=subid)
        print("\nThe subnet {} was deleted.".format(subid))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# List all VPC subnets function


def list_subnets_all():
    listsub = ec2c.describe_subnets()
    lsdict = {}

    for sub in listsub["Subnets"]:
        # print(
        # "Subnet ID = {0} with CIDR of {1} in AZ {2} with {3} available IPs"
        # .format(sub["SubnetId"], sub["CidrBlock"], sub["AvailabilityZone"],
        # str(sub["AvailableIpAddressCount"])))
        print(
            "Subnet ID = {SubnetId} with CIDR of {CidrBlock} in AZ "
            "{AvailabilityZone} with {AvailableIpAddressCount} available "
            "IPs".format(**sub))
        lsdict[sub["SubnetId"]] = sub["CidrBlock"]
    return(lsdict)

# List subnets for a particular AZ function


def list_subnets_az(subaz):
    listsubaz = ec2c.describe_subnets(
        Filters=[{"Name": "availabilityZone", "Values": [subaz]}])

    for sub in listsubaz["Subnets"]:
        print(
            "Subnet ID = {SubnetId} with CIDR of {CidrBlock} in AZ "
            "{AvailabilityZone} with {AvailableIpAddressCount} available "
            "IPs".format(**sub))

# Create new EC2 instances function


def create_inst():
    list_subnets_all()
    subid = input("Enter the subnet ID: ").strip()
    instname = input("Enter the name: ").strip()

    try:
        newinst = ec2c.run_instances(
            ImageId=myami, MinCount=1, MaxCount=1, KeyName=mykey,
            InstanceType=ec2type, SecurityGroupIds=[mysg], SubnetId=subid,
            UserData=userdata)
        ec2c.create_tags(
            Resources=[newinst["Instances"][0]["InstanceId"]],
            Tags=[{"Key": "Name", "Value": instname}])
        print(
            "\nThe instance ID created was {} and is named {}".format(
                newinst["Instances"][0]["InstanceId"], instname))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# Start and stop EC2 instances functions


def start_inst():
    list_inst()
    instid = input("Enter the instance ID: ").strip()

    try:
        ec2c.start_instances(InstanceIds=[instid])
        print("Started instance {}".format(instid))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))


def stop_inst():
    list_inst()
    instid = input("Enter the instance ID: ").strip()

    try:
        ec2c.stop_instances(InstanceIds=[instid])
        print("Stopped instance {}".format(instid))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# Terminate EC2 instances function


def term_inst():
    list_inst()
    instid = input("Enter the instance ID: ").strip()

    try:
        ec2c.terminate_instances(InstanceIds=[instid])
        print("Terminated instance {}".format(instid))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# List EC2 instances function


def list_inst():
    listinst = ec2c.describe_instances()
    dcinst = {}
    for res in listinst["Reservations"]:
        for inst in res["Instances"]:
            print(
                "ID: {InstanceId}  Type: {InstanceType}  AZ: "
                "{Placement[AvailabilityZone]}  State: {State[Name]}  "
                "Name: {Tags[0][Value]}".format(**inst))
            dcinst.update({inst["State"]["Name"]: inst["Tags"][0]["Value"]})
    return(dcinst)

# Rename an EC2 instance function


def ren_inst():
    list_inst()
    instid = input("Enter the instance ID: ").strip()
    newname = input("Enter the new name: ").strip()

    try:
        ec2c.create_tags(
            Resources=[instid], Tags=[{"Key": "Name", "Value": newname}])
        print("The instance was renamed to {}".format(newname))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# Create an Application Load Balancer function


def create_alb():
    albname = input("Enter the name of the ALB: ").strip()
    list_subnets_az("us-west-2a")
    sub1 = input("Enter the subnet for {}a: ".format(region)).strip()
    list_subnets_az("us-west-2b")
    sub2 = input("Enter the subnet for {}b: ".format(region)).strip()
    list_subnets_az("us-west-2c")
    sub3 = input("Enter the subnet for {}c: ".format(region)).strip()
    list_target_groups()
    tgname = input("Enter the target group: ").strip()
    tgarn = elbv2c.describe_target_groups(
        Names=[tgname])["TargetGroups"][0]["TargetGroupArn"]

    try:
        newalb = elbv2c.create_load_balancer(
            Name=albname, Subnets=[sub1, sub2, sub3], SecurityGroups=[mysg],
            Scheme="internet-facing", IpAddressType="ipv4")
        elbv2c.create_listener(
            LoadBalancerArn=newalb["LoadBalancers"][0]["LoadBalancerArn"],
            Protocol="HTTP", Port=80,
            DefaultActions=[{"Type": "forward", "TargetGroupArn": tgarn}])
        print(
            "ALB created. The DNS name is {}".format(
                newalb["LoadBalancers"][0]["DNSName"]))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# List Application Load Balancers function


def list_alb():
    listalb = elbv2c.describe_load_balancers()

    for alb in listalb["LoadBalancers"]:
        print(
            "LB Name = {LoadBalancerName}  "
            "DNS Name = {DNSName}".format(**alb))

# Delete an Application Load Balancer function


def delete_alb():
    list_alb()
    albname = input("Enter the ALB name: ").strip()
    albarn = elbv2c.describe_load_balancers(
        Names=[albname])["LoadBalancers"][0]["LoadBalancerArn"]
    try:
        elbv2c.delete_load_balancer(LoadBalancerArn=albarn)
        print("ALB {} deleted.".format(albname))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# Create an ALB target group function


def create_target_group():
    tgname = input("Enter the name of the target group: ").strip()
    list_inst()
    inst1 = input("Enter the first instance for the group: ").strip()
    inst2 = input("Enter the second instance for the group: ").strip()
    inst3 = input("Enter the third instance for the group: ").strip()

    try:
        newtg = elbv2c.create_target_group(
            Name=tgname, Protocol="HTTP", Port=80, VpcId=myvpc)
        tgarn = newtg["TargetGroups"][0]["TargetGroupArn"]
        elbv2c.register_targets(
            TargetGroupArn=tgarn,
            Targets=[{"Id": inst1}, {"Id": inst2}, {"Id": inst3}])
        print(
            "Target group created. The target group name is {}".format(
                newtg["TargetGroups"][0]["TargetGroupName"]))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# List ALB target groups function


def list_target_groups():
    listtg = elbv2c.describe_target_groups()

    for tg in listtg["TargetGroups"]:
        print(
            "TG Name = {TargetGroupName}  "
            "ARN = {TargetGroupArn}".format(**tg))

# Delete ALB target group function


def delete_target_group():
    tgname = input("Enter the name of the target group: ").strip()
    tgarn = elbv2c.describe_target_groups(
        Names=[tgname])["TargetGroups"][0]["TargetGroupArn"]

    try:
        elbv2c.delete_target_group(TargetGroupArn=tgarn)
        print("Target group {} deleted.".format(tgname))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# Create a key pair function


def create_keypair():
    keyname = input("Enter the key pair name: ").strip()

    try:
        key = ec2c.create_key_pair(KeyName=keyname)
        print("\nKey pair created. The following is the key:\n")
        print(key["KeyMaterial"])
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# List key pairs


def list_keypair():
    listkey = ec2c.describe_key_pairs()
    dckey = {}

    for key in listkey["KeyPairs"]:
        print(
            "Key pair = {KeyName}, fingerprint = {KeyFingerprint}".format(
                **key))
        dckey[key["KeyName"]] = key["KeyFingerprint"]
    return(dckey)

# Delete a key pair


def delete_keypair():
    list_keypair()
    keyname = input("Enter the key pair name: ").strip()

    try:
        ec2c.delete_key_pair(KeyName=keyname)
        print("\nThe key pair {} was deleted.".format(keyname))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# Create S3 bucket function


def create_bucket():
    buckname = input("Enter the bucket name: ").strip()

    try:
        newbuck = s3c.create_bucket(
            Bucket=buckname,
            CreateBucketConfiguration={"LocationConstraint": region})
        print("\nBucket {Location} was created successfully.".format(
            **newbuck))
    except boto3.exceptions.botocore.exceptions.ParamValidationError as e:
        print(e)
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# Delete S3 bucket function


def delete_bucket():
    buckname = input("Enter the bucket name: ").strip()

    try:
        s3c.delete_bucket(Bucket=buckname)
        print("Bucket {} was deleted successfully.".format(buckname))
    except boto3.exceptions.botocore.exceptions.ParamValidationError as e:
        print(e)
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# List S3 buckets function


def list_buckets():
    listbuck = s3r.buckets.all()
    lb = []
    print("\nList of buckets:")
    for b in listbuck:
        print(b.name)
        lb.append(b.name)
    print("\nNumber of buckets: {}".format(len(lb)))
    return(lb)

# List S3 files function


def list_files():
    listfile = s3r.buckets.all()
    for buck in listfile:
        for obj in buck.objects.all():
            print("Bucket: {0}  File: {1}".format(buck.name, obj.key))
    return(listfile)

# Quit function


def quit():
    sys.exit(0)


if __name__ == "__main__":

    # Using dict as switch for calling menu items

    select_dict = {"csub": create_subnet,
                   "dsub": delete_subnet,
                   "lsub": list_subnets_all,
                   "imake": create_inst,
                   "istart": start_inst,
                   "istop": stop_inst,
                   "iterm": term_inst,
                   "ilist": list_inst,
                   "iren": ren_inst,
                   "calb": create_alb,
                   "lalb": list_alb,
                   "dalb": delete_alb,
                   "ctg": create_target_group,
                   "ltg": list_target_groups,
                   "dtg": delete_target_group,
                   "ckey": create_keypair,
                   "lkey": list_keypair,
                   "dkey": delete_keypair,
                   "cbuck": create_bucket,
                   "lbuck": list_buckets,
                   "dbuck": delete_bucket,
                   "ls": list_files,
                   "help": help_menu,
                   "h": help_menu,
                   "x": quit,
                   "exit": quit,
                   "quit": quit,
                   "q": quit,
                   }

# Print help menu

    help_menu()

# Action prompt routine

    while True:
        selection = action_prompt()
        try:
            select_dict[selection]()
        except KeyError:
            print("Invalid selection. Type 'help' for a list of commands")
