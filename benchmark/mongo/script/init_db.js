const dbname = "default";
const conn = new Mongo();
const database = conn.getDB(dbname);

rating_db = "rating";
database.createCollection(rating_db);
database[rating_db].createIndex({["user_id"]: -1});
database[rating_db].createIndex({["film_id"]: -1});
database[rating_db].createIndex({["score"]: -1});

review_db = "bookmark";
database.createCollection(review_db);
database[review_db].createIndex({["user_id"]: -1});
database[review_db].createIndex({["film_id"]: -1});
