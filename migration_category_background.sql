-- Migration: Add background_image column to categories table
-- Date: 2025-11-13

ALTER TABLE categories ADD COLUMN background_image VARCHAR(255) DEFAULT NULL;
