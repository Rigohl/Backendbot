-- Migración: Campos adicionales para mejor funcionalidad
-- Fecha: 2025-09-18
-- Descripción: Añade campos útiles para mejor tracking y funcionalidad

-- Añadir campo de tags a tasks
ALTER TABLE tasks ADD COLUMN tags TEXT;

-- Añadir campo de prioridad a tasks
ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 1;

-- Añadir campo de categoría a metrics
ALTER TABLE metrics ADD COLUMN category TEXT;

-- Añadir campo de fuente a logs
ALTER TABLE logs ADD COLUMN source TEXT;

-- Añadir campo de versión a users
ALTER TABLE users ADD COLUMN version TEXT DEFAULT '2.0.0';

-- Crear tabla para sesiones de usuario
CREATE TABLE IF NOT EXISTS user_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    session_token TEXT UNIQUE,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Crear tabla para backups
CREATE TABLE IF NOT EXISTS backups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    size_bytes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'completed',
    metadata TEXT
);