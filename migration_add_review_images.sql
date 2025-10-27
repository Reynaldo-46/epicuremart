USE epicuremart;

-- Add review_images column if it doesn't exist
ALTER TABLE product_reviews 
ADD COLUMN IF NOT EXISTS review_images TEXT 
AFTER review_text;

-- Verify the change
DESCRIBE product_reviews;

-- Success message
SELECT 'Migration completed successfully!' AS message;