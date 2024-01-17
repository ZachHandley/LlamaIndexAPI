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

    _agent = OpenAI(
        model="gpt-4-1106-preview",
        temperature=0.0,
    )
    _multi_modal_agent = OpenAIMultiModal(
        model="gpt-4-1106-preview",
        temperature=0.0,
    )

    @classmethod
    async def get_instance(cls, user_id: str, has_text_store: bool = False):
        """
        Get the instance of the VectorStore class. If it doesn't exist, create a new one.
        """
        vector_store = cls()
        await vector_store._async_init(
            user_id=user_id, has_text_store=has_text_store
        )
        return vector_store

    def __init__(self):
        """
        Initialize the VectorStore class. If an instance already exists, raise an exception.
        """
        # Create the Qdrant connection -- Local for now
        print("Creating Qdrant Client")
        self.qdrant_client = QdrantClient(url="http://localhost")
        print("Qdrant Client Created")
        self.user_text_store: QdrantVectorStore | None = None
        self.user_image_store: QdrantVectorStore | None = None
        self.user_storage_context: StorageContext | None = None
        self.user_index: MultiModalVectorStoreIndex | None = None
        # Create the Qdrant Vector Stores for the global index
        self.text_store: QdrantVectorStore | None = None
        self.image_store: QdrantVectorStore | None = None
        self.storage_context: StorageContext | None = None

        # Create the MultiModal index for use in our global queries (application wide knowledgebase)
        self.index: MultiModalVectorStoreIndex | None = None

    async def _async_init(self, user_id: str, has_text_store: bool = False):
        # Create the Qdrant connection -- Local for now
        print("Creating Async Qdrant Client")
        self.qdrant_client_async = AsyncQdrantClient(url="http://localhost")
        print("Async Qdrant Client Initialized, initializing user index")
        await self.init_or_get_user_index(
            user_id=user_id, has_text_store=has_text_store
        )
        print("User Index initialized")
        # Create the Qdrant Vector Stores
        self.text_store = QdrantVectorStore(
            client=self.qdrant_client,
            aclient=self.qdrant_client_async,
            collection_name="global_text_store",
        )
        self.image_store = QdrantVectorStore(
            client=self.qdrant_client,
            aclient=self.qdrant_client_async,
            collection_name="global_image_store",
        )
        self.storage_context = StorageContext.from_defaults(
            vector_store=self.text_store,
            image_store=self.image_store,
        )

        # Create the MultiModal index for use in our global queries (application wide knowledgebase)
        self.index = MultiModalVectorStoreIndex(
            nodes=[],
            storage_context=self.storage_context,
            use_async=True,
            show_progress=True,
        )

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

        if self.user_index is not None:
            return self.user_index

        self.user_text_store = QdrantVectorStore(
            client=self.qdrant_client,
            aclient=self.qdrant_client_async,
            collection_name=f"{user_id}_text",
        )
        self.user_image_store = QdrantVectorStore(
            client=self.qdrant_client,
            aclient=self.qdrant_client_async,
            collection_name=f"{user_id}_image",
        )
        self.user_storage_context = StorageContext.from_defaults(
            vector_store=self.user_text_store,
            image_store=self.user_image_store,
        )
        self.user_index = MultiModalVectorStoreIndex(
            nodes=[],
            storage_context=self.user_storage_context,
            use_async=True,
            show_progress=True,
        )
        if not has_text_store:
            print("Inserting global user document for new collection")
            self.user_index.insert(
                Document(
                    doc_id=f"{user_id}",
                    text=f"{user_id} is the users global Appwrite User ID",
                )
            )
        return self.user_index

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
        image_data = image_req_to_base64(image_request)
        index = await self.init_or_get_user_index(user_id=image_request.userId)
        # Create the image node
        image_node = ImageNode(
            doc_id=f"{image_id}",
            image=image_data,
        )
        # insert the node
        index.insert_nodes(nodes=[image_node])
