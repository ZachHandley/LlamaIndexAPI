"""
This module contains the models used in the application. These models are used to define the structure of the data that is sent and received by the application.
"""

# External Libraries
from pydantic import BaseModel, Field
from datetime import datetime

# Python Standard Libraries
from typing import Any
from enum import Enum


class ServerResponse(BaseModel):
    """
    This class represents the structure of a server response. It contains a status code, a message, and any data that the server might return.
    """

    status: int = Field(
        default=200,
        description="The status code of the response.",
    )
    message: str = Field(
        default="",
        description="The message of the response.",
    )
    data: Any = Field(
        default=None,
        description="The data of the response.",
    )


class UserRequest(BaseModel):
    """
    This class represents a request for a user. It contains the user's unique identifier.
    """

    userId: str = Field(
        default="",
        description="The unique identifier for the user.",
    )


class TextIngestion(BaseModel):
    """
    This class represents a text ingestion. It contains the unique identifier for the text ingestion, the time it was created and updated, the user's unique identifier, the text to be ingested, the source of the text, the time the text source was created, the language of the text, whether the text was created by the user, and the unique identifier for any associated image.
    """

    id: str = Field(
        default="",
        alias="$id",
        description="The unique identifier for the text ingestion.",
    )
    createdAt: str = Field(
        default=datetime.now().isoformat(),
        alias="$createdAt",
        description="The time when the text ingestion was created.",
    )
    updatedAt: str = Field(
        default=datetime.now().isoformat(),
        alias="$updatedAt",
        description="The time when the text ingestion was updated.",
    )
    userId: str = Field(
        default="",
        description="The unique identifier for the user.",
    )
    text: str | None = Field(
        default="",
        description="The text to be ingested.",
    )
    source: str = Field(
        default="",
        description="The source of the text.",
    )
    sourceTimestamp: float = Field(
        default=datetime.now().timestamp(),
        description="The time when the text source was created (e.g. time of posting on Twitter).",
    )
    language: str = Field(
        default="",
        description="The language of the text.",
    )
    isUsersCreation: bool = Field(
        default=False,
        description="Whether the text was created by the user or is simply associated e.g. retweet on Twitter, share on Facebook.",
    )
    imageId: str = Field(
        default="",
        description="If the user has an image associated with the text (e.g. Instagram) then this is the unique identifier for the image stored in the user's image collection.",
    )


class TextIngestionRequest(BaseModel):
    """
    This class represents a request for a text ingestion. It contains the user's unique identifier, the text to be ingested, the source of the text, the time the text source was created, the language of the text, whether the text was created by the user, and the unique identifier for any associated image.
    """

    userId: str = Field(
        default="",
        description="The unique identifier for the user.",
    )
    text: str | None = Field(
        default="",
        description="The text to be ingested.",
    )
    source: str = Field(
        default="",
        description="The source of the text.",
    )
    source_timestamp: float = Field(
        default=datetime.now().timestamp(),
        description="The time when the text source was created (e.g. time of posting on Twitter).",
    )
    language: str = Field(
        default="",
        description="The language of the text.",
    )
    isUsersCreation: bool = Field(
        default=False,
        description="Whether the text was created by the user or is simply associated e.g. retweet on Twitter, share on Facebook.",
    )
    imageId: str | None = Field(
        default=None,
        description="If the user has an image associated with the text (e.g. Instagram) then this is the unique identifier for the image stored in the user's image collection.",
    )


class ImageIngestionRequest(BaseModel):
    """
    This class represents a request for an image ingestion. It contains the user's unique identifier, the image to be ingested as a direct URL or in base64 encoded format, the mimetype of the image, and any text to be ingested.
    """

    userId: str = Field(
        default="",
        description="The unique identifier for the user.",
    )
    image_url: str | None = Field(
        default="",
        description="The image to be ingested as a direct URL to the image.",
    )
    image: str | bytes | None = Field(
        default="",
        description="The image to be ingested in base64 encoded format.",
    )
    mimetype: str = Field(
        default="image/jpeg",
        description="The mimetype of the image.",
    )
    text_request: TextIngestionRequest | None = Field(
        default=None,
        description="The text to be ingested, if any",
    )


class AssessmentRequest(BaseModel):
    """
    This class represents a request for an assessment. It contains the user's unique identifier.
    """

    userId: str = Field(
        default="",
        description="The unique identifier for the user.",
    )


class AssessmentResponse(BaseModel):
    """
    This class represents a response for an assessment. It contains the user's unique identifier, the assessment's unique identifier, the assessment's score, and the assessment's label.
    """

    userId: str = Field(
        default="",
        description="The unique identifier for the user.",
    )
    assessmentId: str = Field(
        default="",
        description="The unique identifier for the assessment.",
    )
    assessmentConfidence: float = Field(
        default=0.0, description="The confidence of the assessment."
    )
