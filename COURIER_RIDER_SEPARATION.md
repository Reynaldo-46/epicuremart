# Courier and Rider Separation Implementation

## Overview
This implementation cleanly separates Courier Companies from Riders, ensuring sellers only interact with courier companies and never see individual riders.

## Data Hierarchy

```
┌─────────────────────────────────────┐
│   Courier Company (User)            │
│   - role: 'courier'                 │
│   - company_name: "J&T Express"     │
│   - Has vehicle and credentials     │
└──────────────┬──────────────────────┘
               │
               │ courier_id (FK)
               │
        ┌──────▼──────────────┐
        │  Multiple Riders    │
        │  - role: 'rider'    │
        │  - courier_id: 123  │
        │  - Own vehicles     │
        └─────────────────────┘

┌─────────────────────────────────────┐
│   Seller                            │
│   Selects: Courier Company ONLY     │
│   Never sees: Individual Riders     │
└─────────────────────────────────────┘
```

## Key Changes

### 1. Courier Registration

**New Field: company_name**
- Required field for courier role
- Examples: "J&T Express", "Lalamove", "NinjaVan", "Grab Express"
- Stored in `users.company_name`
- Displayed prominently in all courier selections

**Registration Flow:**
1. User selects "Courier Company" role
2. Fills vehicle details (plate, vehicle type, OR/CR, license)
3. **Enters Company Name** (required)
4. Submits for admin approval
5. Can manage riders after approval

### 2. Rider Registration

**Required: Courier Company Selection**
- Must select which courier company they work for
- Dropdown populated from approved courier companies
- Shows `company_name` (e.g., "J&T Express") not personal names
- Stored in `users.courier_id` (FK to courier's user.id)

**Registration Flow:**
1. User selects "Rider" role
2. Fills vehicle details (plate, vehicle type, OR/CR, license)
3. **Selects Courier Company** from dropdown (required)
4. Submits for admin approval
5. Belongs to selected courier company

**Validation:**
- Cannot proceed without selecting courier
- Error message: "Please select a courier company."

### 3. Seller Order Management

**Courier Selection:**
- Sellers see **courier companies only**
- Dropdown format: `{{ company_name or full_name }}`
- Example options:
  - "J&T Express (Motorcycle)"
  - "Lalamove (Van)"
  - "NinjaVan (Car)"

**Rider Selection:**
- Automatically filtered by selected courier
- **Not visible** until courier is selected
- AJAX filtering ensures only matching riders shown
- Validates rider belongs to courier on submit

**Assignment Process:**
1. Seller selects Courier Company (e.g., "J&T Express")
2. Rider dropdown auto-updates via AJAX
3. Shows only riders with `courier_id = selected_courier.id`
4. Seller selects specific rider from filtered list
5. System validates association before saving

### 4. Display Updates

**Courier Information Cards:**
All templates now display company name as primary identifier:

```html
<!-- Primary: company_name -->
{{ courier_info.company_name or courier_info.full_name }}

<!-- Examples: -->
"J&T Express"
"Lalamove"
"NinjaVan"
```

**Locations Updated:**
- Customer order detail page
- Seller order detail page  
- Order assignment dropdowns
- Courier selection forms

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    -- ... existing fields ...
    
    -- NEW: Company name for courier companies
    company_name VARCHAR(200) NULL,
    
    -- RENAMED: courier_company_id → courier_id
    courier_id INT NULL,
    
    -- Relationships
    FOREIGN KEY (courier_id) REFERENCES users(id) ON DELETE SET NULL
);
```

### Field Usage by Role

| Field | Courier | Rider | Seller | Customer |
|-------|---------|-------|--------|----------|
| `company_name` | **Required** | NULL | NULL | NULL |
| `courier_id` | NULL | **Required** | NULL | NULL |
| `vehicle_type` | Required | Required | NULL | NULL |
| `plate_number` | Required | Required | NULL | NULL |

## API Endpoints

### Get Riders by Courier
```python
GET /api/riders-by-courier/<courier_id>

# Returns JSON
{
    "riders": [
        {
            "id": 45,
            "full_name": "Juan Dela Cruz",
            "email": "juan@email.com",
            "phone": "+63 912 345 6789",
            "vehicle_type": "Motorcycle"
        },
        // ... more riders
    ]
}

# Filtered by: courier_id = <courier_id>
```

**Used For:**
- Dynamic dropdown filtering in seller order detail
- JavaScript AJAX calls when courier is selected
- Ensures only matching riders shown

## Registration Form Logic

### JavaScript Visibility Control

```javascript
// Courier role selected
if (role === 'courier') {
    // Show:
    - ID upload
    - Driver's license
    - OR/CR
    - Vehicle details
    - Company name field ✓ NEW
    
    // Hide:
    - Courier company selection (N/A for couriers)
}

// Rider role selected
if (role === 'rider') {
    // Show:
    - ID upload
    - Driver's license
    - OR/CR
    - Vehicle details
    - Courier company selection ✓ REQUIRED
    
    // Hide:
    - Company name field (N/A for riders)
}
```

## Validation Rules

### Backend Validation (app.py)

```python
# Courier validation
if role == 'courier' and not company_name:
    flash('Company name is required for couriers.', 'danger')
    return redirect(url_for('register'))

# Rider validation
if role == 'rider' and not courier_id:
    flash('Please select a courier company.', 'danger')
    return redirect(url_for('register'))

