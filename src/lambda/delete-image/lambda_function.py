import json
import boto3
import os
import logging 
 
logger = logging.getLogger("Delete Image")
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

        if not image_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing imageId in request payload"})
            }

        # Fetch metadata from DynamoDB in order to delete from S3 bucket and DynamoDB table
        response = table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr("imageId").eq(image_id)
        )

        if not response["Items"]:
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Image not found"})
            }

        item = response["Items"][0]
        key = item["s3_key"]
        user_id = item["userId"]

        # Delete image from S3
        s3.delete_object(Bucket=BUCKET_NAME, Key=key)

        # Delete item from DynamoDB using imageid key
        table.delete_item(
            Key={
                "imageId": image_id,
                "userId": user_id
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Image deleted successfully",
                "imageId": image_id
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
