import os
from dotenv import load_dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

from app.enums import SummarizationStyle

MODEL_NAME = "gpt-4o-mini-2024-07-18"


class LlmService:
    def __init__(self, streaming: bool = False):
        load_dotenv()
        self.api_key = os.environ.get('OPENAI_API_KEY')
        self.llm = init_chat_model("gpt-4o-mini", model_provider="openai", streaming=streaming)

    def build_document(self, content, metadata=None):
        metadata = {"title": "Blog Post"} if metadata is None else metadata
        document = Document(page_content=content, metadata=metadata)

        return document

    def get_output_parser(self, style):
        return {
            SummarizationStyle.BULLET_POINTS: StrOutputParser(),
            SummarizationStyle.BRIEF_TEXT: StrOutputParser(),
            SummarizationStyle.NORMAL: StrOutputParser(),
        }.get(style, StrOutputParser())


    def build_chain(self, style=SummarizationStyle.NORMAL):
        prompt = ChatPromptTemplate.from_template(
            "Summarize this content in a few sentences:\n\n{context}"
            "\n\n"
            "Summarization Style: {style}"
        )

        return create_stuff_documents_chain(self.llm, prompt, output_parser=self.get_output_parser(style))

    def summarize_blog_post(self, content: str, style: SummarizationStyle = SummarizationStyle.NORMAL) -> str:
        chain = self.build_chain(style=style)
        document = self.build_document(content)
        result = chain.invoke({"context": [document], "style": style})
        return result

    def summarize_blog_post_stream(self, content: str, style: SummarizationStyle = SummarizationStyle.NORMAL):
        chain = self.build_chain(style=style)
        document = self.build_document(content)
        for chunk in chain.stream({"context": [document], "style": style}):
            yield chunk
