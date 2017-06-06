# AWS Project for UW PCE Python Py300 class

The intent of this project is to utilize Python to administer resources in Amazon Web Services (AWS)
With these tools, you can perform such functions as:

* Create, list, and delete subnets in the VPC
* Create, list, and delete S3 buckets. Also list the files in the buckets
* Create, list, and rename EC2 instances
* Start, stop, and terminate EC2 instances
* Create, list, and delete EC2 keypair
* Create, list and delete Application Load Balancers

The programs use Python 3 with a module from Amazon called `boto3` which allows interfacing with
AWS resources via Python.

There are two main files for this project: `awstool.py` and `awsclass.py`.

Both programs require certain default values to be added to the `credentials` file that is located in 
the `<home>/.aws` directory. This file will already exist after running the `aws configure`
command and will create the first three values. The other values can be added manually after the
file is created.
The required values are as follows:

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

This is a command-line utility that will perform all the above-specified functions in AWS.
The program begins with showing a help menu with available commands. Some functions require input
that is required for that particular command. I find myself using this tool in my day-to-day
functions at my job.

## awsclass.py

This file contains the `Aws()` class that takes the functions from `awstool.py` and makes them
available in a class format. With these methods, one can easily orchestrate the creation and
deletion of AWS objects. An example can be found in the `buildalb.py` file. This file will create
the building blocks of an Application Load Balancer and then delete the elements. Clearly, these
elements could be more easily created with CloudFormation and a well-crafted JSON file, but this
project provided a good learning experience for using Python.

## Lessons learned and challenges faced

* With boto3, there are some redundant classes that causes confusion. An example would be for EC2,
where EC2 Client and EC2 Resource classes exist, and both allow the creation of EC2 instances
* Some resources can't be built until its dependent resources are fully online. For those situations,
the use of a Waiter function is helpful. An example is for creating an ALB target group. The target
group can't be created until the required instances are in a "running" state. The Waiter function
will pause the program until the instances reach that state.
* The output of the methods is usually some lengthy JSON output, so it took patience to sift
through the output to grab the values that were relevant to what I was trying to achieve.




:pouting_cat: