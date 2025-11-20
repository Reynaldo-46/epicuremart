-- Migration script to add rider feedback system
-- Run this script to enable rider rating and feedback functionality

-- Create rider_feedback table
CREATE TABLE IF NOT EXISTS rider_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    rider_id INT NOT NULL,
    customer_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (rider_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_feedback (order_id, customer_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add index for faster queries
CREATE INDEX idx_rider_feedback_rider_id ON rider_feedback(rider_id);
CREATE INDEX idx_rider_feedback_order_id ON rider_feedback(order_id);
CREATE INDEX idx_rider_feedback_created_at ON rider_feedback(created_at DESC);
