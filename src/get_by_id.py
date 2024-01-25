import json
import uuid
import boto3
import os
import secrets
from aws_lambda_powertools import Tracer
from aws_lambda_powertools.utilities.typing import LambdaContext

URL_TABLE = os.getenv("URL_TABLE", None)
dynamodb = boto3.resource('dynamodb')
ddbTable = dynamodb.Table(URL_TABLE)
# Reuse Boto3 client outside the handler
dynamodb_client = boto3.client('dynamodb')
# Reuse tracer outside the handler
tracer = Tracer()
# Initialize headers outside the handler
headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*'
}


@tracer.capture_lambda_handler
def lambda_handler(event, context):
    route_key = f"{event['httpMethod']} {event['resource']}"

    try:
        if route_key == "GET /getbyuserid/{id}":

            user_id = "user#"+str(event['pathParameters']['id'])  

            response=ddbTable.query(
                IndexName="GSI1PK-GSI1SK-index",
                KeyConditionExpression="GSI1PK=:gsi1pk",
                ExpressionAttributeValues={
                    ":gsi1pk":user_id
                }
            )
            status_code=200


            if "Items" in response:
                response_body=response["Items"]
                status_code = 200
            else:
                status_code=404
                response_body={ "Error":"No item found"}
    except Exception as err:
        status_code = 400
        response_body = {'Error': str(err)}
        print(str(err))

    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }