import os
import uuid
import boto3
from dotenv import load_dotenv

load_dotenv()


def perguntar(pergunta):
    aws_profile = os.getenv("AWS_PROFILE")
    aws_region = os.getenv("AWS_REGION")
    harness_arn = os.getenv("HARNESS_ARN")

    session = boto3.Session(profile_name=aws_profile)

    client = session.client(
        "bedrock-agentcore",
        region_name=aws_region
    )

    response = client.invoke_harness(
        harnessArn=harness_arn,
        runtimeSessionId=str(uuid.uuid4()),
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "text": pergunta
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