# import streamlit as st
# import os
# from dotenv import load_dotenv

# from langchain_groq import ChatGroq
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts import ChatPromptTemplate

# # --------------------------------------------------
# # Load environment variables
# # --------------------------------------------------
# load_dotenv()

# # --------------------------------------------------
# # LangSmith Tracking (Optional)
# # --------------------------------------------------
# os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
# os.environ["LANGCHAIN_TRACING_V2"] = "true"
# os.environ["LANGCHAIN_PROJECT_NAME"] = "Simple Q&A Chatbot With GROQ"

# # --------------------------------------------------
# # Prompt Template
# # --------------------------------------------------
# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", "You are a helpful assistant. Please respond clearly to user queries."),
#         ("user", "Question: {question}")
#     ]
# )

# # --------------------------------------------------
# # LLM Response Generator
# # --------------------------------------------------
# def generate_response(question, api_key, model, temperature, max_tokens):
#     llm = ChatGroq(
#         groq_api_key=api_key,
#         model_name=model,
#         temperature=temperature,
#         max_tokens=max_tokens
#     )

#     output_parser = StrOutputParser()
#     chain = prompt | llm | output_parser
#     answer = chain.invoke({"question": question})
#     return answer

# # --------------------------------------------------
# # Streamlit UI
# # --------------------------------------------------
# st.title("🚀 Enhanced Q&A Chatbot with Groq")

# # Sidebar settings
# st.sidebar.title("Settings")
# api_key = st.sidebar.text_input("Enter your Groq API Key:", type="password")

# # Groq models
# model = st.sidebar.selectbox(
#     "Select Groq Model",
#     [
#         "openai/gpt-oss-120b",
#         "openai/gpt-oss-20b",
#         "openai/gpt-oss-safeguard-20b"
#     ]
# )

# temperature = st.sidebar.slider(
#     "Temperature", min_value=0.0, max_value=1.0, value=0.7
# )

# max_tokens = st.sidebar.slider(
#     "Max Tokens", min_value=50, max_value=1024, value=300
# )

# # Main interface
# st.write("💬 Go ahead and ask any question")
# user_input = st.text_input("You:")

# if user_input and api_key:
#     with st.spinner("Thinking..."):
#         response = generate_response(
#             user_input,
#             api_key,
#             model,
#             temperature,
#             max_tokens
#         )
#     st.success("Response:")
#     st.write(response)

# elif user_input and not api_key:
#     st.warning("⚠️ Please enter your Groq API key in the sidebar.")

# else:
#     st.info("👆 Enter a question to get started.")







# MEMORY

import streamlit as st
import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# --------------------------------------------------
# Load env
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(page_title="Groq Chatbot", layout="wide")
st.title("🧠 Groq Chatbot")

# --------------------------------------------------
# Initialize store
# --------------------------------------------------
if "store" not in st.session_state:
    st.session_state.store = {}

if "current_session" not in st.session_state:
    st.session_state.current_session = "chat1"

# --------------------------------------------------
# Session history getter
# --------------------------------------------------
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in st.session_state.store:
        st.session_state.store[session_id] = ChatMessageHistory()
    return st.session_state.store[session_id]

# --------------------------------------------------
# Sidebar — ChatGPT-style Chat History + Delete
# --------------------------------------------------
st.sidebar.title("💬 Chats")

# New chat
if st.sidebar.button("➕ New Chat"):
    new_id = f"chat{len(st.session_state.store) + 1}"
    st.session_state.current_session = new_id
    get_session_history(new_id)
    st.rerun()

# List chats
for session_id, history in list(st.session_state.store.items()):
    col1, col2 = st.sidebar.columns([4, 1])

    # Chat title
    title = "New Chat"
    for msg in reversed(history.messages):
        if msg.type == "human":
            title = msg.content[:30] + ("..." if len(msg.content) > 30 else "")
            break

    # Select chat
    if col1.button(title, key=f"select_{session_id}"):
        st.session_state.current_session = session_id
        st.rerun()

    # Delete chat
    if col2.button("🗑", key=f"delete_{session_id}"):
        del st.session_state.store[session_id]

        # Handle deleting active chat
        if st.session_state.current_session == session_id:
            if st.session_state.store:
                st.session_state.current_session = list(st.session_state.store.keys())[0]
            else:
                st.session_state.current_session = "chat1"
                get_session_history("chat1")

        st.rerun()

# --------------------------------------------------
# Sidebar — Settings
# --------------------------------------------------
st.sidebar.divider()
st.sidebar.title("⚙ Settings")

api_key = st.sidebar.text_input("Groq API Key", type="password")

model = st.sidebar.selectbox(
    "Groq Model",
    [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "openai/gpt-oss-safeguard-20b",
    ]
)

temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
max_tokens = st.sidebar.slider("Max Tokens", 50, 1024, 300)

# --------------------------------------------------
# Prompt
# --------------------------------------------------
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Use previous conversation context."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ]
)

# --------------------------------------------------
# LLM + Chain
# --------------------------------------------------
llm = ChatGroq(
    groq_api_key=api_key,
    model_name=model,
    temperature=temperature,
    max_tokens=max_tokens
)

chain = prompt | llm | StrOutputParser()

with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

# --------------------------------------------------
# Main Chat Area
# --------------------------------------------------
current_session = st.session_state.current_session
history = get_session_history(current_session)

st.subheader(f"🗂 {current_session}")

# Render messages
for msg in history.messages:
    if msg.type == "human":
        st.chat_message("user").write(msg.content)
    else:
        st.chat_message("assistant").write(msg.content)

# --------------------------------------------------
# Input
# --------------------------------------------------
user_input = st.chat_input("Message ChatGPT...")

if user_input and api_key:
    response = with_message_history.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": current_session}}
    )

    st.chat_message("user").write(user_input)
    st.chat_message("assistant").write(response)

elif user_input and not api_key:
    st.warning("Please enter your Groq API Key")
