-- Evidence Index Schema V0.1
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS evidence_records (
    record_id TEXT PRIMARY KEY,
    source_path TEXT NOT NULL,
    source_type TEXT NOT NULL,
    organ TEXT NOT NULL,
    task_id TEXT,
    commit_hash TEXT,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    status TEXT NOT NULL,
    verdict TEXT NOT NULL,
    tags TEXT NOT NULL,
    created_at_utc TEXT,
    indexed_at_utc TEXT NOT NULL,
    content_excerpt TEXT NOT NULL,
    sha256 TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS evidence_fts USING fts5(
    record_id UNINDEXED,
    title,
    summary,
    content_excerpt,
    tags,
    source_path
);

CREATE TABLE IF NOT EXISTS task_index (
    task_id TEXT NOT NULL,
    record_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    PRIMARY KEY (task_id, record_id),
    FOREIGN KEY (record_id) REFERENCES evidence_records(record_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS commit_index (
    commit_hash TEXT NOT NULL,
    record_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    PRIMARY KEY (commit_hash, record_id),
    FOREIGN KEY (record_id) REFERENCES evidence_records(record_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS capability_index (
    capability_id TEXT NOT NULL,
    record_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    status TEXT NOT NULL,
    verdict TEXT NOT NULL,
    PRIMARY KEY (capability_id, record_id),
    FOREIGN KEY (record_id) REFERENCES evidence_records(record_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS receipt_index (
    receipt_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    verdict TEXT NOT NULL,
    PRIMARY KEY (receipt_name, record_id),
    FOREIGN KEY (record_id) REFERENCES evidence_records(record_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS warning_error_index (
    pattern_id TEXT NOT NULL,
    pattern_label TEXT NOT NULL,
    record_id TEXT NOT NULL,
    source_path TEXT NOT NULL,
    match_count INTEGER NOT NULL,
    severity TEXT NOT NULL,
    PRIMARY KEY (pattern_id, record_id),
    FOREIGN KEY (record_id) REFERENCES evidence_records(record_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS source_file_index (
    source_path TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    organ TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    file_mtime_utc TEXT NOT NULL,
    sha256 TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_evidence_records_source_type ON evidence_records(source_type);
CREATE INDEX IF NOT EXISTS idx_evidence_records_organ ON evidence_records(organ);
CREATE INDEX IF NOT EXISTS idx_evidence_records_verdict ON evidence_records(verdict);
CREATE INDEX IF NOT EXISTS idx_task_index_task_id ON task_index(task_id);
CREATE INDEX IF NOT EXISTS idx_commit_index_commit_hash ON commit_index(commit_hash);
CREATE INDEX IF NOT EXISTS idx_warning_error_pattern_id ON warning_error_index(pattern_id);
