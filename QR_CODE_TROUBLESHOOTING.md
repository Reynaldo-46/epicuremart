# QR Code Troubleshooting Guide

## Problem: "Invalid or expired QR code" Error

### Root Cause
The QR code tokens were being invalidated because the `SECRET_KEY` was being regenerated on every application restart. JWT tokens signed with one secret key cannot be verified with a different secret key.

### Solution Implemented
Changed the SECRET_KEY from a randomly generated value to a persistent value that remains the same across application restarts.

**Before (WRONG):**
```python
app.config['SECRET_KEY'] = secrets.token_hex(32)  # Generates new key on every restart!
```

**After (CORRECT):**
```python
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'epicuremart-secret-key-change-in-production-2024'
```

### Important Notes

1. **The SECRET_KEY must remain constant** across all application restarts for QR codes to work properly.

2. **For Production Use**: Set the SECRET_KEY as an environment variable:
   ```bash
   export SECRET_KEY="your-very-long-random-secret-key-here"
   ```
   
   Generate a secure random key:
   ```python
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **After Applying This Fix**: You need to regenerate QR codes for existing orders:
   - Orders with status `READY_FOR_PICKUP` need new `pickup_token`
   - Orders with status `IN_TRANSIT_TO_RIDER` need new `delivery_token`
   
   **Option A: Via Seller Interface**
   - Seller can toggle order status to regenerate tokens
   
   **Option B: Manual Database Update** (if needed):
   ```sql
   -- Clear old tokens (they will be regenerated when seller confirms order ready again)
   UPDATE orders SET pickup_token = NULL WHERE status = 'READY_FOR_PICKUP';
   UPDATE orders SET delivery_token = NULL WHERE status IN ('IN_TRANSIT_TO_RIDER', 'OUT_FOR_DELIVERY');
   ```

### How QR Code System Works

1. **Seller confirms order ready** → `pickup_token` generated (expires in 24 hours)
2. **Courier scans QR code** → Token verified, courier assigned to order
3. **Courier generates handoff QR** → `delivery_token` generated (expires in 24 hours)  
4. **Rider scans QR code** → Token verified, rider assigned to order
5. **Rider delivers** → Uploads proof photo, order marked as delivered

### Token Expiration
- Default expiration: 24 hours
- After expiration, seller needs to regenerate the QR code
- Tokens are automatically regenerated when order status changes

### Verifying QR Codes

To test if a QR token is valid:

```python
import jwt
from datetime import datetime

token = "your-token-here"
secret_key = "epicuremart-secret-key-change-in-production-2024"

try:
    payload = jwt.decode(token, secret_key, algorithms=['HS256'])
    print("Token is valid!")
    print("Order ID:", payload['order_id'])
    print("Type:", payload['type'])
    print("Expires:", datetime.fromtimestamp(payload['exp']))
except jwt.ExpiredSignatureError:
    print("Token has expired")
except jwt.InvalidTokenError:
    print("Token is invalid")
```

### Testing the Fix

1. **Restart the application** to pick up the new SECRET_KEY configuration
2. **Create a new test order**:
   - Customer places order
   - Seller marks as ready for pickup (generates QR)
3. **Test courier pickup**:
   - Courier scans QR code
   - Should successfully assign courier
4. **Test rider delivery**:
   - Courier hands off to rider (generates delivery QR)
   - Rider scans QR code
   - Should successfully assign rider

### Future Improvements

Consider implementing:
- QR code refresh mechanism for near-expired tokens
- Notification to seller when token expires
- Extended expiry for orders with longer delivery times
- Token revocation system for cancelled orders
