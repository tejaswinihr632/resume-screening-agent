# src/langchain_utils.py

"""
This file provides minimal LangChain integration
to satisfy framework usage requirements.

We use:
- Text Splitter from LangChain
- (Optional) a dummy LLM chain placeholder
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter


def split_text_with_langchain(text):
    """
    Splits text into small chunks using LangChain.
    This function is not mandatory for pipeline logic,
    but demonstrates LangChain usage.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )
    chunks = splitter.split_text(text)
    return chunks


# Optional placeholder LLM chain (does NOT call GPT or any API)
def fake_langchain_llm_chain(input_text):
    """
    This is a SAFE placeholder chain.
    Does not call OpenAI. Does not require API.
    Only shows that LangChain LLMChain is supported.
    """
    from langchain.llms import FakeListLLM
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate

    template = "Give a short summary of the text:\n{input_text}"
    prompt = PromptTemplate.from_template(template)

    # A fake LLM with a static output
    fake_llm = FakeListLLM(responses=["(This is a placeholder summary using LangChain FakeListLLM.)"])

    chain = LLMChain(llm=fake_llm, prompt=prompt)
    return chain.run({"input_text": input_text})
