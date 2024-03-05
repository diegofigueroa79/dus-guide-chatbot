from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Bedrock
from langchain_community.embeddings import BedrockEmbeddings
import boto3

import os
import urllib.parse

from splitters import DUSGuideSplitter


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
    knowledge_base = FAISS.from_documents(texts, bedrock_embeddings)
    print('knowledge base built!')
    return knowledge_base

def parse_response(response):
    response_sections = (response.split('SOURCES:'))
    response = response_sections[0]
    sources_section = response_sections[1]
    sources = sources_section.split(',')
    return response, sources

def process():
    doc_base = 'http://skarlekar.github.io/digital-sme-docs/'
    
    knowledge_base = buildKnowledgeBase()
    
    user_question = "What are the requirements for the transaction approval memo?"
    
    s = ''
    docs = knowledge_base.similarity_search(user_question)

    chain = load_qa_with_sources_chain(llm, chain_type="stuff")
    response = chain.run(input_documents=docs, question=user_question)

    parsed_response, sources = parse_response(response)
    print(parsed_response)
    print("***")
    print(sources)

def main():
    boto_session = boto3.Session()
    aws_region = boto_session.region_name
    bedrock_runtime = boto_session.client("bedrock-runtime", region_name=aws_region)

    modelId = "meta.llama2-70b-chat-v1"
    
    global llm
    llm = Bedrock(model_id=modelId, client=bedrock_runtime, model_kwargs={"temperature": 0})
    
    global bedrock_embeddings
    bedrock_embeddings = BedrockEmbeddings(client=bedrock_runtime)
    
    #process()
    
    loader = DirectoryLoader('/home/sagemaker-user/docs/', glob='**/*.pdf')
    documents = loader.load()
    
    
    splitter = DUSGuideSplitter()
    chunks = splitter.split_documents(documents=documents)
    for chunk in chunks:
        print(chunk)
        print('****************')
    
    
        
if __name__ == '__main__':
    main()





