import json
import os

import boto3

os.environ["AWS_PROFILE"] = "personal"

COLLECTION_ID = "faces"
FACES_BUCKET_NAME = "fa-imagens-jovi-course"
SITE_BUCKET_NAME = "fa-site-jovi-course"

rekognition_client = boto3.client("rekognition")
s3_client = boto3.resource("s3")
bucket = s3_client.Bucket(FACES_BUCKET_NAME)


def detect_faces():
    """
    Identifies the present faces on the image
    """
    return rekognition_client.index_faces(
        CollectionId=COLLECTION_ID,
        DetectionAttributes=["DEFAULT"],
        ExternalImageId="temporary",
        Image={
            "S3Object": {
                "Bucket": FACES_BUCKET_NAME,
                "Name": "_analysis.jpg",
            }
        },
    )


def create_list_from_detected_faces(detected_faces):
    """
    Creates a list of face ids from the detected faces
    """
    return [face["Face"]["FaceId"] for face in detected_faces["FaceRecords"]]


def compare_images(detected_face_ids):
    """
    Compares the detected faces with the faces in the collection
    """
    return [
        rekognition_client.search_faces(
            CollectionId=COLLECTION_ID,
            FaceId=_id,
            FaceMatchThreshold=80,
            MaxFaces=10,
        )
        for _id in detected_face_ids
    ]


def extract_data_to_json(comparision_result):
    """
    Extracts the data from the comparison result to a json format
    """
    return [
        dict(
            nome=face_match["FaceMatches"][0]["Face"]["ExternalImageId"],
            similarity=round(face_match["FaceMatches"][0]["Similarity"], 2),
        )
        for face_match in comparision_result
    ]


def publish_data(json_data):
    """
    Publishes the data to the S3 bucket
    """
    file = s3_client.Object(SITE_BUCKET_NAME, "dados.json")
    file.put(Body=json.dumps(json_data))


def delete_detected_faces(detected_face_ids):
    """
    Deletes the detected faces from the collection
    """
    rekognition_client.delete_faces(
        CollectionId=COLLECTION_ID,
        FaceIds=detected_face_ids,
    )


# if __name__ == "__main__":
def main(event, context):
    print("Started")
    detected_faces = detect_faces()
    detected_face_ids = create_list_from_detected_faces(detected_faces)
    comparision_result = compare_images(detected_face_ids)
    extracted_data = extract_data_to_json(comparision_result)
    publish_data(extracted_data)
    delete_detected_faces(detected_face_ids)
    print("Finished")
