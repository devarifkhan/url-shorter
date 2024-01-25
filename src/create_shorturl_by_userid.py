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
        if route_key == "POST /addurl/{userid}":
            request_json = json.loads(event['body'])
            user_id = str(event['pathParameters']['userid'])  
            user_id_with_hash="user#"+user_id

            print(request_json,user_id)



            # user_id = str(uuid.uuid1())
            user_id = user_id
            short_url = str(secrets.token_hex(16))
            pk = f'shorturl#{short_url}'
            sk = f'shorturl#{short_url}'
            GSI1PK = user_id_with_hash
            GSI1SK = f'shorturl#{short_url}'
            original_url = request_json['url']

            # Use batch_writer to perform batch operations on DynamoDB
            with ddbTable.batch_writer() as batch:
                batch.put_item(Item={
                    'pk': pk,
                    'sk': sk,
                    'original_url': original_url,
                    'user_id': user_id,
                    'GSI1PK': GSI1PK,
                    'GSI1SK': GSI1SK,
                    'short_url': short_url

                })
                status_code = 201

                response_body = {
                    'pk': pk,
                    'sk': sk,
                    'original_url': original_url,
                    'user_id': user_id,
                    'GSI1PK': GSI1PK,
                    'GSI1SK': GSI1SK,
                    'short_url': short_url
                }

    except Exception as err:
        status_code = 400
        response_body = {'Error': str(err)}
        print(str(err))

    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }