
# Overview

This Python API allows to upload user pictures to remote storage, download them to user file system and delete them from remote storage.

# Start using
## Uploading pictures

To upload picture use the next command:
```
curl -s -X POST -F "file=@<path/to/image>" <Load-Balancer-DNS-Name>:5000/
```
Or to upload multiple pictures:
```
curl -s -X POST -F "file=@<path/to/image1>" -F "file=@<path/to/image2>" <Load-Balancer-DNS-Name>:5000/
```

If everything is ok you will receive the message **Uploaded**.

## Downloading picture 

To download picture use:
```
curl -s -X GET -o <path/to/save> -F "name=<username>" <Load-Balancer-DNS-Name>:5000/
```

## Deleting picture

To delete picture use the command:
```
curl -s -X DELETE -F "name=<username>" <Load-Balancer-DNS-Name>:5000/
```

If deletion was successful you will see ***picture-name* deleted**.

## Deleting all pictures

To make bucket empty use:
```
curl -s -X DELETE <Load-Balancer-DNS-Name>:5000/delete-all-pictures
```

If deletion was successful you will see **Pictures deleted**.

# Source code

## - app/app.py

The main code is written using Flask framework. It takes GET, POST and DELETE requests and handles them.

## - cf_template.yaml

Cloudformation template which creates VPC, S3 bucket, Auto Scaling Group, Load Balancer and other additional resouces. It takes four parameters: Commit ID for versioning Docker image, VPC CIDR block, CIDR blocks of the first and the second subnets.

VPC is based in eu-west-1 region and has two public subnets in eu-west-1a and eu-west-1b availability zones.

Auto scaling group uses LaunchConfiguration to configure EC2 instances. Instances in the Auto Scaling group have security group with inbound traffic on 22 and 5000 ports and all outbound traffic. To connect to instance over 22 port ssh key pair was already created. Instances have special permissions to S3 bucket that described in Role Policy.

Application Load Balancer listens 5000 port and distributes incoming traffic across the EC2 instances.

## - Dockerfile

The base image is python:rc-alpine. It installs flask, boto3 and awscli for the application, runs the application code and checks every 15 minutes if the app is healthy.

## - Makefile

Makefile has targets that check the python code, builds images with latest and GIT_COMMIT tags, pushes them to the Docker Hub Registry and deletes them from the local. Also there is a target which updates aws stack.

## - Jenkinsfile_build

This Jenkinsfile is needed for the project build. It runs the lint_py, build, push, clean targets from Makefile.

## - Jenkinsfile_deploy

This Jenkinsfile is needed for the project deploy. It runs the update_stack target from Makefile.