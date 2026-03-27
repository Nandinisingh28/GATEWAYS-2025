# GATEWAYS 2025 — National Level Fest Analytics Platform

An interactive **Streamlit** web application that provides data-driven insights for the GATEWAYS 2025 national-level fest organizing team. The dashboard analyzes participation trends, feedback sentiment, revenue generation, and more — all through rich, interactive visualizations.

---

## Features

### 1. Participation Trend Analysis (India Map + Charts)
- **Interactive India Map** — Choropleth visualization of state-wise participant distribution across India using live GeoJSON data.
- **State Leaderboard** — Ranked listing of states by number of participants with progress bars.
- **Revenue by State** — Bar chart showing revenue generated from each state.
- **Event-wise Participation** — Donut chart and horizontal bar chart showing the distribution of participants across events.
- **Individual vs Group Breakdown** — Grouped bar chart comparing individual and group participation by event.
- **College-wise Participation** — Horizontal bar chart with color-coded average ratings and a ranked college leaderboard.
- **Heatmap** — College × Event participation matrix.
- **Treemap** — Visual representation of college participation share.

### 2. Feedback & Rating Analysis
- **Rating Distribution** — Bar chart visualizing the spread of participant ratings (3–5 stars).
- **Violin Plot** — Rating distribution comparison across individual and group event types.
- **Feedback Frequency** — Horizontal bar chart of the most common feedback phrases, color-coded by sentiment.
- **Sentiment Analysis** — Donut chart splitting feedback into Positive vs Needs Improvement categories using keyword-based classification.
- **Word Cloud** — Visual representation of most frequent feedback terms.
- **Average Rating by State** — Bar chart with an overall average reference line.

### 3. Executive Dashboard
A unified view combining all key metrics and charts:
- **KPI Row** — Total participants, states, events, average rating, and total revenue at a glance.
- **Participation Trends** — Side-by-side event-wise and state-wise participation charts.
- **Top 10 Colleges** — Bar chart colored by average rating.
- **India Map + Rating/Sentiment** — Map alongside rating distribution and sentiment split.
- **Event Type Breakdown** — Individual vs Group participation with per-event average ratings.
- **Revenue & Word Cloud** — State-wise revenue chart alongside a feedback word cloud.
- **Summary Insights** — Key takeaways such as top state, most popular event, top college, and revenue totals.

### Sidebar Filters
- **State** — Filter by a specific state or view all.
- **Event** — Filter by a specific event or view all.
- **Event Type** — Filter by Individual, Group, or all.
- **Rating** — Multi-select to filter by rating values (3, 4, 5).

---

## Tech Stack

| Technology   | Purpose                                      |
|-------------|----------------------------------------------|
| **Streamlit**   | Web application framework                    |
| **Pandas**      | Data loading, manipulation, and aggregation  |
| **Plotly**      | Interactive charts (bar, pie, heatmap, map, treemap, violin) |
| **Matplotlib**  | Word cloud rendering                         |
| **WordCloud**   | Generating feedback word clouds              |
| **Requests**    | Fetching India GeoJSON boundary data         |

---

## Project Structure

```
ETE/
├── app.py                                 # Main Streamlit application
├── C5-FestDataset - fest_dataset.csv      # Fest participation dataset
├── requirements.txt                       # Python dependencies
└── README.md                              # Project documentation
```

---

## Dataset

The application uses `C5-FestDataset - fest_dataset.csv` containing the following fields:

| Column            | Description                          |
|-------------------|--------------------------------------|
| Student Name      | Participant's name                   |
| College           | Participant's college                |
| State             | State the participant is from        |
| Event Name        | Name of the fest event               |
| Event Type        | Individual or Group                  |
| Amount Paid       | Registration fee paid (in Rs.)       |
| Rating            | Participant's rating (3–5)           |
| Feedback on Fest  | Text feedback from the participant   |

---

## Installation & Setup

### Prerequisites
- Python 3.8 or above

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/Nandinisingh28/GATEWAYS-2025.git
   cd GATEWAYS-2025
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run app.py
   ```

4. Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Screenshots

| Tab | Description |
|-----|-------------|
| **India Map** | Interactive choropleth map with state leaderboard and revenue chart |
| **Event Analysis** | Donut chart, event bar charts, individual vs group breakdown, and rating analysis |
| **College Insights** | College participation bar chart, heatmap, and treemap |
| **Feedback & Ratings** | Rating distribution, violin plot, sentiment analysis, and word cloud |
| **Dashboard** | Consolidated executive view with all key metrics and visualizations |

---

## Course Information

**Subject:** Advanced Python Programming  
**Assessment:** End Term Examination  
**Topic:** StreamLit App Development — GATEWAYS 2025 National Level Fest  

### Question Mapping

| S.No | Component | CO | RBT Level |
|------|-----------|-----|-----------|
| 1 | Analysis of participation trends (event-wise, college-wise) with India map visualization | CO1 | L4 (Analyze) |
| 2 | Analysis of participant text feedback and ratings | CO4 | L4 (Analyze) |
| 3 | Interactive and user-friendly dashboard with actionable insights | CO2 | L5 (Evaluate) |

---

## License

This project is developed as part of an academic assessment and is intended for educational purposes.

---

> **Built with ❤️ using Streamlit**
