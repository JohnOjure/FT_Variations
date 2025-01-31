import re
import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_community.chat_models import ChatOllama
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from Free_Think.ft_alpha_factors import *

st.title("R:red[o]nda_free_think")

llm = OllamaLLM(model = 'mistral', temperature = 0.1)
llm2 = OllamaLLM(model = 'llama3', temperature = 0.1)

input_case = st.chat_input("The input case...")

