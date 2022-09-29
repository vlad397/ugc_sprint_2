sh.addShard("mongors1/mongors1n1");
sh.addShard("mongors2/mongors2n1");

const dbname = "default";
const conn = new Mongo();
const database = conn.getDB(dbname);

sh.enableSharding(dbname);

rating_db = "rating";
database.createCollection(rating_db);
sh.shardCollection(`${dbname}.${rating_db}`, {["user_id"]: "hashed"});
database[rating_db].createIndex({["film_id"]: -1});
database[rating_db].createIndex({["score"]: -1});

review_db = "bookmark";
database.createCollection(review_db);
sh.shardCollection(`${dbname}.${review_db}`, {["user_id"]: "hashed"});
database[review_db].createIndex({["film_id"]: -1});
