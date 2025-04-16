import sqlite3
import pandas as pd
from typing import Optional, Union, List, Dict, Any
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

# Create the MCP server
mcp = FastMCP("RealEstate Support")

# Database connection utility
def get_db_connection():
    """Create a database connection"""
    return sqlite3.connect("RealEstate.db")

@mcp.resource("schema://database")
def get_database_schema() -> str:
    """
    Retrieve the full database schema for all tables.
    
    Returns:
        A formatted string describing the database schema
    """
    conn = get_db_connection()
    try:
        # Query to get all table names
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        # Build schema description
        schema_description = "Database Schema:\n"
        for table in tables:
            table_name = table[0]
            schema_description += f"\nTable: {table_name}\n"
            
            # Get column information
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for column in columns:
                # column[1] is name, column[2] is type
                schema_description += f"  {column[1]} ({column[2]})\n"
        
        return schema_description
    finally:
        conn.close()

@mcp.resource("listings://query?city={city}&state={state}&min_beds={min_beds}&max_price={max_price}")
def query_listings(
    city: Optional[str] = None, 
    state: Optional[str] = None, 
    min_beds: Optional[int] = None, 
    max_price: Optional[int] = None
) -> str:
    """
    Query real estate listings with optional filters.
    
    Args:
        city: Filter by city name
        state: Filter by state
        min_beds: Minimum number of bedrooms
        max_price: Maximum listing price
    
    Returns:
        A string representation of matching listings
    """
    conn = get_db_connection()
    try:
        query = "SELECT * FROM Sacramento"
        conditions = []
        params = []

        if city:
            conditions.append("city = ?")
            params.append(city)
        
        if state:
            conditions.append("state = ?")
            params.append(state)
        
        if min_beds:
            conditions.append("beds >= ?")
            params.append(min_beds)
        
        if max_price:
            conditions.append("price <= ?")
            params.append(max_price)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        df = pd.read_sql_query(query, conn, params=params)
        
        # Convert to readable string format
        return df.to_string(index=False)
    finally:
        conn.close()

@mcp.tool()
def describe_columns(table_name: Optional[str] = None) -> str:
    """
    Provide detailed description of columns in a specified table or all tables.
    
    Args:
        table_name: Optional specific table name to describe
    
    Returns:
        Detailed column descriptions
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # If no table specified, get all tables
        if not table_name:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
        else:
            tables = [(table_name,)]
        
        description = "Column Descriptions:\n"
        for table in tables:
            table_name = table[0]
            description += f"\nTable: {table_name}\n"
            
            # Get detailed column information
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            for column in columns:
                # column[0]: cid, column[1]: name, column[2]: type, 
                # column[3]: can be null, column[4]: default value, column[5]: primary key
                description += (
                    f"  - {column[1]} ({column[2]})\n"
                    f"    Nullable: {'Yes' if column[3] == 0 else 'No'}\n"
                    f"    Default Value: {column[4] or 'None'}\n"
                    f"    Primary Key: {'Yes' if column[5] == 1 else 'No'}\n"
                )
        
        return description
    finally:
        conn.close()

@mcp.tool()
def calculate_average_price(
    city: Optional[str] = None, 
    state: Optional[str] = None, 
    beds: Optional[int] = None
) -> Dict[str, Union[float, int]]:
    """
    Calculate average property price with optional filters.
    
    Args:
        city: Optional city filter
        state: Optional state filter
        beds: Optional number of bedrooms filter
    
    Returns:
        Dictionary with price statistics
    """
    conn = get_db_connection()
    try:
        query = "SELECT AVG(price) as avg_price, COUNT(*) as total_listings FROM Sacramento"
        conditions = []
        params = []

        if city:
            conditions.append("city = ?")
            params.append(city)
        
        if state:
            conditions.append("state = ?")
            params.append(state)
        
        if beds:
            conditions.append("beds = ?")
            params.append(beds)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()

        return {
            "average_price": round(result[0], 2) if result[0] is not None else None,
            "total_listings": result[1]
        }
    finally:
        conn.close()

@mcp.tool()
def find_best_deals(
    max_price: int = 500000, 
    min_beds: int = 3, 
    max_distance: float = 10.0,
    reference_lat: float = None,
    reference_lon: float = None
) -> str:
    """
    Find the best real estate deals based on multiple criteria.
    
    Args:
        max_price: Maximum property price
        min_beds: Minimum number of bedrooms
        max_distance: Maximum distance from reference point (in miles)
        reference_lat: Latitude of reference point
        reference_lon: Longitude of reference point
    
    Returns:
        String of best deals
    """
    conn = get_db_connection()
    try:
        query = """
        SELECT 
            * FROM Sacramento
        WHERE 
            price <= ? AND 
            beds >= ?
        """
        params = [max_price, min_beds]

        # If reference location is provided, add distance calculation
        if reference_lat and reference_lon:
            query = """
            SELECT 
                *,
                (6371 * acos(cos(radians(?)) * cos(radians(latitude)) * 
                 cos(radians(longitude) - radians(?)) + 
                 sin(radians(?)) * sin(radians(latitude)))) AS distance
            FROM Sacramento
            WHERE 
                price <= ? AND 
                beds >= ? AND
                distance <= ?
            """
            params = [
                reference_lat, 
                reference_lon, 
                reference_lat, 
                max_price, 
                min_beds,
                max_distance
            ]

        query += " ORDER BY price ASC LIMIT 10"

        df = pd.read_sql_query(query, conn, params=params)
        return df.to_string(index=False)
    finally:
        conn.close()

@mcp.prompt()
def property_search_prompt() -> List[base.Message]:
    """
    Create a prompt template for property searches
    """
    return [
        base.SystemMessage("""
        You are a helpful real estate support agent. 
        Use the available tools to assist the user in finding their ideal property.
        
        Key capabilities:
        - Query listings with city, state, bed, and price filters
        - Get database schema information
        - Calculate average prices for specific areas
        - Find best deals based on price, bedrooms, and location
        
        Available Resources:
        - schema://database: Get full database schema
        - listings://query: Search property listings
        
        Available Tools:
        - describe_columns: Get detailed column descriptions
        - calculate_average_price: Find average prices
        - find_best_deals: Discover top property deals
        """),
        base.UserMessage("How can I help you find your perfect property today?")
    ]

# Lifecycle management
@asynccontextmanager
async def mcp_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """Manage server lifecycle"""
    print("RealEstate MCP Server starting up...")
    try:
        yield {}
    finally:
        print("RealEstate MCP Server shutting down...")

if __name__ == "__main__":
    # Set the lifespan
    mcp.lifespan = mcp_lifespan
    mcp.run(transport='sse')