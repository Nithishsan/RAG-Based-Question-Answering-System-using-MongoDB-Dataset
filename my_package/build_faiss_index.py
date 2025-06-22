from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle


def build_faiss_index(movie_docs, embedding_model_name='all-MiniLM-L6-v2', faiss_index_path='movie_index.faiss', ids_path='movie_ids.pkl'):
    """
    Build FAISS index from movie_docs and save index and ids to disk.

    Args:
        movie_docs (list of dict): Each dict must have keys 'id' and 'text'.
        embedding_model_name (str): SentenceTransformer model name.
        faiss_index_path (str): Path to save the FAISS index.
        ids_path (str): Path to save the IDs mapping.

    Returns:
        faiss.Index: The built FAISS index.
        list: List of document IDs.
    """

    # Load embedding model
    model = SentenceTransformer(embedding_model_name)

    # Extract texts and ids
    texts = [doc['text'] for doc in movie_docs]
    ids = [str(doc['id']) for doc in movie_docs]

    # Embed texts
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    print("emmbeddings region:\n\n",embeddings)

    # Normalize for cosine similarity
    faiss.normalize_L2(embeddings)
    

    # Create FAISS index for cosine similarity
    embedding_dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(embedding_dim)

    # Add vectors
    index.add(embeddings)

    # Save index and ids
    faiss.write_index(index, faiss_index_path)
    with open(ids_path, 'wb') as f:
        pickle.dump(ids, f)

    print(f"FAISS index built with {index.ntotal} vectors and saved to '{faiss_index_path}'")
    print(f"IDs saved to '{ids_path}'")

    return index, ids


def load_faiss_index(faiss_index_path='movie_index.faiss', ids_path='movie_ids.pkl'):
    """
    Load FAISS index and ids from disk.

    Returns:
        faiss.Index: Loaded FAISS index.
        list: List of document IDs.
    """
    index = faiss.read_index(faiss_index_path)
    with open(ids_path, 'rb') as f:
        ids = pickle.load(f)
    return index, ids


def search_movies(query_text, index, ids, model=None, top_k=5):
    """
    Search FAISS index with a query.

    Args:
        query_text (str): Query string.
        index (faiss.Index): FAISS index.
        ids (list): List of document IDs.
        model (SentenceTransformer): Embedding model. If None, default model is loaded.
        top_k (int): Number of top results to return.

    Returns:
        list of dict: Search results with keys 'id', 'score', and 'text_preview'.
    """
    if model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2')

    query_vec = model.encode([query_text], convert_to_numpy=True)
    faiss.normalize_L2(query_vec)
    distances, indices = index.search(query_vec, top_k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        results.append({
            "id": ids[idx],
            "score": float(dist),
            "text_preview": ""  # No text here, load separately if needed
        })

    return results

# def search_movies(query_text, index, ids, movie_docs, model=None, top_k=5):
#     """
#     Search FAISS index with a query.

#     Args:
#         query_text (str): Query string.
#         index (faiss.Index): FAISS index.
#         ids (list): List of document IDs.
#         movie_docs (list of dict): List of documents with 'id' and 'text'.
#         model (SentenceTransformer): Embedding model. If None, default model is loaded.
#         top_k (int): Number of top results to return.

#     Returns:
#         list of dict: Search results with keys 'id', 'score', and 'text_preview'.
#     """
#     if model is None:
#         model = SentenceTransformer('all-MiniLM-L6-v2')

#     query_vec = model.encode([query_text], convert_to_numpy=True)
#     faiss.normalize_L2(query_vec)
#     distances, indices = index.search(query_vec, top_k)

#     # Convert movie_docs list into a dictionary for fast lookup
#     doc_dict = {str(doc['id']): doc['text'] for doc in movie_docs}

#     results = []
#     for dist, idx in zip(distances[0], indices[0]):
#         doc_id = ids[idx]
#         text = doc_dict.get(doc_id, "")
#         text_preview = text[:200] + "..." if text else ""  # preview first 200 characters
#         results.append({
#             "id": doc_id,
#             "score": float(dist),
#             "text_preview": text_preview
#         })

#     return results

# Optional example usage if run as main
# if __name__ == "__main__":
#     # Example: movie_docs should come from your previous code
#     import json

#     # Load or create movie_docs here, e.g. from a file or from your DB extraction script
#     # with open("movie_docs.json") as f:
#     #     movie_docs = json.load(f)

#     # For demo: replace with your actual movie_docs list
#     movie_docs = [
#         {"id": "1", "text": "Title: The Great Train Robbery\nPlot: A group of bandits stage a brazen train hold-up..."},
#         # add more movie docs...
#     ]

#     index, ids = build_faiss_index(movie_docs)

#     query = "A western about train robbery with cowboys and sheriff posse"
#     results = search_movies(query, index, ids)

#     for res in results:
#         print(f"Movie ID: {res['id']}, Score: {res['score']}")
