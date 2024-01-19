"""
This module contains the AIActions class which is responsible for creating detailed analysis prompts and summarizing user data.
"""

# External Libraries
import openai
from dotenv import load_dotenv
from llama_index import PromptTemplate
from llama_index.llms import OpenAI
from llama_index.multi_modal_llms import OpenAIMultiModal
from llama_index.query_engine import SimpleMultiModalQueryEngine
from llama_index.indices.multi_modal.retriever import (
    MultiModalVectorIndexRetriever,
)
from llama_index.vector_stores.types import MetadataFilter, MetadataFilters

# Local Libraries
from app.db.vector_stores import VectorStore

# Default Python Libraries
import os

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


class AIActions:
    """
    AIActions is a class that provides methods for creating detailed analysis prompts and summarizing user data.
    """

    @classmethod
    async def get_instance(cls):
        """
        Returns an instance of AIActions. If it doesn't exist, it creates one.
        """
        self = cls()
        await self._async_init()
        return self

    def __init__(self):
        """
        Initializes an instance of AIActions and sets the vector store.
        """
        self._agent = OpenAI(
            model="gpt-4-1106-preview",
            temperature=0.0,
        )
        self._multi_modal_agent = OpenAIMultiModal(
            model="gpt-4-vision-preview",
            temperature=0.0,
            api_key=os.getenv("OPENAI_API_KEY"),
            max_new_tokens=1500,
            context_window=100000,
        )
        self.vector_store: VectorStore | None = None

    async def _async_init(self):
        """
        Initializes an instance of AIActions asynchronously.
        """
        self.vector_store = await VectorStore.get_instance()

    async def summarize_user(self, user_id: str) -> str | None:
        """
        Summarize the detailed personality traits of the user based on their vector storage.
        """
        try:
            assert self.vector_store is not None
        except:
            return None
        # Initialize or get the user's index and create detailed prompts
        index = await self.vector_store.init_or_get_user_index(user_id=user_id)
        text_qa_template_str = (
            "Context information is below.\n"
            "-----------------------------\n"
            # f"{text_context_str}"
            "Create a personality summary based on the users text data.\n"
            "-----------------------------\n"
            "Given the context information and no prior knowledge, "
            "answer the query as in depth as you possibly can.\n"
            "Query: {query_str}\n"
            "Answer: "
        )
        image_qa_template_str = (
            "Context information is below.\n"
            "-----------------------------\n"
            "{context_str}"
            "-----------------------------\n"
            "Given the context information and no prior knowledge, "
            "answer the query as in depth as you possibly can.\n"
            "Query: {query_str}\n"
            "Answer: "
        )

        # qa_tmpl_text = PromptTemplate(text_qa_template_str)
        qa_tmpl_image = PromptTemplate(image_qa_template_str)

        # Create the Query Engine from the multimodal vector store index
        # retriever = MultiModalVectorIndexRetriever(
        #     index=index,
        #     image_similarity_top_k=5,
        #     similarity_top_k=5,
        #     filters=MetadataFilters(
        #         filters=[
        #             MetadataFilter(
        #                 key="user_id",
        #                 value=user_id,
        #             ),
        #         ],
        #     ),
        # )
        retriever = index.as_retriever(use_async=True)
        image_nodes = await retriever.aretrieve(
            "Find images provided by the user to create a summary of them."
        )
        print(f"Image Nodes: {image_nodes}")
        query_engine = SimpleMultiModalQueryEngine(
            retriever=retriever,
            multi_modal_llm=self._multi_modal_agent,
        )

        # Query the engine for each individual response to aggregate it into an overall response afterwards with additional context
        query_str = "Analyze your knowledgebase of images for the user to create a summary of them."
        ai_response = await query_engine.aquery(query_str)

        # Finally get the response
        response = str(ai_response)
        # image_response = str(image_ai_response)
        return response
