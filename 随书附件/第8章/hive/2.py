from pyhive import hive

cursor = hive.connect(host="master1", port="10000").cursor()

_sql = """CREATE TABLE IF NOT EXISTS imdb_movies.title_principals (
    imdb_title_id string COMMENT "title ID on IMDb",
    ordering int COMMENT "order of importance in the movie",
    imdb_name_id string COMMENT "name ID on IMDb",
    category string COMMENT "category of job done by the cast member", 
    job string COMMENT "specific job done by the cast member",
    characters string COMMENT "name of the character played"
) ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
TBLPROPERTIES ("skip.header.line.count"="1")"""
cursor.execute(_sql)

_sql = "LOAD DATA LOCAL INPATH '/home/hadoop/IMDb title_principals.csv' OVERWRITE INTO TABLE imdb_movies.title_principals"
cursor.execute(_sql)

_sql = "SELECT COUNT(*) FROM imdb_movies.title_principals"
cursor.execute(_sql)
print(cursor.fetchall())
