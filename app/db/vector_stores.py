"""
This module contains the VectorStore class which is responsible for managing the storage of text and image data for each user.
It uses the Qdrant client to create and manage collections of text and image data for each user.
The VectorStore class is a singleton, meaning there can only be one instance of it in the application.
"""

# External Libraries
from llama_index.indices.multi_modal.base import MultiModalVectorStoreIndex
from llama_index.vector_stores import QdrantVectorStore, SimpleVectorStore
from llama_index import SimpleDirectoryReader, StorageContext
from llama_index.llms import OpenAI
from llama_index.multi_modal_llms import OpenAIMultiModal
from llama_index.prompts import PromptTemplate
from llama_index.query_engine import SimpleMultiModalQueryEngine
from llama_index import Document
from llama_index.schema import ImageDocument, ImageNode
from PIL import Image
import aiohttp
import qdrant_client
from qdrant_client import AsyncQdrantClient, QdrantClient
import openai
from dotenv import load_dotenv
import tempfile

# Default Python Libraries
from io import BytesIO
import base64
import os

# Local Libraries
# from app.ai_actions import AIActions
from app.models.models import ImageIngestionRequest
from app.utils.image_utils import (
    fetch_image_from_url,
    pil_image_to_base64,
    image_req_to_base64,
)

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


class VectorStore:
    """
    VectorStore is a singleton class that manages the storage of text and image data for each user.
    It uses the Qdrant client to create and manage collections of text and image data for each user.
    """

    _qdrant_client = QdrantClient(url="http://localhost")
    _qdrant_client_async: AsyncQdrantClient | None = None
    _text_store: QdrantVectorStore | None = None
    _image_store: QdrantVectorStore | None = None
    _index: MultiModalVectorStoreIndex | None = None
    _agent = OpenAI(
        model="gpt-4-1106-preview",
        temperature=0.0,
    )
    _multi_modal_agent = OpenAIMultiModal(
        model="gpt-4-vision-preview",
        temperature=0.0,
    )

    @classmethod
    async def get_instance(cls):
        """
        Get the instance of the VectorStore class. If it doesn't exist, create a new one.
        """
        self = cls()
        if cls._qdrant_client_async is None:
            cls._qdrant_client_async = AsyncQdrantClient(url="http://localhost")
        if cls._text_store is None or cls._image_store is None:
            cls._text_store = QdrantVectorStore(
                "global_text_store",
                client=cls._qdrant_client,
                aclient=cls._qdrant_client_async,
            )
            cls._image_store = QdrantVectorStore(
                "global_image_store",
                client=cls._qdrant_client,
                aclient=cls._qdrant_client_async,
            )
        if cls._index is None:
            cls._index = MultiModalVectorStoreIndex.from_vector_store(
                vector_store=cls._text_store,
                image_vector_store=cls._image_store,
                use_async=True,
                show_progress=True,
            )
        return self

    def __init__(self):
        """
        Initialize the VectorStore class. If an instance already exists, raise an exception.
        """
        pass

    async def init_or_get_user_index(
        self,
        user_id: str,
        has_text_store: bool = False,
    ) -> MultiModalVectorStoreIndex:
        """
        Initialize or get the text and image collections as an index for the specified user.

        Args:
            user_id (str): The user ID to initialize the index for.

        Returns:
            MultiModalVectorStoreIndex: The initialized or retrieved index.
        """
        if not has_text_store:
            print("Inserting global user document for new collection")
            self._index.insert(
                Document(
                    doc_id=f"{user_id}",
                    text=f"{user_id} is the users global Appwrite User ID",
                )
            )
        return self._index

    async def ingest_text(self, user_id: str, text_id: str, text: str) -> None:
        """
        Ingest text into the index of the specified user for later use in summarization.

        Args:
            user_id (str): The user ID to initialize the index for.
            text_id (str): The unique identifier for the text.
            text (str): The text to be ingested.
        """
        # Get or create the users index
        index = await self.init_or_get_user_index(user_id=user_id)
        document = Document(
            doc_id=f"{user_id}_{text_id}",
            text=text,
            metadata={
                "user_id": user_id,
            },
        )
        index.insert(document=document)

    async def ingest_image(
        self,
        image_request: ImageIngestionRequest,
        image_id: str,
    ) -> None:
        """
        Asynchronously ingest an image (by URL) into the index of the specified user for later use in summarization.

        Args:
            user_id (str): The user ID to initialize the index for.
            image_id (str): The unique identifier for the image.
            image_url (str | None): The URL of the image to be ingested.
            image_data (str | None): The Base64 encoded image to be ingested.
        """
        image_data = await image_req_to_base64(image_request)
        index = await self.init_or_get_user_index(user_id=image_request.userId)
        # Create the image document
        image_doc = ImageDocument(
            doc_id=f"{image_id}",
            image=image_data,
            metadata={
                "user_id": image_request.userId,
            },
            text=image_request.text_request.text
            if image_request.text_request
            else "",
            image_mimetype=image_request.mimetype,
        )
        # insert the node
        index.insert(image_doc)
