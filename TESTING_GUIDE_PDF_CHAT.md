# Testing Guide - PDF Export and Chat Enhancements

## Overview
This guide covers testing for the new PDF export functionality and enhanced parcel-based chat messaging system.

## Prerequisites
1. Running MySQL database with epicuremart schema
2. Flask application running on development server
3. Test accounts for each role (admin, seller, customer, courier, rider)
4. Sample orders at different stages (PENDING_PAYMENT, READY_FOR_PICKUP, IN_TRANSIT_TO_RIDER, OUT_FOR_DELIVERY, DELIVERED)

## Database Migration
Before testing, run the migration to update conversation types:

```bash
mysql -u root epicuremart < migration_chat_parcel_updates.sql
```

## Part 1: PDF Export Testing

### Test 1.1: Seller Sales Report PDF Export
**Prerequisites**: Login as seller with at least one order

**Steps**:
1. Navigate to `/seller/sales-report`
2. Verify "Export PDF" button is visible in top-right corner
3. Click "Export PDF" button
4. Verify PDF download starts
5. Open downloaded PDF and verify:
   - Header shows "Seller Sales Report"
   - Report metadata includes shop name, date, and user name
   - Summary section shows correct totals
   - Order details table includes recent orders (if any)
   - All currency amounts are formatted correctly with ₱ symbol

**Expected Result**: PDF downloads successfully with accurate seller data

**Test with Filters**:
- Apply status filter (e.g., DELIVERED only)
- Click Export PDF
- Verify PDF reflects filtered data

### Test 1.2: Admin Sales Report PDF Export
**Prerequisites**: Login as admin

**Steps**:
1. Navigate to `/admin/dashboard`
2. Verify "Export PDF" button is visible
3. Try different time filters:
   - All Time
   - Last Week
   - Last Month
   - Custom date range
4. Click "Export PDF" for each filter
5. Verify each PDF includes correct data for selected period

**Expected Result**: Admin can export reports with different time periods

### Test 1.3: Courier Earnings Report PDF Export
**Prerequisites**: Login as courier with completed deliveries

**Steps**:
1. Navigate to `/courier/dashboard`
2. Click "Export Earnings Report" button
3. Open PDF and verify:
   - Shows total earnings (60% of delivery fees)
   - Lists completed deliveries
   - Shows pending earnings
   - Order details include delivery dates

**Expected Result**: Courier PDF shows accurate earning calculations

### Test 1.4: Rider Earnings Report PDF Export
**Prerequisites**: Login as rider with completed deliveries

**Steps**:
1. Navigate to `/rider/dashboard`
2. Click "Export Earnings Report" button
3. Open PDF and verify:
   - Shows total earnings (40% of delivery fees)
   - Lists completed deliveries
   - Shows pending earnings
   - Order details are accurate

**Expected Result**: Rider PDF shows accurate earning calculations

### Test 1.5: Authorization Testing
**Test unauthorized access**:
1. Try accessing PDF export URLs without login - should redirect to login
2. Try accessing seller PDF export as customer - should show permission error
3. Try accessing courier PDF export as rider - should show permission error

**Expected Result**: All PDF exports properly enforce role-based access control

## Part 2: Chat Messaging Testing

### Test 2.1: Customer-to-Seller Chat (Parcel-Based)
**Prerequisites**: Login as customer with an order

**Steps**:
1. Navigate to order details page
2. Click "Chat with Seller" button
3. Verify conversation opens
4. Send a test message
5. Login as seller
6. Check messages inbox - verify conversation appears
7. Reply to customer
8. Login back as customer - verify reply received

**Expected Result**: Customer and seller can exchange messages about the order

### Test 2.2: Customer-to-Rider Chat
**Prerequisites**: Order with status OUT_FOR_DELIVERY and assigned rider

**Steps**:
1. Login as customer
2. Navigate to order with OUT_FOR_DELIVERY status
3. Click "Chat with Rider" button
4. Send message to rider
5. Login as rider
6. Verify message received in inbox
7. Reply to customer
8. Verify customer receives reply

**Expected Result**: Customer can chat with rider when parcel is out for delivery

### Test 2.3: Customer-to-Courier Chat
**Prerequisites**: Order with courier assigned

**Steps**:
1. Login as customer
2. Navigate to order details
3. Click "Chat with Courier" button (if available)
4. Send message
5. Login as courier
6. Verify message in inbox
7. Reply to customer

**Expected Result**: Customer can communicate with courier about parcel

### Test 2.4: Seller-to-Courier Chat
**Prerequisites**: Order with courier assigned

**Steps**:
1. Login as seller
2. Navigate to order details
3. Click "Chat with Courier" button
4. Send message about pickup
5. Login as courier
6. Verify message received
7. Reply to seller

**Expected Result**: Seller can coordinate with courier about pickups

### Test 2.5: Admin Chat Capabilities
**Test admin starting conversation with user**:

**Steps**:
1. Login as admin
2. Navigate to `/admin/users`
3. Select a user (any role)
4. Use admin conversation start button/link
5. Send message to user
6. Login as that user
7. Verify message received
8. Reply to admin
9. Login as admin and verify reply

**Expected Result**: Admin can initiate conversations with any user

**Test admin viewing existing conversations**:

**Steps**:
1. Create conversation between customer and seller (as per Test 2.1)
2. Login as admin
3. Navigate to messages or admin support dashboard
4. Find the conversation
5. View the conversation
6. Verify admin can see all messages
7. Send a message as admin
8. Verify both customer and seller can see admin's message

**Expected Result**: Admin can view and participate in any conversation

### Test 2.6: Order-Based Chat Authorization
**Test chat availability based on order status**:

