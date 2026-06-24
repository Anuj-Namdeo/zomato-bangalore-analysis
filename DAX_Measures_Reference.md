# DAX Measures Complete Reference
## Zomato Bangalore Restaurant Analysis — Power BI Dashboard
### All 25 measures, grouped by purpose, with line-by-line explanations

---

## How to Use This File

1. Open Power BI Desktop with your data loaded
2. Create a blank table named `_Measures` (Enter Data, leave empty, click Load)
3. Right-click `_Measures` → New Measure
4. Paste each DAX formula
5. Press Enter to confirm

Keeping measures in `_Measures` table keeps Fields panel clean.

---

## GROUP A — CORE COUNT & AGGREGATE MEASURES

### M01: Total Restaurants
```dax
Total Restaurants =
COUNTROWS('Main_Data')
```
> Counts every row in Main_Data under current filter context.
> This is the foundation measure used in almost every other calculation.

---

### M02: Average Rating
```dax
Average Rating =
AVERAGEX(
    FILTER(
        'Main_Data',
        NOT(ISBLANK('Main_Data'[Rate Numeric]))
    ),
    'Main_Data'[Rate Numeric]
)
```
> - `FILTER(table, condition)` → creates a filtered version of Main_Data
>   where Rating is not blank
> - `AVERAGEX(table, expression)` → iterates that filtered table, computes average
> - Explicitly excludes unrated restaurants (Rate Numeric is blank for NEW restaurants)

---

### M03: Median Cost For Two
```dax
Median Cost =
MEDIANX('Main_Data', 'Main_Data'[Approx Cost])
```
> Uses median because cost has extreme outliers (luxury restaurants).
> Median is more robust than AVERAGE for skewed distributions.

---

### M04: Total Votes
```dax
Total Votes =
SUM('Main_Data'[Votes])
```

---

### M05: Average Votes Per Restaurant
```dax
Avg Votes per Restaurant =
DIVIDE(
    [Total Votes],
    [Total Restaurants],
    0           -- return 0 if Total Restaurants = 0 (avoids division error)
)
```
> Composes M01 and M04. Shows average engagement level.
> Compare this across locations to find demand hotspots.

---

### M06: Median Rating
```dax
Median Rating =
MEDIANX(
    FILTER('Main_Data', NOT(ISBLANK('Main_Data'[Rate Numeric]))),
    'Main_Data'[Rate Numeric]
)
```

---

## GROUP B — PERCENTAGE & RATIO MEASURES

### M07: Online Order Percentage
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
> - `CALCULATE()` evaluates COUNTROWS with an ADDED filter condition
> - The added filter (`Online Order = "Yes"`) combines with any existing
>   slicer filters — so if user selects Koramangala, this shows
>   Koramangala's online order %, not the whole city's
> - `* 100` converts decimal to percentage

---

### M08: Table Booking Percentage
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

### M09: High Rated Percentage
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
> Denominator = ONLY restaurants WITH a rating (not all restaurants).
> Unrated restaurants should not dilute the high-rated percentage.
> This is a deliberate analytical decision — document it in your interview.

---

### M10: Full Service Percentage (Both Online + Booking)
```dax
Full Service % =
DIVIDE(
    CALCULATE(
        COUNTROWS('Main_Data'),
        'Main_Data'[Online Order] = "Yes",
        'Main_Data'[Book Table]   = "Yes"
    ),
    [Total Restaurants],
    0
) * 100
```
> Multiple conditions in CALCULATE are combined with AND logic.
> "Online Order = Yes AND Book Table = Yes" simultaneously.

---

### M11: Market Share Percentage (for location visuals)
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
> - `ALL('Main_Data'[Location])` removes all location filters from context
> - `CALCULATE([Total Restaurants], ALL(...))` = count across ALL locations
>   regardless of what location filter is active
> - Dividing gives % of current location vs total
> - Critical concept: ALL() is how you "break out" of filter context

---

### M12: Budget Segment Percentage
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

### M13: Rated Restaurants Percentage
```dax
Rated % =
DIVIDE(
    CALCULATE(
        COUNTROWS('Main_Data'),
        NOT(ISBLANK('Main_Data'[Rate Numeric]))
    ),
    [Total Restaurants],
    0
) * 100
```
> Shows what % of restaurants have received any rating (not NEW).

---

## GROUP C — COMPARISON & DELTA MEASURES

### M14: Rating vs City Average
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
> - `VAR` declares a named variable (calculated once, reused in RETURN)
> - `ALL()` on multiple columns removes those filters completely
> - `CityAvg` = unfiltered average across entire dataset
> - `RETURN` specifies what the measure evaluates to
> - Positive = above city average, Negative = below
> Used in location table to show performance vs benchmark

---

### M15: Online vs Offline Rating Gap
```dax
Online vs Offline Rating Gap =
VAR OnlineRating =
    CALCULATE(
        [Average Rating],
        'Main_Data'[Online Order] = "Yes"
    )
VAR OfflineRating =
    CALCULATE(
        [Average Rating],
        'Main_Data'[Online Order] = "No"
    )
RETURN
    OnlineRating - OfflineRating
```
> If this returns 0.13, online-ordering restaurants average 0.13 points higher.
> Used on Page 5 as the key "Online Impact" insight.

---

## GROUP D — SCORING & COMPOSITE MEASURES

### M16: Opportunity Score
```dax
Opportunity Score =
VAR AvgVotes  = AVERAGEX('Main_Data', 'Main_Data'[Votes])
VAR RestCount = [Total Restaurants]
VAR AvgRating = [Average Rating]
RETURN
    DIVIDE(AvgVotes, RestCount, 0) * AvgRating
```
> Formula: (avg_votes / restaurant_count) × avg_rating
> High demand-per-restaurant × quality indicator = opportunity
> Used on Page 6 strategic recommendations

