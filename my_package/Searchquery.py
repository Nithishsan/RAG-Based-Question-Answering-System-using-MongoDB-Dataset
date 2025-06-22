from .build_faiss_index import load_faiss_index, search_movies, SentenceTransformer
from config.db_config import SessionLocal
from Model.Schema import MovieEmbedding

def get_movie_texts_by_ids(ids):
    session = SessionLocal()
    result = session.query(MovieEmbedding).filter(MovieEmbedding.id.in_(ids)).all()
    session.close()
    return {movie.id: movie.text for movie in result}

class MovieSearcher:
    def __init__(self):
        self.index, self.ids = load_faiss_index()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def search(self, query_text, top_k=5):
        return search_movies(query_text, self.index, self.ids, self.model, top_k)

def export_movie_search(query_text: str, top_k: int = 5) -> str:
    searcher = MovieSearcher()
    results = searcher.search(query_text, top_k=top_k)
    
    top_ids = [r["id"] for r in results]
    movie_texts = get_movie_texts_by_ids(top_ids)

    export_text = f"User Query: {query_text}\n\n"
    for res in results:
        movie_id = res['id']
        score = res['score']
        full_text = movie_texts.get(movie_id, "")
        export_text += f"Movie ID: {movie_id}, Score: {score:.4f}\nPreview:\n{full_text}\n\n"
    print(export_text)
    return export_text

# 🔍 New: Fetch context by title (exact or fuzzy match)
def fetch_movie_context_by_title(title: str, top_k: int = 1) -> str:
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
