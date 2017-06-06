#!/usr/bin/env python3

# Sample build/delete script to use with awsclass.py
# This will build an AWS Application Load Balancer consisting of three EC2
# instances.

# Import modules

from awsclass import Aws
import time

# Instantiate the class

casey = Aws()

# Create an EC2 key pair

print("\n** Creating key pair **")
mykey = casey.create_keypair("webkey")

# Create the subnets where the EC2 instances will exist

print("\n** Creating subnets **")
sub1 = casey.create_subnet("10.94.11.0/24", "us-west-2a")
sub2 = casey.create_subnet("10.94.111.0/24", "us-west-2b")
sub3 = casey.create_subnet("10.94.211.0/24", "us-west-2c")

# Create the EC2 instances using the created key pair and the subnets

print("\n** Creating instances **")
inst1 = casey.create_inst(sub1, mykey, "web-2a")
inst2 = casey.create_inst(sub2, mykey, "web-2b")
inst3 = casey.create_inst(sub3, mykey, "web-2c")

# Create the ALB target group

print("\n** Creating ALB target group **")
tg = casey.create_target_group("web-tg", inst1, inst2, inst3)

# Create the Application Load Balancer

print("\n** Creating Application Load Balancer **")
alb = casey.create_alb("web-alb", sub1, sub2, sub3, tg)

# Pause before deleting the infrastructure

print("Now ready to delete the infrastructure")
input("Press Enter to continue...")

# Delete the Application Load Balancer

print("\n** Deleting Application Load Balancer **")
dalb = casey.delete_alb("web-alb")
time.sleep(20)

# Delete the ALB target group

print("\n** Deleting ALB target group **")
dtg = casey.delete_target_group("web-tg")

# Terminate the EC2 instances

print("\n** Terminating instances **")
dinst1 = casey.term_inst(inst1)
dinst2 = casey.term_inst(inst2)
dinst3 = casey.term_inst(inst3)

# Delete the subnets

print("\n** Deleting subnets **")
dsub1 = casey.delete_subnet(sub1)
dsub2 = casey.delete_subnet(sub2)
dsub3 = casey.delete_subnet(sub3)

# Delete the EC2 key pair
print("\n** Deleting keypair **")
dkey = casey.delete_keypair(mykey)
