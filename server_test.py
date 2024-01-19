import pytest
from fastapi.testclient import TestClient
from app.server import Server
from app.models.models import (
    TextIngestionRequest,
    ImageIngestionRequest,
    AssessmentRequest,
)
import requests


def test_server():
    client = "http://localhost:8000"
    fake_user_id = "1234567890"
    print(f"Testing server with user id: {fake_user_id}")

    # Test text ingestion
    text_request = TextIngestionRequest(
        userId=fake_user_id,
        text="This is a test text",
        source="test",
        language="en",
        isUsersCreation=True,
    )
    print(f"Testing text ingestion with request: {text_request}")
    response = requests.post(
        f"{client}/add_text_source", json=text_request.dict()
    )
    print(f"Text ingestion response: {response.json()}")

    # Test image ingestion
    image_request = ImageIngestionRequest(
        userId=fake_user_id,
        image_url="https://picsum.photos/500",
    )
    print(f"Testing image ingestion with request: {image_request}")
    response = requests.post(
        f"{client}/add_image_and_maybe_text_source", json=image_request.dict()
    )
    print(f"Image ingestion response: {response.json()}")

    # Test getting a summary
    assessment_request = AssessmentRequest(userId=fake_user_id)
    print(f"Testing summary generation with request: {assessment_request}")
    response = requests.post(
        f"{client}/summarize_profile", json=assessment_request.dict()
    )
    print(f"Summary generation response: {response.json()}")


test_server()
