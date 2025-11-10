# Vector Database Creator Setup Guide

## Overview
The Vector Database Creator allows you to convert text files and CSV files into a searchable vector database that runs locally on your machine. This enables semantic search capabilities for your documents.

## Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements_vector_db.txt
```

### 2. Alternative Installation (if requirements file doesn't work)
```bash
pip install pandas chromadb sentence-transformers langchain langchain-community python-dotenv tqdm
```

## Quick Start

### 1. Basic Usage - Process a Single File
```python
from vector_db_creator import VectorDBCreator

# Create vector database instance
vdb = VectorDBCreator(db_path="./my_vector_db", collection_name="my_documents")

# Process a text file
vdb.process_file("path/to/your/document.txt")

# Process a CSV file
vdb.process_file("path/to/your/data.csv", csv_text_columns=['description', 'content'])

# Search the database
results = vdb.search("your search query", n_results=5)
print(results)
```

### 2. Process an Entire Directory
```python
# Process all supported files in a directory
vdb.process_directory("path/to/your/documents", recursive=True)
```

### 3. Run the Example
```bash
python example_usage.py
```

## Command Line Usage

```bash
# Process a single file
python vector_db_creator.py --path "document.txt" --db-path "./my_db"

# Process a directory recursively
python vector_db_creator.py --path "documents/" --recursive --db-path "./my_db"

# Process and test with a search query
python vector_db_creator.py --path "documents/" --search "cruise destinations"
```

## Supported File Types

### Text Files
- `.txt` - Plain text files
- `.md` - Markdown files
- `.rst` - ReStructuredText files

### CSV Files
- `.csv` - Comma-separated values files
- Can specify which columns to use for text content
- Can combine multiple columns or process them separately

## Configuration Options

### Vector Database Settings
- `db_path`: Directory to store the vector database
- `collection_name`: Name of the collection within the database
- `embedding_model`: Sentence transformer model to use (default: "all-MiniLM-L6-v2")

### Text Processing Settings
- `chunk_size`: Maximum size of text chunks (default: 1000 characters)
- `chunk_overlap`: Overlap between text chunks (default: 200 characters)

### CSV Processing Options
- `csv_text_columns`: List of column names to use for text content
- `csv_combine_columns`: Whether to combine columns into single documents (default: True)

## Advanced Features

### 1. Metadata Filtering
```python
# Search only in specific file types
results = vdb.search("query", where={"file_type": "csv"})

# Search in files from specific sources
results = vdb.search("query", where={"source": "important_doc.txt"})
```

### 2. Database Management
```python
# Get database statistics
info = vdb.get_database_info()
print(f"Total documents: {info['document_count']}")

# Delete the collection (be careful!)
# vdb.delete_collection()
```

### 3. Custom Processing
```python
# Process CSV with specific columns only
vdb.process_file(
    "data.csv", 
    csv_text_columns=['title', 'description'], 
    csv_combine_columns=False  # Create separate documents per column
)
```

## Performance Tips

1. **Embedding Model Selection**:
   - `all-MiniLM-L6-v2`: Fast, good for general use (default)
   - `all-mpnet-base-v2`: Better quality, slower
   - `all-distilroberta-v1`: Good balance of speed and quality

2. **Chunk Size**:
   - Smaller chunks (500-1000): Better for precise search
   - Larger chunks (1000-2000): Better for context retention

3. **Hardware**:
   - More RAM: Can process larger files
   - GPU: Install `torch` with CUDA for faster embeddings

## Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements_vector_db.txt
   ```

2. **Memory Issues with Large Files**:
   - Reduce `chunk_size`
   - Process files individually instead of entire directories

3. **Slow Embedding Generation**:
   - Use a smaller/faster model
   - Process files in smaller batches

4. **Search Results Not Relevant**:
   - Try different embedding models
   - Adjust chunk size and overlap
   - Ensure your data quality is good

### Getting Help

If you encounter issues:
1. Check that all dependencies are installed correctly
2. Verify file paths are correct
3. Ensure files are readable and in supported formats
4. Check the logs for error messages

## Example Use Cases

- **Document Search**: Create a searchable database of company documents
- **Knowledge Base**: Build a semantic search system for FAQs or manuals
- **Data Analysis**: Search through CSV data using natural language queries
- **Content Discovery**: Find related content across multiple file types

## Next Steps

After setting up your vector database:
1. Experiment with different search queries
2. Try different embedding models for your use case
3. Integrate the search functionality into your applications
4. Set up automated processing for new files