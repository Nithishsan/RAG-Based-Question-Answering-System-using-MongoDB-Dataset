from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey,Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Movie(Base):
    __tablename__ = 'movies'

    _id = Column(String(24), primary_key=True)  # MongoDB ObjectId is 24 hex chars
    plot = Column(String(1024))
    runtime = Column(Integer)
    poster = Column(String(512))
    title = Column(String(255))
    fullplot = Column(String(4096))
    released = Column(DateTime)
    rated = Column(String(16))
    lastupdated = Column(String(64))
    year = Column(Integer)
    type = Column(String(16))
    num_mflix_comments = Column(Integer)

    # Flattened objects
    awards_wins = Column(Integer)
    awards_nominations = Column(Integer)
    awards_text = Column(String(255))

    imdb_rating = Column(Float)
    imdb_votes = Column(Integer)
    imdb_id = Column(Integer)

    tomatoes_viewer_rating = Column(Float)
    tomatoes_viewer_numReviews = Column(Integer)
    tomatoes_viewer_meter = Column(Integer)
    tomatoes_viewer_fresh = Column(Integer)

    tomatoes_critic_rating = Column(Float)
    tomatoes_critic_numReviews = Column(Integer)
    tomatoes_critic_meter = Column(Integer)
    tomatoes_critic_rotten = Column(Integer)

    tomatoes_lastUpdated = Column(DateTime)

    # Relationships
    genres = relationship("Genre", backref="movie", cascade="all, delete-orphan")
    cast = relationship("Cast", backref="movie", cascade="all, delete-orphan")
    languages = relationship("Language", backref="movie", cascade="all, delete-orphan")
    countries = relationship("Country", backref="movie", cascade="all, delete-orphan")
    directors = relationship("Director", backref="movie", cascade="all, delete-orphan")
    comments = relationship("Comment", backref="movie", cascade="all, delete-orphan")

class Genre(Base):
    __tablename__ = 'genres'
    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(String(24), ForeignKey('movies._id'))
    genre = Column(String(64))

class Cast(Base):
    __tablename__ = 'cast'
    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(String(24), ForeignKey('movies._id'))
    name = Column(String(255))

class Language(Base):
    __tablename__ = 'languages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(String(24), ForeignKey('movies._id'))
    language = Column(String(64))

class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(String(24), ForeignKey('movies._id'))
    country = Column(String(64))

class Director(Base):
    __tablename__ = 'directors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(String(24), ForeignKey('movies._id'))
    name = Column(String(255))

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(String(24), primary_key=True)  # _id as string
    movie_id = Column(String(24), ForeignKey('movies._id'))
    name = Column(String(255))
    email = Column(String(255))
    text = Column(String(4096))
    date = Column(DateTime)

class Theater(Base):
    __tablename__ = 'theaters'
    # id = Column(String(24), primary_key=True, autoincrement=True)  # _id as string
    id = Column(Integer, primary_key=True, autoincrement=True)  # _id as string

    theater_id = Column(Integer)

    street1 = Column(String(255))
    city = Column(String(255))
    state = Column(String(255))
    zipcode = Column(String(32))

    geo_type = Column(String(32))           # Usually "Point"
    geo_lat = Column(Float)
    geo_long = Column(Float)


class MovieEmbedding(Base):
    __tablename__ = 'movie_embeddings'
    id = Column(String(255), primary_key=True)
    text = Column(Text)