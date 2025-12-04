from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from my_package.Searchquery import export_movie_search
# from my_package.build_faiss_index import export_movie_search
from my_package.Lanchain import ask_movie_question  # Your LLM assistant function
from fastapi.middleware.cors import CORSMiddleware


# Define allowed origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://your-frontend-domain.com",
]

app = FastAPI(title="Movie Assistant API")
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # List of allowed origins
    allow_credentials=True,       # Allow cookies, authorization headers
    allow_methods=["*"],          # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # Allow all headers
)



# -------------------------------
# In-memory session history
# -------------------------------
session_history: List[dict] = []

# -------------------------------
# Request and Response Models
# -------------------------------
class MovieQuery(BaseModel):
    question: str

class MovieInfo(BaseModel):
    movie_id: str
    score: float
    title: str
    plot: Optional[str] = None
    full_plot: Optional[str] = None
    cast: Optional[List[str]] = None
    genres: Optional[List[str]] = None
    year: Optional[int] = None
    imdb_rating: Optional[float] = None
    imdb_votes: Optional[int] = None
    awards: Optional[str] = None
    languages: Optional[List[str]] = None
    countries: Optional[List[str]] = None
    directors: Optional[List[str]] = None
    type: Optional[str] = None

class MovieResponse(BaseModel):
    query: str
    assistant_answer: str
    movies: List[MovieInfo]

class ResetResponse(BaseModel):
    message: str

# -------------------------------
# /ask endpoint
# -------------------------------
@app.post("/ask", response_model=MovieResponse)
async def ask_movie(query: MovieQuery):
    """
    Ask about a movie or related movies. Returns:
    - assistant_answer: concise response
    - movies: structured movie info for all matched movies
    """
    # 1️⃣ Generate assistant answer (handles follow-ups using session_history)
    assistant_answer = ask_movie_question(query.question, session_history)

    # 2️⃣ Fetch all movies from FAISS
    raw_context = export_movie_search(query.question)

    # 3️⃣ Parse FAISS results into structured JSON
    movies_list = []
    current_movie = {}
    for line in raw_context.split("\n"):
        line = line.strip()
        if line.startswith("Movie ID:"):
            if current_movie:
                movies_list.append(MovieInfo(**current_movie))
                current_movie = {}
            parts = line.split(", Score:")
            current_movie["movie_id"] = parts[0].split(":")[1].strip()
            current_movie["score"] = float(parts[1].strip())
        elif line.lower().startswith("title:"):
            current_movie["title"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("plot:"):
            current_movie["plot"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("full plot:"):
            current_movie["full_plot"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("cast:"):
            current_movie["cast"] = [c.strip() for c in line.split(":", 1)[1].split(",")]
        elif line.lower().startswith("genres:"):
            current_movie["genres"] = [g.strip() for g in line.split(":", 1)[1].split(",")]
        elif line.lower().startswith("year:"):
            try:
                current_movie["year"] = int(line.split(":", 1)[1].strip())
            except:
                pass
        elif line.lower().startswith("imdb rating:"):
            try:
                current_movie["imdb_rating"] = float(line.split(":", 1)[1].strip())
            except:
                pass
        elif line.lower().startswith("imdb votes:"):
            try:
                current_movie["imdb_votes"] = int(line.split(":", 1)[1].strip())
            except:
                pass
        elif line.lower().startswith("awards:"):
            current_movie["awards"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("languages:"):
            current_movie["languages"] = [l.strip() for l in line.split(":", 1)[1].split(",")]
        elif line.lower().startswith("countries:"):
            current_movie["countries"] = [c.strip() for c in line.split(":", 1)[1].split(",")]
        elif line.lower().startswith("directors:"):
            current_movie["directors"] = [d.strip() for d in line.split(":", 1)[1].split(",")]
        elif line.lower().startswith("type:"):
            current_movie["type"] = line.split(":", 1)[1].strip()

    if current_movie:
        movies_list.append(MovieInfo(**current_movie))

    return MovieResponse(
        query=query.question,
        assistant_answer=assistant_answer,
        movies=movies_list
    )

# -------------------------------
# /reset endpoint
# -------------------------------
@app.post("/reset", response_model=ResetResponse)
async def reset_session():
    """
    Resets the session history.
    """
    session_history.clear()
    return ResetResponse(message="Session history has been reset.")

# -------------------------------
# Optional: /movie/{title} endpoint
# -------------------------------
@app.get("/movie/{title}")
async def get_movie_by_title(title: str):
    """
    Fetch full movie context by title.
    """
    from app.build_faiss_index import fetch_movie_context_by_title
    context = fetch_movie_context_by_title(title)
    return {"title": title, "context": context}
