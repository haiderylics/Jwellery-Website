# Pre-Production Bug Report Template

Use this standardized template to document any functional defect, UI inconsistency, security vulnerability, or data integrity issue discovered during manual testing.

---

## Bug Header

| Field | Value / Details |
|---|---|
| **Bug ID** | `BUG-YYYYMMDD-XXX` (e.g. `BUG-20260814-001`) |
| **Date Reported** | `YYYY-MM-DD` |
| **Reporter** | Name / Role |
| **Environment** | Local Development (`http://localhost:5173`) / Staging |
| **Browser & Version** | e.g. Chrome 127.0, Safari 17.4, Firefox 128.0 |
| **Device / OS** | macOS / Windows 11 / iOS 17.5 / Android 14 |
| **Viewport Size** | Desktop (1440x900) / Tablet (768x1024) / Mobile (390x844) |
| **Related Test ID** | e.g. `TC-CART-02`, `TC-PROD-04` |
| **Severity** | **Blocker** / **Critical** / **Major** / **Minor** / **Trivial** |
| **Priority** | **P0 (Urgent Blocker)** / **P1 (High)** / **P2 (Normal)** / **P3 (Polish)** |

---

## 1. Issue Title
> Concise, descriptive title stating the exact failure condition (e.g. *"Cart quantity decrementing below 1 fails to remove product from local state"*).

---

## 2. Preconditions & Test Data
- **Catalog State**: e.g. Clean catalog seeded via `python manage.py seed_demo_data`
- **User Authentication**: Anonymous Storefront Visitor / Staff Admin
- **Test Data**: Product Slug `royal-solitaire-diamond-ring`, Variant ID `RSR-06`

---

## 3. Steps to Reproduce
1. Navigate to `/shop` and select `The Royal Solitaire Diamond Ring`.
2. Select variant `Size 7 (US)` and click **"Add to Cart"**.
3. Open the `/cart` slideout or cart page.
4. Attempt to edit the quantity input or click the `-` button when quantity is `1`.
5. Observe the UI and local storage state.

---

## 4. Expected Behavior
> State what the system is specified to do per PRD/Architecture (e.g. *"Decrementing quantity from 1 should prompt removal or delete the item from cart and recalculate subtotal to PKR 0"*).

---

## 5. Actual Behavior
> State what actually happened (e.g. *"Quantity field becomes 0 or NaN, causing subtotal calculation to fail with broken NaN display"*).

---

## 6. Visual & Log Evidence
- **Screenshot / Video**: `![Bug Screenshot](path/to/screenshot.png)`
- **Browser Console Output**:
  ```text
  Uncaught TypeError: Cannot read properties of undefined (reading 'base_price')
  ```
- **Network Tab (API Request/Response)**:
  - Request: `GET /api/v1/products/royal-solitaire-diamond-ring/` -> `HTTP 200 OK`
  - Response payload snippet.
- **Server Logs / Security Events**:
  ```text
  2026-08-14 20:15:00 [ERROR] backend.catalog: ...
  ```

---

## 7. Reproducibility
- [ ] **Always (100%)**
- [ ] **Intermittent (<50%)**
- [ ] **Single Occurrence**

---

## 8. Suggested Workaround (if any)
> Temporary mitigation for testers while awaiting fix.

---

## 9. Resolution & Verification (Filled upon fix)
- **Status**: `Open` / `In Progress` / `Resolved` / `Cannot Reproduce` / `Won't Fix`
- **Fix Commit / PR**: `commit_hash`
- **Root Cause Analysis**: Brief explanation of code defect.
- **Regression Test Added**: `backend/tests/test_...py::test_...` or frontend test.
- **Verification Sign-Off**: Name and Date.
