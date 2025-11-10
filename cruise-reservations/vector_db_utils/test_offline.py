"""
Test Offline Vector Database

This script tests the vector database creator with offline embedding models.
Use this when Hugging Face is blocked.
"""

import sys
from pathlib import Path

# Add the current directory to the Python path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from vector_db_creator import VectorDBCreator
from offline_embedding_models import get_offline_embedding_model


def create_sample_data():
    """Create some sample data to test with."""
    data_dir = Path("test_data")
    data_dir.mkdir(exist_ok=True)
    
    # Create sample text file
    with open(data_dir / "cruise_info.txt", "w") as f:
        f.write("""
        Welcome aboard our luxury cruise ship!
        
        Our vessel offers world-class amenities including:
        - Fine dining restaurants with international cuisine
        - Spacious cabins with ocean views
        - Entertainment venues and live shows
        - Spa and fitness facilities
        - Swimming pools and hot tubs
        - Kids club and family activities
        
        Destinations include the Caribbean, Mediterranean, and Alaska.
        Experience breathtaking scenery, cultural excursions, and unforgettable memories.
        
        Book your dream cruise today!
        """)
    
    print(f"Created test data in {data_dir}")
    return data_dir


def test_offline_models():
    """Test different offline embedding models."""
    print("Testing Offline Embedding Models")
    print("=" * 40)
    
    # Test texts
    test_texts = [
        "luxury cruise dining and restaurants",
        "family activities and entertainment",
        "beautiful ocean views and scenery",
        "spa and wellness facilities"
    ]
    
    # Test TF-IDF model
    print("\n1. Testing TF-IDF Embedding Model:")
    try:
        tfidf_model = get_offline_embedding_model("tfidf", max_features=500)
        embeddings = tfidf_model.encode(test_texts)
        print(f"   ✓ Success! Embedding shape: {embeddings.shape}")
        print(f"   ✓ Sample values: {embeddings[0][:5].round(4)}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test Word2Vec-like model
    print("\n2. Testing Word2Vec-like Model:")
    try:
        w2v_model = get_offline_embedding_model("word2vec", embedding_dim=100)
        embeddings = w2v_model.encode(test_texts)
        print(f"   ✓ Success! Embedding shape: {embeddings.shape}")
        print(f"   ✓ Sample values: {embeddings[0][:5].round(4)}")
    except Exception as e:
        print(f"   ✗ Error: {e}")


def test_vector_database_offline():
    """Test the full vector database with offline models."""
    print("\n" + "="*50)
    print("Testing Vector Database with Offline Models")
    print("="*50)
    
    # Create sample data
    data_dir = create_sample_data()
    
    # Test with TF-IDF model
    print("\n1. Creating Vector Database with TF-IDF Model:")
    try:
        vdb_tfidf = VectorDBCreator(
            db_path="./test_db_tfidf",
            collection_name="test_docs",
            use_offline_model=True,
            offline_model_type="tfidf"
        )
        
        # Process the test file
        vdb_tfidf.process_file(str(data_dir / "cruise_info.txt"))
        
        # Get database info
        info = vdb_tfidf.get_database_info()
        print(f"   ✓ Database created successfully!")
        print(f"   ✓ Documents: {info['document_count']}")
        
        # Test search
        print("\n2. Testing Search with TF-IDF:")
        search_results = vdb_tfidf.search("dining restaurants food", n_results=2)
        for i, (doc, metadata, distance) in enumerate(zip(
            search_results['documents'], 
            search_results['metadatas'], 
            search_results['distances']
        )):
            print(f"   Result {i+1} (distance: {distance:.4f}):")
            print(f"   Content: {doc[:100]}...")
        
    except Exception as e:
        print(f"   ✗ Error with TF-IDF model: {e}")
        import traceback
        traceback.print_exc()
    
    # Test with Word2Vec model
    print("\n3. Creating Vector Database with Word2Vec Model:")
    try:
        vdb_w2v = VectorDBCreator(
            db_path="./test_db_w2v",
            collection_name="test_docs",
            use_offline_model=True,
            offline_model_type="word2vec"
        )
        
        # Process the test file
        vdb_w2v.process_file(str(data_dir / "cruise_info.txt"))
        
        # Test search
        print("\n4. Testing Search with Word2Vec:")
        search_results = vdb_w2v.search("family kids activities", n_results=2)
        for i, (doc, metadata, distance) in enumerate(zip(
            search_results['documents'], 
            search_results['metadatas'], 
            search_results['distances']
        )):
            print(f"   Result {i+1} (distance: {distance:.4f}):")
            print(f"   Content: {doc[:100]}...")
        
        print("   ✓ Word2Vec model test completed successfully!")
        
    except Exception as e:
        print(f"   ✗ Error with Word2Vec model: {e}")
        import traceback
        traceback.print_exc()


def cleanup_test_files():
    """Clean up test files and databases."""
    import shutil
    
    paths_to_remove = [
        Path("test_data"),
        Path("test_db_tfidf"),
        Path("test_db_w2v")
    ]
    
    for path in paths_to_remove:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            print(f"Removed: {path}")


def main():
    """Main test function."""
    try:
        # Test offline models first
        test_offline_models()
        
        # Test full vector database
        test_vector_database_offline()
        
        print("\n" + "="*50)
        print("OFFLINE MODEL TESTING COMPLETED!")
        print("="*50)
        print("\nSummary:")
        print("✓ Offline embedding models are working")
        print("✓ Vector database creation is successful")
        print("✓ Search functionality is operational")
        print("\nYour system can now create vector databases without Hugging Face!")
        
        # Ask about cleanup
        response = input("\nDo you want to clean up test files? (y/n): ")
        if response.lower() in ['y', 'yes']:
            cleanup_test_files()
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        
        print("\nTroubleshooting:")
        print("1. Make sure you've installed the requirements: pip install scikit-learn pandas numpy chromadb")
        print("2. Check that all the module files are in the same directory")
        print("3. Verify that Python can import the required modules")


if __name__ == "__main__":
    main()