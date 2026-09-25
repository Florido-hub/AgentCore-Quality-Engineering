import os
import uuid
import boto3
from dotenv import load_dotenv

load_dotenv()

aws_profile = os.getenv("AWS_PROFILE")
aws_region = os.getenv("AWS_REGION")
harness_arn = os.getenv("HARNESS_ARN")

session = boto3.Session(profile_name=aws_profile)

client = session.client(
    "bedrock-agentcore",
    region_name=aws_region
)

session_id = str(uuid.uuid4())

def perguntar(input_data):
    if isinstance(input_data, str):
        turnos = [input_data]
    else:
        turnos = input_data

    resposta = ""

    for turno in turnos:
        response = client.invoke_harness(
            harnessArn=harness_arn,
            runtimeSessionId=session_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "text": turno
                        }
                    ]
                }
            ]
        )

        resposta = ""

        for event in response["stream"]:
            if "contentBlockDelta" in event:
                delta = event["contentBlockDelta"].get("delta", {})

                if "text" in delta:
                    resposta += delta["text"]

    return resposta