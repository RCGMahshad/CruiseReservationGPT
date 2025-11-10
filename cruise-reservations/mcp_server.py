from typing import Any
from mcp.server.fastmcp import FastMCP
import sys
from pathlib import Path
import csv

# Add vector_db_utils to path
sys.path.append(str(Path(__file__).parent / "vector_db_utils"))
from vector_db_utils.vector_db_creator import VectorDBCreator

# Initialize FastMCP server
mcp = FastMCP("cruise-reservation")

@mcp.tool()
async def get_ship_descriptions(query: str, max_results: int = 5) -> str:
    """Search the Royal Caribbean cruise information database
    for information regarding cruises based on the provided query.

    Args:
        query: Users search query, giving context about the types of cruises they are looking for
        max_results: Maximum number of results to return (default: 5)
    """
    try:
        # Initialize vector database connection
        db_path = Path(__file__).parent / "example_vector_db"
        
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


@mcp.tool()
async def get_cruise_itineraries() -> str:
    """Get all available Royal Caribbean cruise itineraries from the CSV file.
    
    Returns a formatted string containing all cruise itinerary information
    including departure dates, destinations, durations, and prices.
    """
    try:
        # Path to the CSV file
        csv_path = Path(__file__).parent / "data" / "cruise_itineraries.csv"
        
        if not csv_path.exists():
            return f"Error: Cruise itineraries file not found at {csv_path}"
        
        # Read the CSV file
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            rows = list(csv_reader)
        
        if not rows:
            return "No itineraries found in the CSV file."
        
        # Format the results
        result = ["Cruise Itineraries\n" + "=" * 80 + "\n"]
        result.append(f"Total Itineraries: {len(rows)}\n")
        result.append("-" * 80 + "\n")
        
        for i, row in enumerate(rows, 1):
            itinerary_text = f"""
Itinerary {i}:
  Ship: {row.get('ship', 'N/A')}
  Dates: {row.get('date', 'N/A')}
  Destinations: {row.get('itinerary', 'N/A')}
  Cabin Type: {row.get('cabin_type', 'N/A')}
  Price (Per Person): ${row.get('price', 'N/A')}
{'-' * 80}
"""
            result.append(itinerary_text)
        
        return "\n".join(result)
        
    except Exception as e:
        return f"Error reading cruise itineraries: {str(e)}"


@mcp.tool()
async def reserve_cruise(email: str, first_name: str, last_name: str, ship: str, sail_date: str, cabin_type: str, num_travelers: int, price: float) -> str:
    """Reserve a cruise for a customer. You only need one name on the reservation, not the names of the other travellers.
    
    Args:
        email: Customer's email address
        first_name: Customer's first name
        last_name: Customer's last name
        ship: Name of the ship
        sail_date: Date of the cruise
        cabin_type: Type of cabin
        num_travelers: Number of travelers
        price: Price per person
    
    Returns:
        Confirmation message with reservation details
    """

    print(email, first_name, last_name, ship, sail_date, cabin_type, price)

    try:
        # Generate a unique reservation ID
        from datetime import datetime
        import random
        reservation_id = f"RC{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        
        # Path to reservations file
        reservations_file = Path(__file__).parent / "data" / "cruise_reservations.csv"
        
        # Create data directory if it doesn't exist
        reservations_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists to determine if we need headers
        file_exists = reservations_file.exists()
        
        # Append reservation to CSV
        with open(reservations_file, 'a', newline='', encoding='utf-8') as file:
            fieldnames = ['reservation_id', 'email', 'first_name', 'last_name', 'ship', 'sail_date', 'cabin_type', 'num_travelers', 'price', 'reservation_date']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # Write header if file is new
            if not file_exists:
                writer.writeheader()
            
            # Write reservation data
            writer.writerow({
                'reservation_id': reservation_id,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'ship': ship,
                'sail_date': sail_date,
                'cabin_type': cabin_type,
                'num_travelers': num_travelers,
                'price': price,
                'reservation_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Format confirmation message
        confirmation = f"""
{'='*80}
CRUISE RESERVATION CONFIRMED
{'='*80}

Reservation ID: {reservation_id}
Customer Name: {first_name} {last_name}
Email: {email}
Ship: {ship}
Sail Date: {sail_date}
Cabin Type: {cabin_type}
Number of Travelers: {num_travelers}
Price (Per Person): ${price:.2f}
Reservation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*80}

Thank you for booking with Royal Caribbean! A confirmation email will be sent to {email}.
Your reservation ID is: {reservation_id}

Please keep this reservation ID for your records.
{'='*80}
"""
        
        return confirmation
        
    except Exception as e:
        return f"Error creating reservation: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')