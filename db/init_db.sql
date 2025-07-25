-- Gigs Table
CREATE TABLE IF NOT EXISTS gigs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(512) NOT NULL,
    link TEXT UNIQUE NOT NULL,
    description TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    category VARCHAR(100),
    budget_amount DECIMAL(10, 2),
    budget_currency VARCHAR(10),
    skills TEXT[], -- PostgreSQL array type for skills
    source_platform VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for gigs table
CREATE UNIQUE INDEX IF NOT EXISTS idx_gigs_link ON gigs (link);
CREATE INDEX IF NOT EXISTS idx_gigs_published_at ON gigs (published_at DESC);
CREATE INDEX IF NOT EXISTS idx_gigs_category ON gigs (category);

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- Store hashed passwords, NEVER plain text
    is_active BOOLEAN DEFAULT TRUE,
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Preferences Table (many-to-many relationship for users and categories)
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_name VARCHAR(100) NOT NULL,
    UNIQUE(user_id, category_name)
);

-- Indexes for user preferences
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences (user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_category_name ON user_preferences (category_name);

-- Table to track sent notifications (to prevent sending duplicates)
CREATE TABLE IF NOT EXISTS sent_notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    gig_id INTEGER NOT NULL REFERENCES gigs(id) ON DELETE CASCADE,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, gig_id) -- A user gets one notification per gig
);

CREATE INDEX IF NOT EXISTS idx_sent_notifications_user_gig ON sent_notifications (user_id, gig_id);
CREATE INDEX IF NOT EXISTS idx_sent_notifications_gig_id ON sent_notifications (gig_id);