CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    current_step TEXT NOT NULL,
    target_url TEXT NOT NULL,
    ad_input TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    variant_name TEXT NOT NULL,
    html_content TEXT NOT NULL,
    confidence_score INTEGER NOT NULL,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);