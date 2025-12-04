# my_package/insert.py
"""
Build movie_docs from SQL models, insert into MovieEmbedding table and build FAISS index.
Run this after you've migrated Mongo -> SQL (main.py).
"""
from config.db_config import SessionLocal
from Model.Schema import Movie, MovieEmbedding
from .build_faiss_index import build_faiss_index
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def insert_movie_docs(movie_docs):
    """
    Persist movie_docs into MovieEmbedding table. movie_docs: list of {'id': str, 'text': str}
    """
    session = SessionLocal()
    try:
        for doc in movie_docs:
            movie_id = str(doc["id"])
            text = doc["text"]
            entry = MovieEmbedding(id=movie_id, text=text)
            session.merge(entry)
        session.commit()
        logger.info("Inserted/updated %d MovieEmbedding rows", len(movie_docs))
    except Exception as e:
        session.rollback()
        logger.exception("Failed to insert movie docs: %s", e)
        raise
    finally:
        session.close()

def process_and_index_movies():
    session = SessionLocal()
    try:
        movies = session.query(Movie).all()
        movie_docs = []
        for movie in movies:
            parts = []
            # Basic text concatenation: keep the same fields as before
            if movie.title:
                parts.append(f"Title: {movie.title}")
            if movie.plot:
                parts.append(f"Plot: {movie.plot}")
            if movie.fullplot:
                parts.append(f"Full Plot: {movie.fullplot}")
            if movie.genres:
                parts.append("Genres: " + ", ".join(g.genre for g in movie.genres if g.genre))
            if movie.cast:
                parts.append("Cast: " + ", ".join(c.name for c in movie.cast if c.name))
            if movie.directors:
                parts.append("Directors: " + ", ".join(d.name for d in movie.directors if d.name))
            if movie.comments:
                comments_str = " | ".join(f"{c.name}: {c.text[:200]}" for c in movie.comments if c.text and c.name)
                parts.append("Comments: " + comments_str)

            text = "\n".join(parts).strip()
            movie_docs.append({"id": str(movie._id), "text": text})

        logger.info("Built %d movie_docs from DB", len(movie_docs))

        # insert into MovieEmbedding table
        insert_movie_docs(movie_docs)

        # build FAISS index and save files in project root
        index, ids = build_faiss_index(movie_docs, faiss_index_path='movie_index.faiss', ids_path='movie_ids.pkl')
        logger.info("FAISS index created. Indexed %d docs.", index.ntotal)
    finally:
        session.close()

if __name__ == "__main__":
    process_and_index_movies()
