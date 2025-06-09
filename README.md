# 📊 Production and Quality Performance Dashboard

An interactive dashboard built with **Streamlit** to monitor and analyze production and quality performance in industries, featuring dynamic visualizations and customizable filters.

---

## 🚀 Features

- **Filtering by date, shift, status, and severity** for detailed data analysis.  
- Graph comparing **planned production vs. actual production**.
- Downtime and available time by month charts.
- Key production KPIs: **OEE, Performance, Availability, and Quality** displayed with half-donut charts.  
- Analysis of non-conformities with Pareto and severity charts.  
- Visualization of affected product distribution and customer geographic distribution (world map).  
- Organized interface with tabs to separate production and quality views for easy navigation.

---

## 📁 File Structure

- `production_data.csv` — Production data (tab-separated).  
- `occurences_data.csv` — Non-conformities/occurrences data (tab-separated).
- `ProductionData.ipynb` — Jypter Notebook to generate data.
- `KPI_Dashboard.py` — Main Streamlit application code.

---

## 🔧 Technologies Used

- Python  
- Streamlit  
- Pandas  
- Plotly (Express and Graph Objects)  

---

## 💻 How to Run Locally

1. Clone the repository:

```bash
git clone https://github.com/your-username/your-repository.git
cd your-repository
```

2. (Optional but recommended) Create and activate a virtual environment:

```
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```pip install streamlit pandas plotly matplotlib```

4. Run the app from the terminal or the command prompt

```streamlit run app.py```

---

## 📊 Data

- CSV files should be placed in the same folder as the script, with these characteristics:
- Separator: tab (\t)
- Production data: columns like Date, Shift, Planned_Quantity, Produced_Quantity, OEE, Performance, Availability, Quality, Downtime_Minutes, Available_Time_Minutes.
- Occurrences data: columns like date, status, severity, type_nonconformity, product, customer.

---

## 🤝 Contributions
Contributions are welcome! Feel free to open issues or submit pull requests.
