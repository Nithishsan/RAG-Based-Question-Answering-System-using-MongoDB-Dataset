from config.db_config import SessionLocal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from config.db_config import engine
from Model.Schema import Base
# Import your ORM models (adjust 'your_models' to your actual module name)
from Model.Schema import Movie, Genre, Cast, Language, Country, Director, Comment,MovieEmbedding
from .build_faiss_index import build_faiss_index,search_movies
# Replace with your actual database URL
Base.metadata.create_all(engine)

def insert_movie_docs(movie_docs):
    session = SessionLocal()
    for doc in movie_docs:
        movie_id = str(doc["id"])  # Make sure ID is string
        text = doc["text"]
        entry = MovieEmbedding(id=movie_id, text=text)
        session.merge(entry)  # insert or update
    session.commit()
    
def process_and_index_movies():
    session = SessionLocal()

    # Query movies with eager loading of related entities for performance
    movies = session.query(Movie).options(
        joinedload(Movie.genres),
        joinedload(Movie.cast),
        joinedload(Movie.languages),
        joinedload(Movie.countries),
        joinedload(Movie.directors),
        joinedload(Movie.comments)
    ).all()

    movie_docs = []

    for movie in movies:
        parts = []

        # movie_text_fields = [
        #     movie.title,
        #     movie.plot,
        #     movie.fullplot,
        #     movie.rated,
        #     movie.lastupdated,
        #     movie.type,
        #     movie.awards_text,
        #     str(movie.awards_wins) if movie.awards_wins else "",
        #     str(movie.awards_nominations) if movie.awards_nominations else "",
        #     str(movie.imdb_rating) if movie.imdb_rating else "",
        #     str(movie.imdb_votes) if movie.imdb_votes else "",
        #     str(movie.imdb_id) if movie.imdb_id else "",
        #     str(movie.tomatoes_viewer_rating) if movie.tomatoes_viewer_rating else "",
        #     str(movie.tomatoes_viewer_numReviews) if movie.tomatoes_viewer_numReviews else "",
        #     str(movie.tomatoes_viewer_meter) if movie.tomatoes_viewer_meter else "",
        #     str(movie.tomatoes_viewer_fresh) if movie.tomatoes_viewer_fresh else "",
        #     str(movie.tomatoes_critic_rating) if movie.tomatoes_critic_rating else "",
        #     str(movie.tomatoes_critic_numReviews) if movie.tomatoes_critic_numReviews else "",
        #     str(movie.tomatoes_critic_meter) if movie.tomatoes_critic_meter else "",
        #     str(movie.tomatoes_critic_rotten) if movie.tomatoes_critic_rotten else "",
        #     str(movie.released) if movie.released else "",
        #     str(movie.tomatoes_lastUpdated) if movie.tomatoes_lastUpdated else "",
        #     str(movie.year) if movie.year else "",
        #     str(movie.num_mflix_comments) if movie.num_mflix_comments else "",
        # ]
        movie_text_fields = [
        f"Title: {movie.title}" if movie.title else "",
        f"Plot: {movie.plot}" if movie.plot else "",
        f"Full Plot: {movie.fullplot}" if movie.fullplot else "",
        f"Rated: {movie.rated}" if movie.rated else "",
        f"Last Updated: {movie.lastupdated}" if movie.lastupdated else "",
        f"Type: {movie.type}" if movie.type else "",
        f"Awards: {movie.awards_text}" if movie.awards_text else "",
        f"Awards Wins: {movie.awards_wins}" if movie.awards_wins else "",
        f"Awards Nominations: {movie.awards_nominations}" if movie.awards_nominations else "",
        f"IMDb Rating: {movie.imdb_rating}" if movie.imdb_rating else "",
        f"IMDb Votes: {movie.imdb_votes}" if movie.imdb_votes else "",
        f"IMDb ID: {movie.imdb_id}" if movie.imdb_id else "",
        f"Tomatoes Viewer Rating: {movie.tomatoes_viewer_rating}" if movie.tomatoes_viewer_rating else "",
        f"Tomatoes Viewer NumReviews: {movie.tomatoes_viewer_numReviews}" if movie.tomatoes_viewer_numReviews else "",
        f"Tomatoes Viewer Meter: {movie.tomatoes_viewer_meter}" if movie.tomatoes_viewer_meter else "",
        f"Tomatoes Viewer Fresh: {movie.tomatoes_viewer_fresh}" if movie.tomatoes_viewer_fresh else "",
        f"Tomatoes Critic Rating: {movie.tomatoes_critic_rating}" if movie.tomatoes_critic_rating else "",
        f"Tomatoes Critic NumReviews: {movie.tomatoes_critic_numReviews}" if movie.tomatoes_critic_numReviews else "",
        f"Tomatoes Critic Meter: {movie.tomatoes_critic_meter}" if movie.tomatoes_critic_meter else "",
        f"Tomatoes Critic Rotten: {movie.tomatoes_critic_rotten}" if movie.tomatoes_critic_rotten else "",
        f"Released: {movie.released}" if movie.released else "",
        f"Tomatoes Last Updated: {movie.tomatoes_lastUpdated}" if movie.tomatoes_lastUpdated else "",
        f"Year: {movie.year}" if movie.year else "",
        f"Number of Comments: {movie.num_mflix_comments}" if movie.num_mflix_comments else "",
    ]

        parts.extend([str(f) for f in movie_text_fields if f])

        if movie.genres:
            parts.append("Genres: " + ", ".join(g.genre for g in movie.genres if g.genre))

        if movie.cast:
            parts.append("Cast: " + ", ".join(c.name for c in movie.cast if c.name))

        if movie.languages:
            parts.append("Languages: " + ", ".join(l.language for l in movie.languages if l.language))

        if movie.countries:
            parts.append("Countries: " + ", ".join(c.country for c in movie.countries if c.country))

        if movie.directors:
            parts.append("Directors: " + ", ".join(d.name for d in movie.directors if d.name))

        if movie.comments:
            comments_str = " | ".join(f"{c.name}: {c.text[:200]}" for c in movie.comments if c.text and c.name)
            parts.append("Comments: " + comments_str)

        text = "\n".join(parts).strip()

        movie_docs.append({"id": movie._id, "text": text})

    session.close()

    # After building movie_docs:
    insert_movie_docs(movie_docs)

    # Optionally print sample output to verify
    # print(movie_docs[0]["text"])  # print first 1000 chars of first movie text

    index = build_faiss_index(movie_docs)
    print(f"Indexed {len(movie_docs)} movies.")
    print(f"FAISS index info: {index}")
    #index, ids = build_faiss_index(movie_docs)

    ## this code sample usage of the fucntion 
    # query = "A western about train robbery with cowboys and sheriff posse"
    # results = search_movies(query, index, ids)

    # for res in results:
    #     print(f"Movie ID: {res['id']}, Score: {res['score']}")

# Close session when done

process_and_index_movies()