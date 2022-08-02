import os

import boto3

os.environ["AWS_PROFILE"] = "personal"

s3_client = boto3.resource("s3")
rekognition_client = boto3.client("rekognition")

COLLECTION_ID = "faces"
FACES_BUCKET_NAME = "fa-imagens-jovi-course"


def list_images(bucket_name: str):
    """
    List all keys from objects in a bucket
    """
    bucket = s3_client.Bucket(bucket_name)

    return [image.key for image in bucket.objects.all()]


def indexes_collection(images: list):
    """
    Indexes the images in the collection
    """
    for image in images:
        rekognition_client.index_faces(
            CollectionId=COLLECTION_ID,
            DetectionAttributes=[],
            ExternalImageId=image[:-4],
            Image={
                "S3Object": {
                    "Bucket": FACES_BUCKET_NAME,
                    "Name": image,
                }
            },
        )


if __name__ == "__main__":
    images = list_images(bucket_name=FACES_BUCKET_NAME)
    indexes_collection(images)
