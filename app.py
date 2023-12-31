import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS, Chroma
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub
from flask import Flask, jsonify, request
# from numpy import array, save, load
from langchain.document_loaders import TextLoader

import json

import numpy as np



def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()

    # all_embeddings = array(embeddings)
    # save('embeddings.npy', embeddings)
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
    # print(embeddings)

    # all_embeddings = load('embeddings.npy', mmap_mode=None, allow_pickle=True)

    # print(all_embeddings)

    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)

    return vectorstore


def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)

    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=vectorstore.as_retriever(), memory=memory)
    return conversation_chain


def handle_userinput(user_question):

    with st.spinner("Processing"):

        response = st.session_state.conversation({'question': user_question})
        st.session_state.chat_history = response['chat_history']

        keep = []
        reversed_arrays = st.session_state.chat_history[::-1]
        for m, reversed_array in enumerate(reversed_arrays):

            keep.append(reversed_array)

            if len(keep) == 2:

                reversed_keep = keep[::-1]

                for i, message in enumerate(reversed_keep):

                    if i % 2 == 1:
                        st.write(bot_template.replace(
                            "{{MSG}}", message.content), unsafe_allow_html=True)
                    else:
                        st.write(user_template.replace(
                            "{{MSG}}", message.content), unsafe_allow_html=True)

                keep = []


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with multiple PDFs",
                       page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

        script = ''
        with open('docs/q_&_a.pdf', 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)

            for page in pdf_reader.pages:
                script += page.extract_text()

        # with open('docs/2306.08161.pdf', 'rb') as pdf_file:
        #     pdf_reader = PdfReader(pdf_file)

        #     for page in pdf_reader.pages:
        #         script += page.extract_text()
        
        # loader = TextLoader('docs/state_of_the_union.txt')
        
        # long_document = loader.load()
        
        # text_splitter = CharacterTextSplitter( chunk_size = 1500, chunk_overlap = 0)
        # docs = text_splitter.split_documents( long_document )
        # print(docs)
        
        
        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        text_chunks = text_splitter.split_text(script)
        # print(text_chunks)
        # return text_chunks

        # text_chunks = get_text_chunks(script)

        embeddings = OpenAIEmbeddings()
        # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
        
        # vectorstoresss = Chroma.from_documents(documents=text_chunks, embedding=embeddings)
        
        # docs_with_embeddings = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        
        
        persist_dir = 'docs'
        
        # dssdsdsd = Chroma.from_documents(documents=text_chunks, embedding=embeddings, persist_directory=persist_dir)
        
        
        llm = ChatOpenAI()
        # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

        memory = ConversationBufferMemory( memory_key='chat_history', return_messages=True)

        st.session_state.conversation = ConversationalRetrievalChain.from_llm( llm=llm, retriever=vectorstore.as_retriever(), memory=memory)
        
        # with open('json_data.json', 'w') as outfile:
        #     json.dump(st.session_state.conversation, outfile)
        
        # return st.session_state.conversation
        
        # save('embeddings.npy', st.session_state.conversation)
        
        # print( st.session_state.conversation)
        
        
        # st.session_state.conversation = load('embeddings.npy', mmap_mode=None, allow_pickle=True)
        
        

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Chat with Bot (beta) :books:")
    user_question = st.text_input("Ask a question about your documents:")
    if user_question:
        handle_userinput(user_question)

    # with st.sidebar:
    #     st.subheader("Your documents")
    #     pdf_docs = st.file_uploader(
    #         "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
    #     if st.button("Process"):
    #         with st.spinner("Processing"):
    #             raw_text = get_pdf_text(pdf_docs)
    #             text_chunks = get_text_chunks(raw_text)
    #             vectorstore = get_vectorstore(text_chunks)
    #             st.session_state.conversation = get_conversation_chain( vectorstore)


if __name__ == '__main__':
    main()
