# External Libraries
import math
import random
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import openai
from dotenv import load_dotenv

# Python Standard Libraries
import os
import nest_asyncio

# Local Libraries
from app.models.models import (
    AssessmentRequest,
    ServerResponse,
    TextIngestionRequest,
    ImageIngestionRequest,
    UserRequest,
)
from app.api.ai_actions import AIActions
from app.db.database import Database
from app.db.vector_stores import VectorStore

from app.utils.image_utils import fetch_image_from_url, image_req_to_base64


# Load environment variables
load_dotenv()

# Set OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Define allowed origins for CORS
origins = ["http://localhost:4321"]

nest_asyncio.apply()


# Server class definition
class Server:
    """
    This class is responsible for managing the server and its routes.
    """

    def __init__(self):
        self.app = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.router = APIRouter()
        self.router.add_api_route(
            "/",
            self.heartbeat,
            methods=["GET"],
        )
        self.router.add_api_route(
            "/add_text_source",
            self.ingest_text,
            methods=["POST"],
            response_model_exclude_none=True,
            response_model_exclude_unset=True,
        )
        self.router.add_api_route(
            "/add_image_and_maybe_text_source",
            self.ingest_image_and_maybe_text,
            methods=["POST"],
            response_model_exclude_none=True,
            response_model_exclude_unset=True,
        )
        self.router.add_api_route(
            "/summarize_profile",
            self.get_summary,
            methods=["POST"],
            response_model_exclude_none=True,
            response_model_exclude_unset=True,
        )
        self.app.include_router(self.router)

    async def heartbeat(self):
        """
        A simple route to check the server status.
        """
        return {"status": "alive"}

    async def ingest_text(
        self,
        text: TextIngestionRequest,
    ) -> ServerResponse:
        """
        This method is used to ingest and store text data.
        """
        try:
            vectordb = await VectorStore.get_instance(
                user_id=text.userId,
                has_text_store=False,
            )
            await vectordb.ingest_text(
                text.userId,
                random.random() * 1000000000000000,
                text.text,
            )
            return ServerResponse(
                status=200,
                message="Text Ingested",
                data=None,
            )
        except Exception as e:
            return ServerResponse(
                status=500,
                message=f"Error ingesting text: {str(e)}",
                data=None,
            )

    async def ingest_image_and_maybe_text(
        self,
        image_request: ImageIngestionRequest,
    ) -> ServerResponse:
        """
        This method is used to ingest and store image data and optionally text data.
        """
        try:
            vectordb = await VectorStore.get_instance(
                user_id=image_request.userId,
                has_text_store=False,
            )
            if (
                image_request.image_url is not None
                and len(image_request.image_url) > 0
            ):
                image_request.image = await fetch_image_from_url(
                    image_request.image_url
                )
                document_id = document.get("$id")  # type: ignore
                if image_request.text_request is not None:
                    await vectordb.ingest_text(
                        image_request.userId,
                        text_id=document_id,  # type: ignore
                        text=image_request.text_request.text,  # type: ignore
                    )
                await vectordb.ingest_image(
                    image_request=image_request,
                    image_id=document_id,
                )
                return ServerResponse(
                    status=200,
                    message="Image and Text (if provided) Ingested",
                    data=document,
                )
            elif image_request.image is not None:
                image_id = math.floor(random.random() * 1000000000000000)
                if image_request.text_request is not None:
                    await vectordb.ingest_text(
                        image_request.userId,
                        text_id=image_id,  # type: ignore
                        text=image_request.text_request.text,  # type: ignore
                    )
                await vectordb.ingest_image(
                    image_request=image_request,
                    image_id=image_id,
                )
                return ServerResponse(
                    status=200,
                    message="Image and Text (if provided) Ingested",
                    data=None,
                )
            else:
                return ServerResponse(
                    status=400,
                    message="No image or image URL provided",
                    data=None,
                )
        except Exception as e:
            return ServerResponse(
                status=500,
                message=f"Error ingesting image and/or text: {str(e)}",
                data=None,
            )

    async def get_summary(
        self,
        assessment: AssessmentRequest,
    ) -> ServerResponse:
        """
        This method is used to generate a summary of the user's data.
        """
        try:
            print(f"Generating summary for user {assessment.userId}")
            actions = await AIActions.get_instance(
                user_id=assessment.userId,
                has_text_store=False,
            )
            print(f"Got AIActions instance for user {assessment.userId}")
            summary = await actions.summarize_user(assessment.userId)
            print(f"Generated summary for user {assessment.userId}")
            return ServerResponse(
                status=200,
                message="Summary Generated",
                data=summary,
            )
        except Exception as e:
            return ServerResponse(
                status=500,
                message=f"Error generating summary: {str(e)}",
                data=None,
            )
