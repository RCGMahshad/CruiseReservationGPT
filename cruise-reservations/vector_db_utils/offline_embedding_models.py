"""
Offline Embedding Models

This module provides alternative embedding methods when Hugging Face is blocked.
Includes simple TF-IDF, Word2Vec, and pre-downloaded model options.
"""

import os
import numpy as np
import pickle
from pathlib import Path
from typing import List, Union, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)


class SimpleEmbeddingModel:
    """Base class for simple embedding models."""
    
    def __init__(self):
        self.is_fitted = False
        self.embedding_dimension = None
    
    def encode(self, texts: Union[str, List[str]], **kwargs) -> np.ndarray:
        """Encode texts into embeddings."""
        raise NotImplementedError
    
    def get_sentence_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        return self.embedding_dimension


class TFIDFEmbeddingModel(SimpleEmbeddingModel):
    """TF-IDF based embedding model that works completely offline."""
    
    def __init__(self, max_features: int = 5000, ngram_range: tuple = (1, 2)):
        super().__init__()
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            stop_words='english',
            lowercase=True,
            token_pattern=r'\b[a-zA-Z][a-zA-Z0-9]*\b'
        )
        self.embedding_dimension = max_features
        logger.info(f"Initialized TF-IDF model with max_features={max_features}")
    
    def fit(self, texts: List[str]):
        """Fit the TF-IDF vectorizer on the provided texts."""
        logger.info("Fitting TF-IDF vectorizer...")
        self.vectorizer.fit(texts)
        self.is_fitted = True
        # Update actual dimension based on fitted vocabulary
        self.embedding_dimension = len(self.vectorizer.vocabulary_)
        logger.info(f"TF-IDF model fitted with vocabulary size: {self.embedding_dimension}")
    
    def encode(self, texts: Union[str, List[str]], show_progress_bar: bool = False) -> np.ndarray:
        """Encode texts using TF-IDF."""
        if isinstance(texts, str):
            texts = [texts]
        
        if not self.is_fitted:
            logger.warning("TF-IDF model not fitted. Fitting on provided texts...")
            self.fit(texts)
        
        try:
            embeddings = self.vectorizer.transform(texts).toarray()
            return embeddings
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            # Return zero embeddings as fallback
            return np.zeros((len(texts), self.embedding_dimension))


class Word2VecEmbeddingModel(SimpleEmbeddingModel):
    """Simple Word2Vec-like model using word averaging."""
    
    def __init__(self, embedding_dim: int = 300):
        super().__init__()
        self.embedding_dimension = embedding_dim
        self.word_vectors = {}
        self._create_simple_word_vectors()
        logger.info(f"Initialized simple Word2Vec model with {embedding_dim} dimensions")
    
    def _create_simple_word_vectors(self):
        """Create simple random word vectors for common words."""
        # Common words that might appear in cruise-related content
        common_words = [
            'cruise', 'ship', 'ocean', 'sea', 'travel', 'vacation', 'luxury', 'dining',
            'restaurant', 'entertainment', 'cabin', 'deck', 'port', 'destination',
            'caribbean', 'mediterranean', 'alaska', 'norway', 'activities', 'family',
            'kids', 'adult', 'spa', 'fitness', 'pool', 'beach', 'excursion', 'tour',
            'culture', 'history', 'scenic', 'beautiful', 'food', 'drink', 'bar',
            'show', 'music', 'dance', 'shopping', 'boutique', 'casino', 'theatre',
            'balcony', 'suite', 'standard', 'premium', 'package', 'booking', 'price',
            'cost', 'schedule', 'itinerary', 'duration', 'night', 'day', 'departure',
            'arrival', 'accommodation', 'service', 'staff', 'friendly', 'professional',
            'clean', 'comfortable', 'spacious', 'modern', 'traditional', 'authentic'
        ]
        
        # Use deterministic random seed for consistency
        np.random.seed(42)
        for word in common_words:
            self.word_vectors[word] = np.random.normal(0, 0.1, self.embedding_dimension)
    
    def _get_word_vector(self, word: str) -> np.ndarray:
        """Get vector for a word, creating one if it doesn't exist."""
        word = word.lower().strip()
        if word in self.word_vectors:
            return self.word_vectors[word]
        else:
            # Create a simple hash-based vector for unknown words
            hash_val = hash(word) % 1000000
            np.random.seed(hash_val)
            vector = np.random.normal(0, 0.1, self.embedding_dimension)
            self.word_vectors[word] = vector
            return vector
    
    def encode(self, texts: Union[str, List[str]], show_progress_bar: bool = False) -> np.ndarray:
        """Encode texts by averaging word vectors."""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = []
        for text in texts:
            # Simple tokenization
            words = text.lower().split()
            word_vectors = []
            
            for word in words:
                # Remove basic punctuation
                clean_word = ''.join(c for c in word if c.isalnum())
                if clean_word:
                    word_vectors.append(self._get_word_vector(clean_word))
            
            if word_vectors:
                # Average the word vectors
                text_embedding = np.mean(word_vectors, axis=0)
            else:
                # Fallback to zero vector
                text_embedding = np.zeros(self.embedding_dimension)
            
            embeddings.append(text_embedding)
        
        return np.array(embeddings)


