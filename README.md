# Microsoft Learn Assistant - LangChain Agent for M365

An intelligent Microsoft 365 agent built with Python, LangChain, and the Model Context Protocol (MCP) that provides access to Microsoft Learn documentation. This agent can search, retrieve, and provide information from official Microsoft documentation to answer questions about Azure, .NET, Microsoft 365, and other Microsoft products and services.

## 🌟 Features

- **🤖 AI-Powered Assistant**: Uses Azure OpenAI with LangChain for intelligent responses
- **📚 Microsoft Learn Integration**: Connects to Microsoft Learn MCP Server for up-to-date documentation
- **🔧 Tool Calling**: Leverages MCP tools to search docs, fetch articles, and find code samples
- **🔐 Azure AD Authentication**: Uses DefaultAzureCredential for secure authentication
- **💬 M365 Bot Integration**: Deploys as a Microsoft 365 bot accessible in Teams and Copilot
- **🎯 Smart Routing**: Automatically determines when to use tools vs. direct answers

## 📋 Prerequisites

- Python 3.8 or higher
- Azure OpenAI Service deployment
- Azure subscription with appropriate permissions
- Microsoft 365 developer account (for bot deployment)

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd M365-Python-Langchain-agent
```

### 2. Set Up Python Environment

Create and activate a virtual environment:

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install microsoft-agents-sdk
pip install langchain-openai
pip install langchain-mcp-adapters
pip install azure-identity
pip install python-dotenv
pip install aiohttp
```

### 3. Configure Environment Variables

Create a `.env.user` file in the root directory with your Azure OpenAI configuration:

```dotenv
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

**Note**: The `.env` file contains the template, while `.env.user` contains your actual values and takes precedence.

### 4. Azure Authentication

The agent uses `DefaultAzureCredential` for authentication. Ensure you're logged in to Azure:

```bash
az login
```

### 5. Run the Agent

Start the server:

```bash
python app.py
```

The server will start on `http://localhost:3978`.

You should see:
```
🚀 Starting Microsoft Learn Assistant...
📚 Connecting to Microsoft Learn MCP Server...
✅ Connected to Microsoft Learn MCP Server with X tools:
   - microsoft_docs_search
   - microsoft_docs_fetch
   - microsoft_code_sample_search
✨ Assistant ready!
```

### 6. Test the Agent

Use the M365 Agents Playground to interact with your agent:

```bash
npm exec @microsoft/m365agentsplayground -e http://localhost:3978/api/messages -c emulator
```

Or use the VS Code task:
- Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
- Select `Tasks: Run Task`
- Choose `Launch M365 Agents Playground`

## 💬 Usage Examples

Once running, you can ask the agent questions like:

- "What is Azure Cosmos DB?"
- "Show me code examples for Azure Functions in Python"
- "How do I deploy a .NET application to Azure?"
- "What are the best practices for Azure Storage?"
- "Explain Azure Active Directory"

The agent will:
1. Use `microsoft_docs_search` to find relevant documentation
2. Use `microsoft_docs_fetch` to get complete articles
3. Use `microsoft_code_sample_search` to find code examples
4. Provide comprehensive answers with links to official documentation

## 🏗️ Project Structure

```
M365-Python-Langchain-agent/
├── app.py                  # Main agent application
├── start_server.py         # Server startup logic
├── .env                    # Environment variable template
├── .env.user              # Your actual configuration (gitignored)
├── appPackage/            # M365 app package
│   └── manifest.json      # Teams/M365 app manifest
└── devTools/              # Development tools
```

## 🔧 Key Components

### LangChain Integration
- Uses `AzureChatOpenAI` for language model integration
- Implements tool calling with `bind_tools()`
- Asynchronous invocation for better performance

### MCP Client
- Connects to Microsoft Learn MCP Server
- Dynamically loads available tools
- Handles tool invocation and result processing

### Microsoft Agents SDK
- Built on `microsoft-agents-sdk` for M365 integration
- Supports deployment to Teams and Copilot
- Handles bot authentication and messaging

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI endpoint URL | `https://your-resource.openai.azure.com/` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Name of your GPT deployment | `gpt-4` |
| `AZURE_OPENAI_API_VERSION` | Azure OpenAI API version | `2024-08-01-preview` |
| `PORT` | Server port (optional) | `3978` |

### Bot Configuration

Edit `appPackage/manifest.json` to customize:
- App name and description
- Bot ID and scopes
- Commands and capabilities

## 🔒 Security

- Uses Azure AD authentication via `DefaultAzureCredential`
- JWT authorization middleware for bot endpoints
- Environment variables for sensitive configuration
- `.env.user` is gitignored to prevent credential leaks

## 🐛 Troubleshooting

**MCP Server Connection Issues**
- The agent will work without MCP tools if the server is unavailable
- Check network connectivity to `https://learn.microsoft.com/api/mcp`

**Azure Authentication Errors**
- Ensure you're logged in with `az login`
- Verify your Azure subscription has access to the OpenAI resource
- Check that the service principal has appropriate permissions

**Module Not Found Errors**
- Verify all dependencies are installed in your virtual environment
- Activate the virtual environment before running

## 📚 Resources

- [Microsoft Agents SDK](https://github.com/microsoft/teams-ai)
- [LangChain Documentation](https://python.langchain.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
- [Microsoft Learn](https://learn.microsoft.com/)
