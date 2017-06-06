# AWS Project for UW PCE Python 300 class

The intent of this project is to utilize Python to administer resources in Amazon Web Services (AWS)
With these tools, you can perform such functions as:

* Create, list, and delete subnets in the VPC
* Create, list, and delete S3 buckets. Also list the files in the buckets
* Create, list, and rename EC2 instances
* Start, stop, and terminate EC2 instances
* Create, list, and delete EC2 keypair
* Create, list and delete Application Load Balancers

There are two main files for this project: `awstool.py` and `awsclass.py`.

Both programs require certain default values to be added to the `credentials` file that is located in 
the `<home>/.aws` directory. These values are as follows:

```
[default]
region = <The AWS region of your account. Example: us-west-2>
aws_access_key_id = <The AWS acceess key ID of your account>
aws_secret_access_key = <The AWS secret access key of your account>
vpc = <The VPC ID of the VPC that you wish to control>
secgroup = <The security group used for EC2 resources>
ami = <The Amazon AMI image to be used for EC2 instances. Example: ami-4836a428>
ec2type = <The EC2 instance type to be used for creating instances. Example: t2-micro>
```

## awstool.py

This is a command-line utility


:pouting_cat: