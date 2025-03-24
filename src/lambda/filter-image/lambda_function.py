import json
import boto3
import os
from boto3.dynamodb.conditions import Attr
import logging 
print(1)
logger = logging.getLogger("Filter Image")
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        logger.info(f'Lambda is running for following event: {event}')
        location = event.get("queryStringParameters", {}).get("location")
        tag = event.get("queryStringParameters", {}).get("tag")

        item = {
            "imageId": "sweta_20250323_img2",
            "userId": "sweta123",
            "tag": "vacation",
            "location": "Goa",
            "s3_key": "sweta_20250323_img2.jpg"
        }

        response = table.put_item(Item=item)

        filter_expr = None

        '''
        this can also be optimized based on like condition for example 
        user typed Ind he can see India , Indonesia or other starting with Ind...
        '''
    
        if location:
            filter_expr = Attr("location").eq(location)
        if tag:
            tag_expr = Attr("tag").contains(tag)
            filter_expr = tag_expr if not filter_expr else filter_expr & tag_expr

        # Scan with or without filters
        if filter_expr:
            response = table.scan(FilterExpression=filter_expr)
        else:
            response = table.scan()
        return {
            "statusCode": 200,
            "body": json.dumps({
                "results": response["Items"],
                "count": len(response["Items"])
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
