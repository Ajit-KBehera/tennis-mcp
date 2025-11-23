from mcp.server.fastmcp import FastMCP
import psycopg2
import pandas as pd
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the MCP Server
mcp = FastMCP("Tennis Analyst")

# Database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "asktennis_db")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_connection():
    """Creates a connection to the PostgreSQL database."""
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
            # Get list of tables in public schema
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()
            
            schema_info = []
            
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
        if not DB_USER or not DB_PASSWORD:
             print("WARNING: DB_USER or DB_PASSWORD not set. Please set them in .env file or environment variables.", file=sys.stderr)
        
        test_conn = get_connection()
        test_conn.close()
        print(f"✓ Database connection verified: postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: Could not connect to database: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run the server
    print(f"Serving Tennis Analyst on postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}...", file=sys.stderr)
    mcp.run(transport='stdio')