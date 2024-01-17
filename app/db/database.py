"""
This module contains the Database class which provides methods for interacting with the database.
"""
# Misc things we need :)
from mimetypes import guess_extension

# The Vector DB Import
from typing import Any
from app.utils.image_utils import get_image_filename, image_to_inputfile

# Local Imports
from app.models.models import (
    ImageIngestionRequest,
    TextIngestion,
    TextIngestionRequest,
)

from app.utils.image_utils import (
    image_to_inputfile,
    pil_image_to_base64,
    image_req_to_base64,
    get_image_filename,
)

# System Imports
import os
from dotenv import load_dotenv
import base64

load_dotenv()

APPWRITE_API_KEY = os.getenv("APPWRITE_API_KEY")
APPWRITE_ENDPOINT = os.getenv("APPWRITE_ENDPOINT")
APPWRITE_PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
USER_DATA_COLLECTION_ID = os.getenv("USER_DATA_COLLECTION_ID")


class Database:
    """
    The Database class provides methods for interacting with the Appwrite database.
    Each instance of the Database class is created for each request due to its minimal overhead.
    """

    @classmethod
    async def get_instance(cls, user_id: str):
        """
        Asynchronous initialization of the class
        """
        self = cls()
        await self.async_init(user_id=user_id)
        return self

    def __init__(self):
        """
        Initialize the Database class and the connections to Appwrite.
        """
        print("Connected to Database")

    async def async_init(self, user_id: str):
        """
        Asynchronous initializer for the Database Connection
        """
        try:
            print("Initialized asynchronously")
        except Exception as e:
            print(
                "Failed to initialize database connection for user: %s", user_id
            )
            print("Error: %s", str(e))
            raise e
