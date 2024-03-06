from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Bedrock
from langchain_community.embeddings import BedrockEmbeddings
import streamlit as st
import boto3

import os
import urllib.parse

from splitters import DUSGuideSplitter


@st.cache_resource
def buildKnowledgeBase():
    loader = DirectoryLoader('/home/sagemaker-user/dus-guide-chatbot/docs/', glob='**/*.pdf')
    documents = loader.load()
    text_splitter = DUSGuideSplitter()
    texts = text_splitter.split_documents(documents)
    knowledge_base = FAISS.from_documents(texts, bedrock_embeddings)
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
    
    knowledge_base = buildKnowledgeBase()
    
    st.header("Ask me anything about Multifamily Underwriting")
    user_question = st.text_input("Ask a question about multifamily underwriting:")
    
    if user_question:
        s = ''
        docs = knowledge_base.similarity_search(user_question)
        
        chain = load_qa_with_sources_chain(llm, chain_type="stuff")
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
    boto_session = boto3.Session()
    aws_region = boto_session.region_name
    bedrock_runtime = boto_session.client("bedrock-runtime", region_name=aws_region)
    
    modelId = "meta.llama2-70b-chat-v1"
    
    global llm
    llm = Bedrock(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0})
    
    global bedrock_embeddings
    bedrock_embeddings = BedrockEmbeddings(client=bedrock_runtime)
    
    st.set_page_config(page_title="Fannie Mae Multifamily Underwriting SME")
    hide_streamlit_menu_and_footer()
    process()
        
if __name__ == '__main__':
    main()