-- Migration to add new conversation types for parcel-based chat
-- This adds seller_courier, buyer_courier, and admin conversation types

-- For MySQL, we need to modify the ENUM type
-- First, check if the column exists and update it

ALTER TABLE conversations 
MODIFY COLUMN conversation_type ENUM(
    'buyer_seller', 
    'seller_rider', 
    'buyer_rider', 
    'seller_courier', 
    'buyer_courier', 
    'user_support', 
    'user_admin',
    'admin_seller',
    'admin_courier',
    'admin_rider',
    'admin_customer'
) NOT NULL;
