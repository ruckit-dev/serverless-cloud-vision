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
    ocr_result = MessageToDict(res)
    text_annotations = ocr_result.get('textAnnotations', [])
    ocr_result_text = [item.get('description', '') for item in text_annotations]
    response = {
        "attachment": image_url,
        "ocr_result": {
            "responses": [
                ocr_result
            ]
        },
        "ocr_result_text": ocr_result_text
    }
    return response


def lambda_handler(event, context):
    """AWS Lambda Handler for API Gateway input"""
    post_args = json.loads(event.get("body", {}))
    ticket = post_args["ticket"]
    ticket_id = ticket["identifier"]
    image_url = ticket["remote_attachment_url"]

    logging.debug("Detecting image from URL: %s" % image_url)

    response_body = {
        "id": None,
        "identifier": ticket_id,
        "attachment": image_url,
        "attachment_height": None,
        "attachment_width": None,
        "created_at": None,
        "driver": None,
        "errors": None,
        "properties": None,
        "status": None,
        "tags": None,
        "text_matches": None,
        "truck": None,
        "updated_at": None
    }
    response_body.update(ocr_image(image_url))
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
        },
        "body": json.dumps(response_body)
    }

    return response
