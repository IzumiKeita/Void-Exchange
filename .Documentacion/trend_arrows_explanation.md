# Trend System Explanation (Arrows and Colors)

This document details the technical and functional logic behind the trend indicators (red and green arrows) displayed on the Dashboard and item details.

## 1. Mathematical Calculation (`market_service.py`)

The trend is calculated by comparing the **average price** of the last available record with the immediately preceding record in the 48-hour history.

The formula used is:

```python
trend = ((current_price - previous_price) / previous_price) * 100
```

- **current_price**: Average price of the last recorded hour.
- **previous_price**: Average price of the previous hour.

The result is a **percentage** indicating how much the price has varied.

## 2. Visual Representation (`Dashboard.vue`)

The system interprets this percentage to display arrows and colors:

### A. Positive Trend (Green Arrow ▲)
- **Condition**: The result is **greater than or equal to 0** (`trend >= 0`).
- **Meaning**: The item price has **RISEN** (or remains the same) compared to the previous hour.
- **User Interpretation**:
  - **For Sellers**: It's a good time, the object is worth more.
  - **For Buyers**: The object is getting more expensive.

### B. Negative Trend (Red Arrow ▼)
- **Condition**: The result is **negative** (`trend < 0`).
- **Meaning**: The item price has **FALLEN** compared to the previous hour.
- **User Interpretation**:
  - **For Sellers**: The object is losing value.
  - **For Buyers**: It's a bidding opportunity, it's cheaper.

## 3. Practical Example

If a Warframe "Rhino Prime Set":
- Previous hour worth: **100 pl**
- Current hour worth: **90 pl**

Calculation: `(90 - 100) / 100 * 100 = -10%`

**On-screen Result**:
- **Arrow**: ▼ (Down)
- **Color**: Red
- **Value**: -10%
- **Reading**: The price has fallen by 10%.

## 4. Technical Notes
- If there is no previous data (it's the first record), the trend is 0%.
- The system rounds the percentage to 2 decimal places.
- This logic is applied consistently in both the Dashboard and the AI Chat for recommendations.
