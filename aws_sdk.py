import boto3
AWS_REGION = 'eu-west-1'
EC2_RESOURCE = boto3.resource('ec2', region_name=AWS_REGION)
instances = EC2_RESOURCE.instances.all()

def get_ec2_instances():
    for instance in instances:
        return instance.public_ip_address

