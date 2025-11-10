"""
Vector Database Creator

This module provides functionality to convert text and CSV files into a local vector database
using embeddings. The vector database can be used for semantic search and retrieval.

Dependencies:
- pip install pandas sentence-transformers chromadb langchain langchain-community python-dotenv
"""

import os
import json
import logging
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

# Vector database and embedding imports
import chromadb
from chromadb.config import Settings

# Try to import sentence transformers, fallback to offline models if blocked
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Using offline models.")

# Import offline embedding models
try:
    from offline_embedding_models import get_offline_embedding_model
    OFFLINE_MODELS_AVAILABLE = True
except ImportError:
    OFFLINE_MODELS_AVAILABLE = False

# Text processing imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDBCreator:
    """
    A class to create and manage a local vector database from text and CSV files.
    """
    
    def __init__(self, 
                 db_path: str = "./vector_db",
                 collection_name: str = "documents",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 use_offline_model: bool = False,
                 offline_model_type: str = "tfidf"):
        """
        Initialize the VectorDBCreator.
        
        Args:
            db_path: Path to store the vector database
            collection_name: Name of the collection in the database
            embedding_model: Name of the sentence transformer model to use
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks
            use_offline_model: Whether to use offline embedding models
            offline_model_type: Type of offline model ('tfidf', 'word2vec')
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)
        
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.use_offline_model = use_offline_model
        
        # Initialize embedding model
        self._initialize_embedding_model(embedding_model, offline_model_type)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "Document embeddings for semantic search"}
            )
            logger.info(f"Created new collection: {collection_name}")
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
    
    def _initialize_embedding_model(self, model_name: str, offline_model_type: str):
        """Initialize the appropriate embedding model."""
        if self.use_offline_model or not SENTENCE_TRANSFORMERS_AVAILABLE:
            # Use offline model
            if OFFLINE_MODELS_AVAILABLE:
                logger.info(f"Using offline embedding model: {offline_model_type}")
                if offline_model_type == "tfidf":
                    self.embedding_model = get_offline_embedding_model(
                        "tfidf", max_features=1000, ngram_range=(1, 2)
                    )
                elif offline_model_type == "word2vec":
                    self.embedding_model = get_offline_embedding_model(
                        "word2vec", embedding_dim=300
                    )
                else:
                    logger.warning(f"Unknown offline model type: {offline_model_type}. Using TF-IDF")
                    self.embedding_model = get_offline_embedding_model("tfidf")
                
                # For offline models, we need to collect texts first to fit the model
                self._offline_texts_for_fitting = []
                self._model_fitted = False
            else:
                raise ImportError("Offline models not available. Please check offline_embedding_models.py")
        else:
            # Use sentence transformers
            try:
                logger.info(f"Loading sentence transformer model: {model_name}")
                self.embedding_model = SentenceTransformer(model_name)
                self._model_fitted = True
            except Exception as e:
                logger.error(f"Failed to load sentence transformer model: {e}")
                logger.info("Falling back to offline TF-IDF model")
                if OFFLINE_MODELS_AVAILABLE:
                    self.embedding_model = get_offline_embedding_model("tfidf")
                    self._offline_texts_for_fitting = []
                    self._model_fitted = False
                    self.use_offline_model = True
                else:
                    raise ImportError("Both online and offline models are unavailable")
    
    def process_text_file(self, file_path: str) -> List[Document]:
        """
        Process a text file and split it into chunks.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            List of Document objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Create document
            document = Document(
                page_content=content,
                metadata={
                    "source": file_path,
                    "file_type": "text",
                    "processed_at": datetime.now().isoformat()
                }
            )
            
            # Split into chunks
            chunks = self.text_splitter.split_documents([document])
            
            # Add chunk information to metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata.update({
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
            
            logger.info(f"Processed text file {file_path}: {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
            return []
    
    def process_csv_file(self, 
                        file_path: str, 
                        text_columns: Optional[List[str]] = None,
                        combine_columns: bool = True) -> List[Document]:
        """
        Process a CSV file and convert rows to documents.
        
        Args:
            file_path: Path to the CSV file
            text_columns: Specific columns to use for text content (if None, use all)
            combine_columns: Whether to combine all columns into single documents
            
        Returns:
            List of Document objects
        """
        try:
            df = pd.read_csv(file_path)
            documents = []
            
            # If no text columns specified, use all string columns
            if text_columns is None:
                text_columns = df.select_dtypes(include=['object']).columns.tolist()
            
            if combine_columns:
                # Combine all specified columns into single documents per row
                for idx, row in df.iterrows():
                    # Create content by combining text columns
                    content_parts = []
                    for col in text_columns:
                        if pd.notna(row[col]):
                            content_parts.append(f"{col}: {row[col]}")
                    
                    if content_parts:
                        content = " | ".join(content_parts)
                        
                        # Create metadata with all columns
                        metadata = {
                            "source": file_path,
                            "file_type": "csv",
                            "row_index": idx,
                            "processed_at": datetime.now().isoformat()
                        }
                        
                        # Add all non-text columns as metadata
                        for col in df.columns:
                            if col not in text_columns and pd.notna(row[col]):
                                metadata[f"data_{col}"] = str(row[col])
                        
                        document = Document(
                            page_content=content,
                            metadata=metadata
                        )
                        documents.append(document)
            else:
                # Create separate documents for each text column
                for col in text_columns:
                    for idx, value in enumerate(df[col].dropna()):
                        metadata = {
                            "source": file_path,
                            "file_type": "csv",
                            "column": col,
                            "row_index": idx,
                            "processed_at": datetime.now().isoformat()
                        }
                        
                        # Add related row data as metadata
                        for other_col in df.columns:
                            if other_col != col and pd.notna(df.iloc[idx][other_col]):
                                metadata[f"data_{other_col}"] = str(df.iloc[idx][other_col])
                        
                        document = Document(
                            page_content=str(value),
                            metadata=metadata
                        )
                        documents.append(document)
            
            logger.info(f"Processed CSV file {file_path}: {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Error processing CSV file {file_path}: {e}")
            return []
    
    def add_documents_to_db(self, documents: List[Document]) -> None:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of Document objects to add
        """
        if not documents:
            logger.warning("No documents to add to database")
            return
        
        # Extract texts and metadata
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # For offline models, collect texts for fitting if not yet fitted
        if self.use_offline_model and not self._model_fitted:
            self._offline_texts_for_fitting.extend(texts)
            # Fit the model if we have enough texts
            if len(self._offline_texts_for_fitting) >= 10:  # Minimum texts for fitting
                logger.info("Fitting offline model with collected texts...")
                if hasattr(self.embedding_model, 'fit'):
                    self.embedding_model.fit(self._offline_texts_for_fitting)
                self._model_fitted = True
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(texts)} documents...")
        try:
            embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            # Try without progress bar as fallback
            try:
                embeddings = self.embedding_model.encode(texts)
            except Exception as e2:
                logger.error(f"Failed to generate embeddings: {e2}")
                return
        
        # Generate unique IDs
        existing_count = self.collection.count()
        ids = [f"doc_{existing_count + i}" for i in range(len(documents))]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(documents)} documents to the vector database")
    
    def process_file(self, 
                    file_path: str, 
                    file_type: Optional[str] = None,
                    csv_text_columns: Optional[List[str]] = None,
                    csv_combine_columns: bool = True) -> None:
        """
        Process a single file and add it to the vector database.
        
        Args:
            file_path: Path to the file to process
            file_type: Type of file ('text' or 'csv'). If None, infer from extension
            csv_text_columns: For CSV files, columns to use for text content
            csv_combine_columns: For CSV files, whether to combine columns
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File does not exist: {file_path}")
            return
        
        # Infer file type if not provided
        if file_type is None:
            if file_path.suffix.lower() in ['.txt', '.md', '.rst']:
                file_type = 'text'
            elif file_path.suffix.lower() == '.csv':
                file_type = 'csv'
            else:
                logger.error(f"Cannot infer file type for {file_path}. Please specify file_type.")
                return
        
        # Process based on file type
        documents = []
        if file_type == 'text':
            documents = self.process_text_file(str(file_path))
        elif file_type == 'csv':
            documents = self.process_csv_file(
                str(file_path), 
                csv_text_columns, 
                csv_combine_columns
            )
        else:
            logger.error(f"Unsupported file type: {file_type}")
            return
        
        # Add to database
        self.add_documents_to_db(documents)
    
    def process_directory(self, 
                         directory_path: str,
                         file_extensions: Optional[List[str]] = None,
                         recursive: bool = True) -> None:
        """
        Process all supported files in a directory.
        
        Args:
            directory_path: Path to the directory
            file_extensions: List of file extensions to process (default: ['.txt', '.csv', '.md'])
            recursive: Whether to process subdirectories
        """
        if file_extensions is None:
            file_extensions = ['.txt', '.csv', '.md', '.rst']
        
        directory_path = Path(directory_path)
        
        if not directory_path.exists():
            logger.error(f"Directory does not exist: {directory_path}")
            return
        
        # Find files to process
        pattern = "**/*" if recursive else "*"
        files_to_process = []
        
        for file_path in directory_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in file_extensions:
                files_to_process.append(file_path)
        
        logger.info(f"Found {len(files_to_process)} files to process")
        
        # Process each file
        for file_path in files_to_process:
            logger.info(f"Processing: {file_path}")
            self.process_file(str(file_path))
    
    def search(self, 
               query: str, 
               n_results: int = 5,
               where: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Search the vector database for similar documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            where: Metadata filters
            
        Returns:
            Dictionary containing search results
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Search the collection
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where
        )
        
        return {
            'query': query,
            'documents': results['documents'][0],
            'metadatas': results['metadatas'][0],
            'distances': results['distances'][0],
            'ids': results['ids'][0]
        }
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get information about the current database.
        
        Returns:
            Dictionary with database statistics
        """
        count = self.collection.count()
        return {
            'collection_name': self.collection_name,
            'document_count': count,
            'database_path': str(self.db_path),
            'embedding_model': self.embedding_model.get_sentence_embedding_dimension()
        }
    
    def delete_collection(self) -> None:
        """Delete the current collection and all its data."""
        self.client.delete_collection(self.collection_name)
        logger.info(f"Deleted collection: {self.collection_name}")


def main():
    """Example usage of the VectorDBCreator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create a vector database from files")
    parser.add_argument("--path", required=True, help="Path to file or directory")
    parser.add_argument("--db-path", default="./vector_db", help="Database path")
    parser.add_argument("--collection", default="documents", help="Collection name")
    parser.add_argument("--recursive", action="store_true", help="Process directories recursively")
    parser.add_argument("--search", help="Search query to test the database")
    
    args = parser.parse_args()
    
    # Create vector database
    vdb = VectorDBCreator(
        db_path=args.db_path,
        collection_name=args.collection
    )
    
    # Process files
    path = Path(args.path)
    if path.is_file():
        vdb.process_file(str(path))
    elif path.is_directory():
        vdb.process_directory(str(path), recursive=args.recursive)
    else:
        logger.error(f"Invalid path: {path}")
        return
    
    # Show database info
    info = vdb.get_database_info()
    print(f"\nDatabase Info:")
    print(f"Collection: {info['collection_name']}")
    print(f"Documents: {info['document_count']}")
    print(f"Path: {info['database_path']}")
    
    # Test search if query provided
    if args.search:
        results = vdb.search(args.search)
        print(f"\nSearch Results for '{args.search}':")
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'], 
            results['metadatas'], 
            results['distances']
        )):
            print(f"\n{i+1}. Distance: {distance:.4f}")
            print(f"Source: {metadata.get('source', 'Unknown')}")
            print(f"Content: {doc[:200]}...")


if __name__ == "__main__":
    main()