DDL = """
CREATE TABLE IF NOT EXISTS articles (
  article_id        VARCHAR PRIMARY KEY,
  provider          VARCHAR,
  provider_id       VARCHAR,
  url               VARCHAR,
  title             VARCHAR,
  summary           VARCHAR,
  body              VARCHAR,
  image_url         VARCHAR,
  published_at      TIMESTAMP,

  source_name       VARCHAR,
  source_domain     VARCHAR,
  source_country    VARCHAR,
  language          VARCHAR,

  topics            VARCHAR, -- store as JSON string list for simplicity
  inserted_at       TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_articles_url ON articles(url);
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_articles_country ON articles(source_country);
CREATE INDEX IF NOT EXISTS idx_articles_language ON articles(language);

-- add image_url if table already exists without it
ALTER TABLE articles ADD COLUMN IF NOT EXISTS image_url VARCHAR;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS body VARCHAR;
"""
