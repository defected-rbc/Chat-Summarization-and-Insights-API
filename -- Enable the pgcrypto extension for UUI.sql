-- Enable the pgcrypto extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create the conversations table
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT,
    metadata JSONB
);

-- Create the messages table
CREATE TABLE messages (
    message_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id),
    user_id TEXT NOT NULL,
    sender_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    CONSTRAINT unique_message UNIQUE (conversation_id, user_id, content, timestamp)
);

-- Create the summaries table
CREATE TABLE summaries (
    summary_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conversation_id UUID NOT NULL UNIQUE REFERENCES conversations(conversation_id),
    summary_text TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model_used VARCHAR(255),
    metadata JSONB
);

-- Create the insights table (Optional)
CREATE TABLE insights (
    insight_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(conversation_id),
    insight_type VARCHAR(100) NOT NULL,
    insight_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    model_used VARCHAR(255),
    metadata JSONB
);

-- Create indexes for optimization

-- Index for retrieving messages by conversation
CREATE INDEX messages_conversation_id_idx ON messages (conversation_id);

-- Index for retrieving messages by user
CREATE INDEX messages_user_id_idx ON messages (user_id);

-- Index for filtering messages by timestamp
CREATE INDEX messages_timestamp_idx ON messages ("timestamp");

-- Index for retrieving messages in chronological order within a conversation
CREATE INDEX messages_conversation_id_timestamp_idx ON messages (conversation_id, "timestamp" DESC);

-- Index for filtering conversations by creation date
CREATE INDEX conversations_created_at_idx ON conversations (created_at);

-- Index for filtering conversations by update date
CREATE INDEX conversations_updated_at_idx ON conversations (updated_at);

-- JSONB indexes for metadata fields
CREATE INDEX messages_metadata_idx ON messages USING gin (metadata jsonb_path_ops);
CREATE INDEX conversations_metadata_idx ON conversations USING gin (metadata jsonb_path_ops);
CREATE INDEX insights_metadata_idx ON insights USING gin (metadata jsonb_path_ops);

-- Indexes for the insights table
CREATE INDEX insights_conversation_id_idx ON insights (conversation_id);
CREATE INDEX insights_insight_type_idx ON insights (insight_type);

-- Insert dummy data to test the schema
-- Insert into conversations table
INSERT INTO conversations (title, metadata) 
VALUES ('Test Conversation', '{"topic": "Sample", "participants": 3}');

-- Insert into messages table
INSERT INTO messages (conversation_id, user_id, sender_type, content, metadata) 
VALUES (
    (SELECT conversation_id FROM conversations LIMIT 1), 
    'user_123', 
    'user', 
    'Hello! This is a test message.', 
    '{"emotion": "neutral", "language": "en"}'
);

-- Insert into summaries table
INSERT INTO summaries (conversation_id, summary_text, model_used, metadata) 
VALUES (
    (SELECT conversation_id FROM conversations LIMIT 1), 
    'This is a summary of the test conversation.', 
    'GPT-4', 
    '{"summary_type": "brief"}'
);

-- Insert into insights table
INSERT INTO insights (conversation_id, insight_type, insight_data, model_used, metadata) 
VALUES (
    (SELECT conversation_id FROM conversations LIMIT 1), 
    'Key Points', 
    '{"key_point_1": "Test point", "key_point_2": "Another test point"}', 
    'GPT-4', 
    '{"analysis_type": "topic extraction"}'
);
