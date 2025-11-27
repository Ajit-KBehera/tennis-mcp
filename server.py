from mcp.server.fastmcp import FastMCP
import psycopg2
import sqlite3
import pandas as pd
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the MCP Server
mcp = FastMCP("Tennis Analyst")

# Database configuration
USE_SQLITE = os.getenv("USE_SQLITE", "false").lower() == "true"
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "tennis_data_tour.db")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "asktennis_db")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_connection():
    """Creates a connection to the database (PostgreSQL or SQLite)."""
    if USE_SQLITE:
        if not os.path.exists(SQLITE_DB_PATH):
             # Try to look in current directory if path is relative and not found
             if not os.path.isabs(SQLITE_DB_PATH) and os.path.exists(os.path.join(os.getcwd(), SQLITE_DB_PATH)):
                 return sqlite3.connect(os.path.join(os.getcwd(), SQLITE_DB_PATH))
             # If strictly not found
             if not os.path.exists(SQLITE_DB_PATH):
                 # Just creating it might be what sqlite3 does by default, 
                 # but for a read-tool we probably want it to exist. 
                 # However, standard sqlite3.connect creates it if missing. 
                 # Given the context of "tennis_data_tour.db", it should likely exist.
                 # I'll let it connect, but maybe print a warning if it's new/empty?
                 # Actually, let's just connect.
                 pass
        
        return sqlite3.connect(SQLITE_DB_PATH)

    if not DB_USER or not DB_PASSWORD:
         raise ValueError("DB_USER and DB_PASSWORD environment variables must be set.")
    
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
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
            schema_info = []

            if USE_SQLITE:
                # SQLite Schema Retrieval
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    columns = cursor.fetchall()
                    # PRAGMA table_info returns: (cid, name, type, notnull, dflt_value, pk)
                    col_str = ", ".join([f"{col[1]} ({col[2]})" for col in columns])
                    schema_info.append(f"Table '{table_name}': {col_str}")
            else:
                # PostgreSQL Schema Retrieval
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = cursor.fetchall()
                
                for table in tables:
                    table_name = table[0]
                    # Get column info for each table
                    cursor.execute("""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = %s
                        ORDER BY ordinal_position
                    """, (table_name,))
                    columns = cursor.fetchall()
                    
                    # Format: column_name (type)
                    col_str = ", ".join([f"{col[0]} ({col[1]})" for col in columns])
                    schema_info.append(f"Table '{table_name}': {col_str}")
            
            return "\n".join(schema_info)
        finally:
            conn.close()
    except Exception as e:
        return f"Error getting schema: {str(e)}"

@mcp.tool()
def run_sql_query(query: str) -> str:
    """
    Executes a read-only SQL query on the tennis database.
    Use this to aggregate stats, find head-to-head records, or analyze trends.
    ALWAYS check the schema using get_database_schema before writing a query.
    """
    # Basic safety check
    if any(keyword in query.upper() for keyword in ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "GRANT", "REVOKE"]):
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
    except Exception as e:
        return f"SQL Error: {str(e)}"

if __name__ == "__main__":
    # Test connection
    try:
        if USE_SQLITE:
             print(f"Connecting to SQLite database at {SQLITE_DB_PATH}...", file=sys.stderr)
        elif not DB_USER or not DB_PASSWORD:
             print("WARNING: DB_USER or DB_PASSWORD not set. Please set them in .env file or environment variables.", file=sys.stderr)
        
        test_conn = get_connection()
        test_conn.close()
        if USE_SQLITE:
             print(f"✓ SQLite database connection verified: {SQLITE_DB_PATH}", file=sys.stderr)
        else:
             print(f"✓ Database connection verified: postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: Could not connect to database: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run the server
    db_msg = f"sqlite://{SQLITE_DB_PATH}" if USE_SQLITE else f"postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print(f"Serving Tennis Analyst on {db_msg}...", file=sys.stderr)
    mcp.run(transport='stdio')