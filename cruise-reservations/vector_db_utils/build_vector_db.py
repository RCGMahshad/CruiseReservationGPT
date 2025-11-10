from vector_db_creator import VectorDBCreator
import os
from pathlib import Path

def main():
    
    ship_desc_path = Path("data/ship_descriptions")
    itinerary_path = Path("data/itineraries")
    
    # Configuration
    db_path = "./example_vector_db"
    collection_name = "cruise_docs"
    offline_model_type = "word2vec"  # Options: "tfidf" or "word2vec"
    
    # Check if database exists and clean up if needed to avoid dimension mismatch
    db_path_obj = Path(db_path)
    if db_path_obj.exists():
        print("\n⚠ Existing database found. Cleaning up to avoid dimension mismatch...")
        import shutil
        shutil.rmtree(db_path_obj)
        print("✓ Old database removed.")
    
    # Step 2: Initialize the vector database creator with offline model
    print("\n1. Initializing Vector Database (Offline Mode)...")
    vdb = VectorDBCreator(
        db_path=db_path,
        collection_name=collection_name,
        chunk_size=500,
        chunk_overlap=50,
        use_offline_model=True,  # Use offline model instead of Hugging Face
        offline_model_type=offline_model_type
    )
    print(f"✓ Using {offline_model_type} embedding model")
    
    # Step 3: Process all files in ship descriptions folder
    print("\n2. Processing ship description files...")
    if ship_desc_path.exists():
        vdb.process_directory(str(ship_desc_path), recursive=False)
        print(f"   ✓ Processed all files in {ship_desc_path}")
    else:
        print(f"   ⚠ Ship descriptions folder not found: {ship_desc_path}")
        print("   Creating sample file for testing...")
        ship_desc_path.mkdir(parents=True, exist_ok=True)
        sample_file = ship_desc_path / "sample_cruise_info.txt"
        with open(sample_file, 'w') as f:
            f.write("Sample cruise ship with luxury amenities and dining options.")
        vdb.process_file(str(sample_file))
    
    '''
    # Step 3: Process the CSV file (optional)
    print("\n3. Processing CSV file...")
    vdb.process_file(
        str(itinerary_path / "cruise_destinations.csv"),
        csv_text_columns=['description', 'activities'],
        csv_combine_columns=True
    )
    '''
    
    # Step 4: Show database information
    print("\n3. Database Information:")
    info = vdb.get_database_info()
    print(f"   Collection: {info['collection_name']}")
    print(f"   Documents: {info['document_count']}")
    print(f"   Path: {info['database_path']}")
    
    # Step 5: Perform some example searches
    print("\n4. Example Searches:")
    
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
    
    print("\n5. Advanced Search with Filters:")
    # Search only in text files from ship descriptions
    text_results = vdb.search(
        "luxury amenities and facilities", 
        n_results=3,
        where={"file_type": "text"}
    )
    
    print(f"   Query: 'luxury amenities and facilities' (text files only)")
    for i, (doc, metadata, distance) in enumerate(zip(
        text_results['documents'], 
        text_results['metadatas'], 
        text_results['distances']
    )):
        print(f"   Result {i+1}:")
        print(f"   Source: {Path(metadata.get('source', 'Unknown')).name}")
        print(f"   Similarity: {1-distance:.3f}")
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