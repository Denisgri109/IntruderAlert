CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE device (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    device_code TEXT UNIQUE,
    mode TEXT DEFAULT 'schedule',
    is_online INTEGER DEFAULT 0,
    last_seen TEXT,
    FOREIGN KEY (user_id) REFERENCES user (id) ON DELETE CASCADE
);

CREATE TABLE schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    start_time TEXT DEFAULT '22:00',
    end_time TEXT DEFAULT '05:00',
    FOREIGN KEY (device_id) REFERENCES device (id) ON DELETE CASCADE
);

CREATE TABLE alert (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    alert_type TEXT,
    message TEXT,
    buzzer_triggered INTEGER DEFAULT 0,
    acknowledged INTEGER DEFAULT 0,
    FOREIGN KEY (device_id) REFERENCES device (id) ON DELETE CASCADE
);