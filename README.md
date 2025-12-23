# Groq-Powered Chatbot with Memory (Streamlit)

This repository contains a Streamlit application (`app.py`) that serves as a user-friendly interface for Groq's Large Language Models (LLMs). The code includes two versions: a basic stateless chatbot (commented out) and an advanced, stateful chatbot that mimics the "ChatGPT" experience with session management.

## 🛠️ Environment Setup

To run this application, you need to set up your environment and install the necessary dependencies.

```bash
# Create a virtual environment
conda create -p venv python==3.10 -y
conda activate venv/

# Install dependencies
pip install streamlit python-dotenv langchain-groq langchain-community

```

---

## 📂 Code Analysis: `app.py`

The `app.py` file is divided into two distinct sections.

### 1. The Basic Version (Commented Out)

The top half of the file (lines 1–77) contains a "Stateless" Q&A bot. It takes a question, sends it to Groq, and prints the answer. It does **not** remember previous questions.

### 2. The Advanced Version (Active Code)

The active code (starting line 85) builds a fully functional chat interface with **Memory** and **Session Management**. Here is the detailed breakdown:

#### **A. Initialization & State Management**

Streamlit apps "rerun" the entire script every time you click a button. To keep data (like chat history) alive between reruns, we use `st.session_state`.

* **`st.set_page_config(...)`**: Sets the browser tab title and layout.
* **`st.session_state.store`**: A dictionary initialized to hold *all* conversation histories. Keys are session IDs (e.g., "chat1"), and values are the message logs.
* **`st.session_state.current_session`**: Tracks which chat tab the user is currently viewing.

#### **B. Session Logic**

* **`get_session_history(session_id)`**: This is a helper function used by LangChain. When the LLM needs to know what was said previously, it calls this function with a specific ID to retrieve the `ChatMessageHistory` object.

#### **C. The Sidebar (Chat Management)**

This section mimics the ChatGPT sidebar.

* **New Chat**: When clicked, it generates a new ID (e.g., `chat2`), updates the `current_session`, and reruns the app to show a blank screen.
* **Chat List Loop**: The code iterates through `st.session_state.store` to create a button for every active chat.
* **Dynamic Titles**: It looks at the first "human" message in the history to name the chat button (e.g., "What is Python...").
* **Delete Button**: Allows the user to remove a specific session from the memory store.



#### **D. LangChain Configuration**

This is the "Brain" of the application.

1. **`ChatPromptTemplate`**:
* `system`: Tells the AI it is a helpful assistant.
* `MessagesPlaceholder(variable_name="history")`: This is crucial. It tells LangChain, "Insert the entire conversation history *here* before sending the prompt to the AI".


2. **`ChatGroq`**: Initializes the connection to the Groq API using the key and settings (Model, Temperature) selected in the sidebar.
3. **`RunnableWithMessageHistory`**:
* This wrapper combines the **Chain** (Prompt + LLM) with the **History** (Session Store).
* It automatically saves the user's input and the AI's response to the history after every turn.



#### **E. The Chat Interface**

* **Rendering History**: The code loops through the current session's messages (`history.messages`) and uses `st.chat_message()` to display them on the screen (User messages on the right/left, AI on the opposite).
* **`st.chat_input()`**: The text box at the bottom. When the user types and hits enter:
1. It invokes `with_message_history.invoke(...)`.
2. It passes the `session_id` so the AI knows *which* conversation memory to use.



---

## 📚 Libraries Used

| Library | Purpose in this App |
| --- | --- |
| **`streamlit`** | Builds the web interface (Sidebar, Chat bubbles, Input fields) without requiring HTML/CSS knowledge. |
| **`os` & `dotenv**` | Used to securely load the `.env` file where API keys might be stored (though this app also allows manual input). |
| **`langchain_groq`** | The specific connector that allows LangChain to talk to Groq's high-speed inference engine. |
| **`langchain_core`** | Provides the building blocks: `ChatPromptTemplate` for structuring queries and `StrOutputParser` for cleaning up the text response. |
| **`langchain_community`** | Provides `ChatMessageHistory`, the specific class used to store the list of messages in memory. |

---

## 🚀 How to Run

1. Ensure you have your **Groq API Key** ready.
2. Run the application:
```bash
streamlit run app.py
```
