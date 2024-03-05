import boto3
import json
import time
client = boto3.client('sagemaker')

import subprocess

# Construct the command with arguments and output redirection
command = ["streamlit", "run", "chat-bedrock.py"]
with open("streamlit-log.txt", "w") as logfile:
    # Run the command in the background, redirecting stdout to the logfile
    subprocess.Popen(command, stdout=logfile, stderr=subprocess.STDOUT)


time.sleep(5)

with open("streamlit-log.txt","r") as f:
    content=f.read()
    #print(content)

import re

# Extract the Network URL using regular expressions
pattern = r"Network URL: (http://.*)"
match = re.search(pattern, content)

if match:
    network_url = match.group(1)
    print(f"Network URL: {network_url}")
    port_number = network_url.split(':')[2]
    print(f"port number: {port_number}")
else:
    print("Network URL not found in the provided content.")



with open("/opt/ml/metadata/resource-metadata.json", "r") as f:
    data = json.load(f)
    domainId = data['DomainId']
    spaceName = False #data['SpaceName']
    resourceArn=data['ResourceArn']
    resourceName=data['ResourceName']
    region=resourceArn.split(":")[3]
    
    print(data)

#json.loads

if spaceName:
    response = client.describe_space(DomainId = domainId, 
                          SpaceName=spaceName)
    print("hello world!!!!!!")
    url =  response['Url']
    streamlit_url = url+f"/proxy/{port_number}/"
else:
    #build studio url
    streamlit_url=f"https://{domainId}.studio.{region}.sagemaker.aws/jupyter/{resourceName}/proxy/{port_number}/"


print(f"click the url to launch UI: {streamlit_url}")