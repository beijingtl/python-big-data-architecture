-- CREATE SQL
CREATE TABLE movies (
    imdb_title_id string COMMENT "title ID on IMDb",
    title string COMMENT "title name",
    original_title string COMMENT "original title name",
    year int COMMENT "year of release", 
    date_published string COMMENT "date of release",
    genre string COMMENT "movie genre",
    duration string COMMENT "duration (in minutes)",
    country string COMMENT "movie country",
    language string COMMENT "movie language",
    director string COMMENT "director name",
    writer string COMMENT "writer name",
    production_company string COMMENT "production company",
    actors string COMMENT "actor names",
    description string COMMENT "plot descrption",
    avg_vote float COMMENT "average vote",
    votes int COMMENT "number of votes received",
    budget string COMMENT "budget",
    usa_gross_income string COMMENT "USA gross income",
    worlwide_gross_income string COMMENT "worldwide gross income",
    metascore float COMMENT "metascore rating",
    reviews_from_users float COMMENT "number of reviews from users",
    reviews_from_critics float COMMENT "number of reviews from critics"
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
TBLPROPERTIES ("skip.header.line.count"="1");

-- 调整字段格式
ALTER TABLE movies REPLACE COLUMNS (imdb_title_id string);

-- LOAD SQL
LOAD DATA LOCAL INPATH '/home/hadoop/IMDb movies.csv' OVERWRITE INTO TABLE movies;

-- 基本查询
SELECT * FROM movies LIMIT 2;
select description from movies limit 2;

-- 此处主要使用 PyHive
-- pyhs2 - 对应 HiveServer2

-- 创建视图
CREATE VIEW IF NOT EXISTS ods_movies (
    imdb_title_id  COMMENT "title ID on IMDb",
    title  COMMENT "title name",
    original_title  COMMENT "original title name",
    year  COMMENT "year of release", 
    date_published  COMMENT "date of release",
    genre  COMMENT "movie genre",
    duration  COMMENT "duration (in minutes)",
    country  COMMENT "movie country",
    language  COMMENT "movie language",
    director  COMMENT "director name",
    writer  COMMENT "writer name",
    production_company  COMMENT "production company",
    actors  COMMENT "actor names",
    description  COMMENT "plot descrption",
    avg_vote  COMMENT "average vote",
    votes  COMMENT "number of votes received",
    budget  COMMENT "budget",
    usa_gross_income  COMMENT "USA gross income",
    worlwide_gross_income  COMMENT "worldwide gross income",
    metascore  COMMENT "metascore rating",
    reviews_from_users  COMMENT "number of reviews from users",
    reviews_from_critics  COMMENT "number of reviews from critics"
)
AS SELECT 
    imdb_title_id,
    title,
    original_title,
    year, 
    date_published,
    genre,
    duration,
    country,
    language,
    director,
    writer,
    production_company,
    actors,
    description,
    avg_vote,
    cast(votes as int) as votes,
    budget,
    usa_gross_income,
    worlwide_gross_income,
    cast(metascore as float) as metascore,
    cast(reviews_from_users as float) as reviews_from_users,
    cast(reviews_from_critics as float) as reviews_from_critics
FROM movies;