class PreDownloadedModel(SimpleEmbeddingModel):
    """Wrapper for pre-downloaded sentence transformer models."""
    
    def __init__(self, model_path: str):
        super().__init__()
        self.model_path = Path(model_path)
        self.model = None
        self.embedding_dimension = 384  # Default for many models
        
        if self.model_path.exists():
            try:
                # Try to load a pre-downloaded sentence transformer model
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(str(model_path), local_files_only=True)
                self.embedding_dimension = self.model.get_sentence_embedding_dimension()
                logger.info(f"Loaded pre-downloaded model from {model_path}")
            except Exception as e:
                logger.warning(f"Could not load model from {model_path}: {e}")
                self.model = None
        else:
            logger.warning(f"Model path does not exist: {model_path}")
    
    def encode(self, texts: Union[str, List[str]], show_progress_bar: bool = False) -> np.ndarray:
        """Encode using the pre-downloaded model or fallback."""
        if self.model:
            return self.model.encode(texts, show_progress_bar=show_progress_bar)
        else:
            # Fallback to simple method
            logger.warning("Using fallback encoding method")
            fallback_model = TFIDFEmbeddingModel(max_features=self.embedding_dimension)
            return fallback_model.encode(texts)


def get_offline_embedding_model(
    model_type: str = "tfidf",
    model_path: Optional[str] = None,
    **kwargs
) -> SimpleEmbeddingModel:
    """
    Get an offline embedding model.
    
    Args:
        model_type: Type of model ('tfidf', 'word2vec', 'predownloaded')
        model_path: Path to pre-downloaded model (for 'predownloaded' type)
        **kwargs: Additional arguments for the model
    
    Returns:
        An embedding model that works offline
    """
    
    if model_type.lower() == "tfidf":
        return TFIDFEmbeddingModel(**kwargs)
    elif model_type.lower() == "word2vec":
        return Word2VecEmbeddingModel(**kwargs)
    elif model_type.lower() == "predownloaded":
        if not model_path:
            raise ValueError("model_path is required for predownloaded model type")
        return PreDownloadedModel(model_path)
    else:
        logger.warning(f"Unknown model type: {model_type}. Defaulting to TF-IDF")
        return TFIDFEmbeddingModel()


def download_model_manually():
    """
    Instructions for manually downloading models when Hugging Face is blocked.
    """
    instructions = """
    MANUAL MODEL DOWNLOAD INSTRUCTIONS
    ==================================
    
    If Hugging Face is blocked, you can manually download models:
    
    1. ON A DIFFERENT NETWORK (where HF is accessible):
       
       from sentence_transformers import SentenceTransformer
       model = SentenceTransformer('all-MiniLM-L6-v2')
       model.save('./local_models/all-MiniLM-L6-v2')
    
    2. COPY THE MODEL FILES:
       - Copy the entire './local_models/all-MiniLM-L6-v2' folder
       - Place it in your project directory
    
    3. USE WITH PREDOWNLOADED MODEL:
       
       model = get_offline_embedding_model(
           model_type="predownloaded",
           model_path="./local_models/all-MiniLM-L6-v2"
       )
    
    ALTERNATIVE DOWNLOAD SOURCES:
    ============================
    
    1. Direct download from model repositories
    2. Use a VPN to access Hugging Face
    3. Download via Google Colab and transfer files
    4. Use the offline models provided in this module
    
    """
    return instructions


if __name__ == "__main__":
    # Test the offline models
    print("Testing Offline Embedding Models")
    print("=" * 35)
    
    test_texts = [
        "luxury cruise dining experience",
        "family activities on cruise ship",
        "beautiful ocean views and scenery"
    ]
    
    # Test TF-IDF model
    print("\n1. Testing TF-IDF Model:")
    tfidf_model = get_offline_embedding_model("tfidf", max_features=1000)
    tfidf_embeddings = tfidf_model.encode(test_texts)
    print(f"   Embeddings shape: {tfidf_embeddings.shape}")
    print(f"   Sample embedding (first 10 values): {tfidf_embeddings[0][:10]}")
    
    # Test Word2Vec model
    print("\n2. Testing Word2Vec Model:")
    w2v_model = get_offline_embedding_model("word2vec", embedding_dim=100)
    w2v_embeddings = w2v_model.encode(test_texts)
    print(f"   Embeddings shape: {w2v_embeddings.shape}")
    print(f"   Sample embedding (first 10 values): {w2v_embeddings[0][:10]}")
    
    # Test similarity
    print("\n3. Testing Similarity:")
    similarity = cosine_similarity([w2v_embeddings[0]], [w2v_embeddings[1]])[0][0]
    print(f"   Similarity between first two texts: {similarity:.4f}")
    
    print("\n4. Manual Download Instructions:")
    #download_model_manually()