import os
import boto3
import uuid
from dotenv import load_dotenv

load_dotenv()

AWS_PROFILE = os.getenv("AWS_PROFILE")
AWS_REGION = os.getenv("AWS_REGION")
HARNESS_ARN = os.getenv("HARNESS_ARN")

client_session = boto3.Session(
    profile_name=AWS_PROFILE
)

client = client_session.client(
    "bedrock-agentcore",
    region_name=AWS_REGION
)

response = client.invoke_harness(
    harnessArn='arn:aws:bedrock-agentcore:us-east-2:370401801748:harness/LogiBot-zw2HeRgZgd',
    runtimeSessionId=str(uuid.uuid4()),
    messages=[
        {
            'role': 'user',
            'content': [{'text': 'Qual o notebook mais barato?'}]
        }
    ]
)

for event in response['stream']:
    if 'contentBlockDelta' in event:
        delta = event['contentBlockDelta'].get('delta', {})
        if 'text' in delta:
            print(delta['text'], end='')
print()