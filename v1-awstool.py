#!/usr/bin/env python3

""" AWS Configuration Tool by Paul Casey

This program is a menu-driven AWS utility that performs the following:

- Create, list, and delete subnets in the VPC
- Create, list, and delete S3 buckets. Also list the files in the buckets
- Create, list, and rename EC2 instances
- Start, stop, and terminate EC2 instances

"""

# Import Modules
import boto3
# import pprint
# import sys
# from textwrap import dedent
# import json

# Set the "resource" and "client" variables for EC2 and S3

ec2 = boto3.resource("ec2", region_name="us-west-2")
ec2c = boto3.client("ec2", region_name="us-west-2")
s3 = boto3.resource("s3", region_name="us-west-2")
s3c = boto3.client("s3", region_name="us-west-2")

# Insert your VPC ID on this line

vpc = ec2.Vpc("vpc-8089aee4")

# Main prompt


# def action_prompt():
#     action = input("==> ")
#     return action.strip()

# Create VPC subnet


def create_subnet(subnetvar, az):
    try:
        newsub = vpc.create_subnet(CidrBlock=subnetvar, AvailabilityZone=az)
        print("\nThe subnet ID created was {}".format(newsub.id))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# Delete VPC subnet


def delete_subnet(subid):
    try:
        ec2c.delete_subnet(SubnetId=subid)
        print("\nThe subnet {} was deleted.".format(subid))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# List VPC subnets


def list_subnets():
    listsub = ec2c.describe_subnets()

    for sub in listsub["Subnets"]:
        print("Subnet ID = {} with CIDR of {} in AZ {} with {} available IPs".format(sub["SubnetId"], sub["CidrBlock"], sub["AvailabilityZone"], str(sub["AvailableIpAddressCount"])))
    return listsub

# Create new EC2 instances


def create_inst(subid, instname):
    try:
        newinst = ec2.create_instances(ImageId="ami-b04e92d0", MinCount=1, MaxCount=1, InstanceType="t2.micro", SecurityGroupIds=["sg-3b319442"], SubnetId=subid)
        ec2c.create_tags(Resources=[newinst[0].id], Tags=[{"Key": "Name", "Value": instname}])
        print("\nThe instance ID created was {} and is named {}".format(newinst[0].id, instname))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

    # return newinst

# Start and stop EC2 instances


def start_inst(instid):
    try:
        ec2c.start_instances(InstanceIds=[instid])
        print("Started instance {}".format(instid))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))
    # return(pprint.pprint(ec2c.start_instances(InstanceIds=[instid])))


def stop_inst(instid):
    try:
        ec2c.stop_instances(InstanceIds=[instid])
        print("Stopped instance {}".format(instid))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# Terminate EC2 instances


def term_inst(instid):
    try:
        ec2c.terminate_instances(InstanceIds=[instid])
        print("Terminated instance {}".format(instid))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))


# List EC2 instances


def list_inst():
    listinst = ec2.instances.all()
    for i in listinst:
        print("ID: {0}  Name: {1}  Type: {2}  State: {3}".format(i.id, i.tags[0]["Value"], i.instance_type, i.state["Name"]))
    return(listinst)

# Rename an EC2 instance


def ren_inst(instid, newname):
    try:
        ec2c.create_tags(Resources=[instid], Tags=[{"Key": "Name", "Value": newname}])
        print("The instance was renamed to {}".format(newname))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# Create S3 bucket


def create_bucket(buckname):
    try:
        newbuck = s3c.create_bucket(Bucket=buckname)
        print("\nBucket {} was created successfully.".format(newbuck["Location"]))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# Delete S3 bucket


def delete_bucket(buckname):
    try:
        s3c.delete_bucket(Bucket=buckname)
        print("Bucket {} was deleted successfully.".format(buckname))
    except boto3.exceptions.botocore.client.ClientError as e:
        print(e.response["Error"]["Message"].strip("\""))

# List S3 buckets


def list_buckets():
    listbuck = s3.buckets.all()
    print("\nList of buckets:")
    for b in listbuck:
        print(b.name)
    return(listbuck)

# List S3 files


def list_files():
    listfile = s3.buckets.all()
    for buck in listfile:
        for obj in buck.objects.all():
            print("Bucket: {}  File: {}".format(buck.name, obj.key))
    return(listfile)

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
Type 'cbuck' to create an S3 bucket
Type 'dbuck' to delete an S3 buckets
Type 'lbuck' to list the S3 buckets
Type 'ls' to list all S3 files
Type 'x' to exit

"""


def main():

    resp = ""
    print(intro)
    while True:
        resp = input("==> ").strip().lower()

        if resp == "csub":
            sub = input("Enter the subnet: ").strip()
            whichaz = input("Enter the availability zone: ").strip()
            create_subnet(sub, whichaz)
        elif resp == "dsub":
            sub = input("Enter the subnet ID: ").strip()
            delete_subnet(sub)
        elif resp == "lsub":
            list_subnets()
        elif resp == "imake":
            sub = input("Enter the subnet ID: ").strip()
            name = input("Enter the name: ").strip()
            create_inst(sub, name)
        elif resp == "istart":
            inst = input("Enter the instance ID: ").strip()
            start_inst(inst)
        elif resp == "istop":
            inst = input("Enter the instance ID: ").strip()
            stop_inst(inst)
        elif resp == "iterm":
            inst = input("Enter the instance ID: ").strip()
            term_inst(inst)
        elif resp == "ilist":
            list_inst()
        elif resp == "iren":
            inst = input("Enter the instance ID: ").strip()
            name = input("Enter the new name: ").strip()
            ren_inst(inst, name)
        elif resp == "cbuck":
            buck = input("Enter the bucket name: ").strip()
            create_bucket(buck)
        elif resp == "dbuck":
            buck = input("Enter the bucket name: ").strip()
            delete_bucket(buck)
        elif resp == "lbuck":
            list_buckets()
        elif resp == "ls":
            list_files()
        elif resp == "x" or resp == "quit" or resp == "q" or resp == "exit":
            break
        elif resp == "help":
            print(intro)
        else:
            print("Enter a command. Type 'help' for a list of commands.")

if __name__ == "__main__":
    main()
