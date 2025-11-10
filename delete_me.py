from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import sys
from pathlib import Path

# Add vector_db_utils to path
sys.path.append(str(Path(__file__).parent / "vector_db_utils"))
from vector_db_utils.vector_db_creator import VectorDBCreator

# Initialize FastMCP server
mcp = FastMCP("cruise-reservation")

@mcp.tool()
async def search_cruise_info(query: str, max_results: int = 5) -> str:
    """Search the cruise information database for relevant documents.

    Args:
        query: The search query to find relevant cruise information
        max_results: Maximum number of results to return (default: 5)
    """
    try:
        # Initialize vector database connection
        db_path = Path(__file__).parent / "vector_db_utils" / "example_vector_db"
        
        if not db_path.exists():
            return "Error: Vector database not found. Please run build_vector_db.py first to create the database."
        
        # Load the vector database
        vdb = VectorDBCreator(
            db_path=str(db_path),
            collection_name="cruise_docs",
            use_offline_model=True,
            offline_model_type="word2vec"
        )
        
        # Search the database
        results = vdb.search(query, n_results=max_results)
        
        if not results['documents']:
            return f"No relevant information found for query: '{query}'"
        
        # Format the results
        formatted_results = [f"Search Results for: '{query}'\n" + "=" * 50 + "\n"]
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'], 
            results['metadatas'], 
            results['distances']
        ), 1):
            similarity_score = 1 - distance
            source_file = Path(metadata.get('source', 'Unknown')).name
            
            result_text = f"""
Result {i} (Relevance: {similarity_score:.2%}):
Source: {source_file}
Content: {doc}
{'-' * 50}
"""
            formatted_results.append(result_text)
        
        return "\n".join(formatted_results)
        
    except Exception as e:
        return f"Error searching cruise database: {str(e)}"


def main():
    # Initialize and run the server
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
