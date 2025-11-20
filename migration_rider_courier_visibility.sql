-- Migration: Add Rider and Courier Visibility Features
-- Date: 2025-11-20

-- 1. Create rider_feedback table
CREATE TABLE IF NOT EXISTS rider_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rider_id INT NOT NULL,
    customer_id INT NOT NULL,
    order_id INT NOT NULL,
    rating INT NOT NULL,
    feedback_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rider_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    INDEX idx_rider_id (rider_id),
    INDEX idx_order_id (order_id)
);

-- 2. Update conversation_type enum to include buyer_courier and courier_rider
ALTER TABLE conversations 
MODIFY COLUMN conversation_type ENUM(
    'buyer_seller', 
    'seller_rider', 
    'buyer_rider', 
    'user_support', 
    'user_admin', 
    'seller_courier', 
    'buyer_courier', 
    'courier_rider'
) NOT NULL;
