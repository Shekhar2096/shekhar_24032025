import json
import boto3
import uuid
import base64
import os
import datetime 
import logging 

logger = logging.getLogger("Upload Image")
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

# Taking this data from Environment variable to make it parametrized.
TABLE_NAME = os.environ["TABLE_NAME"]
BUCKET_NAME = os.environ["BUCKET_NAME"]

table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        '''
        I am considering user is manually seding the metadata having required columns we created
        in DynamoDB Table. In real world secnario it can be auto generated using some AI Capabilities.

        '''

        logger.info(f'Lambda is running for following event: {event}')

        body = json.loads(event['body'])
        image_base64 = body['image_base64']
        
        if image_base64.startswith("data:image"):        
            image_base64 = image_base64.split(",")[1]

        image_data = base64.b64decode(image_base64)

        metadata = body.get('metadata', {})

        # adding timestamp for uniquesness of imageid everytime
        timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        image_id = f"{timestamp}_{uuid.uuid4()}"

        key = f"{image_id}.jpg"
        # Upload image to S3
        response = s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=image_data)

        # Storing metadta in DynaoDB table for given request,
        item = {
            "imageId": image_id,
            "userId": metadata.get("userId", "Unknown"),
            "tag": metadata.get("tag", "Unknown"),
            "location": metadata.get("location", "Unknown"),
            "s3_key": key
        }

        response = table.put_item(Item=item) 

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Image uploaded successfully",
                "imageId": image_id
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e)
            })
        }
