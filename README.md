# MovieRag2.0

**AI-Powered Movie Recommendation and Discovery System**

MovieRag2.0 is a movie search and recommendation application that uses *Retrieval-Augmented Generation (RAG)*, *machine learning*, *FAISS vector search*, *FastAPI backend*, *Streamlit frontend*, and *MongoDB* storage.  
This project includes model files, configuration scripts, and movie metadata for intelligent movie query handling.

## Features

### Intelligent Search and Recommendations

* RAG-based movie recommendation system  
* Natural language movie search  
* FAISS vector database for similarity search  
* AI-powered movie assistant backend  

### Backend (FastAPI)

* RESTful API endpoints  
* Uses `movie_index.faiss` and `movie_ids.pkl`  
* Modular API and model structure  

### Frontend (Streamlit & Next js app)

* Interactive search UI  
* Real-time recommendations  
* Movie metadata display  

### Database (MongoDB)

* Stores movie metadata  
* Works with vector search  
* Supports mflix sample dataset  

## Technology Stack

| Component | Technology |
|----------|:----------:|
| Backend | FastAPI, Python |
| Frontend | Streamlit |
| Database | MongoDB |
| Vector Search | FAISS |
| Data Processing | Python, pickle |
| API Architecture | REST |

## Project Structure
<img width="" height="576" alt="image" src="https://github.com/user-attachments/assets/e243cea4-667d-41e6-84a9-cdd6cdd5c360" />

## System Architecture

> Streamlit UI  
> sends queries to  
>> FastAPI Backend  
>> which interacts with  
>>> FAISS Vector Database  
>>> and MongoDB Metadata Storage  

## API Examples

### Search Movies



GET /api/movies/search?q=Inception


### Get Recommendations



GET /api/movies/recommend?id=<movie_id>


## Setup Instructions

### Clone the Repository



git clone https://github.com/your-username/MovieRag2.0.git

cd MovieRag2.0


### Install Dependencies



pip install -r requirements.txt


### Run Backend



uvicorn backend.main:app --reload


### Start Frontend



streamlit run frontend/app.py


## Environment Configuration

Create a `.env` file:



MONGODB_URI=mongodb://localhost:27017
DB_NAME=movies
FAISS_INDEX_PATH=backend/movie_index.faiss
MOVIE_ID_MAP_PATH=backend/movie_ids.pkl


## Future Improvements

1. Add TMDB or IMDB API integration  
2. Deploy backend and frontend  
3. Improve LLM reasoning  
4. Add user profiles and favorites  

