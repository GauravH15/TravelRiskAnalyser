# Travel Risk Analyzer API - Example Payloads

## 1. USER AUTHENTICATION ENDPOINTS

### 1.1 Register User
**Endpoint:** `POST /user/register`

**Request Payload:**
```json
{
  "username": "john_traveler",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "role": "traveler",
  "date_of_birth": "1990-05-15",
  "gender": "Male",
  "nationality": "US",
  "department": "Business Development",
  "job_title": "Manager",
  "employee_id": "EMP12345",
  "timezone": "America/New_York"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 1.2 Login User
**Endpoint:** `POST /user/login`

**Request Payload:**
```json
{
  "username": "john_traveler",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_traveler",
  "role": "traveler",
  "email": "john@example.com",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 2. TRAVELER ENDPOINTS

### 2.1 Create Traveler Profile
**Endpoint:** `POST /core/travelers/`
**Authentication:** Required (Bearer Token)

**Request Payload:**
```json
{
  "passport_number": "US123456789",
  "passport_issuing_country": "United States",
  "passport_expiry_date": "2028-12-31",
  "health_conditions": "Asthma, controlled with daily medication",
  "frequent_traveler": true
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user": "550e8400-e29b-41d4-a716-446655440000",
  "passport_number": "US123456789",
  "passport_issuing_country": "United States",
  "passport_expiry_date": "2028-12-31",
  "health_conditions": "Asthma, controlled with daily medication",
  "frequent_traveler": true,
  "created_at": "2025-12-16T10:30:00Z"
}
```

---

### 2.2 Get All Travelers
**Endpoint:** `GET /core/travelers/`
**Authentication:** Required (Bearer Token)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "user": "550e8400-e29b-41d4-a716-446655440000",
    "passport_number": "US123456789",
    "passport_issuing_country": "United States",
    "passport_expiry_date": "2028-12-31",
    "health_conditions": "Asthma, controlled with daily medication",
    "frequent_traveler": true,
    "created_at": "2025-12-16T10:30:00Z"
  }
]
```

---

### 2.3 Get Specific Traveler
**Endpoint:** `GET /core/travelers/{id}/`
**Authentication:** Required (Bearer Token)

**Response (200 OK):**
```json
{
  "id": 1,
  "user": "550e8400-e29b-41d4-a716-446655440000",
  "passport_number": "US123456789",
  "passport_issuing_country": "United States",
  "passport_expiry_date": "2028-12-31",
  "health_conditions": "Asthma, controlled with daily medication",
  "frequent_traveler": true,
  "created_at": "2025-12-16T10:30:00Z"
}
```

---

### 2.4 Update Traveler Profile
**Endpoint:** `PUT /core/travelers/{id}/`
**Authentication:** Required (Bearer Token)

**Request Payload:**
```json
{
  "passport_number": "US123456789",
  "passport_issuing_country": "United States",
  "passport_expiry_date": "2029-12-31",
  "health_conditions": "Asthma, controlled with daily medication. Recently diagnosed with allergies.",
  "frequent_traveler": true
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user": "550e8400-e29b-41d4-a716-446655440000",
  "passport_number": "US123456789",
  "passport_issuing_country": "United States",
  "passport_expiry_date": "2029-12-31",
  "health_conditions": "Asthma, controlled with daily medication. Recently diagnosed with allergies.",
  "frequent_traveler": true,
  "created_at": "2025-12-16T10:30:00Z"
}
```

---

### 2.5 Partial Update Traveler Profile
**Endpoint:** `PATCH /core/travelers/{id}/`
**Authentication:** Required (Bearer Token)

**Request Payload:**
```json
{
  "frequent_traveler": false
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user": "550e8400-e29b-41d4-a716-446655440000",
  "passport_number": "US123456789",
  "passport_issuing_country": "United States",
  "passport_expiry_date": "2028-12-31",
  "health_conditions": "Asthma, controlled with daily medication",
  "frequent_traveler": false,
  "created_at": "2025-12-16T10:30:00Z"
}
```

---

### 2.6 Delete Traveler Profile
**Endpoint:** `DELETE /core/travelers/{id}/`
**Authentication:** Required (Bearer Token)

**Response:** 204 No Content

---

## 3. TRIP ENDPOINTS

### 3.1 Create Trip
**Endpoint:** `POST /core/trips/`
**Authentication:** Required (Bearer Token)

**Request Payload (Traveler):**
```json
{
  "destination_country": "Egypt",
  "destination_city": "Cairo",
  "start_date": "2025-12-20",
  "end_date": "2025-12-28",
  "purpose": "Business Conference",
  "accommodation": "Hilton Cairo Zamalek",
  "transport_mode": "Flight"
}
```

**Request Payload (Admin/HR - must specify traveler):**
```json
{
  "traveler": 1,
  "destination_country": "Egypt",
  "destination_city": "Cairo",
  "start_date": "2025-12-20",
  "end_date": "2025-12-28",
  "purpose": "Business Conference",
  "accommodation": "Hilton Cairo Zamalek",
  "transport_mode": "Flight"
}
```

**Response (201 Created):**
```json
{
  "id": 5,
  "traveler": 1,
  "destination_country": "Egypt",
  "destination_city": "Cairo",
  "start_date": "2025-12-20",
  "end_date": "2025-12-28",
  "purpose": "Business Conference",
  "accommodation": "Hilton Cairo Zamalek",
  "transport_mode": "Flight",
  "created_at": "2025-12-16T14:22:00Z"
}
```

---

### 3.2 Get All Trips
**Endpoint:** `GET /core/trips/`
**Authentication:** Required (Bearer Token)

**Note:** 
- **Travelers** see only their own trips
- **Admin/HR** see all trips

**Response (200 OK):**
```json
[
  {
    "id": 5,
    "traveler": 1,
    "destination_country": "Egypt",
    "destination_city": "Cairo",
    "start_date": "2025-12-20",
    "end_date": "2025-12-28",
    "purpose": "Business Conference",
    "accommodation": "Hilton Cairo Zamalek",
    "transport_mode": "Flight",
    "created_at": "2025-12-16T14:22:00Z"
  },
  {
    "id": 6,
    "traveler": 1,
    "destination_country": "Singapore",
    "destination_city": "Singapore",
    "start_date": "2026-01-10",
    "end_date": "2026-01-15",
    "purpose": "Trade Fair",
    "accommodation": "Marina Bay Sands",
    "transport_mode": "Flight",
    "created_at": "2025-12-16T15:30:00Z"
  }
]
```

---

### 3.3 Get Specific Trip
**Endpoint:** `GET /core/trips/{id}/`
**Authentication:** Required (Bearer Token)

**Response (200 OK):**
```json
{
  "id": 5,
  "traveler": 1,
  "destination_country": "Egypt",
  "destination_city": "Cairo",
  "start_date": "2025-12-20",
  "end_date": "2025-12-28",
  "purpose": "Business Conference",
  "accommodation": "Hilton Cairo Zamalek",
  "transport_mode": "Flight",
  "created_at": "2025-12-16T14:22:00Z"
}
```

---

### 3.4 Update Trip
**Endpoint:** `PUT /core/trips/{id}/`
**Authentication:** Required (Bearer Token)

**Request Payload:**
```json
{
  "traveler": 1,
  "destination_country": "Egypt",
  "destination_city": "Cairo",
  "start_date": "2025-12-21",
  "end_date": "2025-12-29",
  "purpose": "Business Conference & Networking",
  "accommodation": "Nile Hilton Cairo",
  "transport_mode": "Flight"
}
```

**Response (200 OK):**
```json
{
  "id": 5,
  "traveler": 1,
  "destination_country": "Egypt",
  "destination_city": "Cairo",
  "start_date": "2025-12-21",
  "end_date": "2025-12-29",
  "purpose": "Business Conference & Networking",
  "accommodation": "Nile Hilton Cairo",
  "transport_mode": "Flight",
  "created_at": "2025-12-16T14:22:00Z"
}
```

---

### 3.5 Partial Update Trip
**Endpoint:** `PATCH /core/trips/{id}/`
**Authentication:** Required (Bearer Token)

**Request Payload:**
```json
{
  "accommodation": "Four Seasons Cairo Nile Plaza"
}
```

**Response (200 OK):**
```json
{
  "id": 5,
  "traveler": 1,
  "destination_country": "Egypt",
  "destination_city": "Cairo",
  "start_date": "2025-12-20",
  "end_date": "2025-12-28",
  "purpose": "Business Conference",
  "accommodation": "Four Seasons Cairo Nile Plaza",
  "transport_mode": "Flight",
  "created_at": "2025-12-16T14:22:00Z"
}
```

---

### 3.6 Delete Trip
**Endpoint:** `DELETE /core/trips/{id}/`
**Authentication:** Required (Bearer Token)

**Response:** 204 No Content

---

### 3.7 Analyze Trip Risk ⭐
**Endpoint:** `POST /core/trips/{id}/analyze-risk/`
**Authentication:** Required (Bearer Token)

**Request Payload:** (No body required, uses trip data)

**Response (200 OK):**
```json
{
  "overall_risk_score": 65,
  "risk_level": "Medium",
  "political_and_war_risk": {
    "level": "Medium",
    "summary": "Egypt faces intermittent political unrest and occasional terrorist threats, particularly in urban areas like Cairo."
  },
  "labour_law_and_immigration": {
    "risk_level": "Low",
    "notes": "The business traveler is expected to face standard immigration procedures without significant risks. Visa regulations are generally straightforward for business visitors."
  },
  "health_and_safety": {
    "risk_level": "Medium",
    "notes": "Cairo has healthcare facilities, but travelers should remain cautious of air quality affecting asthma and ensure access to medical services."
  },
  "key_risk_factors": "Political unrest, public health concerns affecting respiratory conditions, and urban crime rates.",
  "recommendations": "Stay informed about the local political situation, carry all necessary medications, and follow health advisories regarding air quality and safety precautions."
}
```

---

## 4. REQUEST HEADERS

All authenticated requests should include:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

---

## 5. EXAMPLE WORKFLOW

### Step 1: Register a New User
```bash
POST /user/register
Body: {
  "username": "alice_smith",
  "email": "alice@company.com",
  "password": "SecurePassword123!",
  "role": "traveler",
  "nationality": "UK",
  "gender": "Female"
}
```

### Step 2: Login to Get Token
```bash
POST /user/login
Body: {
  "username": "alice_smith",
  "password": "SecurePassword123!"
}
Response includes: access_token
```

### Step 3: Create Traveler Profile
```bash
POST /core/travelers/
Headers: Authorization: Bearer {access_token}
Body: {
  "passport_number": "UK987654321",
  "passport_issuing_country": "United Kingdom",
  "passport_expiry_date": "2029-06-30",
  "health_conditions": "None",
  "frequent_traveler": true
}
```

### Step 4: Create a Trip
```bash
POST /core/trips/
Headers: Authorization: Bearer {access_token}
Body: {
  "destination_country": "Singapore",
  "destination_city": "Singapore",
  "start_date": "2026-01-10",
  "end_date": "2026-01-15",
  "purpose": "Trade Fair",
  "accommodation": "Marina Bay Sands",
  "transport_mode": "Flight"
}
```

### Step 5: Analyze Trip Risk
```bash
POST /core/trips/{trip_id}/analyze-risk/
Headers: Authorization: Bearer {access_token}
```

---

## 6. ERROR RESPONSE EXAMPLES

### 400 Bad Request
```json
{
  "field_name": ["Error message explaining what went wrong"]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 7. ROLE-BASED ACCESS CONTROL

| Endpoint | Traveler | HR Manager | Admin |
|----------|----------|-----------|-------|
| GET /core/travelers/ | Own profile only | All | All |
| POST /core/travelers/ | Own profile | Own profile | Own profile |
| GET /core/trips/ | Own trips | All trips | All trips |
| POST /core/trips/ | Own trips | Any traveler | Any traveler |
| POST /core/trips/{id}/analyze-risk/ | Own trips | All trips | All trips |
| DELETE /core/trips/ | Own trips | All trips | All trips |

---
