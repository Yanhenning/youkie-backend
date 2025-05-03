import pytest
from langchain_core.documents import Document

from app.services.llm_service import LlmService
from app.enums import SummarizationStyle


@pytest.fixture
def mock_chat_model(mocker):
    mock_llm = mocker.Mock()
    mock_init_chat_model = mocker.patch("app.services.llm_service.init_chat_model")
    mock_init_chat_model.return_value = mock_llm
    return mock_llm


@pytest.fixture
def llm_service(mock_chat_model):
    return LlmService(streaming=False)


@pytest.fixture
def mock_prompt_template(mocker):
    return mocker.patch("app.services.llm_service.ChatPromptTemplate")


@pytest.fixture
def mock_create_stuff_documents_chain(mocker):
    mock_chain_func = mocker.patch(
        "app.services.llm_service.create_stuff_documents_chain"
    )
    mock_chain = mocker.Mock()
    mock_chain_func.return_value = mock_chain
    mock_chain.invoke.return_value = "This is a mock summary"
    mock_chain.stream.return_value = ["This ", "is ", "a ", "mock ", "summary"]
    return mock_chain


@pytest.fixture
def mock_document():
    return Document(page_content="Test content", metadata={"title": "Blog Post"})


class TestLlmService:
    def test_build_document(self, llm_service):
        content = "Test content"
        document = llm_service.build_document(content)

        assert isinstance(document, Document)
        assert document.page_content == content
        assert document.metadata == {"title": "Blog Post"}

        custom_metadata = {"title": "Custom Title"}
        document = llm_service.build_document(content, metadata=custom_metadata)
        assert document.metadata == custom_metadata

    def test_get_output_parser(self, llm_service):
        for style in SummarizationStyle:
            parser = llm_service.get_output_parser(style)
            assert parser is not None

    def test_build_chain(
        self,
        llm_service,
        mock_prompt_template,
        mocker,
    ):
        mock_create_stuff_documents_chain = mocker.patch("app.services.llm_service.create_stuff_documents_chain")

        llm_service.build_chain()

        mock_prompt_template.from_template.assert_called_once_with(
            "Summarize this content in a few sentences:\n\n{context}"
            "\n\n"
            "Summarization Style: {style}"
        )
        mock_create_stuff_documents_chain.assert_called_once()


    def test_summarize_blog_post(
        self, llm_service, mock_create_stuff_documents_chain, mocker
    ):
        mocker.patch.object(
            llm_service, "build_chain", return_value=mock_create_stuff_documents_chain
        )
        mock_document = Document(
            page_content="Test content", metadata={"title": "Blog Post"}
        )
        mocker.patch.object(llm_service, "build_document", return_value=mock_document)

        content = "Test content"
        result = llm_service.summarize_blog_post(content)

        llm_service.build_chain.assert_called_once_with(style=SummarizationStyle.NORMAL)
        llm_service.build_document.assert_called_once_with(content)
        mock_create_stuff_documents_chain.invoke.assert_called_once_with(
            {"context": [mock_document], "style": SummarizationStyle.NORMAL}
        )
        assert result == "This is a mock summary"

        # Test with different style
        llm_service.build_chain.reset_mock()
        llm_service.build_document.reset_mock()
        mock_create_stuff_documents_chain.invoke.reset_mock()

        result = llm_service.summarize_blog_post(
            content, style=SummarizationStyle.BULLET_POINTS
        )

        llm_service.build_chain.assert_called_once_with(
            style=SummarizationStyle.BULLET_POINTS
        )
        llm_service.build_document.assert_called_once_with(content)
        mock_create_stuff_documents_chain.invoke.assert_called_once_with(
            {"context": [mock_document], "style": SummarizationStyle.BULLET_POINTS}
        )

    def test_summarize_blog_post_stream(
        self, llm_service, mock_create_stuff_documents_chain, mocker
    ):
        mocker.patch.object(
            llm_service, "build_chain", return_value=mock_create_stuff_documents_chain
        )
        mock_document = Document(
            page_content="Test content", metadata={"title": "Blog Post"}
        )
        mocker.patch.object(llm_service, "build_document", return_value=mock_document)

        content = "Test content"
        result = list(llm_service.summarize_blog_post_stream(content))

        llm_service.build_chain.assert_called_once_with(style=SummarizationStyle.NORMAL)
        llm_service.build_document.assert_called_once_with(content)
        mock_create_stuff_documents_chain.stream.assert_called_once_with(
            {"context": [mock_document], "style": SummarizationStyle.NORMAL}
        )
        assert result == ["This ", "is ", "a ", "mock ", "summary"]

        # Test with different style
        llm_service.build_chain.reset_mock()
        llm_service.build_document.reset_mock()
        mock_create_stuff_documents_chain.stream.reset_mock()

        result = list(
            llm_service.summarize_blog_post_stream(
                content, style=SummarizationStyle.BRIEF_TEXT
            )
        )

        llm_service.build_chain.assert_called_once_with(
            style=SummarizationStyle.BRIEF_TEXT
        )
        llm_service.build_document.assert_called_once_with(content)
        mock_create_stuff_documents_chain.stream.assert_called_once_with(
            {"context": [mock_document], "style": SummarizationStyle.BRIEF_TEXT}
        )
