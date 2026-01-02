# Tennis Analyst MCP Server

A Model Context Protocol (MCP) server for analyzing tennis data. This server provides tools to query tennis databases (PostgreSQL or SQLite) and retrieve database schemas for AI-assisted tennis data analysis.

## Features

- **Database Schema Inspection**: Get table structures and column information
- **SQL Query Execution**: Run read-only SQL queries on tennis databases
- **Multi-Database Support**: Works with both PostgreSQL and SQLite databases
- **Safe Query Execution**: Only allows SELECT queries to prevent data modification

## Prerequisites

- Python 3.8 or higher
- PostgreSQL (optional, if not using SQLite)
- A tennis database (PostgreSQL or SQLite)

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your database connection (see Configuration section below)

## Quick Start

### For Browser Users (Chrome, Firefox, etc.)

If you want to use this in a browser, use the MCP SuperAssistant Proxy:

```bash
npx @srbhptl39/mcp-superassistant-proxy@latest --config ./mcp-config.json
```

Then open the provided URL in your browser. See [Option 3: Using with Browser-Based MCP Clients](#option-3-using-with-browser-based-mcp-clients-chrome-firefox-etc) for detailed instructions.

### For Desktop Users

- **Claude Desktop**: Add configuration to `claude_desktop_config.json` (see [Option 1](#option-1-using-with-claude-desktop-recommended))
- **Cursor IDE**: Configure in Settings → Features → MCP Servers (see [Option 2](#option-2-using-with-cursor-ide))

## Configuration

The server supports two database backends: **SQLite** (default) or **PostgreSQL**.

### SQLite Configuration (Default)

By default, the server uses SQLite. Create a `.env` file in the project root with:

```env
USE_SQLITE=true
SQLITE_DB_PATH=tennis_data_tour.db
```

Or simply ensure `tennis_data_tour.db` exists in the project directory.

### PostgreSQL Configuration

To use PostgreSQL, create a `.env` file with:

```env
USE_SQLITE=false
DB_HOST=localhost
DB_PORT=5432
DB_NAME=asktennis_db
DB_USER=your_username
DB_PASSWORD=your_password
```

## How to Use This Extension

This is an MCP (Model Context Protocol) server that provides tennis data analysis tools to AI assistants. It's not a traditional browser extension, but can be used with various MCP-compatible clients.

### Option 1: Using with Claude Desktop (Recommended)

Claude Desktop is the official desktop application from Anthropic that supports MCP servers.

1. **Install Claude Desktop** (if not already installed):
   - Download from: https://claude.ai/download
   - Available for macOS, Windows, and Linux

2. **Configure MCP Server**:
   - Open the MCP configuration file:
     - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
     - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
     - **Linux**: `~/.config/Claude/claude_desktop_config.json`

3. **Add the Tennis Analyst Server**:
   ```json
   {
     "mcpServers": {
       "tennis-analyst": {
         "command": "python3",
         "args": ["server.py"],
         "cwd": "/Users/ajitbehera/Codes/tennis-mcp"
       }
     }
   }
   ```
   ⚠️ **Important**: Update the `cwd` path to match your actual project directory path.

4. **Restart Claude Desktop** to load the new MCP server.

5. **Use in Claude Desktop**:
   - Open Claude Desktop
   - The Tennis Analyst tools will be available automatically
   - Ask questions like: "What tables are in the tennis database?" or "Show me player statistics"

### Option 2: Using with Cursor IDE

Cursor IDE has built-in MCP support for AI-powered coding assistance.

1. **Open Cursor Settings**:
   - Go to Settings → Features → MCP Servers

2. **Add Server Configuration**:
   - Click "Add Server" or edit the MCP configuration file
   - Add the configuration (same JSON as above)

3. **Restart Cursor** to activate the server.

4. **Use in Cursor**:
   - The AI assistant in Cursor can now query your tennis database
   - Use it in chat or code completion to analyze tennis data

### Option 3: Using with Browser-Based MCP Clients (Chrome, Firefox, etc.)

For browser-based usage, you can use the **MCP SuperAssistant Proxy** to expose your MCP server to web interfaces:

#### Using MCP SuperAssistant Proxy

The MCP SuperAssistant Proxy allows you to use MCP servers with browser-based AI assistants and web interfaces.

1. **Prerequisites**:
   - Node.js and npm installed on your system
   - The `mcp-config.json` file in your project directory (already included)

2. **Start the Proxy Server**:
   ```bash
   npx @srbhptl39/mcp-superassistant-proxy@latest --config ./mcp-config.json
   ```

3. **Access via Browser**:
   - The proxy will start a local web server (typically on `http://localhost:3000` or similar)
   - Open the provided URL in Chrome, Firefox, or any modern browser
   - You can now interact with the Tennis Analyst MCP server through the web interface

4. **Configuration**:
   - The proxy uses the `mcp-config.json` file in your project root
   - Make sure the `cwd` path in `mcp-config.json` is correct (absolute path)
   - The proxy will automatically start your MCP server when needed

5. **Usage**:
   - Once the proxy is running, you can query the tennis database through the web interface
   - Ask questions like: "What tables are in the database?" or "Show me player statistics"
   - The proxy bridges the MCP server to the browser interface

**Note**: Keep the proxy running in a terminal while using the browser interface. Press `Ctrl+C` to stop it.

#### Alternative Browser Options

- **MCP Inspector** (if available): Some MCP clients provide web interfaces
- **Web-Based AI Assistants**: Some platforms support MCP servers through WebSocket connections
- **API Gateways**: Custom REST APIs that wrap MCP functionality for browser access

### Option 4: Using with Other MCP Clients

Any MCP-compatible client can use this server. Common clients include:
- **Continue.dev** - VS Code extension with MCP support
- **Aider** - AI pair programming tool
- Custom MCP clients

Add the same configuration to your client's MCP settings file.

## MCP Configuration

The MCP configuration format is standardized. Add this to your client's MCP configuration:

```json
{
  "mcpServers": {
    "tennis-analyst": {
      "command": "python3",
      "args": ["server.py"],
      "cwd": "/path/to/tennis-mcp"
    }
  }
}
```

**Configuration Notes**:
- `command`: The Python interpreter (use `python3` or full path)
- `args`: Arguments to pass (just the server script)
- `cwd`: Working directory (must be absolute path to your project)

## Usage

### Running the Server

The server runs via stdio transport and is typically invoked by MCP clients:

```bash
python3 server.py
```

The server will:
1. Load environment variables from `.env` file
2. Test the database connection
3. Start serving MCP tools via stdio

### Available Tools

#### `get_database_schema()`
Returns the list of tables and their column names/types. Use this to understand the database structure before writing queries.

#### `run_sql_query(query: str)`
Executes a read-only SQL query on the tennis database. 
- Only SELECT queries are allowed
- Results are returned in markdown format
- Results are limited to 100 rows to prevent context overflow

### Example Queries

Once connected, you can ask questions like:
- "What are the tables in the database?"
- "Show me the schema of the matches table"
- "Find head-to-head records between two players"
- "Get tournament statistics for a specific year"

## Project Structure

```
tennis-mcp/
├── server.py              # Main MCP server implementation
├── requirements.txt        # Python dependencies
├── mcp-config.json        # MCP configuration (ready for proxy use)
├── tennis_data_tour.db    # SQLite database (if using SQLite)
├── .env                   # Environment variables (create this)
└── README.md              # This file
```

**Note**: The `mcp-config.json` file is pre-configured and ready to use with the MCP SuperAssistant Proxy. Just update the `cwd` path if your project is in a different location.

## Development

### Testing the Connection

The server automatically tests the database connection on startup. If there are connection issues, check:

1. Database credentials in `.env`
2. Database server is running (for PostgreSQL)
3. Database file exists (for SQLite)
4. Network connectivity (for remote PostgreSQL)

### Error Handling

- Connection errors are displayed on startup
- SQL errors are returned in query results
- Unauthorized operations (INSERT, UPDATE, DELETE, etc.) are blocked

## Dependencies

- `mcp` - Model Context Protocol framework
- `psycopg2-binary` - PostgreSQL adapter
- `pandas` - Data manipulation and formatting
- `python-dotenv` - Environment variable management

## License

This project is provided as-is for tennis data analysis purposes.

## Browser Usage Notes

⚠️ **Important**: MCP servers are **local processes** that run on your computer, not browser extensions. They cannot be installed directly in Chrome or Firefox like traditional extensions.

### Why MCP Servers Work Differently

- MCP servers communicate via **stdio** (standard input/output) or **SSE** (Server-Sent Events)
- They require a **local Python environment** and database access
- They're designed to work with **desktop AI applications**, not web browsers directly

### Browser-Based Alternatives

If you need browser-based access, consider:

1. **Use Claude Desktop** (desktop app) - Most seamless MCP experience
2. **Use Cursor IDE** - Browser-like interface with MCP support
3. **Create a Web API Wrapper** - Build a REST API that wraps the MCP server for browser access
4. **Use MCP Web Gateway** - Some tools provide web interfaces to MCP servers

### Quick Start for Browser Users

If you want to use this from a browser:

1. **Install Claude Desktop** (works like a browser but supports MCP)
2. **Or use Cursor IDE** (web-based IDE with MCP support)
3. **Or run the server as a local API** (requires additional development)

## Troubleshooting

### Server Not Connecting

- **Check Python path**: Ensure `python3` is in your PATH
- **Verify database**: Make sure your database file exists or PostgreSQL is running
- **Check permissions**: Ensure the server has read access to the database
- **Review logs**: Check stderr output for connection errors

### Browser/Web Client Issues

- **MCP servers don't run in browsers**: Use the MCP SuperAssistant Proxy or a desktop MCP client
- **Proxy not starting**: Ensure Node.js is installed (`node --version` to check)
- **Proxy connection errors**: Verify the `cwd` path in `mcp-config.json` is an absolute path
- **Path issues**: Always use absolute paths in MCP configuration
- **Python not found**: Use full path to Python in the `command` field
- **Proxy port conflicts**: The proxy may use a different port if 3000 is occupied

### Common Errors

- **"Database connection failed"**: Check `.env` file and database credentials
- **"Command not found"**: Verify Python 3 is installed and accessible
- **"Permission denied"**: Check file permissions for `server.py` and database files

## Support

For issues or questions, please check:
- MCP documentation: https://modelcontextprotocol.io
- Database connection logs in stderr output
- Verify your MCP client supports stdio transport

