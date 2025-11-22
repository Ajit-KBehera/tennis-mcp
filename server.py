from mcp.server.fastmcp import FastMCP
import sqlite3
import pandas as pd
import os
import sys

# Initialize the MCP Server
mcp = FastMCP("Tennis Analyst")

# PATH TO YOUR SQLITE DATA
# Using explicit absolute path to ensure it works regardless of working directory
DB_PATH = "/Users/ajitbehera/Codes/tennis-mcp/tennis_data.db"

def get_connection():
    """Creates a connection to the SQLite database."""
    # check_same_thread=False is needed because MCP might call this from different threads
    if not os.path.exists(DB_PATH):
        error_msg = (
            f"Could not find database at {DB_PATH}\n"
            f"Current working directory: {os.getcwd()}\n"
            f"Script location: {os.path.abspath(__file__) if '__file__' in globals() else 'unknown'}\n"
            f"Please ensure tennis_data.db exists at: /Users/ajitbehera/Codes/tennis-mcp/tennis_data.db"
        )
        raise FileNotFoundError(error_msg)
    
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

@mcp.tool()
def get_database_schema() -> str:
    """
    Returns the list of tables and their column names/types.
    The AI uses this to know how to write SQL queries.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            schema_info = []
            
            for table in tables:
                table_name = table[0]
                # Get column info for each table
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # Format: column_name (type)
                # row[1] is name, row[2] is type in SQLite PRAGMA output
                col_str = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
                schema_info.append(f"Table '{table_name}': {col_str}")
            
            return "\n".join(schema_info)
        finally:
            conn.close()
    except FileNotFoundError as e:
        return f"Database Error: {str(e)}\n\nPlease verify that tennis_data.db exists at: {DB_PATH}"
    except Exception as e:
        return f"Error getting schema: {str(e)}\n\nDatabase path: {DB_PATH}\nCurrent directory: {os.getcwd()}"

@mcp.tool()
def run_sql_query(query: str) -> str:
    """
    Executes a read-only SQL query on the tennis database.
    Use this to aggregate stats, find head-to-head records, or analyze trends.
    ALWAYS check the schema using get_database_schema before writing a query.
    """
    # Basic safety check
    if any(keyword in query.upper() for keyword in ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER"]):
        return "Error: Only SELECT queries are allowed for safety."

    try:
        conn = get_connection()
        try:
            # using pandas read_sql_query handles headers and formatting automatically
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                return "No results found."
            
            # Limit rows to prevent overflowing the AI context window
            if len(df) > 100:
                return f"Result too large ({len(df)} rows). Showing first 100:\n" + df.head(100).to_markdown(index=False)
                
            return df.to_markdown(index=False)
        finally:
            conn.close()
    except FileNotFoundError as e:
        return f"Database Error: {str(e)}\n\nPlease verify that tennis_data.db exists at: {DB_PATH}"
    except Exception as e:
        return f"SQL Error: {str(e)}\n\nDatabase path: {DB_PATH}\nCurrent directory: {os.getcwd()}"

if __name__ == "__main__":
    # Verify database exists before starting server
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database not found at {DB_PATH}", file=sys.stderr)
        print(f"Current working directory: {os.getcwd()}", file=sys.stderr)
        print(f"Please ensure tennis_data.db exists at the path above.", file=sys.stderr)
        sys.exit(1)
    
    # Test connection
    try:
        test_conn = get_connection()
        test_conn.close()
        print(f"✓ Database connection verified: {DB_PATH}", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: Could not connect to database: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run the server
    print(f"Serving Tennis Analyst on {DB_PATH}...", file=sys.stderr)
    mcp.run(transport='stdio')