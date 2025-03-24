import boto3
import json
import os
import logging 

logger = logging.getLogger("Download Image")
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

TABLE_NAME = os.environ["TABLE_NAME"]
BUCKET_NAME = os.environ["BUCKET_NAME"] 

table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        logger.info(f'Lambda is running for following event: {event}')
        image_id = event.get("queryStringParameters", {}).get("imageId")
        user_id = event.get("queryStringParameters", {}).get("userId")

        # For given image id in parameter , get item from DynaoDB table
        response = table.get_item(Key={"imageId": image_id, "userId": user_id})
        print(response)
        if "Item" not in response:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Image not found"})
            }

        key = response["Item"]["s3_key"]

        # Generate a pre-signed URL for download so that using this pre-signed URL user can download image
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': BUCKET_NAME, 'Key': key},
            ExpiresIn=600   
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "download_url": presigned_url,
                "message": "Use this URL to download the image. Link is valid for 10 minutes."
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
