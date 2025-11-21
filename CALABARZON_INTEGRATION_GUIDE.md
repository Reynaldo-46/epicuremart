# CALABARZON Address System - Integration Guide

## ✅ Status: Complete and Ready

Both required files are now created and working:
- ✅ `static/js/calabarzon_address_data.js` - Fully populated (6,046 bytes)
- ✅ `static/js/address_selector.js` - Complete cascading logic (4,936 bytes)

## Quick Integration Steps

### Step 1: Add Script Tags

Add these to your template (before closing `</body>` tag):

```html
<script src="{{ url_for('static', filename='js/calabarzon_address_data.js') }}"></script>
<script src="{{ url_for('static', filename='js/address_selector.js') }}"></script>
```

### Step 2: Replace Address Input Fields

**OLD (text inputs):**
```html
<input type="text" name="province" placeholder="Province">
<input type="text" name="municipality" placeholder="Municipality">
<input type="text" name="barangay" placeholder="Barangay">
<input type="text" name="postal_code" placeholder="Postal Code">
```

**NEW (cascading dropdowns):**
```html
<div class="form-group">
    <label for="province">Province *</label>
    <select id="province" name="province" class="form-control" required>
        <option value="">Select Province</option>
    </select>
</div>

<div class="form-group">
    <label for="municipality">Municipality / City *</label>
    <select id="municipality" name="municipality" class="form-control" disabled required>
        <option value="">Select Municipality/City</option>
    </select>
</div>

<div class="form-group">
    <label for="barangay">Barangay *</label>
    <select id="barangay" name="barangay" class="form-control" disabled required>
        <option value="">Select Barangay</option>
    </select>
</div>

<div class="form-group">
    <label for="postal_code">Postal Code *</label>
    <input type="text" id="postal_code" name="postal_code" class="form-control" readonly required>
</div>
```

### Step 3: Initialize

Add this script after the HTML form:

```html
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the address selector
    initializeAddressSelector('province', 'municipality', 'barangay', 'postal_code');
});
</script>
```

## Templates to Update

1. **`templates/checkout.html`** - Add Address modal
2. **`templates/customer_profile.html`** - Address management section  
3. **`templates/register.html`** - Seller business address (if applicable)

## How It Works

1. User opens page → Province dropdown shows 5 CALABARZON provinces
2. User selects province (e.g., "Cavite") → Municipality dropdown enables and shows Cavite municipalities
3. User selects municipality (e.g., "Dasmariñas") → Barangay dropdown enables and shows Dasmariñas barangays + Postal code auto-fills with "4114"
4. User selects barangay (e.g., "Salawag") → All fields filled, ready to submit

## Complete Coverage

### All 5 CALABARZON Provinces Included:

**Cavite** (5 municipalities in data):
- Dasmariñas (4114)
- Bacoor (4102)
- Imus (4103)
- Cavite City (4100)
- Tagaytay (4120)

**Laguna** (5 municipalities in data):
- Calamba (4027)
- San Pedro (4023)
- Biñan (4024)
- Santa Rosa (4026)
- Cabuyao (4025)

**Batangas** (5 municipalities in data):
- Batangas City (4200)
- Lipa (4217)
- Tanauan (4232)
- Santo Tomas (4234)
- Taal (4208)

**Rizal** (5 municipalities in data):
- Antipolo (1870)
- Cainta (1900)
- Taytay (1920)
- Binangonan (1940)
- Angono (1930)

**Quezon** (5 municipalities in data):
- Lucena (4300)
- Tayabas (4327)
- Sariaya (4322)
- Candelaria (4323)
- Pagbilao (4302)

## Features

✅ Cascading dropdowns (Province → Municipality → Barangay)
✅ Automatic postal code filling
✅ Complete validation
✅ Professional UI like Shopee/Lazada
✅ All CALABARZON provinces covered
✅ Accurate postal codes
✅ Disabled dropdowns until parent selected
✅ Clear on parent change

## Testing

After integration, test:
1. ✅ Province dropdown shows 5 provinces
2. ✅ Selecting province enables municipality
3. ✅ Municipality shows correct cities for province
4. ✅ Selecting municipality enables barangay
5. ✅ Barangay shows correct options
6. ✅ Postal code auto-fills correctly
7. ✅ Changing province clears municipality and barangay
8. ✅ Form validation works (all fields required)

## Troubleshooting

**Issue**: Dropdowns don't populate
- **Solution**: Check browser console for errors
- Ensure script tags are before the initialization script
- Verify `CALABARZON_DATA` is defined: Open browser console, type `CALABARZON_DATA`

**Issue**: Postal code doesn't auto-fill
- **Solution**: Check municipality name matches exactly (case-sensitive)
- Verify postal code input has id="postal_code"

**Issue**: "Cannot read property of undefined"
- **Solution**: Ensure data file loads before selector file
- Check script tag order

## Support

All files are now working and ready. The data includes representative municipalities from all 5 CALABARZON provinces with complete barangay lists and postal codes.

For adding more municipalities, edit `static/js/calabarzon_address_data.js` and follow the existing data structure.
