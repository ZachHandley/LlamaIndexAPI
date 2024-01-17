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
    async def get_instance(cls, user_id: str, has_text_store: bool = False):
        """
        Returns an instance of AIActions. If it doesn't exist, it creates one.
        """
        self = cls()
        await self._async_init(user_id=user_id, has_text_store=has_text_store)
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

    async def _async_init(self, user_id: str, has_text_store: bool = False):
        """
        Initializes an instance of AIActions asynchronously.
        """
        self.vector_store = await VectorStore.get_instance(
            user_id=user_id, has_text_store=has_text_store
        )

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
        retriever = MultiModalVectorIndexRetriever(
            index=index,
            image_similarity_top_k=5,
            similarity_top_k=5,
        )
        image_nodes = await retriever.atext_to_image_retrieve(
            "Analyze the provided images of the user to find the ones that you believe would showcase personality traits."
        )
        print(f"Image Nodes: {image_nodes}")
        query_engine = SimpleMultiModalQueryEngine(
            retriever=retriever,
            image_qa_template=qa_tmpl_image,
            multi_modal_llm=self._multi_modal_agent,
        )

        # Query the engine for each individual response to aggregate it into an overall response afterwards with additional context
        query_str = "Analyze your knowledgebase of images for the user to create a summary of them."
        ai_response = await query_engine.aquery(query_str)

        # Finally get the response
        response = str(ai_response)
        # image_response = str(image_ai_response)
        return response

        print(f"Text Response from AI: {text_response}")
        print(f"Image Response from AI: {image_response}")

        # Define detailed queries based on create_profile.txt
        overall_personality_query = (
            "The AI's overarching goal is to synthesize personality assessments from multiple inputs - including images, texts, and potentially other data sources - to construct a holistic, multifaceted personality profile. This integrated analysis aims to merge diverse insights, capturing the complexity and depth of an individual's personality.\n"
            "Reasoning: Multimodal Personality Synthesis\n\n"
            "Cross-Analysis of Inputs:\n"
            "Correlate findings from image-based and text-based assessments, looking for consistent traits, emotions, and patterns.\n"
            "Identify any contrasting or complementary elements across different inputs to gain a well-rounded understanding.\n\n"
            "Comprehensive Trait Analysis:\n"
            "Compile personality traits identified from each input source, considering both explicit and subtle indicators.\n"
            "Assess the congruence or divergence of these traits across different forms of expression (visual, textual, etc.).\n\n"
            "Emotional and Psychological Integration:\n"
            "Merge emotional profiles and psychological tendencies identified from each analysis, acknowledging a spectrum of emotional states and mental processes.\n\n"
            "Interests, Values, and Motivations:\n"
            "Combine insights into the individual's interests, values, and motivations, recognizing patterns or unique aspects presented in different mediums.\n\n"
            "Overall Personality Dynamics:\n"
            "Evaluate the dynamic interaction of personality traits, emotional patterns, and cognitive styles as reflected across all analyses.\n\n"
            "Action: Unified Personality Profile\n\n"
            "Synthesized Personality Overview:\n"
            "Present a unified personality profile that encapsulates findings from the multimodal analysis.\n\n"
            "Trait and Emotional Spectrum:\n"
            "Highlight a comprehensive spectrum of traits and emotions, explaining their manifestation and interplay across different contexts and expressions.\n\n"
            "Cohesive Interests and Values:\n"
            "Deliver an integrated view of the individual's interests and values, underlining any recurring themes or diverse interests revealed through the analyses.\n\n"
            "Psychological and Behavioral Insights:\n"
            "Offer insights into psychological patterns, behavioral tendencies, and potential motivations derived from the combined assessments.\n\n"
            "Conclusion and Implications:\n"
            "Conclude with an overall assessment, discussing the implications of the synthesized personality profile for understanding the individual's character and behavior.\n\n"
        )

        overall_qa_template_str = (
            "Context information is below.\n"
            "-----------------------------\n"
            "Below are the analysis results from the text and image data we have indexed. Use it as additional context for the user's personality traits and combine it with your final analysis to reach a more complete summary.\n\n"
            f"Text Analysis: {text_response}\n\nImage Analysis: {image_response}"
            "-----------------------------\n"
            "Given the context information and no prior knowledge, "
            "answer the query as in depth as you possibly can.\n"
            "Query: {query_str}\n"
            "Answer: "
        )

        # Create the overall query template
        overall_qa_tmpl = PromptTemplate(overall_qa_template_str)

        # Another overall query engine
        query_engine = index.as_query_engine(
            multi_modal_llm=AIActions._multi_modal_agent,
            text_qa_template=overall_qa_tmpl,
        )

        # Query the engine for the overall response
        overall_ai_response = query_engine.query(overall_personality_query)

        # Finally get the response
        overall_response = str(overall_ai_response)

        return overall_response
