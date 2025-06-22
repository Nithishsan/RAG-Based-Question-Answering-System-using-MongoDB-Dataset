# main.py (or any other file in your project)
from config.mongo_connection import client
from config.db_config import SessionLocal
from Model.Schema import Movie, Genre, Cast, Language, Country, Director, Comment, Theater
from my_package.insertMovie import insert_movie_from_json
from Model.Schema import Base
from config.db_config import engine
import pandas as pd
Base.metadata.create_all(engine)
# You can now use the 'client' object to interact with MongoDB
# For example, accessing a database:
db = client['sample_mflix']
# Example operation: Get a list of collections in the database
collections = db.list_collection_names()
movies = list(db["movies"].find())



# # df = pd.json_normalize(movies)
# # print(df.head())
session = SessionLocal()
# # Fetch shared theaters
# all_theaters = list(db["theaters"].find())

# for theater_doc in all_theaters:
#     # Convert ObjectId to string if needed
#     theater_doc['id'] = str(theater_doc['_id'])
#     # Remove _id to avoid SQLAlchemy confusion
#     theater_doc.pop('_id', None)
#     # Check if theater already exists before inserting
#     exists = session.query(Theater).filter_by(id=theater_doc['id']).first()
#     if not exists:
#         session.add(Theater(**theater_doc))
# session.commit()
def convert_keys(theater_doc):
    return {
        
        "theater_id": theater_doc["theaterId"],
        "street1": theater_doc.get("location", {}).get("address", {}).get("street1"),
        "city": theater_doc.get("location", {}).get("address", {}).get("city"),
        "state": theater_doc.get("location", {}).get("address", {}).get("state"),
        "zipcode": theater_doc.get("location", {}).get("address", {}).get("zipcode"),
        "geo_type": theater_doc.get("location", {}).get("geo", {}).get("type"),
        "geo_lat": theater_doc.get("location", {}).get("geo", {}).get("coordinates", [None, None])[1],
        "geo_long": theater_doc.get("location", {}).get("geo", {}).get("coordinates", [None, None])[0],
    }

all_theaters = list(db["theaters"].find())

for theater_doc in all_theaters:
    theater_doc['id'] = str(theater_doc['_id'])
    theater_doc.pop('_id', None)
    exists = session.query(Theater).filter_by(id=theater_doc['id']).first()
    if not exists:
        theater = Theater(**convert_keys(theater_doc))
        session.add(theater)
session.commit()


# # Insert movies and related data
# # Insert movies and related data
def migrate_mflix_data(): ## this migrate function helps to conver the mongodb json data into sql 
    for movie_doc in db["movies"].find({},no_cursor_timeout=True):
        movie_id = movie_doc["_id"]
        movie_doc["comments"] = list(db["comments"].find({"movie_id": movie_id}))
        movie_doc["theaters"] = all_theaters  # Optional filtering can be done here
        insert_movie_from_json(movie_doc, session)
        print("The movies from mongoDB migrated into sql data with flatterd nature and foriegn keys....")

# insert_movie_from_json(movie_doc, session)
# print(df.isnull().sum())
# Print out the collections in your database
# print(movies)
# print(f"Collections in database '{db.name}':")
# for collection in collections:
#     print(collection)


migrate_mflix_data()