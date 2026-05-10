-- IMDb movies.csv
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

-- 加载数据
LOAD DATA LOCAL INPATH '/home/hadoop/IMDb movies.csv' OVERWRITE INTO TABLE movies;

-- 创建视图
CREATE VIEW IF NOT EXISTS ods_movies
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



-- IMDb title_principals.csv
CREATE TABLE IF NOT EXISTS imdb_movies.title_principals (
    imdb_title_id string COMMENT "title ID on IMDb",
    ordering int COMMENT "order of importance in the movie",
    imdb_name_id string COMMENT "name ID on IMDb",
    category string COMMENT "category of job done by the cast member", 
    job string COMMENT "specific job done by the cast member",
    characters string COMMENT "name of the character played"
) ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
TBLPROPERTIES ("skip.header.line.count"="1")

LOAD DATA LOCAL INPATH '/home/hadoop/IMDb title_principals.csv' OVERWRITE INTO TABLE imdb_movies.title_principals

CREATE VIEW IF NOT EXISTS imdb_movies.ods_title_principals
AS SELECT 
    imdb_title_id,
    cast(ordering as int) as ordering,
    imdb_name_id,
    category, 
    job,
    characters
FROM imdb_movies.title_principals


-- 基于日期进行字段拓展
SELECT 
    year, 
    date_published,
    quarter(date_published) as quarter,
    month(date_published) as month,
    weekofyear(date_published) as weekofyear,
    date_format(date_published, "W") as weekinmonth,
    date_format(date_published, "D") as dayinyear,
    day(date_published) as dayinmonth,
    date_format(date_published, "u") as dayinweek,
    year(current_date()) - cast(year as int) as yearstotoday,
    datediff(current_date(), date_published) as daystotoday
FROM ods_movies
LIMIT 5;

-- 对文字信息进行处理
SELECT 
    genre,
    split(genre, ",") as words_in_genre,
    split(genre, ", |,") as trim_words_in_genre,
    split(lower(genre), ", |,") as trim_words_in_genre
FROM ods_movies
LIMIT 5;

WITH T1 AS (
    SELECT explode(
        split(lower(genre), ", |,")) as genre_words
    FROM ods_movies
) SELECT 
    genre_words, 
    COUNT(*) AS counts
FROM T1 
GROUP BY genre_words

EXPLAIN SELECT lower(genre) AS lower_genre FROM ods_movies


-- 创建模拟数据
CREATE TABLE example (
    name string,
    sex string,
    age int
);
INSERT INTO example VALUES ("zhang3","male",15), 
("li4","male",12), 
("wang5","female",21), 
("zhao6","female",37);

-- 窗口函数
SELECT 
 title,
 duration,
 year,
 rank() OVER (PARTITION BY year ORDER BY duration)
FROM ods_movies 
WHERE year in ("1911", "1912")

-- 窗口 - 导航函数
SELECT title, date_published, director,
    LEAD(title, 1) OVER ( PARTITION BY director 
        ORDER BY date_published),
    LAG(title, 2) OVER ( PARTITION BY director 
        ORDER BY date_published),
    FIRST_VALUE(title) OVER ( PARTITION BY director 
        ORDER BY date_published),
    LAST_VALUE(title) OVER ( PARTITION BY director 
        ORDER BY date_published)
FROM ods_movies
WHERE director IS NOT NULL AND director != ""
LIMIT 20;


SELECT title, duration, director,
    RANK() OVER ( PARTITION BY director 
        ORDER BY duration) AS rank,
    DENSE_RANK() OVER ( PARTITION BY director 
        ORDER BY duration) AS dense_rank,
    ROW_NUMBER() OVER ( PARTITION BY director 
        ORDER BY duration) AS row_number
FROM ods_movies
WHERE director IN ("A. Edward Sutherland", "A. Dean Bell");


SELECT title, duration, director,
    ROUND( CUME_DIST() OVER ( 
        PARTITION BY director 
        ORDER BY duration), 2) AS cume_dist,
    PERCENT_RANK() OVER ( PARTITION BY director 
        ORDER BY duration) AS percent_rank,
    NTILE(5) OVER ( PARTITION BY director 
        ORDER BY duration) AS ntile
FROM ods_movies
WHERE director IN ("A. Edward Sutherland", "A. Dean Bell");

SELECT SUM(duration), director
FROM ods_movies
WHERE director IN ("A. Edward Sutherland", "A. Dean Bell")
GROUP BY director;