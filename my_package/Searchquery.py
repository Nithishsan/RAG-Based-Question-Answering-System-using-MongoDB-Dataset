from .build_faiss_index import load_faiss_index, search_movies
from sentence_transformers import SentenceTransformer
from config.db_config import SessionLocal
from Model.Schema import MovieEmbedding
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# Global embedding model (CPU-only)
# -------------------------------
try:
    logger.info("Loading global SentenceTransformer model on CPU...")
    GLOBAL_EMBEDDING_MODEL = SentenceTransformer(
        'all-MiniLM-L6-v2',
        device='cpu'  # force CPU to avoid meta tensor issues
    )
    logger.info("SentenceTransformer model loaded successfully.")
except Exception as e:
    logger.exception("Failed to load SentenceTransformer model.")
    raise e


def get_movie_texts_by_ids(ids):
    """
    Load full text fields for a list of ids from the MovieEmbedding table.
    Returns dict: {id: text}
    """
    if not ids:
        return {}
    session = SessionLocal()
    try:
        # MovieEmbedding.id is stored as string - ensure type match
        ids_str = [str(i) for i in ids]
        rows = session.query(MovieEmbedding).filter(MovieEmbedding.id.in_(ids_str)).all()
        return {str(r.id): r.text for r in rows}
    finally:
        session.close()


class MovieSearcher:
    def __init__(self, faiss_index_path='movie_index.faiss', ids_path='movie_ids.pkl'):
        # Load FAISS index + ids
        self.index, self.ids = load_faiss_index(faiss_index_path, ids_path)

        # Reuse the global embedding model instead of creating a new one
        self.model = GLOBAL_EMBEDDING_MODEL

    def search(self, query_text, top_k=5):
        return search_movies(query_text, self.index, self.ids, self.model, top_k)


def export_movie_search(query_text: str, top_k: int = 5) -> str:
    """
    Returns a formatted string containing the top results and full text for RAG context.
    """
    searcher = MovieSearcher()
    results = searcher.search(query_text, top_k=top_k)
    top_ids = [r["id"] for r in results]
    movie_texts = get_movie_texts_by_ids(top_ids)

    export_text = f"User Query: {query_text}\n\n"
    for res in results:
        movie_id = res['id']
        score = res['score']
        full_text = movie_texts.get(movie_id, "")
        preview = (full_text[:800] + "...") if len(full_text) > 800 else full_text
        export_text += f"Movie ID: {movie_id}, Score: {score:.4f}\nPreview:\n{preview}\n\n"
    return export_text.strip()


def fetch_movie_context_by_title(title: str, top_k: int = 1) -> str:
    """
    A simple fuzzy search by title using the same FAISS index.
    """
    if not title:
        return "No title provided."

    searcher = MovieSearcher()
    results = searcher.search(title, top_k=top_k)
    if not results:
        return f"No movie found matching title '{title}'."

    top_ids = [r["id"] for r in results]
    movie_texts = get_movie_texts_by_ids(top_ids)

    export_text = f"Movie information for: '{title}'\n\n"
    for res in results:
        movie_id = res['id']
        score = res['score']
        full_text = movie_texts.get(movie_id, "")
        export_text += f"Movie ID: {movie_id}, Score: {score:.4f}\nFull Info:\n{full_text}\n\n"
    return export_text.strip()
