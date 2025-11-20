# Rider and Courier Visibility Implementation

## Overview
This implementation adds full rider and courier visibility features along with cross-role chat functionality, similar to Shopee's delivery tracking system.

## Features Implemented

### 1. Rider Feedback System
- New `RiderFeedback` model to store customer ratings and feedback for riders
- Customers can rate riders (1-5 stars) and provide text feedback after delivery
- Rider profiles display average rating and total number of reviews
- Recent feedback (last 3 reviews) shown on rider information cards

### 2. Enhanced Visibility

#### For Customers (Order Detail Page)
- **Rider Information** (when status is OUT_FOR_DELIVERY or DELIVERED):
  - Full name
  - Email address
  - Phone number
  - Profile picture
  - Average rating and total reviews
  - Last 3 feedback items
  - Chat with Rider button

- **Courier Information** (when courier is assigned):
  - Full name
  - Email address
  - Phone number
  - Profile picture
  - Vehicle type
  - Chat with Courier button

#### For Sellers (Order Detail Page)
- **Rider Information** (when status is OUT_FOR_DELIVERY or DELIVERED):
  - Full name, email, phone
  - Profile picture
  - Average rating
  - Chat with Rider button

- **Courier Information** (enhanced display):
  - Full name, email, phone
  - Profile picture
  - Vehicle type
  - Chat with Courier button

#### For Couriers (Dashboard)
- Rider column in orders table
- Chat with Rider button for assigned orders
- Quick access to rider contact info

### 3. Cross-Role Chat Features

New conversation types supported:
- **buyer_courier**: Customer ↔ Courier
- **courier_rider**: Courier ↔ Rider

All chat features:
- ✅ Seller ↔ Rider (existing)
- ✅ Customer ↔ Rider (existing)
- ✅ Seller ↔ Courier (existing)
- ✅ Customer ↔ Courier (NEW)
- ✅ Courier ↔ Rider (NEW)

### 4. Rider Feedback Collection

After delivery:
- Modal dialog for rating rider
- 1-5 star rating system
- Optional text feedback
- One feedback per order per customer
- Feedback aggregated on rider profile

## Database Changes

### New Table: rider_feedback
```sql
CREATE TABLE rider_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rider_id INT NOT NULL,
    customer_id INT NOT NULL,
    order_id INT NOT NULL,
    rating INT NOT NULL,
    feedback_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rider_id) REFERENCES users(id),
    FOREIGN KEY (customer_id) REFERENCES users(id),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

### Updated Table: conversations
Added new conversation types:
- `buyer_courier`
- `courier_rider`

## API Endpoints

### New Routes

1. **POST /order/<order_id>/rider-feedback**
   - Submit rider rating and feedback
   - Requires: customer role, delivered order
   - Parameters: rating (1-5), feedback_text (optional)

2. **GET /api/rider/<rider_id>/rating**
   - Get rider's average rating and recent feedback
   - Returns: JSON with avg_rating, total_feedbacks, recent_feedbacks

3. **GET /messages/start-courier-rider-chat/<order_id>**
   - Start conversation between courier and rider
   - Requires: courier or rider role
   - Creates new conversation or redirects to existing

4. **GET /messages/start-with-courier/<order_id>**
   - Start conversation with courier (for customer or seller)
   - Determines conversation type based on initiator

## Migration Instructions

1. Run the migration script:
```bash
mysql -u root -p epicuremart < migration_rider_courier_visibility.sql
```

Or use Python migration tool:
```bash
python3 run_migrations.py
```

2. The migration will:
   - Create the `rider_feedback` table
   - Update the `conversations` table enum to include new conversation types

## Usage Examples

### For Customers
1. View order details
2. When order is OUT_FOR_DELIVERY, see rider information with rating
3. Click "Chat with Rider" to communicate
4. Click "Chat with Courier" to contact courier
5. After delivery, rate the rider via modal dialog

### For Sellers
1. View order details
2. See assigned courier information
3. Chat with courier for pickup coordination
4. View rider information when out for delivery
5. Chat with rider if needed

### For Couriers
1. Dashboard shows assigned orders
2. Rider column shows assigned rider
3. Click chat icon to contact rider
4. Coordinate handoff and delivery

## UI Components

### Rider Information Card
- Background: Info blue
- Icon: Motorcycle
- Contents: Profile pic, name, contact, rating
- Actions: Chat button, (rate button for customers)

### Courier Information Card
- Background: Primary blue
- Icon: Truck
- Contents: Profile pic, name, contact, vehicle type
- Actions: Chat button

### Rider Feedback Modal
- Star rating input (1-5 stars)
- Text feedback textarea
- Submit/Cancel buttons
- Only shown if not already rated

## Security Considerations

- Role-based access control on all routes
- Customer can only rate riders for their own delivered orders
- One feedback per order per customer
- Chat conversations restricted to relevant parties
- Order ownership verified before displaying information

## Testing Checklist

- [ ] Create test orders and assign courier/rider
- [ ] Verify rider info displays when OUT_FOR_DELIVERY
- [ ] Test customer → rider chat
- [ ] Test customer → courier chat
- [ ] Test courier → rider chat
- [ ] Submit rider feedback after delivery
- [ ] Verify rating appears on rider profile
- [ ] Test that duplicate ratings are prevented
- [ ] Verify seller can view rider information
- [ ] Test courier dashboard rider column and chat

## Notes

- All existing chat functionality remains unchanged
- Profile pictures are optional; generic icons shown if missing
- Phone numbers are optional; hidden if not set
- Rating calculation is real-time average
- Recent feedback limited to 3 items for brevity
