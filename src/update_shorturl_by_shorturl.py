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

            print(request_json)

            short_url = str(event['pathParameters']['shorturl'])  


            pk = f'shorturl#{short_url}'
            sk = f'shorturl#{short_url}'

            update_expression = 'SET '
            expression_attribute_values = {}

            for attribute_name, new_value in request_json.items():
                update_expression += f"{attribute_name} = :{attribute_name}, "
                expression_attribute_values[f":{attribute_name}"] = new_value

            if 'user_id' in request_json:
                update_expression+='GSI1PK=:gsi1pk, '
                expression_attribute_values[':gsi1pk'] = f"user#{request_json['user_id']}"

            update_expression = update_expression[:-2]
            print("Update expression",update_expression)


            



            response = ddbTable.update_item(
                Key={
                    'pk': pk,
                    'sk': sk
                },
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues="ALL_NEW"
            )

            response_body = json.loads(json.dumps(response['Attributes'], default=str))
            status_code = 200

    except Exception as err:
        status_code = 400
        response_body = {'Error': str(err)}
        print(str(err))

    return {
        'statusCode': status_code,
        'body': json.dumps(response_body),
        'headers': headers
    }