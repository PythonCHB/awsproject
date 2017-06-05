#!/usr/bin/env python3

from awsclass import Aws

d = Aws()

print("\n** Creating key pair **")
mykey = d.create_keypair("webkey")

print("\n** Creating subnets **")
sub1 = d.create_subnet("10.94.11.0/24", "us-west-2a")
sub2 = d.create_subnet("10.94.111.0/24", "us-west-2b")
sub3 = d.create_subnet("10.94.211.0/24", "us-west-2c")

print("\n** Creating instances **")
inst1 = d.create_inst(sub1, mykey, "web-2a")
inst2 = d.create_inst(sub2, mykey, "web-2b")
inst3 = d.create_inst(sub3, mykey, "web-2c")

print("\n** Creating ALB target group **")
tg = d.create_target_group("web-tg", inst1, inst2, inst3)

print("\n** Creating Application Load Balancer **")
alb = d.create_alb("web-alb", sub1, sub2, sub3, tg)
