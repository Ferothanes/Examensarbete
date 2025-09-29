CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    source TEXT,
    published_at TIMESTAMP,
    url TEXT UNIQUE,
    image_url TEXT,
    country VARCHAR(5),
    language VARCHAR(5),
    category VARCHAR(50),
    fetched_at TIMESTAMP DEFAULT NOW()
);
