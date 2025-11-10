"""
Example usage of the Vector Database Creator

This script demonstrates how to use the VectorDBCreator class to:
1. Process text and CSV files
2. Create a local vector database
3. Perform semantic search queries

Run this after installing dependencies:
pip install -r requirements_vector_db.txt
"""

from vector_db.vector_db_creator import VectorDBCreator
import os
from pathlib import Path


def create_sample_files():
    """Create some sample files for testing."""
    sample_dir = Path("sample_data")
    sample_dir.mkdir(exist_ok=True)
    
    # Create a sample text file
    with open(sample_dir / "cruise_info.txt", "w") as f:
        f.write("""
        Welcome to our luxury cruise experience!
        
        Our cruise ships offer world-class dining, entertainment, and accommodations.
        We visit exotic destinations including the Caribbean, Mediterranean, and Alaska.
        
        Onboard amenities include:
        - Multiple restaurants and bars
        - Swimming pools and hot tubs
        - Fitness centers and spas
        - Live entertainment and shows
        - Shopping boutiques
        - Kids' clubs and family activities
        
        Book your dream vacation today!
        """)
    
    # Create a sample CSV file
    import pandas as pd
    cruise_data = {
        'destination': ['Caribbean', 'Mediterranean', 'Alaska', 'Norwegian Fjords', 'Baltic Sea'],
        'duration': [7, 10, 14, 12, 8],
        'price': [1200, 2500, 3200, 2800, 2100],
        'description': [
            'Tropical paradise with beautiful beaches and crystal clear waters',
            'Historic ports with ancient architecture and delicious cuisine',
            'Breathtaking glaciers and wildlife viewing opportunities',
            'Dramatic landscapes with waterfalls and steep cliffs',
            'Cultural cities with rich history and beautiful architecture'
        ],
        'activities': [
            'Beach excursions, snorkeling, water sports',
            'Historical tours, wine tasting, cultural experiences',
            'Glacier viewing, wildlife spotting, hiking',
            'Scenic cruising, hiking, photography',
            'City tours, museums, cultural experiences'
        ]
    }
    
    df = pd.DataFrame(cruise_data)
    df.to_csv(sample_dir / "cruise_destinations.csv", index=False)
    
    print(f"Created sample files in {sample_dir}")
    return sample_dir


def main():
    """Main example function."""
    print("Vector Database Creator Example")
    print("=" * 40)
    
    # Step 1: Create sample files
    sample_dir = create_sample_files()
    
    # Step 2: Initialize the vector database creator
    print("\n1. Initializing Vector Database...")
    vdb = VectorDBCreator(
        db_path="./example_vector_db",
        collection_name="cruise_docs",
        chunk_size=500,
        chunk_overlap=50
    )
    
    # Step 3: Process the text file
    print("\n2. Processing text file...")
    vdb.process_file(str(sample_dir / "cruise_info.txt"))
    
    # Step 4: Process the CSV file
    print("\n3. Processing CSV file...")
    vdb.process_file(
        str(sample_dir / "cruise_destinations.csv"),
        csv_text_columns=['description', 'activities'],
        csv_combine_columns=True
    )
    
    # Step 5: Show database information
    print("\n4. Database Information:")
    info = vdb.get_database_info()
    print(f"   Collection: {info['collection_name']}")
    print(f"   Documents: {info['document_count']}")
    print(f"   Path: {info['database_path']}")
    
    # Step 6: Perform some example searches
    print("\n5. Example Searches:")
    
    search_queries = [
        "luxury dining and restaurants",
        "Alaska cruise with glaciers",
        "family activities for kids",
        "Mediterranean history and culture",
        "swimming pools and water activities"
    ]
    
    for query in search_queries:
        print(f"\n   Query: '{query}'")
        results = vdb.search(query, n_results=2)
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][:2], 
            results['metadatas'][:2], 
            results['distances'][:2]
        )):
            print(f"   Result {i+1} (similarity: {1-distance:.3f}):")
            print(f"   Source: {metadata.get('source', 'Unknown')}")
            print(f"   Content: {doc[:150]}...")
            print()
    
    print("\n6. Advanced Search with Filters:")
    # Search only in CSV files
    csv_results = vdb.search(
        "beautiful scenery and nature", 
        n_results=3,
        where={"file_type": "csv"}
    )
    
    print(f"   Query: 'beautiful scenery and nature' (CSV files only)")
    for i, (doc, metadata, distance) in enumerate(zip(
        csv_results['documents'], 
        csv_results['metadatas'], 
        csv_results['distances']
    )):
        print(f"   Result {i+1}:")
        print(f"   Destination: {metadata.get('data_destination', 'Unknown')}")
        print(f"   Price: ${metadata.get('data_price', 'Unknown')}")
        print(f"   Content: {doc[:100]}...")
        print()


def cleanup_example():
    """Clean up example files and database."""
    import shutil
    
    # Remove sample data
    sample_dir = Path("sample_data")
    if sample_dir.exists():
        shutil.rmtree(sample_dir)
        print("Removed sample_data directory")
    
    # Remove example database
    db_dir = Path("example_vector_db")
    if db_dir.exists():
        shutil.rmtree(db_dir)
        print("Removed example_vector_db directory")


if __name__ == "__main__":
    try:
        main()
        
        # Ask user if they want to clean up
        response = input("\nDo you want to clean up the example files and database? (y/n): ")
        if response.lower() in ['y', 'yes']:
            cleanup_example()
        else:
            print("Example files and database preserved for your exploration!")
            
    except ImportError as e:
        print(f"\nError: Missing required dependencies.")
        print("Please install the required packages:")
        print("pip install -r requirements_vector_db.txt")
        print(f"\nSpecific error: {e}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Make sure all dependencies are installed correctly.")