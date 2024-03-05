from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.callbacks import get_openai_callback
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader
import streamlit as st

import os
import urllib.parse


@st.cache_resource
def buildKnowledgeBase():
    loader = DirectoryLoader('/home/sagemaker-user/docs/', glob='**/*.pdf')
    documents = loader.load()
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    knowledge_base = FAISS.from_documents(texts, embeddings)
    print('knowledge base built!')
    return knowledge_base

def parse_response(response):
    response_sections = (response.split('SOURCES:'))
    response = response_sections[0]
    sources_section = response_sections[1]
    sources = sources_section.split(',')
    return response, sources

def hide_streamlit_menu_and_footer():
    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        footer:after {
            content: 'Made by Multifamily Architecture';
            visibility: visible;
            display: block;
            position: relative;
            #background-color: red;
            padding: 5px;
            top: 2px;
        }
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def process():
    doc_base = 'http://skarlekar.github.io/digital-sme-docs/'
    
    model_radio = st.sidebar.radio(
        "choose a model to use:",
        ("gpt-3.5-turbo", "gpt-4")
    )
    
    knowledge_base = buildKnowledgeBase()
    
    st.header("Ask me anything about Multifamily Underwriting")
    user_question = st.text_input("ask a question about multifamily underwriting:")
    
    if user_question:
        s = ''
        docs = knowledge_base.similarity_search(user_question)
        
        llm = ChatOpenAI(temperature=0, model=model_radio)
        chain = load_qa_with_sources_chain(llm, chain_type="stuff")
        with get_openai_callback() as cb:
            response = chain.run(input_documents=docs, question=user_question)
           
        parsed_response, sources = parse_response(response)
        st.write(parsed_response)
        st.markdown('***SOURCES:***')
        s = ''
        for i in sources:
            source = i.strip().replace('/home/sagemaker-user/', '').replace('\\', '/')
            url = "{}{}".format(doc_base, urllib.parse.quote(source))
            s += "- [{}]({}) \n".format(i.strip().replace('digital-sme\docs\\', ''), url)
        st.markdown(s)


def main():
    #set open api key here
    st.set_page_config(page_title="Fannie Mae Multifamily Underwriting SME")
    hide_streamlit_menu_and_footer()
    process()
        
if __name__ == '__main__':
    main()