# EpicureMart Testing Guide

## Manual Testing Checklist

### 1. Admin Features Testing

#### Account Approval
- [ ] Register as seller with ID and business permit
- [ ] Register as rider with ID, driver's license, OR/CR, plate number, vehicle type
- [ ] Verify admin sees pending approvals
- [ ] Verify all documents are viewable in approval page
- [ ] Test approve button - user should receive email and be able to login
- [ ] Test reject button - user should be deleted and receive email

#### Account Management
- [ ] Test suspending a user account with reason
- [ ] Verify suspended user cannot login
- [ ] Verify suspended user shows "Suspended" status in user list
- [ ] Test unsuspending a user
- [ ] Test deleting a user account
- [ ] Verify admin accounts cannot be suspended/deleted

### 2. Cart & Stock Validation Testing

#### Add to Cart
- [ ] Test adding item with quantity = stock (should work)
- [ ] Test adding item with quantity > stock (should show error)
- [ ] Add item, then try adding same item again exceeding stock (should show warning)
- [ ] Verify cart badge shows transaction count (not total quantity)
- [ ] Verify each "Add to Cart" creates separate cart entry

#### Cart Page
- [ ] Test updating quantity to exceed stock (should show error)
- [ ] Test updating quantity to valid amount (should work)
- [ ] Verify items exceeding stock are highlighted in red
- [ ] Verify "Proceed to Checkout" is disabled when stock exceeded
- [ ] Test removing items from cart

#### Checkout
- [ ] Verify checkout blocked when any item exceeds stock
- [ ] Test successful checkout with valid quantities
- [ ] Verify stock is deducted after order placement
- [ ] Verify cart is cleared after successful checkout

### 3. Registration & Verification Testing

#### Email Verification
- [ ] Register new account
- [ ] Verify 6-digit code received via email
- [ ] Test entering correct code (should verify account)
- [ ] Test entering incorrect code (should show error)
- [ ] Wait 48 hours and test expired code (should show error)
- [ ] Test resending verification code

#### Seller Registration
- [ ] Verify ID upload is required
- [ ] Verify business permit upload is required
- [ ] Test registration without documents (should fail)
- [ ] Test successful registration with all documents
- [ ] Verify phone number is optional for sellers

#### Rider/Courier Registration
- [ ] Verify ID upload is required
- [ ] Verify driver's license upload is required
- [ ] Verify OR/CR upload is required
- [ ] Verify plate number field is required
- [ ] Verify vehicle type selection is required
- [ ] Test registration without any document (should fail)
- [ ] Verify phone number is required for riders/couriers

#### Address Fields
- [ ] Test registration with required address fields only
- [ ] Test registration with optional fields (street, block, lot)
- [ ] Verify address is properly formatted in full_address

### 4. Seller Sales Report Testing

#### Report Access
- [ ] Login as seller
- [ ] Navigate to sales report
- [ ] Verify summary cards show correct totals

#### Commission Breakdown
- [ ] Create test order with ₱1000 subtotal
- [ ] Mark as delivered
- [ ] Verify report shows:
  - Subtotal: ₱1000
  - Commission (5%): ₱50
  - Seller Earnings (95%): ₱950
- [ ] Verify commission is calculated per transaction, not per product

#### Filtering
- [ ] Test "All Orders" filter
- [ ] Test "Delivered" filter
- [ ] Test "Pending" filter
- [ ] Verify pagination works correctly

### 5. Courier/Rider Earnings Testing

#### Courier Dashboard
- [ ] Login as courier
- [ ] Verify "Total Deliveries" count is correct
- [ ] Verify "Pending Deliveries" count is correct
- [ ] Complete a delivery with ₱100 delivery fee
- [ ] Verify courier earnings shows ₱60 (60% of ₱100)

#### Rider Dashboard
- [ ] Login as rider
- [ ] Verify "Total Deliveries" count is correct
- [ ] Verify "Pending Deliveries" count is correct
- [ ] Complete a delivery with ₱100 delivery fee
- [ ] Verify rider earnings shows ₱40 (40% of ₱100)

### 6. Notification Badges Testing

#### Cart Badge
- [ ] Login as customer
- [ ] Verify cart badge shows 0 when empty
- [ ] Add item to cart
- [ ] Verify badge shows 1
- [ ] Add same item again (separate transaction)
- [ ] Verify badge shows 2 (transaction count, not quantity)

#### Message Badge
- [ ] Have another user send you a message
- [ ] Verify message badge appears with count
- [ ] Open message conversation
- [ ] Mark message as read
- [ ] Verify badge count decreases

#### All User Types
- [ ] Test badges visible for customer
- [ ] Test badges visible for seller
- [ ] Test badges visible for rider
- [ ] Test badges visible for courier
- [ ] Test badges visible for admin

### 7. Database Migration Testing

#### Run Migration
```bash
# Connect to MySQL
mysql -u root -p

# Select database
USE epicuremart;

# Run migration
source migration_comprehensive_updates.sql;

# Verify tables
SHOW TABLES;
DESCRIBE cart_items;
DESCRIBE users;
DESCRIBE orders;
DESCRIBE addresses;
```

#### Verify Schema
- [ ] Verify `cart_items` table exists
- [ ] Verify `users` table has new columns:
  - verification_code
  - verification_code_expires
  - business_permit
  - drivers_license
  - or_cr
  - plate_number
  - vehicle_type
  - is_suspended
  - suspension_reason
- [ ] Verify `orders` table has new columns:
  - courier_earnings
  - rider_earnings
  - shipping_fee_split_courier
  - shipping_fee_split_rider
- [ ] Verify `addresses` table has new columns:
  - street
  - block
  - lot

### 8. Integration Testing Scenarios

#### Complete Order Flow
1. Customer registers and verifies email
2. Customer adds items to cart
3. Customer checks out
4. Seller marks order ready for pickup
5. Courier picks up order
6. Courier hands off to rider
7. Rider delivers order
8. Verify commissions calculated correctly:
   - Admin gets 5% of subtotal
   - Seller gets 95% of subtotal
   - Courier gets 60% of delivery fee
   - Rider gets 40% of delivery fee

#### Seller Approval Flow
1. Seller registers with ID and business permit
2. Admin views pending approval with documents
3. Admin approves seller
4. Seller receives email notification
5. Seller can login and create shop
6. Seller adds products
7. Seller views sales report with commission breakdown

## Automated Testing (Future Enhancement)

### Unit Tests to Add
- Cart quantity validation logic
- Commission calculation functions
- Verification code generation and validation
- Stock deduction on order creation

### Integration Tests to Add
- Complete order workflow
- User registration and approval flow
- Cart to checkout flow
- Earnings calculation flow

## Performance Testing

### Load Testing Scenarios
- [ ] Multiple users adding to cart simultaneously
- [ ] Multiple admins approving users simultaneously
- [ ] Large number of orders in sales report
- [ ] Concurrent message sending

## Browser Compatibility Testing

Test on:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile browsers (Chrome Mobile, Safari iOS)

## Accessibility Testing

- [ ] Test with screen reader
- [ ] Test keyboard navigation
- [ ] Verify ARIA labels on badges
- [ ] Test form field labels and error messages

## Notes

- Most testing should be done on a staging/development database
- Create test data scripts for easier testing
- Document any bugs found during testing
- Verify all email notifications are sent correctly
- Check audit logs for all admin actions