**Steps**:
1. Create order in PENDING_PAYMENT status
   - Verify "Chat with Seller" is available
   - Verify "Chat with Courier" is NOT available (no courier assigned)
   - Verify "Chat with Rider" is NOT available (no rider assigned)

2. Mark order as READY_FOR_PICKUP
   - Verify seller can still be contacted
   - No courier/rider chat yet

3. Courier picks up order (IN_TRANSIT_TO_RIDER)
   - Verify "Chat with Courier" becomes available
   - Verify courier can see customer/seller messages

4. Rider picks up from courier (OUT_FOR_DELIVERY)
   - Verify "Chat with Rider" becomes available
   - Verify rider can communicate

**Expected Result**: Chat options appear based on parcel ownership/status

### Test 2.7: Message Persistence and History
**Steps**:
1. Start conversation between customer and seller
2. Send 10 messages back and forth
3. Close browser/logout
4. Login again
5. Open same conversation
6. Verify all messages are present
7. Verify messages are in chronological order
8. Verify read/unread status is tracked

**Expected Result**: All messages persist correctly with proper timestamps

### Test 2.8: Multiple Active Conversations
**Steps**:
1. As customer, create order from Shop A
2. Create another order from Shop B
3. Start chat with Seller A about Order 1
4. Start chat with Seller B about Order 2
5. Start chat with rider for Order 1
6. Verify all 3 conversations appear in inbox
7. Verify messages stay in correct conversations
8. Reply in each conversation
9. Verify no cross-contamination of messages

**Expected Result**: Multiple conversations work independently

## Part 3: Edge Cases and Error Handling

### Test 3.1: Empty Messages
**Steps**:
1. Open any conversation
2. Try to send empty message
3. Try to send message with only spaces

**Expected Result**: Error message "Message cannot be empty"

### Test 3.2: Chat Before Assignment
**Steps**:
1. Create order (READY_FOR_PICKUP)
2. Try to chat with courier before courier accepts pickup
3. Try to chat with rider before rider is assigned

**Expected Result**: Error message indicating courier/rider not assigned yet

### Test 3.3: Conversation Type Validation
**Steps**:
1. Manually try to create conversation with invalid type
2. Try to access conversation you don't own (without admin)

**Expected Result**: Proper authorization errors

### Test 3.4: Large Dataset PDF Export
**Steps**:
1. As seller with 100+ orders, export PDF
2. Verify PDF is limited to 100 most recent orders
3. Check PDF generation time

**Expected Result**: PDF generates successfully, limited to 100 records

### Test 3.5: Concurrent Messaging
**Steps**:
1. Open same conversation in two browser tabs
2. Send message from tab 1
3. Send message from tab 2 quickly
4. Verify both messages appear correctly
5. Check message ordering

**Expected Result**: No race conditions, messages appear in order

## Part 4: Performance Testing

### Test 4.1: PDF Generation Performance
**Steps**:
1. Export PDF with 100 orders
2. Measure time to generate and download
3. Verify file size is reasonable (<2MB)

**Expected Result**: PDF generates in under 5 seconds

### Test 4.2: Message Loading Performance
**Steps**:
1. Create conversation with 100+ messages
2. Open conversation
3. Measure page load time

**Expected Result**: Page loads in under 2 seconds

## Test Results Template

| Test Case | Status | Notes | Tester | Date |
|-----------|--------|-------|--------|------|
| 1.1 Seller PDF Export | ☐ Pass ☐ Fail | | | |
| 1.2 Admin PDF Export | ☐ Pass ☐ Fail | | | |
| 1.3 Courier PDF Export | ☐ Pass ☐ Fail | | | |
| 1.4 Rider PDF Export | ☐ Pass ☐ Fail | | | |
| 1.5 Authorization | ☐ Pass ☐ Fail | | | |
| 2.1 Customer-Seller Chat | ☐ Pass ☐ Fail | | | |
| 2.2 Customer-Rider Chat | ☐ Pass ☐ Fail | | | |
| 2.3 Customer-Courier Chat | ☐ Pass ☐ Fail | | | |
| 2.4 Seller-Courier Chat | ☐ Pass ☐ Fail | | | |
| 2.5 Admin Chat | ☐ Pass ☐ Fail | | | |
| 2.6 Order-Based Auth | ☐ Pass ☐ Fail | | | |
| 2.7 Message Persistence | ☐ Pass ☐ Fail | | | |
| 2.8 Multiple Convos | ☐ Pass ☐ Fail | | | |
| 3.1 Empty Messages | ☐ Pass ☐ Fail | | | |
| 3.2 Chat Before Assignment | ☐ Pass ☐ Fail | | | |
| 3.3 Type Validation | ☐ Pass ☐ Fail | | | |
| 3.4 Large Dataset PDF | ☐ Pass ☐ Fail | | | |
| 3.5 Concurrent Messaging | ☐ Pass ☐ Fail | | | |
| 4.1 PDF Performance | ☐ Pass ☐ Fail | | | |
| 4.2 Message Performance | ☐ Pass ☐ Fail | | | |

## Known Limitations
1. PDFs are limited to 100 most recent records to prevent performance issues
2. Chat notifications are not real-time (requires page refresh)
3. File attachments not supported in chat (text only)

## Troubleshooting

### Issue: PDF not downloading
- Check browser console for errors
- Verify user is logged in with correct role
- Check server logs for Python errors

### Issue: Chat messages not appearing
- Verify database migration was run
- Check conversation_type is valid
- Verify both users have correct roles

### Issue: Authorization errors
- Check user role in database
- Verify order ownership
- Check audit logs for details
