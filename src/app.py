import os
from langchain.chat_models import init_chat_model
from langchain_core.vectorstores import InMemoryVectorStore
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.agents.middleware import SummarizationMiddleware
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import ToolMessage
from langchain.tools import tool
from langchain.agents import create_agent
from dotenv import load_dotenv

# Load environment variables and initialize model and vector store
load_dotenv() # Load environment variables from .env file
api_key = os.getenv("GOOGLE_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key
model = init_chat_model("google_genai:gemini-2.5-flash-lite")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Load existing vector store
vector_store = InMemoryVectorStore.load('../Vector_Store_RAG', embeddings)

# Tool for retrieving context
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=3 ) #ใช้ similarity search หา top-2 documents
    serialized = "\n\n".join(f"Source: {doc.metadata}\nContent: {doc.page_content}" for doc in retrieved_docs)
    return serialized, retrieved_docs

from langchain.agents import create_agent
# ใส่ system prompt เพื่อควบคุมพฤติกรรมของโมเดล
system_prompt =("""
    You are an AI assistant for a Task Management System.

Your role is to answer user questions using information retrieved from the system's knowledge base.
When a retrieval tool is used, you MUST:
- Read and understand the retrieved content.
- Synthesize the information into a clear, concise, and helpful answer.
- Base your response ONLY on the retrieved information.

If the retrieved information is insufficient or not relevant:
- Clearly state that the information is not available in the current knowledge base.

DO NOT return an empty response.
"""
)
agent = create_agent(
    model,
    tools=[retrieve_context],
    system_prompt=system_prompt)

# --------------------------------------------------------------------
# 1. HELPER FUNCTIONS (AFTER MODEL)
# --------------------------------------------------------------------
def format_sources(raw_sources):
    """
    Clean and deduplicate sources from ToolMessages.
    """
    unique_sources = {}
    formatted_list = []
    
    # raw_sources in this context usually comes from ToolMessage content which might be a JSON string or text
    # But based on existing code, it seems to be the output of retrive_context tool
    
    for src in raw_sources:
        # Simple deduplication based on content string
        # In a real scenario, we might parse JSON if retrive_context returns structural data
        if src not in unique_sources:
            unique_sources[src] = True
            formatted_list.append(src)
            
    return formatted_list

# --------------------------------------------------------------------
# 2. ROUTING AGENT SETUP
# --------------------------------------------------------------------

# General Agent (Chit-chat) - Now Stateful
general_model = init_chat_model("google_genai:gemini-2.5-flash-lite")

general_system_prompt = """You are a general conversational assistant.
    Answer politely and briefly.
    If the question is outside the task management system,
    answer generally instead of declining."""

general_agent = create_agent(
    general_model,
    tools=[], # General agent might not need tools, or we can add dummy ones
    system_prompt=general_system_prompt,
    checkpointer=InMemorySaver()
)

# Router Definition
class RouteQuery(BaseModel):
    """
    Decide which agent should handle the user's query.
    """
    datasource: str = Field(
        ...,
        description=(
            "Choose which agent should handle the user's question.\n"
            "- Use 'task_agent' for questions related to the Task Management System, "
            "such as system features, user roles, workflows, permissions, projects, or tasks. "
            "These questions should be answered using the knowledge base (RAG).\n"
            "- Use 'general_agent' for greetings, casual conversation, or questions that are "
            "not related to the Task Management System."
        ),
    )

llm_router = init_chat_model("google_genai:gemini-2.5-flash-lite")
structured_llm_router = llm_router.with_structured_output(RouteQuery)

def route_question(query: str):
    """
    Hybrid routing:
    - Rule-based first (force system-related questions to task_agent)
    - LLM-based fallback
    """
    system_keywords = [
        "task", "project", "user", "role", "admin",
        "permission", "kanban", "workflow", "system",
        "feature", "member"
    ]

    # 🔴 FIX: force RAG for system questions
    if any(k in query.lower() for k in system_keywords):
        return "task_agent"

    try:
        result = structured_llm_router.invoke(query)
        return result.datasource
    except Exception as e:
        print(f"Routing Error: {e}")
        return "task_agent"   # fallback = RAG


# --------------------------------------------------------------------
# 3. Task Assistant AGENT (EXISTING RAG AGENT)
# --------------------------------------------------------------------
# Rename 'agent' to 'task_agent' for clarity
task_agent = create_agent(
    model,
    tools=[retrieve_context],
    system_prompt=system_prompt,
    middleware=[
        SummarizationMiddleware(
            model="google_genai:gemini-2.5-flash-lite",
            trigger=("tokens", 4000),
            keep=("messages", 20)
        )
    ],
    checkpointer=InMemorySaver()
)
# --------------------------------------------------------------------
# 5. MAIN EXECUTION FUNCTION
# --------------------------------------------------------------------

def get_answer(query: str, thread_id: str = "1") -> any:
    """Get final answer from the agent with Routing and Middleware."""
    # 0. Logging Input
    print(f"📝 User Query: {query} (Thread ID: {thread_id})")

    # 1. Routing
    destination = route_question(query)
    print(f"Routing to: {destination} (Thread ID: {thread_id})")

    response_text = ""
    sources = []
    
    # Config for the agent execution
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}} 
    final_messages = []
    target_agent = None
    
    if destination == "general_agent":
        target_agent = general_agent
    else: 
        target_agent = task_agent

    # Execute Selected Agent
    for event in target_agent.stream(
        {"messages": [{"role": "user", "content": query}]},
        config=config,
        stream_mode="values",
    ):
        final_messages = event["messages"]
            
    last_message = final_messages[-1]
    response_text = last_message.content
    
    # Extract sources from ToolMessages
    for msg in final_messages:
        if isinstance(msg, ToolMessage):
            sources.append(msg.content)

    # 3. After Model (Format Sources)
    clean_sources = format_sources(sources)

    return response_text, clean_sources