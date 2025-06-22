from Model.Schema import Movie,Genre,Cast,Language,Country,Director,Comment,Theater
def insert_movie_from_json(json_doc, session):
    # Convert ObjectId to string if needed
    movie_id = str(json_doc["_id"])
    # Check if movie already exists
    # existing_movie = session.query(Movie).filter_by(_id=movie_id).first()
    # if existing_movie:
    #     # print(f"Movie with _id {movie_id} already exists. Skipping.")
    #     # return
    # Insert main movie data
    movie = Movie(
        _id=json_doc["_id"],
        plot=json_doc.get("plot"),
        runtime=json_doc.get("runtime"),
        poster=json_doc.get("poster"),
        title=json_doc.get("title"),
        fullplot=json_doc.get("fullplot"),
        released=json_doc.get("released"),
        rated=json_doc.get("rated"),
        lastupdated=json_doc.get("lastupdated"),
        year=json_doc.get("year"),
        type=json_doc.get("type"),
        num_mflix_comments=json_doc.get("num_mflix_comments"),
        awards_wins=json_doc.get("awards", {}).get("wins"),
        awards_nominations=json_doc.get("awards", {}).get("nominations"),
        awards_text=json_doc.get("awards", {}).get("text"),
        imdb_rating=json_doc.get("imdb", {}).get("rating"),
        imdb_votes=json_doc.get("imdb", {}).get("votes"),
        imdb_id=json_doc.get("imdb", {}).get("id"),
        tomatoes_viewer_rating=json_doc.get("tomatoes", {}).get("viewer", {}).get("rating"),
        tomatoes_viewer_numReviews=json_doc.get("tomatoes", {}).get("viewer", {}).get("numReviews"),
        tomatoes_viewer_meter=json_doc.get("tomatoes", {}).get("viewer", {}).get("meter"),
        tomatoes_viewer_fresh=json_doc.get("tomatoes", {}).get("viewer", {}).get("fresh"),
        tomatoes_critic_rating=json_doc.get("tomatoes", {}).get("critic", {}).get("rating"),
        tomatoes_critic_numReviews=json_doc.get("tomatoes", {}).get("critic", {}).get("numReviews"),
        tomatoes_critic_meter=json_doc.get("tomatoes", {}).get("critic", {}).get("meter"),
        tomatoes_critic_rotten=json_doc.get("tomatoes", {}).get("critic", {}).get("rotten"),
        tomatoes_lastUpdated=json_doc.get("tomatoes", {}).get("lastUpdated"),
    )
    session.add(movie)

    # Related lists
    for g in json_doc.get("genres", []):
        session.add(Genre(movie_id=movie._id, genre=g))
    for a in json_doc.get("cast", []):
        session.add(Cast(movie_id=movie._id, name=a))
    for l in json_doc.get("languages", []):
        session.add(Language(movie_id=movie._id, language=l))
    for c in json_doc.get("countries", []):
        session.add(Country(movie_id=movie._id, country=c))
    for d in json_doc.get("directors", []):
        session.add(Director(movie_id=movie._id, name=d))

    # Add comments (if any)
    for comment in json_doc.get("comments", []):
        session.add(Comment(
            id=comment.get("_id"),
            movie_id=movie._id,
            name=comment.get("name"),
            email=comment.get("email"),
            text=comment.get("text"),
            date=comment.get("date")
        ))

    # Add theaters (if any)
    for theater in json_doc.get("theaters", []):
        location = theater.get("location", {})
        geo = location.get("geo", {})
        coordinates = geo.get("coordinates", [None, None])
        # session.add(Theater(movie_id=movie._id, theater_id=str(theater["_id"])))


        # session.add(Theater(
        #     id=str(theater.get("_id")),
        #     theater_id=theater.get("theaterId"),
        #     street1=location.get("address", {}).get("street1"),
        #     city=location.get("address", {}).get("city"),
        #     state=location.get("address", {}).get("state"),
        #     zipcode=location.get("address", {}).get("zipcode"),
        #     geo_type=geo.get("type"),
        #     geo_lat=coordinates[1],
        #     geo_long=coordinates[0]
        # ))

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error inserting movie {movie_id}: {e}")
