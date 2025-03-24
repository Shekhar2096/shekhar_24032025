# Shekhar_22032025
This repo has been created to complete a assessment. 

## Assessment:

You are developing the service layer of an application like Instagram. You are working
on a module which is responsible for supporting image upload and storage in the
Cloud. Along with the image, its metadata must be persisted in a NoSQL storage.
Multiple users are going to use this service at the same time. For this reason, the
service should be scalable.


 Tasks:
1. Create APIs for:
     Uploading image with metadata
     List all images, support at least two filters to search
     View/download image
     Delete an image

2. Write unit tests to cover all scenarios
3. API documentation and usage instructions

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Approach:   

# Create resources using Cloudformation Template

# 1. Create S3 bucket using IaaC to store images uploaded by user
    Bucket:
        Unique Name
        Encrypted bucket(using Amazon Managed Key)
        Enable Versioning

# 2. Create DynamoDB table to store metadata of images uploaded by user.
    Table:
        Take care of Partition Key and Sort key during the time of table create. Also Create Secondary index as user can filter images based on location or tags. 

# 3.  Lambda FUnctions for asked functionality.  
    1. Upload Imagge
        Considering image size is less than 10MB as API gateways has payload limit for 10 MB. 

    2. List images with filters.
        Considering filter for now location and tag
    
    3. View or Download : Getimages Lambda
        It should give a download pre-signed URL to user in order to download the images. The expiration time for URL is 10 mins.

    4. Delete image Lambda function
        Based on image id in payload it should delete the image from S3 bucket as well as delete the metadata from DynamoDB table.

# 4. API Gateway:
    Create API Gateway using IaaC and create resources like 
        /uploadImage : Method POST
        /filterImages  : Method GET || Parameter: location and tag
        /downloadImage : Method GET || Parameter: imageId
        /deleteImage:  Method DELETE || Parameter: imageId

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## API Deign:

# 1. Upload Image
    URL: /uploadImage
    Method: POST

    Body:
    {
      "image_base64": "<base64-encoded-image>",
      "metadata": {
        "userId": "Shekhar",
        "tag": "vacation",
        "location": "Pune"
      }
    }

    Success Response (200):

    {
      "message": "Image uploaded successfully",
      "imageId": "S3 bucket image id Key"
    }



# 2. filter Images 
    URL: /filterImages
    Method: GET
    
    Query Parameters (optional):
    tag
    location
    Examples:
    /filterImages → returns all images
    /filterImages?tag=sunset
    /filterImages?location=Goa
    /filterImages?location=Goa&tag=vacation
    
    Success Response:
    {
      "count": 2,
      "results": [
        {
          "imageId": "...",
          "userId": "Shekhar",
          "tag": "vacation",
          "location": "Goa",
          "s3_key": "S3 bucket image id Key"
        },
        ...
      ]
    }

# 3. Download Image
    URL: /downloadImage/{imageId}
    Method: GET

    Path Parameter:
    imageId – the full ID of the image

    Response:
    {
      "download_url": "S3 Pre-signed URL""
      "message": "Use this URL to download the image. Link is valid for 10 minutes."
    }

# 4. Delete Image
    URL: /deleteImage
    Method: DELETE
    Body:
    {
      "imageId": "Image Id" # Basically its s3 key
    }
    Response:
    {
      "message": "Image deleted successfully",
      "imageId": "s3 bucket image Id key"
    }

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Functionality to Test

# 1. Image Upload (/uploadImage)
    Code Validation: In the Lambda function, we have wrapped the S3 and DynamoDB operations inside a try-except block to ensure any boto3 errors are  handled.
    What to Test:
        Verify that the image is successfully uploaded to the S3 bucket.
        Check that metadata is properly stored in the DynamoDB table.
        Validate the response includes the generated imageId.

# 2. filter Images (/filterImages)
    What to Test:
        When a user applies filters like tag or location, only matching images should be returned in the response.
        If no filter is passed, it should return all available images.
        Validate filtering combinations (tag only, location only, both tag and location).

# 3. Download Image (/downloadImage/{imageId})
    What to Test:
        Ensure that a pre-signed S3 URL is successfully generated for the given imageId.
        Validate that the user can download the image using that URL within the allowed time frame (10 minutes).
        After the pre-signed URL expires, confirm that trying to access it returns an error (invalid or expired link).

# 4. Delete Image (/deleteImage)
    What to Test:
        When a valid imageId is passed, the image should be deleted from both S3 and DynamoDB.
        Verify that the item is no longer present in the DynamoDB table.
        Attempting to download the image after deletion should result in a 404 or “not found” error.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## To Scale this application:

1. Let users upload images directly to S3 instead of sending them through the API.
2. Use SQS to queue image uploads and process them in the backend asynchronously.
3. Each feature has its own Lambda, so they can scale independently and are easier to manage.
4. We can increase lambda timeout and memory based on image size and processing time.
5. Also set the provisioned reserved cuncurrenncy. Helps handle more traffic without throttling (but may increase cost).
6. For filterimage endpoint as it can retrun multiple value in response we can use pagination.
6. We can use cloudwatch to track issues early and respond before they impact users.

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Deployment:

## 1. Install AWS CLI
## 2. Install SAM CLI
###     sam build
###     sam deploy --stack-name ABC --role-arn arn:aws:iam::986559698146:role/ShekharCFTAdminRole --region ap-south-1 --capabilities CAPABILITY_NAMED_IAM --s3-bucket shekhar-deployment-code-lambda-986559698146



## https://jyma00auf0.execute-api.ap-south-1.amazonaws.com/v1/upload

## https://jyma00auf0.execute-api.ap-south-1.amazonaws.com/v1/download?imageId=20250323074319872613_0f546889-9f79-43c6-80e3-563d04e4e32d&userId=Shekhar

## https://jyma00auf0.execute-api.ap-south-1.amazonaws.com/v1/delete?imageId=20250323074319872613_0f546889-9f79-43c6-80e3-563d04e4e32d&userId=Shekhar

## https://jyma00auf0.execute-api.ap-south-1.amazonaws.com/v1/filter?location=Goa&tag=vacation