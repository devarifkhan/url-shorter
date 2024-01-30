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
        if route_key == "PUT /update/shorturl/{shorturl}":
            request_json = json.loads(event['body'])
            short_url = str(event['pathParameters']['shorturl'])  
            short_url_with_hash="shorturl#"+short_url

            print(request_json,user_id)



            # user_id = str(uuid.uuid1())
            user_id = str(uuid.uuid1())
            pk = f'shorturl#{short_url}'
            sk = f'shorturl#{short_url}'
            GSI1PK =  f'user#{user_id}'
            GSI1SK = short_url_with_hash
            original_url = request_json['url']




            response = ddbTable.update_item(
                Key={
                    'pk': pk,
                    'sk': sk
                },
                UpdateExpression="SET original_url = :original_url,user_id= :user_id,GSI1PK= :GSI1PK,GSI1SK= :GSI1SK,short_url= :short_url ",
                ExpressionAttributeValues={
                    ':original_url': original_url,
                    ':user_id':user_id,
                    ':GSI1PK':GSI1PK,
                    ':GSI1SK':GSI1SK,
                    ':short_url':short_url

                },
                ReturnValues="ALL_NEW"
            )

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