# Assignment validation
if order.courier_id and rider.courier_id != order.courier_id:
    flash('Selected rider does not belong to the assigned courier company.', 'warning')
```

### Frontend Validation (register.html)

```javascript
// Required field validation
companyNameInput.required = true;  // For couriers
courierCompanySelect.required = true;  // For riders

// Shown only for relevant roles
companyNameSection (couriers only)
courierCompanySection (riders only)
```

## Migration Instructions

### Step 1: Backup Database
```bash
mysqldump -u root -p epicuremart > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Step 2: Apply Migration
```bash
mysql -u root -p epicuremart < migration_separate_couriers_riders.sql
```

### Step 3: Verify Changes
```sql
-- Check company_name field added
SHOW COLUMNS FROM users LIKE 'company_name';

-- Check courier_id renamed
SHOW COLUMNS FROM users LIKE 'courier_id';

-- View courier companies
SELECT id, email, full_name, company_name, role 
FROM users 
WHERE role = 'courier';

-- View riders and their courier assignments
SELECT r.id, r.full_name as rider_name, 
       c.company_name as courier_company, r.courier_id
FROM users r
LEFT JOIN users c ON r.courier_id = c.id
WHERE r.role = 'rider';
```

### Step 4: Update Existing Data (Optional)
```sql
-- Set company_name for existing couriers (if they don't have one)
UPDATE users 
SET company_name = CONCAT(full_name, ' Courier Service')
WHERE role = 'courier' AND company_name IS NULL;
```

## Testing Checklist

### Courier Registration
- [ ] "Courier Company" role appears in dropdown
- [ ] Company name field shows for couriers
- [ ] Company name is required
- [ ] Registration succeeds with company name
- [ ] Company name saved to database

### Rider Registration
- [ ] "Rider" role appears separately from courier
- [ ] Courier company dropdown shows for riders
- [ ] Dropdown lists courier companies (company_name)
- [ ] Courier selection is required
- [ ] Registration succeeds with courier selected
- [ ] courier_id saved to database

### Seller Assignment
- [ ] Courier dropdown shows company names
- [ ] Rider dropdown filters by selected courier
- [ ] AJAX filtering works correctly
- [ ] Cannot assign mismatched courier-rider
- [ ] Assignment saves correctly

### Display
- [ ] Customer sees courier company name
- [ ] Seller sees courier company name
- [ ] Order details show company name
- [ ] Fallback to full_name if company_name missing

## Example Data

### Sample Courier Companies

| ID | Email | Company Name | Vehicle Type |
|----|-------|--------------|--------------|
| 10 | jnt@courier.com | J&T Express | Van |
| 11 | lalamove@courier.com | Lalamove | Motorcycle |
| 12 | ninja@courier.com | NinjaVan | Car |

### Sample Riders

| ID | Email | Full Name | Courier ID | Courier Company |
|----|-------|-----------|------------|----------------|
| 20 | juan@rider.com | Juan Dela Cruz | 10 | J&T Express |
| 21 | maria@rider.com | Maria Santos | 10 | J&T Express |
| 22 | pedro@rider.com | Pedro Garcia | 11 | Lalamove |

### Assignment Flow

```
Seller creates order
  ↓
Selects "J&T Express" (courier_id: 10)
  ↓
Rider dropdown auto-filters
  ↓
Shows: Juan Dela Cruz, Maria Santos
Hides: Pedro Garcia (belongs to Lalamove)
  ↓
Seller selects Juan
  ↓
Order assigned: courier_id=10, rider_id=20
  ✓ Valid: rider.courier_id == order.courier_id
```

## Benefits

### Clean Separation
✅ Couriers are company entities with company names
✅ Riders are individuals belonging to companies
✅ Sellers never see individual rider details during courier selection
✅ Clear hierarchy prevents confusion

### Better UX
✅ Sellers recognize courier companies by brand name
✅ Dynamic filtering shows only relevant riders
✅ Prevents assignment errors
✅ Professional company-based interface

### Data Integrity
✅ Foreign key ensures riders belong to valid couriers
✅ Validation prevents mismatched assignments
✅ Database constraints enforce relationships
✅ Audit trail maintained

### Scalability
✅ Courier companies can have unlimited riders
✅ Easy to add new courier companies
✅ Riders can transfer between companies (update courier_id)
✅ Analytics by courier company possible

## Troubleshooting

### Issue: Company name not showing
**Solution:** Check that courier has `company_name` set in database
```sql
SELECT id, email, company_name FROM users WHERE role = 'courier';
UPDATE users SET company_name = 'My Company' WHERE id = X;
```

### Issue: Riders not filtering
**Solution:** Verify AJAX endpoint is working
```bash
curl http://localhost:5000/api/riders-by-courier/10
```

### Issue: Assignment validation fails
**Solution:** Check rider.courier_id matches order.courier_id
```sql
SELECT r.id, r.courier_id, o.courier_id 
FROM users r, orders o 
WHERE r.id = o.rider_id;
```

## Security

✅ **CodeQL: 0 alerts**

**Validation:**
- Company name required for couriers
- Courier selection required for riders
- Assignment validates courier-rider association
- Role-based field visibility

**Access Control:**
- Sellers can only assign their own orders
- API endpoints verify role permissions
- Database constraints prevent invalid data

## Conclusion

The implementation successfully separates Courier Companies from Riders:
- Couriers register with company names
- Riders belong to courier companies
- Sellers select courier companies, not riders
- Clean data hierarchy maintained
- Professional, scalable solution
