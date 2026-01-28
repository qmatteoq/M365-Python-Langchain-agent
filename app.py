# app.py
from microsoft_agents.hosting.core import (
    AgentApplication,
    TurnState,
    TurnContext,
    MemoryStorage,
)
from microsoft_agents.hosting.aiohttp import CloudAdapter
from start_server import start_server
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_mcp_adapters.client import MultiServerMCPClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
import os
from pathlib import Path

# Load environment variables from .env (template) and .env.user (actual values)
# .env.user takes precedence if both files have the same variable
load_dotenv()  # Load .env first
load_dotenv(Path(__file__).parent / '.env.user', override=True)  # .env.user overrides

# Get Azure AD token provider using DefaultAzureCredential
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default"
)

# Initialize LangChain agent for Microsoft product information using Azure OpenAI
llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_ad_token_provider=token_provider,
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0.7
)

# System prompt with Microsoft Learn MCP server capabilities
system_prompt = """You are a knowledgeable assistant specializing in Microsoft products and services.
You have access to Microsoft Learn MCP Server tools:
- microsoft_docs_search: Search Microsoft documentation
- microsoft_docs_fetch: Fetch complete articles
- microsoft_code_sample_search: Find code examples

Use these tools to provide accurate, up-to-date information with links to documentation."""

# Initialize MCP client for Microsoft Learn
mcp_client = MultiServerMCPClient({
    "microsoft_learn": {
        "transport": "http",
        "url": "https://learn.microsoft.com/api/mcp"
    }
})

mcp_tools = None

async def initialize_mcp_tools():
    """Initialize tools from MCP server"""
    global mcp_tools
    try:
        mcp_tools = await mcp_client.get_tools()
        print(f"✅ Connected to Microsoft Learn MCP Server with {len(mcp_tools)} tools:")
        for tool in mcp_tools:
            print(f"   - {tool.name}")
    except Exception as e:
        print(f"⚠️  Could not connect to Microsoft Learn MCP Server: {e}")
        print("   Agent will work without MCP tools")

AGENT_APP = AgentApplication[TurnState](
    storage=MemoryStorage(), adapter=CloudAdapter()
)

async def _help(context: TurnContext, _: TurnState):
    await context.send_activity(
        "Welcome to the Microsoft Learn Assistant 🚀\n\n"
        "I can help you with questions about Microsoft products using official Microsoft Learn documentation.\n\n"
        "Type /help for this message or ask me about Azure, .NET, Microsoft 365, and more!"
    )

AGENT_APP.conversation_update("membersAdded")(_help)

AGENT_APP.message("/help")(_help)


@AGENT_APP.activity("message")
async def on_message(context: TurnContext, _):
    user_message = context.activity.text
    
    try:
        # Bind tools to LLM if available
        if mcp_tools:
            llm_with_tools = llm.bind_tools(mcp_tools)
            
            # Invoke LLM with tool calling capability
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            ai_msg = await llm_with_tools.ainvoke(messages)
            
            # Check if LLM wants to use tools
            if hasattr(ai_msg, 'tool_calls') and ai_msg.tool_calls:
                # Execute tool calls
                tool_results = []
                for tool_call in ai_msg.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    
                    # Find and invoke the tool
                    for tool in mcp_tools:
                        if tool.name == tool_name:
                            result = await tool.ainvoke(tool_args)
                            tool_results.append(f"[{tool_name}]: {result}")
                            break
                
                # Send results back to LLM for final answer
                final_messages = messages + [
                    {"role": "assistant", "content": f"I'll use tools to help answer: {', '.join([tc['name'] for tc in ai_msg.tool_calls])}"},
                    {"role": "user", "content": f"Tool Results:\\n" + "\\n".join(tool_results) + "\\n\\nNow provide a comprehensive answer based on these results."}
                ]
                final_response = await llm.ainvoke(final_messages)
                await context.send_activity(final_response.content)
            else:
                # LLM answered directly without tools
                await context.send_activity(ai_msg.content)
        else:
            # Fallback without MCP tools
            simple_prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a knowledgeable assistant specializing in Microsoft products and services."),
                ("user", "{question}")
            ])
            chain = simple_prompt | llm | StrOutputParser()
            response = await chain.ainvoke({"question": user_message})
            await context.send_activity(response)
            
    except Exception as e:
        await context.send_activity(f"Sorry, I encountered an error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    
    async def startup():
        print("🚀 Starting Microsoft Learn Assistant...")
        print("📚 Connecting to Microsoft Learn MCP Server...")
        await initialize_mcp_tools()
        print("✨ Assistant ready!")
    
    try:
        # Initialize MCP connection
        asyncio.run(startup())
        start_server(AGENT_APP, None)
    except Exception as error:
        raise error
