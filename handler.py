import logging
import os
import sys
import json
from google.cloud import vision
from google.cloud.vision import types
from google.protobuf.json_format import MessageToDict

here = os.path.dirname(os.path.realpath(__file__))
credentials_json = os.path.join(here, "google-application-credentials.json")


def get_vision_client():
    client = vision.ImageAnnotatorClient.from_service_account_json(credentials_json)
    return client


def ocr_image(image_url):
    client = get_vision_client()
    res = client.document_text_detection({'source': {'image_uri': image_url}}, timeout=5.0)
    data = MessageToDict(res).get('textAnnotations', None)
    response = {
        "statusCode": 200,
        "body": json.dumps(data)
    }
    return response


def lambda_handler(event, context):
    """AWS Lambda Handler for API Gateway input"""
    post_args = json.loads(event.get("body", {}))
    image_url = post_args["image_url"]

    logging.debug("Detecting image from URL: %s" % image_url)

    response = ocr_image(image_url)
    return response
