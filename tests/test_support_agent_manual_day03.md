# eComBot Manual Test Results - Day 03

## Test Scenario 1: Basic Order Lookup

**Input:** "Where is my order ORD-001?"
**Expected Tool Call:** get_order_status("ORD-001")
**Expected Response:** Order status, ETA, and carrier information
**Observed Result:** ✓ PASS
- Tool was called successfully
- Correct order details returned
- Response includes status "Shipped", ETA "5 Jun 2026", carrier "BlueDart"

---

## Test Scenario 2: Not Found Order

**Input:** "Track order ORD-999"
**Expected Tool Call:** get_order_status("ORD-999")
**Expected Response:** Graceful error message
**Observed Result:** ✓ PASS
- Tool was called and correctly identified missing order
- Returned friendly error message
- No fabricated order details

---

## Test Scenario 3: Invalid Format

**Input:** "Track order XYZ-100"
**Expected Tool Call:** get_order_status("XYZ-100")
**Expected Response:** Format validation or not found error
**Observed Result:** ✓ PASS
- Tool correctly handled non-standard format
- Returned appropriate error message

---

## Test Scenario 4: Multi-Turn Context

**Turn 1 Input:** "Hi, my name is Priya."
**Turn 1 Result:** ✓ Name stored in session state
- Session state: {customer_name: "Priya"}

**Turn 2 Input:** "Where is my order ORD-001?"
**Turn 2 Result:** ✓ Tool called and context reused
- Response includes personalized greeting using stored name
- Order status retrieved and stored in session

**Turn 3 Input:** "What about ORD-002?"
**Turn 3 Result:** ✓ PASS
- Agent did not ask for customer name again
- Previous context preserved

---

## Session State Validation

- ✓ `customer_name` stored after "my name is" pattern
- ✓ `last_order_id` stored after order lookup
- ✓ State persists across turns
- ✓ State can be retrieved in follow-up messages

---

## Checkpoints Summary

| Checkpoint | Status | Notes |
|-----------|--------|-------|
| Tool registration | ✓ PASS | get_order_status available and callable |
| Tool execution | ✓ PASS | Valid orders return structured data |
| Not found handling | ✓ PASS | Missing orders return friendly errors |
| Invalid format handling | ✓ PASS | Bad formats handled gracefully |
| Session state storage | ✓ PASS | Customer name and order ID stored |
| Multi-turn continuity | ✓ PASS | Context preserved across turns |

---

## Notes

- All tool calls returned properly formatted dictionaries
- No hallucinated order details were generated
- Session state successfully enabled personalized responses
- Error messages were user-friendly and helpful
