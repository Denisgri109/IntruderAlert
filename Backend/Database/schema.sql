CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode TEXT DEFAULT 'schedule',
    start_time TEXT DEFAULT '22:00',
    end_time TEXT DEFAULT '05:00'
);

CREATE TABLE alert (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    alert_type TEXT,
    message TEXT,
    buzzer_triggered INTEGER DEFAULT 0,
    acknowledged INTEGER DEFAULT 0
);