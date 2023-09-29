import boto3
import time

ec2_client = boto3.client('ec2')

start_time = time.time()

security_groups = ec2_client.describe_security_groups()['SecurityGroups']

for sg in security_groups:
    group_id = sg['GroupId']
    
    enis = ec2_client.describe_network_interfaces(Filters=[{'Name': 'group-id', 'Values': [group_id]}])['NetworkInterfaces']
    
    if not enis:
        name = sg['GroupName']
        print(f"Security Group ID: {group_id}, Name: {name}")


end_time = time.time()
execution_time = end_time - start_time


print(f"Tempo de execução: {execution_time} segundos")
