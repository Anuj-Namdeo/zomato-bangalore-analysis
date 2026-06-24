# 🍽️ Zomato Bangalore Restaurant Analysis
### Data-Driven Insights for the Bangalore Food Industry

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.2-green?logo=pandas)
![Power BI](https://img.shields.io/badge/PowerBI-Dashboard-yellow?logo=powerbi)
![SQL](https://img.shields.io/badge/SQL-25+_Queries-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📌 Project Summary

A production-grade end-to-end data analysis of **51,717 restaurants** on Zomato's Bangalore platform — covering location intelligence, cuisine trends, pricing strategy, online ordering adoption, and rating dynamics.

**Business Context:** Helping new and existing restaurants in Bangalore make data-driven decisions on location selection, pricing, service offerings, and cuisine positioning.

---

## 🎯 Key Business Questions Answered

| # | Question | Method |
|---|----------|--------|
| 1 | Which areas have highest restaurant density? | Aggregation + Bar chart |
| 2 | Does online ordering correlate with better ratings? | T-Test + Violin plot |
| 3 | What is the price-rating sweet spot? | Binning + Dual-axis chart |
| 4 | Which cuisines command premium pricing? | GroupBy + Horizontal bar |
| 5 | Does table booking indicate quality? | Chi-square + Multi-metric bar |
| 6 | Which locations offer best value for money? | Composite score + Scatter quadrant |
| 7 | Where should a new restaurant open? | Opportunity scoring |
| 8 | Which restaurant segments exist naturally? | KMeans clustering |
| 9 | What drives virality (votes)? | Pareto + Percentile analysis |
| 10 | Which cuisines are underserved but highly rated? | Market gap analysis |
| ... | 15 more business questions | See notebooks/04_Business_Insights.ipynb |

---

## 📊 Key Findings

- **Top 5 areas** (Koramangala, BTM, Indiranagar, Jayanagar, JP Nagar) hold **~38%** of all restaurants
- Restaurants with **online ordering** have statistically significantly higher ratings (p < 0.05)
- **Mid-range (₹300–₹600)** segment has highest count + competitive ratings — most crowded market
- **Table booking** restaurants average **₹200+ more** per meal and 0.3 higher rating — premium signal
- Top 1% of restaurants by votes capture **~40%** of all vote traffic (Pareto principle in action)
- **Continental and Italian** cuisines are under-represented but command premium ratings

---

## 🗂️ Project Structure

```
Zomato_Bangalore_Analysis/
├── data/
│   ├── raw/              # zomato.csv (download from Kaggle)
│   └── cleaned/          # zomato_cleaned.csv, zomato_powerbi.xlsx
├── notebooks/
│   ├── 01_Data_Inspection.ipynb
│   ├── 02_Data_Cleaning.ipynb
│   ├── 03_EDA.ipynb
│   └── 04_Business_Insights.ipynb
├── src/
│   ├── utils.py           # Shared utilities, logging, paths
│   ├── data_cleaning.py   # Full cleaning pipeline
│   ├── preprocessing.py   # Feature engineering, validation
│   ├── eda.py             # 10 EDA visualizations
│   ├── business_analysis.py  # 25 business questions
│   ├── visualization.py   # Advanced composites + Folium map
│   └── powerbi_export.py  # Excel export for Power BI
├── dashboard/             # Power BI build guide
├── sql/
│   └── zomato_analysis.sql  # 25 advanced SQL queries
├── images/                # All generated charts
├── reports/               # Final report PDF
├── guide.txt              # 📋 COMPLETE IMPLEMENTATION MANUAL
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/zomato-bangalore-analysis.git
cd zomato-bangalore-analysis

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Place dataset
# Download from: https://www.kaggle.com/datasets/himanshupoddar/zomato-bangalore-restaurants
# Place zomato.csv in data/raw/

# 5. Run cleaning pipeline
python -m src.data_cleaning

# 6. Run feature engineering + export
python -m src.preprocessing
python -m src.powerbi_export

# 7. Open notebooks sequentially
jupyter notebook
```

---

## 📈 Dashboard Preview

> Power BI dashboard with 6 pages:
> - **Overview** — KPI cards + restaurant map
> - **Location Analysis** — Density heatmap + top areas
> - **Cuisine Insights** — Premium pricing + rating matrix
> - **Price & Rating** — Sweet spot analysis + segments
> - **Online Adoption** — Service penetration by area
> - **Executive Summary** — Strategic recommendations

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| Data Manipulation | Pandas 2.2, NumPy 1.26 |
| Visualization | Matplotlib 3.9, Seaborn 0.13, Plotly 5.22 |
| Geospatial | Folium 0.16, GeoPy 2.4 |
| Statistical Analysis | SciPy 1.13, Statsmodels 0.14 |
| Machine Learning | scikit-learn 1.5 (KMeans clustering) |
| BI Dashboard | Microsoft Power BI Desktop |
| Database | PostgreSQL / SQLite |
| IDE | VS Code + Jupyter |

---

## 💼 Business Recommendations

1. **Location Strategy**: Target Whitefield and Hebbal — high opportunity score, under-served relative to engagement signals
2. **Online Ordering**: Mandatory for new entrants — 60%+ of high-rated restaurants use it
3. **Pricing**: ₹400–₹700 mid-range is most competitive; go premium (₹900+) only with differentiated quality
4. **Cuisine Gap**: Continental, Mediterranean, Lebanese cuisines show high ratings but low competition
5. **Quality Signal**: Restaurants scoring below 3.5 despite high vote counts need operational audit

---

## 📄 Dataset

- **Source**: [Kaggle — Zomato Bangalore Restaurants](https://www.kaggle.com/datasets/himanshupoddar/zomato-bangalore-restaurants)
- **Size**: ~51,717 rows × 17 columns (raw)
- **Cleaned**: ~48,000 rows × 22 columns (after cleaning + feature engineering)

---

## 👤 Author

**[Your Name]**  
Data Analyst | Python • SQL • Power BI  
[LinkedIn](https://linkedin.com/in/yourprofile) | [GitHub](https://github.com/yourusername) | [Portfolio](https://yourportfolio.com)

---

## 📜 License

MIT License — free to use, modify, and distribute with attribution.

---

*Built as a portfolio project demonstrating end-to-end data analytics workflow: ingestion → cleaning → EDA → business insights → dashboard → recommendations.*
