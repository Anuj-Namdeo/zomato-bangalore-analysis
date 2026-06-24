# 🍽️ Zomato Bangalore — Complete Power BI Dashboard Implementation Guide
### Phase 7 of the End-to-End Data Analyst Portfolio Project
### Version 2.0 — Production Grade

---

## 📋 Table of Contents

1. [Step 7.1 — Export Cleaned Data](#step-71)
2. [Step 7.2 — Import in Power BI](#step-72)
3. [Step 7.3 — Data Model & Relationships](#step-73)
4. [Step 7.4 — All DAX Measures (20+ fully explained)](#step-74)
5. [Step 7.5 — Calculated Columns in Power BI](#step-75)
6. [Step 7.6 — Dashboard Pages (6 pages, full wireframes)](#step-76)
7. [Step 7.7 — Theme JSON & Formatting](#step-77)
8. [Step 7.8 — Bookmarks & Drill-Through](#step-78)
9. [Step 7.9 — Publish & Export to PDF](#step-79)
10. [Step 7.10 — Performance Optimisation](#step-710)
11. [Step 7.11 — Troubleshooting](#step-711)
12. [Interview Talking Points](#interview)

---

## Step 7.1 — Export Cleaned Data {#step-71}

### Run the Export Script

```bash
# Activate virtual environment first
source venv/bin/activate          # Mac/Linux
venv\Scripts\activate             # Windows

# Run from project root
python -m src.powerbi_export
```

**Expected terminal output:**
```
✅ Sheet 'Main_Data':          50,489 rows written
✅ Sheet 'Location_Summary':      93 rows written
✅ Sheet 'Cuisine_Summary':       89 rows written
✅ Sheet 'RestType_Summary':      22 rows written
✅ Sheet 'KPI_Table':              1 rows written
✅ Sheet 'Segment_Pivot':        312 rows written
✅ Sheet 'Opportunity_Score':     78 rows written
✅ Sheet 'Cost_Rating_Matrix':    38 rows written

🎉 Power BI export complete → data/cleaned/zomato_powerbi.xlsx
```

### What Each Sheet Does in Power BI

| Sheet | Role in PBI | Used For |
|-------|-------------|----------|
| `Main_Data` | **Fact Table** — central table, one row per restaurant | All detailed visuals, slicers |
| `Location_Summary` | **Dimension** — pre-aggregated location stats | Map visual, location charts, summary cards |
| `Cuisine_Summary` | **Dimension** — pre-aggregated cuisine stats | Cuisine comparison charts |
| `RestType_Summary` | **Dimension** — pre-aggregated type stats | Type analysis visuals |
| `KPI_Table` | **KPI Snapshot** — single row | Static KPI cards (backup for DAX) |
| `Segment_Pivot` | **Cross-tab** — Location × RestType | Matrix visual, treemap |
| `Opportunity_Score` | **Ranked locations** | Page 6 strategic recommendations |
| `Cost_Rating_Matrix` | **Cost × Type cross-tab** | Heatmap matrix visual |

---

## Step 7.2 — Import in Power BI {#step-72}

### Prerequisites
- **Power BI Desktop** (free): https://powerbi.microsoft.com/desktop
- Version: April 2024 or later (required for some visual features)
- Windows only (Mac: use Power BI in browser via powerbi.com)

### Import Steps

**1. Open Power BI Desktop**
   - Launch the application
   - Dismiss the splash screen (click X or "Skip")

**2. Get Data**
   - Click `Home` ribbon → `Get Data` → `Excel Workbook`
   - Navigate to: `[your project]/data/cleaned/zomato_powerbi.xlsx`
   - Click **Open**

**3. Navigator Window**
   - You will see all 8 sheet names listed on the left
   - Check the box next to **ALL 8 sheets**:
     ```
     ☑ Main_Data
     ☑ Location_Summary
     ☑ Cuisine_Summary
     ☑ RestType_Summary
     ☑ KPI_Table
     ☑ Segment_Pivot
     ☑ Opportunity_Score
     ☑ Cost_Rating_Matrix
     ```
   - Click **Load** (NOT "Transform Data" — data is already clean)

**4. Wait for Loading**
   - Main_Data has 50k rows → may take 15–30 seconds
   - Watch the loading progress bar at the bottom

**5. Verify Load**
   - Click `Data` view (table icon on left sidebar)
   - Click each table in the Fields panel (right)
   - Verify row counts match expected output

### Power Query Quick Check (Optional)
If you want to verify column types:
- `Home` → `Transform Data` (opens Power Query Editor)
- Click each table → verify column types shown in the header row
- Click `Close & Apply` when done

---

## Step 7.3 — Data Model & Relationships {#step-73}

### Relationship Architecture

```
                    ┌──────────────────────────────┐
                    │        Main_Data (FACT)       │
                    │  50,489 rows — one per        │
                    │  restaurant                   │
                    │                               │
                    │  Location ──────────────────► Location_Summary
                    │  Primary Cuisine ───────────► Cuisine_Summary
                    │  Primary Rest Type ─────────► RestType_Summary
                    │                               │
                    └──────────────────────────────┘

   KPI_Table ────── Standalone (no relationship needed)
   Segment_Pivot ── Standalone (pre-aggregated, used directly)
   Opportunity_Score ── Standalone (used on Page 6)
   Cost_Rating_Matrix ── Standalone (used on Page 4)
```

### Creating Relationships

Click the **Model** view (third icon on left sidebar).

**Relationship 1: Main_Data → Location_Summary**
```
Table A:       Main_Data
Column A:      Location           (Many side)

Table B:       Location_Summary
Column B:      Location           (One side)

Cardinality:   Many-to-One  (★ to 1)
Cross-filter:  Both
Active:        Yes
```

**How to create:**
1. In Model view, drag `Main_Data[Location]` onto `Location_Summary[Location]`
2. The relationship line appears
3. Double-click the line → Edit Relationship dialog
4. Set Cardinality: `Many to One (*:1)`
5. Set Cross filter direction: `Both`
6. Click OK

**Relationship 2: Main_Data → Cuisine_Summary**
```
Table A:       Main_Data
Column A:      Primary Cuisine    (Many side)

Table B:       Cuisine_Summary
Column B:      Primary Cuisine    (One side)

Cardinality:   Many-to-One
Cross-filter:  Both
Active:        Yes
```

**Relationship 3: Main_Data → RestType_Summary**
```
Table A:       Main_Data
Column A:      Primary Rest Type  (Many side)

Table B:       RestType_Summary
Column B:      Primary Rest Type  (One side)

Cardinality:   Many-to-One
Cross-filter:  Both
Active:        Yes
```

### Final Model Diagram

After setup, your Model view should look like this:

```
┌─────────────────┐    ★:1    ┌──────────────────────┐
│  Main_Data      │◄─────────►│  Location_Summary    │
│  (50,489 rows)  │           │  (93 rows)           │
│                 │    ★:1    ├──────────────────────┤
│                 │◄─────────►│  Cuisine_Summary     │
│                 │           │  (89 rows)           │
│                 │    ★:1    ├──────────────────────┤
│                 │◄─────────►│  RestType_Summary    │
│                 │           │  (22 rows)           │
└─────────────────┘           └──────────────────────┘

Standalone tables (no relationships):
  KPI_Table  |  Segment_Pivot  |  Opportunity_Score  |  Cost_Rating_Matrix
```

### Why "Both" Cross-Filter Direction?

With **Single** direction: clicking a location in a location chart filters
the restaurant list, but clicking in the restaurant list does NOT filter
the location chart.

With **Both** direction: filtering works in BOTH directions — clicking
anywhere on the dashboard filters everything related. This is what makes
Power BI dashboards feel interactive and cohesive.

> ⚠️ **Note:** "Both" can cause ambiguous relationship errors if you have
> circular paths. With our star schema (all relationships point outward
> from Main_Data), it is safe and preferred.

---

## Step 7.4 — All DAX Measures {#step-74}

### How to Create a Measure
1. Click the `Main_Data` table in the Fields panel (right side)
2. Click `...` (three dots) → `New Measure`
3. Type or paste the DAX formula
4. Press **Enter** or click the checkmark

> 💡 **Best Practice:** Store ALL measures in a dedicated **Measure Table**
> (a blank table you create). Right-click Fields panel → `Enter Data` →
> name it `_Measures` → leave blank → Load. Move all measures here.
> This keeps the Fields panel organised.

---

### GROUP A — CORE KPI MEASURES

#### Measure 1: Total Restaurants
```dax
Total Restaurants =
COUNTROWS('Main_Data')
```
**Explanation:**
- `COUNTROWS()` — counts every row in the table
- Power BI automatically applies any active filter context
- If user selects "Koramangala" in location slicer, this measure counts
  only Koramangala restaurants
- **Used on:** Page 1, 2, 3, 4, 5 — everywhere as the base count

---

#### Measure 2: Average Rating
```dax
Average Rating =
AVERAGEX(
    FILTER('Main_Data', NOT(ISBLANK('Main_Data'[Rate Numeric]))),
    'Main_Data'[Rate Numeric]
)
```
**Explanation:**
- `AVERAGEX()` — iterates over table rows and averages an expression
- `FILTER()` — removes rows where rating is blank (new restaurants)
- Why not just `AVERAGE('Main_Data'[Rate Numeric])`?
  - `AVERAGE()` also ignores blanks automatically, so both work
  - `AVERAGEX + FILTER` version gives you explicit control and is more
    transparent — you can see exactly what's being excluded
- **Used on:** All 6 pages

---

#### Measure 3: Median Cost for Two
```dax
Median Cost =
MEDIANX('Main_Data', 'Main_Data'[Approx Cost])
```
**Explanation:**
- `MEDIANX()` — computes median by iterating over the table
- We use **median** not mean because cost has a long right tail
  (a few ₹10,000+ restaurants would inflate the mean significantly)
- Median is more representative of "typical" restaurant cost
- **Used on:** Page 1, 4

---

#### Measure 4: Total Votes
```dax
Total Votes =
SUM('Main_Data'[Votes])
```
**Explanation:**
- Simple sum of all vote counts in current filter context
- **Used on:** Page 1, 2, 5

---

#### Measure 5: Average Votes per Restaurant
```dax
Avg Votes per Restaurant =
DIVIDE(
    [Total Votes],
    [Total Restaurants],
    0
)
```
**Explanation:**
- `DIVIDE(numerator, denominator, alternate_result)`
- `alternate_result = 0` — if denominator is 0, return 0 (not error)
- References other measures `[Total Votes]` and `[Total Restaurants]`
- This composability is a key DAX strength — build complex measures
  from simpler ones
- **Used on:** Page 2, 6

---

### GROUP B — PERCENTAGE MEASURES

#### Measure 6: Online Order Percentage
```dax
Online Order % =
DIVIDE(
    CALCULATE(
        COUNTROWS('Main_Data'),
        'Main_Data'[Online Order] = "Yes"
    ),
    [Total Restaurants],
    0
) * 100
```
**Explanation:**
- `CALCULATE()` — THE most important DAX function
  - Evaluates first argument (COUNTROWS) in a MODIFIED filter context
  - Adds the filter `Online Order = "Yes"` to existing filters
  - So: "count restaurants where Online Order = Yes, within current context"
- Divide by total → get ratio → multiply by 100 → percentage
- **Used on:** Page 1, 5

---

#### Measure 7: Table Booking Percentage
```dax
Table Booking % =
DIVIDE(
    CALCULATE(
        COUNTROWS('Main_Data'),
        'Main_Data'[Book Table] = "Yes"
    ),
    [Total Restaurants],
    0
) * 100
```

---

#### Measure 8: High Rated Percentage
```dax
High Rated % =
DIVIDE(
    CALCULATE(
        COUNTROWS('Main_Data'),
        'Main_Data'[Is High Rated] = "Yes"
    ),
    CALCULATE(
        COUNTROWS('Main_Data'),
        NOT(ISBLANK('Main_Data'[Rate Numeric]))
    ),
    0
) * 100
```
**Explanation:**
- Numerator: restaurants rated ≥ 4.0 (Is High Rated = "Yes")
- Denominator: restaurants that HAVE a rating (exclude unrated ones)
- Why this denominator? If we used Total Restaurants, new unrated
  restaurants would dilute the high-rated percentage unfairly
- **Used on:** Page 1, 4

---

#### Measure 9: Full Service Percentage (Online + Booking)
```dax
Full Service % =
DIVIDE(
    CALCULATE(
        COUNTROWS('Main_Data'),
        'Main_Data'[Online Order] = "Yes",
        'Main_Data'[Book Table] = "Yes"
    ),
    [Total Restaurants],
    0
) * 100
```
**Explanation:**
- Multiple filters in CALCULATE are ANDed together
- "Both online order AND table booking" = full service restaurants
- **Used on:** Page 5

---

#### Measure 10: Budget Segment Percentage
```dax
Budget Segment % =
DIVIDE(
    CALCULATE(
        COUNTROWS('Main_Data'),
        'Main_Data'[Cost Bucket] = "Budget (≤300)"
    ),
    [Total Restaurants],
    0
) * 100
```

---

### GROUP C — CONDITIONAL / DYNAMIC MEASURES

#### Measure 11: Rating Status Label
```dax
Rating Status =
SWITCH(
    TRUE(),
    [Average Rating] >= 4.2, "⭐ Excellent",
    [Average Rating] >= 4.0, "✅ High Quality",
    [Average Rating] >= 3.5, "📊 Average",
    [Average Rating] >= 3.0, "⚠️ Below Average",
    "❌ Poor"
)
```
**Explanation:**
- `SWITCH(TRUE(), condition1, result1, ...)` — evaluates conditions
  top-to-bottom, returns first TRUE match
- First argument is `TRUE()` — trick to make SWITCH work like IF-ELSEIF chain
- Used to display dynamic text labels in cards
- **Used on:** Page 1 (status card)

---

#### Measure 12: Rating Colour (for Conditional Formatting)
```dax
Rating Color =
SWITCH(
    TRUE(),
    [Average Rating] >= 4.0, "#27AE60",   -- Green
    [Average Rating] >= 3.5, "#F39C12",   -- Amber
    [Average Rating] >= 3.0, "#E67E22",   -- Orange
    "#E74C3C"                              -- Red
)
```
**Explanation:**
- Returns a hex colour string based on the rating value
- Used in Power BI's **Conditional Formatting** → "Field value" option
- Go to: Format visual → Data colours → Conditional formatting → Field value
  → point to this measure
- **Used on:** KPI cards, matrix cells

---

#### Measure 13: Market Share % (Selected Location)
```dax
Market Share % =
DIVIDE(
    [Total Restaurants],
    CALCULATE(
        [Total Restaurants],
        ALL('Main_Data'[Location])
    ),
    0
) * 100
```
**Explanation:**
- `ALL('Main_Data'[Location])` — removes all location filters from context
- `CALCULATE([Total Restaurants], ALL(...))` → total across ALL locations
- Dividing current context count by ALL context count = market share
- `ALL()` is how you "escape" the current filter context in DAX
- **Used on:** Page 2 location table (as a column in matrix visual)

---

#### Measure 14: Opportunity Score (DAX Version)
```dax
Opportunity Score =
VAR AvgVotes =
    AVERAGEX('Main_Data', 'Main_Data'[Votes])
VAR TotalRests =
    [Total Restaurants]
VAR AvgRating =
    [Average Rating]
RETURN
DIVIDE(AvgVotes, TotalRests, 0) * AvgRating
```
**Explanation:**
- `VAR` — declares a variable (calculated once, reused)
- `RETURN` — specifies the final output expression
- Variables make DAX readable and avoid repetition
- This is the same formula as Python: avg_votes/count × avg_rating
- **Used on:** Page 2 (location table column), Page 6

---

#### Measure 15: Value for Money Score
```dax
Value For Money Score =
DIVIDE(
    [Average Rating],
    LOG([Median Cost] + 1),
    0
)
```
**Explanation:**
- `LOG()` — natural logarithm (dampens the effect of cost scale)
- Higher rating with lower cost = higher value score
- `+ 1` inside LOG prevents LOG(0) error if cost is 0
- **Used on:** Page 4

---

#### Measure 16: Rating vs Benchmark (Delta)
```dax
Rating vs City Avg =
VAR CityAvg =
    CALCULATE(
        [Average Rating],
        ALL('Main_Data'[Location]),
        ALL('Main_Data'[Primary Cuisine]),
        ALL('Main_Data'[Primary Rest Type])
    )
RETURN
[Average Rating] - CityAvg
```
**Explanation:**
- `ALL()` on multiple columns removes filters from all those dimensions
- `CityAvg` = average across entire dataset (all contexts removed)
- Returns positive if current selection is above city average, negative if below
- Used for comparison cards (e.g., "Koramangala is +0.12 above city avg")
- **Used on:** Page 2

---

### GROUP D — SEGMENT & CLASSIFICATION MEASURES

#### Measure 17: Top Location Name
```dax
Top Location =
TOPN(
    1,
    SUMMARIZE('Main_Data', 'Main_Data'[Location], "_Count", COUNTROWS('Main_Data')),
    [_Count],
    DESC
)
```
**Explanation:**
- `TOPN(N, table, order_expression)` — returns top N rows
- `SUMMARIZE()` — creates a summary table grouped by Location with count
- Combined: gets the location with the highest restaurant count
- **Used on:** Page 1 KPI card ("Top Area: Koramangala")

> **Simpler alternative (for card visual):**
> Create a calculated column instead:
> `Top Location = FIRSTNONBLANK('Location_Summary'[Location], 1)`
> This works if Location_Summary is already sorted by count.

---

#### Measure 18: Pareto Threshold Count (Top 20% locations, 80% restaurants)
```dax
Pareto 80pct Location Count =
VAR TotalRestaurants = CALCULATE([Total Restaurants], ALL('Main_Data'))
VAR CumulativePct    = 0.80
RETURN
COUNTROWS(
    FILTER(
        ADDCOLUMNS(
            SUMMARIZE('Main_Data', 'Main_Data'[Location]),
            "_Count", CALCULATE([Total Restaurants])
        ),
        [_Count] >= CumulativePct * TotalRestaurants / 10
    )
)
```
**Explanation:**
- This is an advanced DAX measure demonstrating Pareto analysis
- `ADDCOLUMNS()` — adds a calculated column to a summarized table
- `SUMMARIZE()` — creates one row per location
- For each location, calculates restaurant count
- Returns number of locations needed to cover 80% of market
- **Used on:** Page 6 (insight card: "Just X areas hold 80% of restaurants")

---

#### Measure 19: Cost Tier Label (Dynamic)
```dax
Cost Tier Label =
SWITCH(
    TRUE(),
    [Median Cost] <= 300,  "💚 Budget (≤₹300)",
    [Median Cost] <= 600,  "💛 Mid (₹301-600)",
    [Median Cost] <= 1000, "🟠 Premium (₹601-1000)",
    [Median Cost] <= 1500, "🔴 Upscale (₹1001-1500)",
                           "💎 Luxury (>₹1500)"
)
```
**Used on:** Page 4 — dynamic label card that changes with slicer selection

---

#### Measure 20: Service Mix Label
```dax
Service Mix =
VAR OnlinePct  = [Online Order %]
VAR BookingPct = [Table Booking %]
RETURN
"Online: " & FORMAT(OnlinePct, "0.0") & "% | Booking: " & FORMAT(BookingPct, "0.0") & "%"
```
**Explanation:**
- `FORMAT(value, format_string)` — formats number as string
- `&` — string concatenation in DAX
- Returns a readable label: "Online: 62.3% | Booking: 18.7%"
- **Used on:** Page 5 summary card

---

#### Measure 21: Restaurant Density Tier
```dax
Density Tier =
SWITCH(
    TRUE(),
    [Total Restaurants] >= 3000, "🔴 Hyper Dense",
    [Total Restaurants] >= 1000, "🟠 High Density",
    [Total Restaurants] >= 500,  "💛 Medium Density",
    [Total Restaurants] >= 100,  "💚 Low Density",
                                 "⬜ Sparse"
)
```

---

#### Measure 22: Selected Location Name (for page titles)
```dax
Selected Location =
IF(
    HASONEVALUE('Main_Data'[Location]),
    SELECTEDVALUE('Main_Data'[Location]),
    "All Locations"
)
```
**Explanation:**
- `HASONEVALUE()` — TRUE if exactly one value is selected in filter context
- `SELECTEDVALUE()` — returns the single selected value (or blank if multiple)
- Returns "All Locations" when no filter or multiple locations selected
- **Used on:** Dynamic page title text boxes

---

### GROUP E — ADVANCED ANALYTICS MEASURES

#### Measure 23: Rating Distribution — % Above 4.0
```dax
Pct Rated Above 4 =
DIVIDE(
    CALCULATE(
        COUNTROWS('Main_Data'),
        'Main_Data'[Rate Numeric] >= 4.0
    ),
    CALCULATE(
        COUNTROWS('Main_Data'),
        NOT(ISBLANK('Main_Data'[Rate Numeric]))
    ),
    0
) * 100
```

---

#### Measure 24: Votes Concentration (Gini-like proxy)
```dax
Top 10pct Vote Share =
VAR Top10Count =
    CALCULATE(
        SUM('Main_Data'[Votes]),
        TOPN(
            CALCULATE(COUNTROWS('Main_Data'), ALL('Main_Data')) * 0.1,
            ALL('Main_Data'),
            'Main_Data'[Votes],
            DESC
        )
    )
RETURN
DIVIDE(Top10Count, [Total Votes], 0) * 100
```
**Explanation:**
- Calculates what % of total votes are held by top 10% of restaurants
- High value → votes are concentrated in few popular places (Pareto effect)
- **Used on:** Page 6 insight card

---

#### Measure 25: Online Adoption Growth Proxy
```dax
Online vs Offline Rating Gap =
VAR OnlineRating =
    CALCULATE([Average Rating], 'Main_Data'[Online Order] = "Yes")
VAR OfflineRating =
    CALCULATE([Average Rating], 'Main_Data'[Online Order] = "No")
RETURN
OnlineRating - OfflineRating
```
**Used on:** Page 5 — shows the rating premium for online-ordering restaurants

---

## Step 7.5 — Calculated Columns in Power BI {#step-75}

Some columns are better created in Power BI (not Python) because they
depend on DAX functions or are needed purely for visual formatting.

### Calculated Column 1: Rating Band
**Table:** Main_Data
```dax
Rating Band =
SWITCH(
    TRUE(),
    'Main_Data'[Rate Numeric] >= 4.5, "4.5-5.0 ⭐⭐⭐",
    'Main_Data'[Rate Numeric] >= 4.0, "4.0-4.4 ⭐⭐",
    'Main_Data'[Rate Numeric] >= 3.5, "3.5-3.9 ⭐",
    'Main_Data'[Rate Numeric] >= 3.0, "3.0-3.4",
    'Main_Data'[Rate Numeric] >= 1.0, "Below 3.0",
    "Not Rated"
)
```
**Why in PBI not Python:** This uses Power BI's SWITCH for clean null handling
and the emojis display natively in visuals.

---

### Calculated Column 2: Cost Bucket Sort Order
**Table:** Main_Data
```dax
Cost Bucket Sort =
SWITCH(
    'Main_Data'[Cost Bucket],
    "Budget (≤300)",       1,
    "Mid (301-600)",       2,
    "Premium (601-1000)",  3,
    "Upscale (1001-1500)", 4,
    "Luxury (>1500)",      5,
    9
)
```
**Purpose:** Right-click `Cost Bucket` column → `Sort by column` →
select `Cost Bucket Sort`. This ensures bars appear in price order, not alphabetical.

---

### Calculated Column 3: Service Level Description
**Table:** Main_Data
```dax
Service Description =
SWITCH(
    'Main_Data'[Service Level],
    0, "🔴 No Digital Service",
    1, "🟡 Online Order Only",
    2, "🔵 Booking Only",
    3, "🟢 Full Service",
    "Unknown"
)
```

---

### Calculated Column 4: Location Quadrant (for value matrix)
**Table:** Location_Summary
```dax
Location Quadrant =
VAR MedRating = MEDIAN('Location_Summary'[Avg_Rating])
VAR MedCost   = MEDIAN('Location_Summary'[Avg_Cost])
RETURN
SWITCH(
    TRUE(),
    'Location_Summary'[Avg_Rating] >= MedRating &&
        'Location_Summary'[Avg_Cost] <= MedCost,  "🟢 Best Value",
    'Location_Summary'[Avg_Rating] >= MedRating &&
        'Location_Summary'[Avg_Cost] > MedCost,   "🔵 Premium Quality",
    'Location_Summary'[Avg_Rating] < MedRating &&
        'Location_Summary'[Avg_Cost] <= MedCost,  "🟡 Budget Underperformer",
                                                   "🔴 Overpriced"
)
```

---

## Step 7.6 — Dashboard Pages (Full Wireframes & Build Instructions) {#step-76}

---

### PAGE 1: EXECUTIVE OVERVIEW

**Business Story:** "At a glance — the entire Bangalore restaurant industry snapshot."

#### Wireframe
```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🍽️  ZOMATO BANGALORE RESTAURANT ANALYTICS                    [Page Nav] ▶  ║
║  Empowering Restaurant Strategy with Data Intelligence                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐  ║
║  │  51,000+ │ │  ⭐ 3.71  │ │  ₹ 400  │ │  62.3%  │ │   27.5%          │  ║
║  │  Rests   │ │  Avg     │ │  Median  │ │  Online  │ │   High Rated     │  ║
║  │  [Card]  │ │  Rating  │ │  Cost    │ │  Order%  │ │   (≥4.0)         │  ║
║  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────────────┘  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ┌────────────────────────────────────────┐  ┌────────────────────────────┐ ║
║  │  TOP 10 LOCATIONS BY RESTAURANT COUNT  │  │  RATING DISTRIBUTION       │ ║
║  │  [Horizontal Bar Chart]                │  │  [Column / Histogram Chart]│ ║
║  │  Y: Location | X: Count               │  │  X: Rating Band | Y: Count │ ║
║  │  Sorted descending                     │  │  Sorted by rating order    │ ║
║  └────────────────────────────────────────┘  └────────────────────────────┘ ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ┌─────────────────────────┐  ┌─────────────────────────────────────────┐   ║
║  │  ONLINE ORDER SPLIT     │  │  PRICE SEGMENT DISTRIBUTION             │   ║
║  │  [Donut Chart]          │  │  [Stacked Bar or Column Chart]          │   ║
║  │  62% Yes / 38% No       │  │  X: Cost Bucket | Y: Count             │   ║
║  └─────────────────────────┘  └─────────────────────────────────────────┘   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  SLICERS (horizontal strip at bottom):                                       ║
║  [Location ▼]  [Primary Cuisine ▼]  [Cost Bucket ▼]  [Min Rating: ░░░ 0-5] ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

#### Visual-by-Visual Build Instructions

**KPI Card 1: Total Restaurants**
1. Insert → Card visual
2. Fields: Drag measure `[Total Restaurants]` to **Fields** well
3. Format pane → Callout value → Font size: 32, Bold, Color: #E23744
4. Format pane → Category label → Text: "Total Restaurants"
5. Format pane → Background → On, Color: #FFFFFF, Transparency: 0%
6. Format pane → Border → On, Color: #E23744, Width: 3, rounded: Top only
7. Resize to approximately 1/5 of the top strip width

**KPI Card 2: Average Rating**
1. Same as above, Fields: `[Average Rating]`
2. Format pane → Callout value format: `0.00`
3. Add conditional formatting:
   - Format pane → Callout value → Conditional formatting → On
   - Format: Color scale or Field value → `[Rating Color]` measure

**KPI Card 3: Median Cost**
1. Fields: `[Median Cost]`
2. Callout value format: `₹#,##0` (add prefix "₹" in Display units)
3. Or: use format code `\₹#,##0` in conditional formatting

**KPI Card 4: Online Order %**
1. Fields: `[Online Order %]`
2. Callout value format: `0.0"%"`

**KPI Card 5: High Rated %**
1. Fields: `[High Rated %]`
2. Color: Green (#27AE60) when above 25%, else amber

**Top 10 Locations Bar Chart**
1. Insert → Clustered Bar Chart
2. Y-axis: `Main_Data[Location]`
3. X-axis: `[Total Restaurants]`
4. Visual filter (top N): `Filters on this visual` pane →
   `Location` → Filter type: Top N → Show items: Top 10 → By value: `[Total Restaurants]`
5. Data labels: On, Font size 9
6. Sort: By `[Total Restaurants]` descending
7. Colors: Gradient from #FFB829 (bottom) to #E23744 (top)
   - Format → Data colors → Default color → Conditional formatting → Color scale

**Rating Distribution Column Chart**
1. Insert → Clustered Column Chart
2. X-axis: `Main_Data[Rating Band]` (the calculated column you created)
3. Y-axis: `[Total Restaurants]`
4. Sort by: Rating Band Sort (create a sort column: "4.5-5.0" → 1, "4.0-4.4" → 2, etc.)
5. Colors: Gradient — low rating = red, high = green
6. Data labels: On

**Online Order Donut Chart**
1. Insert → Donut Chart
2. Legend: `Main_Data[Online Order]`
3. Values: `[Total Restaurants]`
4. Colors: Yes = #E23744, No = #BDC3C7
5. Inner radius: 60% (Format → Shape → Inner radius: 60)
6. Add center label: Use Text Box overlaid with measure value

**Price Segment Column Chart**
1. Insert → Clustered Column Chart
2. X-axis: `Main_Data[Cost Bucket]`
3. Y-axis: `[Total Restaurants]`
4. Sort by: `Cost Bucket Sort` (the sort column)
5. Colors: Gradient from green (budget) to red (luxury)

**Slicers (bottom strip)**
1. Insert → Slicer → Field: `Main_Data[Location]`
   - Format → Style: Dropdown (saves space)
   - Enable "Select All" option
2. Repeat for `Primary Cuisine`, `Cost Bucket`
3. For Min Rating slider:
   - Slicer → Field: `Main_Data[Rate Numeric]`
   - Format → Style: Between (shows range slider)

**Page Interactions:**
- Select all visuals (Ctrl+A) → Format → Edit Interactions
- Ensure all visuals cross-filter each other
- The location bar chart should filter all other visuals when clicked

---

### PAGE 2: LOCATION ANALYSIS

**Business Story:** "Where is Bangalore's restaurant activity concentrated?
Which areas are overpriced or undervalued? Where should you open next?"

#### Wireframe
```
╔══════════════════════════════════════════════════════════════════════════════╗
║  📍  LOCATION INTELLIGENCE                              [◄ Page Nav ►]       ║
╠═══════════════════════╦══════════════════════════════════════════════════════╣
║                       ║  ┌────────────────────────────────────────────────┐  ║
║  BANGALORE MAP        ║  │  LOCATION PERFORMANCE TABLE                   │  ║
║  [Bubble Map]         ║  │  [Matrix Visual]                               │  ║
║  Bubble size = count  ║  │  Rows: Location (top 20)                       │  ║
║  Bubble colour = rating║ │  Columns: Count | Avg Rating | Avg Cost |      │  ║
║  Tooltip: area stats  ║  │           Online% | Opp Score | Rating vs Avg  │  ║
║                       ║  └────────────────────────────────────────────────┘  ║
╠═══════════════════════╩══════════════════════════════════════════════════════╣
║  ┌─────────────────────────────────────────┐  ┌──────────────────────────┐  ║
║  │  LOCATION VALUE MATRIX                  │  │  ONLINE ORDER ADOPTION   │  ║
║  │  [Scatter Plot]                         │  │  BY LOCATION             │  ║
║  │  X: Avg Cost | Y: Avg Rating            │  │  [100% Stacked Bar]      │  ║
║  │  Size: Restaurant Count                 │  │  Top 15 locations        │  ║
║  │  Colour: Location Quadrant              │  │  Y: Yes/No split         │  ║
║  │  Labels on large areas                  │  │                          │  ║
║  └─────────────────────────────────────────┘  └──────────────────────────┘  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Filters: [Location Tier ▼]  [Min Restaurant Count: 50]  [Location ▼]        ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

#### Bing Map Visual Build

1. Insert → Map visual (uses Bing Maps — requires internet)
2. Fields setup:
   ```
   Location:       Location_Summary[Location]
   Latitude:       Location_Summary[Latitude]
   Longitude:      Location_Summary[Longitude]
   Size:           Location_Summary[Restaurant_Count]
   Color saturation: Location_Summary[Avg_Rating]
   Tooltips:       Restaurant_Count, Avg_Rating, Avg_Cost, Online_Order_Pct
   ```
3. Format → Bubbles → Min size: 5px, Max size: 25px
4. Format → Map styles → Style: Road
5. Format → Category labels: On, show area names
6. Format → Zoom buttons: On

> ⚠️ **If Map doesn't load:** Go to File → Options → Security →
> Enable map and filled map visuals → Restart PBI

#### Location Performance Matrix

1. Insert → Matrix visual
2. Rows: `Location_Summary[Location]`
3. Values (in order):
   - `Location_Summary[Restaurant_Count]`
   - `[Average Rating]` (measure)
   - `[Median Cost]` (measure)
   - `[Online Order %]` (measure)
   - `[Opportunity Score]` (measure)
   - `[Rating vs City Avg]` (measure)
4. Conditional formatting on each column:
   - Avg Rating: Color scale (red low, green high)
   - Opportunity Score: Color scale (white to #E23744)
   - Rating vs City Avg: Diverging scale (red negative, green positive)
5. Add totals: On for count column, Off for rating/cost averages
6. Enable drill-down: Select a location → cross-filter entire page

#### Location Value Scatter Plot

1. Insert → Scatter Chart
2. X-axis: `Location_Summary[Avg_Cost]`
3. Y-axis: `Location_Summary[Avg_Rating]`
4. Size: `Location_Summary[Restaurant_Count]`
5. Legend: `Location_Summary[Location Quadrant]` (calculated column)
6. Play axis: Leave blank (we don't have time dimension)
7. Tooltips: Add Location, all four metrics
8. Format → Data labels: On, font size 8
9. Add reference lines:
   - X constant line: median cost value (Format → X-axis → Constant line)
   - Y constant line: median rating value

**Colour the quadrants manually:**
- Click a bubble in each quadrant → Format → Data colors
- 🟢 Best Value = #27AE60
- 🔵 Premium Quality = #2D9CDB
- 🟡 Budget Underperformer = #F39C12
- 🔴 Overpriced = #E74C3C

---

### PAGE 3: CUISINE INSIGHTS

**Business Story:** "Which cuisines dominate? Which command premium pricing?
Where are the quality gaps and market opportunities?"

#### Wireframe
```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🍛  CUISINE INTELLIGENCE                               [◄ Page Nav ►]       ║
╠════════════════════════════════════════╦═════════════════════════════════════╣
║  TOP 15 CUISINES BY COUNT             ║  CUISINE PREMIUM PRICING            ║
║  [Horizontal Bar Chart]               ║  [Horizontal Bar Chart]             ║
║  Y: Primary Cuisine                   ║  Y: Primary Cuisine (top 12)        ║
║  X: [Total Restaurants]               ║  X: [Median Cost]                   ║
║  Colour: Avg Rating (gradient)        ║  Colour: Avg Rating                 ║
╠════════════════════════════════════════╩═════════════════════════════════════╣
║  ┌──────────────────────────────┐  ┌──────────────────────────────────────┐ ║
║  │  CUISINE × LOCATION MATRIX   │  │  MARKET GAP ANALYSIS                 │ ║
║  │  [Matrix Visual]             │  │  [Scatter Chart]                     │ ║
║  │  Rows: Primary Cuisine       │  │  X: Restaurant Count                 │ ║
║  │  Cols: Location (top 8)      │  │  Y: Avg Rating                       │ ║
║  │  Values: Avg Rating          │  │  Size: Avg Votes                     │ ║
║  │  Colour: Heat scale          │  │  Label: Gap Opportunity cuisines     │ ║
║  └──────────────────────────────┘  └──────────────────────────────────────┘ ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Filters: [Cuisine ▼]  [Location ▼]  [Market Gap Flag ▼]                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

#### Market Gap Scatter Chart (Most Impressive Visual)

1. Insert → Scatter Chart
2. X-axis: `Cuisine_Summary[Restaurant_Count]`
3. Y-axis: `Cuisine_Summary[Avg_Rating]`
4. Size: `Cuisine_Summary[Avg_Votes]`
5. Legend: `Cuisine_Summary[Market_Gap_Flag]`
6. Tooltips: Primary Cuisine, Restaurant_Count, Avg_Rating, Avg_Cost, Avg_Votes
7. Data labels: Only show labels for `Market_Gap_Flag = "Gap Opportunity"` items
   - Achieved via: Format → Data labels → Conditional formatting

**Annotation via Text Box:**
Add a floating text box: "↖ HIGH OPPORTUNITY ZONE: High quality, low competition"
Place it in the upper-left quadrant of the scatter.

#### Cuisine × Location Matrix (Heatmap)

1. Insert → Matrix
2. Rows: `Cuisine_Summary[Primary Cuisine]` (top 10)
3. Columns: `Main_Data[Location]` (top 8 by count)
4. Values: `[Average Rating]`
5. Conditional formatting on Values:
   - Color scale: Min = 3.0 (#E74C3C/Red), Mid = 3.7 (#F39C12/Amber), Max = 4.5 (#27AE60/Green)
6. Cell elements: Data bars disabled, show values
7. Format → Grid: Cell padding: 8px, Horizontal alignment: Center

---

### PAGE 4: PRICE & RATING ANALYSIS

**Business Story:** "What is the price-quality relationship? Where is the
sweet spot? Which segments are most competitive?"

#### Wireframe
```
╔══════════════════════════════════════════════════════════════════════════════╗
║  💰  PRICE & RATING INTELLIGENCE                        [◄ Page Nav ►]       ║
╠══════════════════════╦═══════════════════════════════════════════════════════╣
║  KPI STRIP           ║  PRICE SEGMENT vs RATING                             ║
║  Median Cost: ₹400  ║  [Dual-Axis Combo Chart]                             ║
║  Avg Rating: 3.71   ║  X: Cost Bucket (sorted)                             ║
║  High Rated: 27.5%  ║  Left Y (bars): Restaurant Count                     ║
║  VFM Score: 0.62    ║  Right Y (line): Avg Rating                          ║
╠══════════════════════╩═══════════════════════════════════════════════════════╣
║  ┌───────────────────────────────┐  ┌───────────────────────────────────┐   ║
║  │  COST DISTRIBUTION HISTOGRAM  │  │  RESTAURANT SEGMENT PROFILES      │   ║
║  │  [Column Chart]               │  │  [Clustered Bar Chart]            │   ║
║  │  X: Approx Cost (binned)      │  │  Y: Restaurant Segment            │   ║
║  │  Y: Count                     │  │  X: Avg Rating / Avg Cost / Count │   ║
║  │  Reference line: Median       │  │  Legend: Metric                   │   ║
║  └───────────────────────────────┘  └───────────────────────────────────┘   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ┌──────────────────────────────────────────────────────────────────────┐    ║
║  │  COST × RESTAURANT TYPE MATRIX                                       │    ║
║  │  [Matrix Visual from Cost_Rating_Matrix sheet]                       │    ║
║  │  Rows: Cost Bucket | Cols: Primary Rest Type | Values: Avg Rating    │    ║
║  │  Conditional formatting: heat scale                                  │    ║
║  └──────────────────────────────────────────────────────────────────────┘    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Filters: [Cost Bucket ▼]  [Restaurant Segment ▼]  [Primary Rest Type ▼]    ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

#### Dual-Axis Combo Chart Build

1. Insert → Line and Clustered Column Chart
2. X-axis (Shared): `Main_Data[Cost Bucket]`
3. Column Y-axis: `[Total Restaurants]`
4. Line Y-axis: `[Average Rating]`
5. Sort X by: `Cost Bucket Sort` column
6. Format → Column series colour: `#FFB829`
7. Format → Line series: Colour #E23744, Stroke width: 3, Markers: On
8. Data labels: On for both series
9. Secondary Y-axis range: 3.0 to 4.5 (Format → Y-axis → Secondary)

---

### PAGE 5: SERVICE ANALYSIS

**Business Story:** "How does service model (online ordering + table booking)
affect ratings, costs, and engagement? Which areas lead in digital adoption?"

#### Wireframe
```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🔧  SERVICE INTELLIGENCE                               [◄ Page Nav ►]       ║
╠══════════════════╦═══════════════════════════════════════════════════════════╣
║  KPI STRIP       ║  SERVICE LEVEL vs RATING                                 ║
║  Online: 62.3%  ║  [Clustered Column Chart]                                ║
║  Booking: 18.7% ║  X: Service Description (0-3)                            ║
║  Full Svc: 15.2%║  Y: [Average Rating]                                     ║
║  Gap: +0.13     ║  Data labels: On, Format: 0.00                           ║
╠══════════════════╩═══════════════════════════════════════════════════════════╣
║  ┌───────────────────────────────────┐  ┌───────────────────────────────┐   ║
║  │  ONLINE ORDER ADOPTION BY AREA    │  │  FULL SERVICE PREMIUM MATRIX  │   ║
║  │  [100% Stacked Bar Chart]         │  │  [Matrix Visual]              │   ║
║  │  Y: Location (top 15)             │  │  Rows: Online Order (Yes/No)  │   ║
║  │  X: % Yes | % No                  │  │  Cols: Book Table (Yes/No)    │   ║
║  │  Sorted by Online% desc           │  │  Values: Avg Rating, Avg Cost │   ║
║  └───────────────────────────────────┘  └───────────────────────────────┘   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ┌──────────────────────────────────────────────────────────────────────┐    ║
║  │  RATING COMPARISON: ONLINE vs OFFLINE (Violin / Box equivalent)      │    ║
║  │  [Box Plot — requires AppSource visual: "Box and Whisker Chart"]     │    ║
║  │  Category: Online Order (Yes/No)                                     │    ║
║  │  Sampling: Rate Numeric                                               │    ║
║  │  Shows: Min, Q1, Median, Q3, Max per group                           │    ║
║  └──────────────────────────────────────────────────────────────────────┘    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Filters: [Location ▼]  [Primary Rest Type ▼]  [Cost Bucket ▼]              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

#### 100% Stacked Bar Chart Build (Online Adoption by Area)

1. Insert → 100% Stacked Bar Chart
2. Y-axis: `Main_Data[Location]`
3. X-axis: `[Total Restaurants]`
4. Legend: `Main_Data[Online Order]` (Yes / No)
5. Colors: Yes = #E23744, No = #BDC3C7
6. Sort Y-axis by: Online Order % descending
   - You need to sort the Location field by Online_Order_Pct from Location_Summary
   - Or add a calculated measure `[Online Order %]` and sort by it
7. Enable Top N filter on Location: Top 15 by `[Total Restaurants]`
8. Data labels: On, show percentages
9. Format → Legend position: Bottom

#### Full Service Premium Matrix

1. Insert → Matrix
2. Rows: `Main_Data[Online Order]`
3. Columns: `Main_Data[Book Table]`
4. Values:
   - `[Total Restaurants]`
   - `[Average Rating]`
   - `[Median Cost]`
   - `[Avg Votes per Restaurant]`
5. Grand totals: Off (they add noise here)
6. Conditional format Avg Rating with color scale

---

### PAGE 6: STRATEGIC RECOMMENDATIONS

**Business Story:** "Translate all data into actionable business recommendations
for investors, restaurant owners, and food brand managers."

#### Wireframe
```
╔══════════════════════════════════════════════════════════════════════════════╗
║  🎯  STRATEGIC INTELLIGENCE                             [◄ Page Nav ►]       ║
╠════════════════════════════════════════╦═════════════════════════════════════╣
║  OPPORTUNITY SCORE — TOP 10 AREAS     ║  MARKET GAP SUMMARY CARDS           ║
║  [Horizontal Bar Chart]               ║  ┌──────────────────────────────┐   ║
║  From: Opportunity_Score sheet        ║  │  Market Gap Cuisines: X      │   ║
║  Y: Location | X: Opportunity Score   ║  │  Under-served Areas: X       │   ║
║  Annotate top 3 areas                 ║  │  Top Opportunity Area: ...   │   ║
║                                       ║  └──────────────────────────────┘   ║
╠════════════════════════════════════════╩═════════════════════════════════════╣
║  ┌─────────────────────────────────────────────────────────────────────┐     ║
║  │  KEY FINDINGS TEXT BOX (Formatted)                                  │     ║
║  │                                                                     │     ║
║  │  📍 LOCATION:  Whitefield & Hebbal — Highest Opportunity Score      │     ║
║  │  🍛 CUISINE:   Continental & Mediterranean — High rating, low count │     ║
║  │  💻 SERVICE:   Online ordering shows +0.13 rating premium           │     ║
║  │  💰 PRICING:   Mid-range (₹400-600) = most competitive segment      │     ║
║  │  📊 VIRALITY:  Top 1% restaurants capture 40% of all votes          │     ║
║  └─────────────────────────────────────────────────────────────────────┘     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ┌───────────────────────────────┐  ┌────────────────────────────────────┐  ║
║  │  COMPETITIVE DENSITY MAP      │  │  RECOMMENDATION BUTTONS            │  ║
║  │  [Treemap]                    │  │  [Bookmark Navigator Buttons]      │  ║
║  │  Group: Location              │  │  "View Location Analysis"          │  ║
║  │  Size: Restaurant Count       │  │  "View Cuisine Analysis"           │  ║
║  │  Colour: Avg Rating           │  │  "View Price Analysis"             │  ║
║  └───────────────────────────────┘  └────────────────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

#### Opportunity Score Bar Chart

1. Use `Opportunity_Score` table (not Main_Data — use pre-computed scores)
2. Insert → Clustered Bar Chart
3. Y-axis: `Opportunity_Score[Location]`
4. X-axis: `Opportunity_Score[Opportunity_Score]`
5. Filter: Top N → Top 10 by Opportunity_Score
6. Color: Gradient from #FFB829 to #E23744
7. Data labels: On, Format: 0.000
8. Add reference line at median value
9. Annotate top 3: Use text boxes or custom tooltips

#### Treemap for Competitive Density

1. Insert → Treemap
2. Category: `Main_Data[Location]`
3. Values: `[Total Restaurants]`
4. Color saturation: `[Average Rating]`
5. Tooltips: Add all metrics
6. Filter: Top 20 locations by count

#### Key Findings Text Box

1. Insert → Text Box
2. Format with rich text:
   - Title: 20pt, Bold, #E23744
   - Body bullets: 12pt, regular
3. Content (update with your actual values):

```
🎯 TOP 5 STRATEGIC INSIGHTS FROM THIS ANALYSIS

📍 LOCATION STRATEGY
   → Whitefield and Hebbal: Highest opportunity score (demand/supply ratio)
   → Koramangala: Maximum visibility but maximum competition (12% market share)
   → Recommendation: New entrants → target Hebbal/Yelahanka growth zones

🍛 CUISINE POSITIONING
   → Continental, Mediterranean, Lebanese: <100 outlets, ≥4.0 avg rating
   → North Indian: Saturated at 30%+ share — differentiation critical
   → Recommendation: Enter with Continental → premium pricing, low competition

💻 SERVICE MODEL
   → Online ordering correlates with +0.13 higher rating (stat. significant)
   → Full-service restaurants (both options): ₹200+ higher avg cost
   → Recommendation: Online ordering is NON-NEGOTIABLE for new restaurants

💰 PRICING SWEET SPOT
   → Mid-range ₹400-600: Highest restaurant count, competitive but proven demand
   → Budget ≤₹300: Second largest, high volume, low margin
   → Recommendation: Launch at ₹450-600 to balance volume and profitability

📊 VIRALITY DYNAMICS
   → Top 1% restaurants hold ~40% of all votes (Pareto principle confirmed)
   → Viral restaurants (>1000 votes): require both quality (≥4.2) AND online ordering
   → Recommendation: Invest in online reputation management from Day 1
```

---

## Step 7.7 — Theme JSON & Formatting {#step-77}

### Apply the Zomato Theme

1. Open Power BI Desktop
2. View ribbon → Themes → Browse for themes
3. Navigate to: `dashboard/zomato_theme.json`
4. Click Open

### Theme JSON File

Save this as `dashboard/zomato_theme.json`:

```json
{
  "name": "Zomato Bangalore Analytics",
  "dataColors": [
    "#E23744",
    "#FC6B21",
    "#FFB829",
    "#2D9CDB",
    "#6FCF97",
    "#9B51E0",
    "#F39C12",
    "#27AE60",
    "#E74C3C",
    "#8E44AD"
  ],
  "background": "#FFFFFF",
  "foreground": "#252525",
  "tableAccent": "#E23744",
  "visualStyles": {
    "*": {
      "*": {
        "fontFamily": [{ "value": "Segoe UI" }],
        "fontSize": [{ "value": 11 }],
        "fontColor": [{ "value": "#252525" }],
        "background": [{ "color": { "solid": { "color": "#FFFFFF" } } }]
      },
      "title": {
        "fontColor": [{ "value": "#252525" }],
        "fontSize": [{ "value": 14 }],
        "fontFamily": [{ "value": "Segoe UI Semibold" }],
        "background": [{ "color": { "solid": { "color": "#FFFFFF" } } }]
      }
    },
    "card": {
      "*": {
        "calloutFontSize": [{ "value": 32 }],
        "fontColor": [{ "value": "#E23744" }]
      }
    },
    "clusteredBarChart": {
      "*": {
        "dataColor": [{ "color": { "solid": { "color": "#E23744" } } }]
      }
    }
  },
  "textClasses": {
    "title": {
      "fontSize": 18,
      "fontFace": "Segoe UI Semibold",
      "color": "#E23744"
    },
    "header": {
      "fontSize": 14,
      "fontFace": "Segoe UI Semibold",
      "color": "#252525"
    },
    "body": {
      "fontSize": 11,
      "fontFace": "Segoe UI",
      "color": "#252525"
    },
    "label": {
      "fontSize": 10,
      "fontFace": "Segoe UI",
      "color": "#6B6B6B"
    }
  }
}
```

### Page-Level Formatting (Apply to ALL 6 pages)

**Canvas Settings:**
- View → Canvas settings → Type: Custom
- Width: 1920, Height: 1080 (Full HD — standard portfolio screenshot size)

**Page Background:**
- Format → Wallpaper → Color: #F5F5F5 (very light grey)
- Transparency: 0%

**Visual Container Styling (apply to each visual):**
- Background: #FFFFFF, Transparency: 0%
- Border: On, Color: #E8E8E8, Rounded corners: 8px
- Shadow: On, Preset: Small (subtle lift effect)
- Padding: 12px all sides

**Title Bar (at top of each page):**
- Insert → Text Box
- Text: Page title in 20pt, Segoe UI Semibold, #E23744
- Background: White
- Width: Full page width, Height: 50px
- Add a thin red line below (Insert → Shapes → Rectangle,
  height 3px, color #E23744, no border)

**Colour Reference Card (keep on hand):**
```
Primary Red:     #E23744  → KPIs, titles, primary bars, donut Yes slice
Secondary Orange: #FC6B21  → Secondary metrics
Yellow/Amber:    #FFB829  → Warning, mid values, bar charts
Blue:            #2D9CDB  → Information, No slices, info cards
Green:           #6FCF97  → Positive, high ratings, good metrics
Purple:          #9B51E0  → Segmentation colours
Dark Text:       #252525  → All body text
Light Grey:      #E8E8E8  → Borders, lines
Background:      #F5F5F5  → Page background
White:           #FFFFFF  → Visual backgrounds, card backgrounds
```

---

## Step 7.8 — Bookmarks & Drill-Through {#step-78}

### Bookmark Setup

Bookmarks capture the current state of the dashboard (filters, visible visuals,
selection state). They power "reset to default" buttons and view toggles.

**Creating Bookmarks:**
1. View ribbon → Bookmarks (opens Bookmarks pane)
2. Click `+ Add` for each state you want to save

**Recommended Bookmarks:**

| Bookmark Name | When to Activate | How |
|---------------|------------------|-----|
| `Default_P1` | Initial state, no filters | Page 1, no slicers selected |
| `Koramangala_Focus` | Pre-filtered to Koramangala | Select Koramangala in slicer, click Add |
| `Budget_Restaurants` | Cost ≤₹300 only | Select Budget bucket, click Add |
| `High_Rated_Only` | Rating ≥ 4.0 | Select High Rated filter, click Add |
| `Premium_Zones` | Tier-1 locations only | Select Tier-1 in tier slicer, click Add |

**Adding Bookmark Buttons:**
1. Insert → Buttons → Blank
2. Format pane → Action → Type: Bookmark
3. Format pane → Action → Bookmark: select your bookmark
4. Style the button: Border, fill, text, hover state

### Drill-Through Setup

Drill-through lets users right-click a data point to navigate to a detail page.

**Setup: Location Drill-Through Page**

1. Add a new page: "Location Detail (Drill-Through)"
2. On this page, add `Main_Data[Location]` to the **Drill through** filter well
   (found in the Filters pane when on this page)
3. Build this page as a deep-dive for ONE location:
   - Top 5 restaurants in that location (table visual)
   - Rating distribution for that location (histogram)
   - Cuisine breakdown (bar chart)
   - Cost distribution (histogram)
   - Online order split (donut)

4. Back button appears automatically when drill-through is set up
   - Customise it: Format the auto-generated Back button

**How users use drill-through:**
1. On Page 2, user sees Indiranagar in the location chart
2. Right-click on Indiranagar bar
3. Sees "Drill through → Location Detail"
4. Clicks → arrives at Location Detail page filtered to Indiranagar
5. Clicks Back button → returns to Page 2

### Tooltip Page Setup

Tooltip pages show a custom floating panel when user hovers over a data point.

1. Add a new page: "Tooltip — Location"
2. Page settings → Page type: Tooltip
3. Canvas size: Width 400, Height 200
4. Build a compact card layout:
   ```
   [Location Name]
   ████ Count: X  |  ⭐ X.X  |  ₹X
   [Opportunity Score bar indicator]
   Online: X% | Booking: X%
   ```
5. On Page 2 visuals → Format → General → Tooltip → Type: Report page
   → Page: "Tooltip — Location"

---

## Step 7.9 — Publish & Export to PDF {#step-79}

### Save the .pbix File

1. File → Save As
2. Navigate to: `dashboard/`
3. Filename: `Zomato_Bangalore_Dashboard.pbix`
4. Click Save

> 💡 **GitHub note:** `.pbix` files are binary and don't version-control well.
> Add to `.gitignore` OR use Git LFS (Large File Storage).
> Better practice: commit screenshots instead of the `.pbix`.

### Publish to Power BI Service (Optional but recommended)

1. **Sign in:** Home ribbon → Sign In → use Microsoft account (free)
2. **Publish:** Home ribbon → Publish
3. Select workspace: "My Workspace" (default, free tier)
4. Wait for upload (30–60 seconds for 50k rows)
5. Click the link that appears → opens your dashboard in browser

**What you get with published dashboard:**
- Shareable URL to include in portfolio
- Mobile-responsive layout (configure in View → Mobile layout)
- Scheduled data refresh (not needed for static CSV)
- Embed code for your portfolio website

### Export to PDF

**Method A: From Power BI Desktop**
1. File → Export → Export to PDF
2. All 6 pages export as separate PDF pages
3. Choose: "Export current page" or "All pages"
4. PDF renders at your canvas size (1920×1080 → landscape A3 essentially)
5. Save as: `reports/Zomato_Dashboard_Report.pdf`

**Method B: From Power BI Service (better quality)**
1. Open your published report in browser
2. File menu (top-left) → Export → PDF
3. Select: Include all pages
4. Download → save to `reports/`

**Method C: Print to PDF (backup)**
1. File → Print
2. Printer: Microsoft Print to PDF
3. Settings: Landscape, All pages, High quality
4. Save as PDF

### Take High-Quality Screenshots for GitHub

**Recommended tools:**
- Windows: Win + Shift + S (Snip & Sketch) → region screenshot
- Mac: Cmd + Shift + 4 → drag selection
- Better: Use browser (publish to PBI Service) → zoom to 100% → screenshot

**Screenshot checklist for each page:**
```
Page 1: images/dashboard/p1_executive_overview.png   (1920×1080)
Page 2: images/dashboard/p2_location_analysis.png
Page 3: images/dashboard/p3_cuisine_insights.png
Page 4: images/dashboard/p4_price_rating.png
Page 5: images/dashboard/p5_service_analysis.png
Page 6: images/dashboard/p6_strategic_recommendations.png
Model:  images/dashboard/data_model.png
```

**For README.md — embed the best screenshot:**
```markdown
## 📊 Dashboard Preview
![Executive Overview](images/dashboard/p1_executive_overview.png)
```

---

## Step 7.10 — Performance Optimisation {#step-710}

### Why Performance Matters

With 50,000 rows, Power BI should be fast. But poor DAX or too many visuals
can make dashboards slow. Here's how to keep it snappy:

### Optimisation 1: Use Summary Tables for Heavy Visuals

❌ **Slow:** Location bar chart pulling from Main_Data (50k rows), computing
`COUNT()` and `AVG()` for each location on every interaction.

✅ **Fast:** Location bar chart pulling from Location_Summary (93 rows) which
is pre-aggregated. No computation needed.

**Implementation:** For location-level charts, always use `Location_Summary`
as the data source, not `Main_Data`.

### Optimisation 2: Limit Top N in Visuals

Every visual that shows "all locations" forces PBI to render 93+ data points.
Use Top N filters:
- Location charts: Top 15 or Top 20
- Cuisine charts: Top 15
- Matrix rows: Maximum 20

Add Top N filter:
- Visual Filters pane → Add field → filter type: Top N → Show items: Top 15

### Optimisation 3: Avoid Bidirectional Relationships on Large Tables

If you notice slowness, change `Main_Data → Location_Summary` relationship
to **Single** direction (Main → Location only). You lose some cross-filter
interactivity but gain significant speed.

### Optimisation 4: Reduce Visual Count Per Page

**Target:** Maximum 8-10 visuals per page.
More visuals = more DAX evaluated = slower page load.
Our 6-page design stays within this limit.

### Optimisation 5: Disable Auto Date/Time

Power BI automatically creates hidden date tables for every date column.
We don't have date columns, but check:
File → Options → Current File → Data Load → Auto date/time → OFF

### Optimisation 6: Disable Visual Interactions You Don't Need

Not every visual needs to cross-filter every other visual.
Format → Edit Interactions → Set to "None" for visuals that don't
benefit from cross-filtering (e.g., KPI cards in some contexts).

---

## Step 7.11 — Troubleshooting {#step-711}

### Problem 1: Map Visual Not Showing

**Symptom:** Blank/grey box where map should be.

**Cause A:** Map visuals disabled in options.
**Fix:** File → Options → Security → Map and Filled Map visuals: ✅ Enable

**Cause B:** Location column not recognised as geographic.
**Fix:**
1. Click `Location_Summary[Location]` in Fields panel
2. Column tools ribbon → Data category: City
3. Also set `City` column → Data category: City
4. `Country` column → Data category: Country
5. `State` column → Data category: State or Province

**Cause C:** Latitude/Longitude values are blank.
**Fix:** Check the Python export — ensure `build_location_summary()` populates
lat/lon. Add `Latitude` and `Longitude` to map visual's Latitude/Longitude fields.

---

### Problem 2: Relationship Error — "This relationship... creates ambiguity"

**Symptom:** Power BI refuses to create a relationship or shows an error icon.

**Cause:** You have two tables that both have a column called "Location" and
you're trying to connect both to Main_Data. If there's a path between the
two dimension tables through Main_Data, PBI flags ambiguity.

**Fix:** Check that Cuisine_Summary, Location_Summary, RestType_Summary
are ONLY connected to Main_Data, not to each other.

---

### Problem 3: Cost Bucket Appears in Wrong Order

**Symptom:** Cost Bucket shows "Budget → Luxury → Mid → Premium → Upscale"
(alphabetical instead of price order).

**Fix:**
1. Select `Main_Data[Cost Bucket]` in Fields panel
2. Column tools → Sort by column → Select `Cost Bucket Order`
3. If `Cost Bucket Order` doesn't exist, create a calculated column:
   ```dax
   Cost Bucket Sort =
   SWITCH('Main_Data'[Cost Bucket],
     "Budget (≤300)", 1, "Mid (301-600)", 2,
     "Premium (601-1000)", 3, "Upscale (1001-1500)", 4, "Luxury (>1500)", 5, 9)
   ```

---

### Problem 4: Slicers Not Filtering Visuals from Other Tables

**Symptom:** Selecting a location in the Main_Data slicer doesn't filter
a visual built from Location_Summary.

**Cause:** Cross-filter direction is Single (not Both) OR relationship doesn't exist.

**Fix:**
1. Model view → Double-click the relationship line
2. Cross filter direction: **Both**
3. Click OK
4. Test by selecting a location — Location_Summary visual should update

---

### Problem 5: DAX Measure Shows Error or Blank

**Symptom:** Measure card shows a red circle or blank value.

**Common causes and fixes:**

| Error | Cause | Fix |
|-------|-------|-----|
| Division by zero | Denominator can be 0 | Add 3rd argument to DIVIDE() |
| BLANK | No data in filter context | Use IF(ISBLANK([measure]), 0, [measure]) |
| Data type mismatch | Comparing text to number | Ensure columns are correctly typed |
| Circular reference | Measure references itself | Check for circular measure chains |

---

### Problem 6: Export to PDF Cuts Off Visuals

**Symptom:** PDF shows partial visuals or cuts off on the right.

**Fix:**
- Canvas size must match PDF page size
- For A4 landscape: Width 1169, Height 827
- For HD landscape: Width 1920, Height 1080
- Ensure no visual extends beyond canvas boundaries (select all → check alignment)

---

## Interview Talking Points {#interview}

When a recruiter or hiring manager asks about your Power BI dashboard:

### "Walk me through your dashboard design decisions."

> "I built a 6-page dashboard following a narrative arc: starting with
> the executive overview (what's the big picture?), drilling into location
> and cuisine intelligence, then price-rating relationships, then service
> models, and finishing with strategic recommendations.
>
> For the data model, I used a star schema — one fact table (Main_Data with
> 50k rows) surrounded by three dimension tables. I pre-aggregated location,
> cuisine, and restaurant-type summaries in Python before export, so heavy
> visuals use 93-row or 89-row tables instead of the 50k fact table.
> This keeps every visual snappy under 1 second.
>
> I wrote 25 DAX measures covering KPIs, percentages, conditional labels,
> market share calculations using ALL() to escape filter context, and composite
> metrics like Opportunity Score and Value-for-Money."

### "What is DAX and how did you use CALCULATE()?"

> "DAX is Power BI's formula language. CALCULATE() is its most powerful function —
> it evaluates an expression inside a modified filter context.
>
> For example, my Online Order % measure: `CALCULATE(COUNTROWS(Main_Data),
> Online_Order = 'Yes')`. Without CALCULATE, COUNTROWS would count everything.
> CALCULATE lets me add the condition that online order must be Yes, while
> still respecting any external filters from slicers. It's the mechanism that
> makes every metric in the dashboard interactive.
>
> I also used ALL() inside CALCULATE for measures like Market Share%, which
> needs to compute totals across all locations — ignoring the location filter
> context — and divide the current selection into it."

### "How did you ensure the dashboard performs well with 50k rows?"

> "Three main strategies. First, pre-aggregation in Python: summary tables
> for locations and cuisines have 93 and 89 rows respectively — visuals
> use these instead of scanning 50,000 rows every time.
>
> Second, I used star schema relationships with controlled cross-filter
> directions — bidirectional only where needed, avoiding circular paths.
>
> Third, I limited Top N filters on all multi-item visuals to 15-20 items,
> which reduces rendering time without losing meaningful insights."

---

## Quick Reference — DAX Cheat Sheet

```
COUNTROWS(table)                    → Count rows in table/filter context
AVERAGE(column)                     → Mean, ignores blanks
MEDIANX(table, expression)          → Median value
SUM(column)                         → Sum, ignores blanks
DIVIDE(num, denom, alternate)       → Safe division
CALCULATE(expr, filter1, filter2)   → Evaluate expr in modified filter context
ALL(table/column)                   → Remove all filters (escape context)
FILTER(table, condition)            → Return filtered table
SWITCH(TRUE(), cond1, res1, ...)    → Multi-condition if-else
SELECTEDVALUE(column)               → Value when exactly one is selected
HASONEVALUE(column)                 → TRUE if exactly one value selected
VAR name = expr  RETURN expr2       → Variable assignment
FORMAT(value, "format_string")      → Format as string
TOPN(N, table, expression, order)   → Return top N rows
SUMMARIZE(table, group_col, ...)    → Group-by summary table
ADDCOLUMNS(table, "name", expr)     → Add calculated column to table
```

---

*Jai Bharat Mata 🇮🇳 | Built with data, discipline, and devotion 🙏*

*Guide version 2.0 | Zomato Bangalore Analysis Portfolio Project*