---

### M17: Value For Money Score
```dax
Value For Money Score =
DIVIDE(
    [Average Rating],
    LOG([Median Cost] + 1, 10),
    0
)
```
> LOG([Median Cost] + 1, 10) = log base-10 of cost
> This dampens cost differences (₹500 vs ₹1000 is less impactful than ₹50 vs ₹100)
> Higher score = better rating per (log) rupee spent
> +1 prevents LOG(0) error if cost somehow equals 0

---

### M18: Demand Supply Ratio
```dax
Demand Supply Ratio =
DIVIDE(
    [Avg Votes per Restaurant],
    LOG([Total Restaurants] + 1, 10),
    0
)
```
> High votes per restaurant relative to how many restaurants exist.
> Used alongside Opportunity Score for deeper location analysis.

---

## GROUP E — DYNAMIC LABEL & STATUS MEASURES

### M19: Rating Status Label
```dax
Rating Status =
SWITCH(
    TRUE(),
    [Average Rating] >= 4.2, "⭐ Excellent",
    [Average Rating] >= 4.0, "✅ High Quality",
    [Average Rating] >= 3.7, "📊 Above Average",
    [Average Rating] >= 3.5, "➡️ Average",
    [Average Rating] >= 3.0, "⚠️ Below Average",
    NOT(ISBLANK([Average Rating])), "❌ Poor",
    "— Not Rated"
)
```
> Dynamic text label based on the current rating value.
> Used in a Card visual to show qualitative status alongside the number.

---

### M20: Rating Color Code
```dax
Rating Color =
SWITCH(
    TRUE(),
    [Average Rating] >= 4.0, "#27AE60",
    [Average Rating] >= 3.5, "#F39C12",
    [Average Rating] >= 3.0, "#E67E22",
    NOT(ISBLANK([Average Rating])), "#E74C3C",
    "#BDC3C7"
)
```
> Returns hex color string for conditional formatting.
> Apply via: Format visual → Data colors → Conditional formatting → Field value

---

### M21: Cost Tier Label
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

---

### M22: Selected Location Display
```dax
Selected Location =
IF(
    HASONEVALUE('Main_Data'[Location]),
    SELECTEDVALUE('Main_Data'[Location]),
    "All Locations (" & FORMAT([Total Restaurants], "#,##0") & " restaurants)"
)
```
> - `HASONEVALUE()` = TRUE when exactly one location is selected
> - `SELECTEDVALUE()` = returns that one selected value
> - Otherwise returns "All Locations (51,000 restaurants)"
> Used in page titles for dynamic header text

---

### M23: Service Mix Summary
```dax
Service Mix =
"Online: " & FORMAT([Online Order %], "0.0") & "%" &
" | Booking: " & FORMAT([Table Booking %], "0.0") & "%" &
" | Full: " & FORMAT([Full Service %], "0.0") & "%"
```
> Concatenates three percentages into one readable label string.
> Power BI's `&` operator concatenates strings.
> `FORMAT(number, "pattern")` formats number as string.

---

## GROUP F — ADVANCED ANALYTICS MEASURES

### M24: Votes Concentration (Top 10% Share)
```dax
Top 10pct Vote Share =
VAR TotalRests = CALCULATE(COUNTROWS('Main_Data'), ALL('Main_Data'))
VAR TopNCount  = ROUNDUP(TotalRests * 0.1, 0)
VAR TopVotes   =
    CALCULATE(
        SUM('Main_Data'[Votes]),
        TOPN(
            TopNCount,
            ALL('Main_Data'),
            'Main_Data'[Votes],
            DESC
        )
    )
RETURN
DIVIDE(TopVotes, [Total Votes], 0) * 100
```
> Shows what % of all votes go to the top 10% of restaurants.
> High value (e.g., 70%) confirms Pareto effect — viral restaurants dominate.
> `TOPN(N, table, expression, direction)` returns top N rows.
> `ALL('Main_Data')` removes all filters to operate on full dataset.

---

### M25: Market Gap Cuisine Count
```dax
Market Gap Cuisines =
CALCULATE(
    COUNTROWS('Cuisine_Summary'),
    'Cuisine_Summary'[Market_Gap_Flag] = "Gap Opportunity"
)
```
> Counts cuisines classified as market gaps (high rating, low count).
> Used on Page 6 as a KPI card.

---

## Quick Lookup: Measure → Page Mapping

| Measure | P1 | P2 | P3 | P4 | P5 | P6 |
|---------|----|----|----|----|----|----|
| Total Restaurants | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Average Rating | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Median Cost | ✅ | | | ✅ | | |
| Total Votes | ✅ | ✅ | | | ✅ | |
| Avg Votes per Restaurant | | ✅ | | | | ✅ |
| Online Order % | ✅ | ✅ | | | ✅ | |
| Table Booking % | | | | | ✅ | |
| High Rated % | ✅ | | | ✅ | | |
| Full Service % | | | | | ✅ | |
| Market Share % | | ✅ | | | | |
| Rating vs City Avg | | ✅ | | | | |
| Online vs Offline Gap | | | | | ✅ | ✅ |
| Opportunity Score | | ✅ | | | | ✅ |
| Value For Money Score | | | | ✅ | | ✅ |
| Rating Status Label | ✅ | | | | | |
| Rating Color | ✅ | ✅ | ✅ | ✅ | | |
| Cost Tier Label | | | | ✅ | | |
| Selected Location | | ✅ | | | | |
| Top 10% Vote Share | | | | | | ✅ |
| Market Gap Cuisines | | | ✅ | | | ✅ |

---

*Jai Bharat Mata 🇮🇳 | Hare Krishna 🙏*
