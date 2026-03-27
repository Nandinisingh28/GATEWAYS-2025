import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import requests

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GATEWAYS 2025",
    page_icon="G",
    layout="wide",
    initial_sidebar_state="expanded",
)

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="sans-serif", color="#000000", size=12),
    margin=dict(t=45, b=20, l=10, r=10),
    colorway=["#00d4ff", "#7c3aed", "#ff6b35", "#22c55e", "#f59e0b", "#ec4899", "#06b6d4"],
)

CYAN   = "#00d4ff"
PURPLE = "#7c3aed"
ORANGE = "#ff6b35"
GREEN  = "#22c55e"
AMBER  = "#f59e0b"

TITLE_FONT = dict(size=14, color="#000000")

def ct(text: str) -> dict:
    """Return a Plotly title dict with consistent font styling."""
    return dict(text=text, font=TITLE_FONT)


STATE_COORDS = {
    "Kerala":        (10.85,  76.27),
    "Tamil Nadu":    (11.13,  78.66),
    "Karnataka":     (15.32,  75.71),
    "Telangana":     (17.85,  78.00),
    "Maharashtra":   (19.75,  75.71),
    "Delhi":         (28.61,  77.21),
    "Uttar Pradesh": (26.85,  80.95),
    "Rajasthan":     (27.02,  74.22),
    "Gujarat":       (22.26,  71.19),
}

# ─────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("C5-FestDataset - fest_dataset.csv")
    df.columns = df.columns.str.strip()
    return df

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_india_geojson():
    """Fetch India state boundaries GeoJSON. Returns None on failure."""
    urls = [
        
        "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson",

        "https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/master/Indian_States",
    ]
    for url in urls:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data:
                    return data
        except Exception:
            continue
    return None


df = load_data()

def build_india_map(state_counts, geojson, height=600):
    map_layout = {**CHART_LAYOUT, "margin": dict(t=10, b=0, l=0, r=0)}

    if geojson:
        fig = px.choropleth(
            state_counts,
            geojson=geojson,
            locations="State",
            featureidkey="properties.NAME_1",
            color="Participants",
            hover_name="State",
            hover_data={"Participants": True, "Avg_Rating": True, "Revenue": True,
                        "lat": False, "lon": False},
            color_continuous_scale=[[0, "#0d1540"], [0.5, CYAN], [1.0, PURPLE]],
        )
        fig.update_geos(fitbounds="locations", visible=False, bgcolor="rgba(0,0,0,0)")
    else:
        fig = go.Figure()
        fig.add_trace(go.Scattergeo(
            lon=state_counts["lon"],
            lat=state_counts["lat"],
            text=state_counts["State"],
            mode="markers+text",
            textposition="top center",
            textfont=dict(color="#000000", size=11),
            marker=dict(
                size=state_counts["Participants"] / state_counts["Participants"].max() * 45 + 10,
                color=state_counts["Participants"],
                colorscale=[[0, "#1a3a7a"], [0.5, CYAN], [1.0, PURPLE]],
                colorbar=dict(
                    title=dict(text="Participants", font=dict(color="#000000")),
                    tickfont=dict(color="#000000"),
                ),
                symbol="square",
                line=dict(color=CYAN, width=1.5),
                opacity=0.88,
            ),
            hovertext=[
                f"<b>{r['State']}</b><br>Participants: {r['Participants']}<br>"
                f"Avg Rating: {r['Avg_Rating']}<br>Revenue: Rs.{r['Revenue']:,}"
                for _, r in state_counts.iterrows()
            ],
            hovertemplate="%{hovertext}<extra></extra>",
        ))
        fig.update_layout(
            geo=dict(
                scope="asia",
                center=dict(lat=22, lon=82),
                projection_scale=6.5,
                showland=True, landcolor="rgba(10,20,60,0.9)",
                showocean=True, oceancolor="rgba(5,6,26,1)",
                showcountries=True, countrycolor="rgba(0,212,255,0.2)",
                showcoastlines=True, coastlinecolor="rgba(0,212,255,0.25)",
                bgcolor="rgba(0,0,0,0)",
                showsubunits=True, subunitcolor="rgba(0,212,255,0.15)",
            ),
        )

    fig.update_layout(**map_layout, height=height)
    return fig

st.sidebar.title("GATEWAYS 2025")
st.sidebar.caption("National Level Fest · Analytics Hub")
st.sidebar.divider()

st.sidebar.subheader("Filters")

all_states = ["All States"] + sorted(df["State"].unique().tolist())
all_events = ["All Events"] + sorted(df["Event Name"].unique().tolist())
all_types  = ["All Types"]  + df["Event Type"].unique().tolist()

sel_state  = st.sidebar.selectbox("State",      all_states)
sel_event  = st.sidebar.selectbox("Event",      all_events)
sel_type   = st.sidebar.selectbox("Event Type", all_types)
sel_rating = st.sidebar.multiselect("Rating", [3, 4, 5], default=[3, 4, 5])

st.sidebar.divider()

# Apply filters
fdf = df.copy()
if sel_state != "All States":
    fdf = fdf[fdf["State"] == sel_state]
if sel_event != "All Events":
    fdf = fdf[fdf["Event Name"] == sel_event]
if sel_type != "All Types":
    fdf = fdf[fdf["Event Type"] == sel_type]
if sel_rating:
    fdf = fdf[fdf["Rating"].isin(sel_rating)]

st.sidebar.metric("Records Shown", len(fdf),
                  f"{len(fdf) - len(df)} delta" if len(fdf) != len(df) else "Full dataset")
st.sidebar.caption(
    f"Dataset: {len(df)} participants · {df['Event Name'].nunique()} events · {df['State'].nunique()} states"
)

#  HEADER

st.title("GATEWAYS 2025")
st.caption(
    f"National Level Fest · {len(df)} Participants · "
    f"{df['State'].nunique()} States · {df['Event Name'].nunique()} Events"
)
st.divider()


#  KPI ROW

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Participants", f"{len(fdf):,}")
k2.metric("States Represented", fdf["State"].nunique())
k3.metric("Events", fdf["Event Name"].nunique())
avg_r = round(fdf["Rating"].mean(), 2) if len(fdf) else 0
k4.metric("Avg Rating", f"{avg_r} / 5")
k5.metric("Revenue Collected", f"Rs.{fdf['Amount Paid'].sum():,}")

st.divider()

#  TABS
tab1, tab2, tab3, tab4, tab_dash = st.tabs([
    "India Map",
    "Event Analysis",
    "College Insights",
    "Feedback & Ratings",
    "Dashboard",
])
#  TAB 1 — INDIA MAP

with tab1:
    st.subheader("State-wise Participation across India")

    state_counts = fdf.groupby("State").agg(
        Participants=("Student Name", "count"),
        Avg_Rating=("Rating", "mean"),
        Revenue=("Amount Paid", "sum"),
    ).reset_index()
    state_counts["lat"] = state_counts["State"].map(
        lambda s: STATE_COORDS.get(s, (20, 78))[0]
    )
    state_counts["lon"] = state_counts["State"].map(
        lambda s: STATE_COORDS.get(s, (20, 78))[1]
    )
    state_counts["Avg_Rating"] = state_counts["Avg_Rating"].round(2)

    col_map, col_board = st.columns([7, 3])

    with col_map:
        st.subheader("India Participation Map")
        with st.spinner("Fetching India map data, please wait..."):
            geojson = fetch_india_geojson()
        fig_map = build_india_map(state_counts, geojson, height=620)
        st.plotly_chart(fig_map, use_container_width=True)

    with col_board:
        st.subheader("State Leaderboard")
        ranked = state_counts.sort_values("Participants", ascending=False).reset_index(drop=True)
        rank_labels = ["1st", "2nd", "3rd"] + [f"#{i+4}" for i in range(20)]
        board_container = st.container(height=620)
        for i, row in ranked.iterrows():
            pct = row["Participants"] / ranked["Participants"].sum() * 100
            board_container.progress(
                int(pct * 2),
                text=f"**{rank_labels[i]}** {row['State']} — {int(row['Participants'])} ({pct:.1f}%)"
            )

    st.divider()
    st.subheader("Revenue Generated by State")

    fig_rev = go.Figure(go.Bar(
        x=ranked["State"],
        y=ranked["Revenue"],
        marker=dict(
            color=ranked["Revenue"],
            colorscale=[[0, "#1a3a7a"], [0.5, CYAN], [1.0, PURPLE]],
        ),
        text=[f"Rs.{v:,}" for v in ranked["Revenue"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Revenue: Rs.%{y:,}<extra></extra>",
    ))

    fig_rev.update_layout(
        **{**CHART_LAYOUT, "margin": dict(t=60, b=20, l=10, r=10)},
        height=420,
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
    )
    st.plotly_chart(fig_rev, use_container_width=True)

#  TAB 2 — EVENT ANALYSIS
with tab2:
    st.subheader("Event-wise Participation Breakdown")

    event_stats = fdf.groupby("Event Name").agg(
        Participants=("Student Name", "count"),
        Avg_Rating=("Rating", "mean"),
        Revenue=("Amount Paid", "sum"),
        Avg_Fee=("Amount Paid", "mean"),
    ).reset_index().sort_values("Participants", ascending=False)

    c1, c2 = st.columns(2)

    with c1:
        fig_donut = go.Figure(go.Pie(
            labels=event_stats["Event Name"],
            values=event_stats["Participants"],
            hole=0.55,
            marker=dict(
                colors=[CYAN, PURPLE, ORANGE, GREEN, AMBER, "#ec4899", "#06b6d4"],
                line=dict(color="#111", width=2),
            ),
            textinfo="label+percent",
            textposition="inside",
            insidetextorientation="radial",
            automargin=True,
            hovertemplate="<b>%{label}</b><br>%{value} participants (%{percent})<extra></extra>",
        ))
        fig_donut.add_annotation(
            text=f"<b>{len(fdf)}</b><br>Total",
            x=0.5, y=0.5, xref="paper", yref="paper",
            showarrow=False, font=dict(size=18, color=CYAN),
        )
        donut_layout = {**CHART_LAYOUT, "margin": dict(t=45, b=20, l=20, r=120)}
        fig_donut.update_layout(
            **donut_layout,
            title=ct("Participation Share by Event"),
            height=420,
            legend=dict(
                orientation="v",
                x=1.0, y=0.5,
                font=dict(size=11, color="#000000"),
            ),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with c2:
        fig_hbar = go.Figure(go.Bar(
            y=event_stats["Event Name"],
            x=event_stats["Participants"],
            orientation="h",
            marker=dict(color=event_stats["Participants"],
                        colorscale=[[0, "#1a3a7a"], [1, CYAN]]),
            text=event_stats["Participants"],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x} participants<extra></extra>",
        ))
        fig_hbar.update_layout(
            **CHART_LAYOUT,
            title=ct("Participants per Event"),
            height=420,
            xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
            yaxis=dict(showgrid=False, autorange="reversed"),
        )
        st.plotly_chart(fig_hbar, use_container_width=True)

    st.divider()
    st.subheader("Individual vs Group Participation")

    type_breakdown = fdf.groupby(["Event Name", "Event Type"]).size().reset_index(name="Count")
    fig_group = px.bar(
        type_breakdown, x="Event Name", y="Count", color="Event Type",
        barmode="group",
        color_discrete_map={"Individual": CYAN, "Group": ORANGE},
        labels={"Count": "Participants", "Event Name": ""},
    )
    fig_group.update_layout(
        **CHART_LAYOUT,
        title=ct("Individual vs Group by Event"),
        height=320,
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
    )
    st.plotly_chart(fig_group, use_container_width=True)

    st.divider()
    st.subheader("Average Rating per Event")

    colors_list = [CYAN, PURPLE, ORANGE, GREEN, AMBER, "#ec4899", "#06b6d4"]
    fig_rating_event = go.Figure()
    for i, row in event_stats.reset_index(drop=True).iterrows():
        fig_rating_event.add_trace(go.Bar(
            x=[row["Event Name"]], y=[row["Avg_Rating"]],
            name=row["Event Name"],
            marker_color=colors_list[i % len(colors_list)],
            showlegend=False,
            hovertemplate=f"<b>{row['Event Name']}</b><br>Avg Rating: {row['Avg_Rating']:.2f}<extra></extra>",
        ))
    overall_avg = fdf["Rating"].mean()
    fig_rating_event.add_hline(
        y=overall_avg, line_dash="dash", line_color="rgba(255,255,255,0.4)",
        annotation_text=f"Overall avg: {overall_avg:.2f}",
        annotation_font_color="#000000",
    )
    fig_rating_event.update_layout(
        **CHART_LAYOUT,
        height=300,
        yaxis=dict(range=[0, 5.5], showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
    )
    st.plotly_chart(fig_rating_event, use_container_width=True)

    st.divider()
    st.subheader("Event Summary Table")

    display_stats = event_stats.copy()
    display_stats["Avg_Rating"] = display_stats["Avg_Rating"].round(2)
    display_stats["Revenue"]    = display_stats["Revenue"].apply(lambda x: f"Rs.{x:,}")
    display_stats["Avg_Fee"]    = display_stats["Avg_Fee"].apply(lambda x: f"Rs.{x:.0f}")
    display_stats.columns = ["Event", "Participants", "Avg Rating", "Revenue", "Avg Fee"]
    st.dataframe(display_stats, use_container_width=True, hide_index=True)

#  TAB 3 — COLLEGE INSIGHTS
with tab3:
    st.subheader("College-wise Participation")

    college_stats = fdf.groupby("College").agg(
        Participants=("Student Name", "count"),
        Avg_Rating=("Rating", "mean"),
        Revenue=("Amount Paid", "sum"),
        Events_Count=("Event Name", "nunique"),
    ).reset_index().sort_values("Participants", ascending=False)

    c1, c2 = st.columns([3, 2])

    with c1:
        fig_col = go.Figure(go.Bar(
            x=college_stats["Participants"],
            y=college_stats["College"],
            orientation="h",
            marker=dict(
                color=college_stats["Avg_Rating"],
                colorscale=[[0, "#1a3a7a"], [0.5, CYAN], [1, GREEN]],
                colorbar=dict(
                    title=dict(text="Avg Rating", font=dict(color="#000000")),
                    tickfont=dict(color="#000000"),
                ),
            ),
            text=college_stats["Participants"],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Participants: %{x}<extra></extra>",
        ))
        fig_col.update_layout(
            **CHART_LAYOUT,
            title=ct("Participants & Avg Rating by College"),
            height=600,
            yaxis=dict(autorange="reversed", showgrid=False),
            xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
        )
        st.plotly_chart(fig_col, use_container_width=True)

    with c2:
        st.subheader("Top Colleges")
        rank_labels = ["1st", "2nd", "3rd"] + [f"#{i+4}" for i in range(20)]
        for i, row in college_stats.head(10).reset_index(drop=True).iterrows():
            st.metric(
                label=f"{rank_labels[i]} {row['College']}",
                value=f"{int(row['Participants'])} participants",
                delta=f"Rating: {row['Avg_Rating']:.1f} | Rs.{int(row['Revenue']):,}",
            )

    st.divider()
    st.subheader("College x Event Participation Heatmap")

    heat_data  = fdf.groupby(["College", "Event Name"]).size().reset_index(name="Count")
    heat_pivot = heat_data.pivot(index="College", columns="Event Name", values="Count").fillna(0)

    fig_heat = go.Figure(go.Heatmap(
        z=heat_pivot.values,
        x=heat_pivot.columns.tolist(),
        y=heat_pivot.index.tolist(),
        colorscale=[[0, "#05061a"], [0.3, "#0d2060"], [0.7, CYAN], [1, PURPLE]],
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.0f} participants<extra></extra>",
        colorbar=dict(
            title=dict(text="Count", font=dict(color="#000000")),
            tickfont=dict(color="#000000"),
        ),
    ))
    fig_heat.update_layout(
        **CHART_LAYOUT,
        height=450,
        xaxis=dict(tickangle=-20, showgrid=False),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()
    st.subheader("College Participation Treemap")

    fig_tree = px.treemap(
        college_stats,
        path=["College"],
        values="Participants",
        color="Avg_Rating",
        color_continuous_scale=[[0, "#0d1540"], [0.5, CYAN], [1, GREEN]],
        title="Size = Participants · Color = Avg Rating",
    )
    fig_tree.update_layout(**CHART_LAYOUT, height=400)
    fig_tree.update_traces(
        hovertemplate="<b>%{label}</b><br>Participants: %{value}<br>Rating: %{color:.2f}<extra></extra>",
    )
    st.plotly_chart(fig_tree, use_container_width=True)

#  TAB 4 — FEEDBACK & RATINGS
with tab4:
    st.subheader("Participant Feedback & Rating Analysis")

    c1, c2 = st.columns(2)

    with c1:
        rating_counts = fdf["Rating"].value_counts().sort_index()
        labels_map = {3: "3 Stars - Good", 4: "4 Stars - Great", 5: "5 Stars - Excellent"}
        fig_rating = go.Figure(go.Bar(
            x=[labels_map.get(r, str(r)) for r in rating_counts.index],
            y=rating_counts.values,
            marker=dict(color=[ORANGE, CYAN, GREEN], line=dict(color="#111", width=2)),
            text=rating_counts.values,
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
        ))
        fig_rating.update_layout(
            **CHART_LAYOUT,
            title=ct("Rating Distribution"),
            height=340,
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
        )
        st.plotly_chart(fig_rating, use_container_width=True)

    with c2:
        fig_violin = go.Figure()
        for etype, color in [("Individual", CYAN), ("Group", ORANGE)]:
            vals = fdf[fdf["Event Type"] == etype]["Rating"]
            fig_violin.add_trace(go.Violin(
                y=vals,
                name=etype,
                box_visible=True,
                meanline_visible=True,
                fillcolor=color,
                opacity=0.7,
                line_color=color,
                hovertemplate=f"<b>{etype}</b><br>Rating: %{{y}}<extra></extra>",
            ))
        fig_violin.update_layout(
            **CHART_LAYOUT,
            title=ct("Rating Distribution by Event Type (Violin)"),
            height=340,
            yaxis=dict(range=[2, 6]),
        )
        st.plotly_chart(fig_violin, use_container_width=True)

    st.divider()
    st.subheader("Feedback Frequency & Sentiment")

    feedback_counts = fdf["Feedback on Fest"].value_counts().reset_index()
    feedback_counts.columns = ["Feedback", "Count"]

    NEGATIVE_KW = ["improvement", "issue", "poor", "bad", "worst", "timing"]
    feedback_counts["Sentiment"] = feedback_counts["Feedback"].apply(
        lambda x: "Needs Improvement" if any(kw in x.lower() for kw in NEGATIVE_KW) else "Positive"
    )

    c1, c2 = st.columns([3, 2])

    with c1:
        colors_fb = [ORANGE if s == "Needs Improvement" else CYAN
                     for s in feedback_counts["Sentiment"]]
        fig_fb = go.Figure(go.Bar(
            x=feedback_counts["Count"],
            y=feedback_counts["Feedback"],
            orientation="h",
            marker=dict(color=colors_fb),
            text=feedback_counts["Count"],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>",
        ))
        fig_fb.update_layout(
            **CHART_LAYOUT,
            title=ct("Feedback Frequency"),
            height=420,
            yaxis=dict(autorange="reversed", showgrid=False),
            xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
        )
        st.plotly_chart(fig_fb, use_container_width=True)

    with c2:
        pos_n = feedback_counts[feedback_counts["Sentiment"] == "Positive"]["Count"].sum()
        neg_n = feedback_counts[feedback_counts["Sentiment"] == "Needs Improvement"]["Count"].sum()
        total_n = pos_n + neg_n

        fig_sent = go.Figure(go.Pie(
            labels=["Positive", "Needs Improvement"],
            values=[pos_n, neg_n],
            hole=0.55,
            marker=dict(colors=[CYAN, ORANGE], line=dict(color="#111", width=3)),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>%{value} responses<extra></extra>",
        ))
        fig_sent.add_annotation(
            text=f"<b>{pos_n/total_n*100:.0f}%</b><br>Positive",
            x=0.5, y=0.5, xref="paper", yref="paper",
            showarrow=False, font=dict(size=16, color=CYAN),
        )
        fig_sent.update_layout(
            **CHART_LAYOUT,
            title=ct("Sentiment Split"),
            height=280,
        )
        st.plotly_chart(fig_sent, use_container_width=True)

        st.info(
            f"**{pos_n}** of **{total_n}** responses ({pos_n/total_n*100:.1f}%) were positive."
        )
        st.success(
            f"Most common feedback: **\"{feedback_counts.iloc[0]['Feedback']}\"** "
            f"— {feedback_counts.iloc[0]['Count']} mentions"
        )

    st.divider()
    st.subheader("Feedback Word Cloud")

    all_text = " ".join(fdf["Feedback on Fest"].tolist())
    try:
        wc = WordCloud(
            width=900, height=350,
            background_color=None,
            mode="RGBA",
            colormap="cool",
            max_words=80,
            prefer_horizontal=0.7,
        ).generate(all_text)

        fig_wc, ax = plt.subplots(figsize=(12, 4))
        fig_wc.patch.set_alpha(0)
        ax.set_facecolor("none")
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig_wc)
    except Exception as e:
        st.warning(f"Word cloud unavailable: {e}. Run: pip install wordcloud")

    st.divider()
    st.subheader("Average Rating by State")

    state_rating = (
        fdf.groupby("State")["Rating"].mean()
        .reset_index()
        .sort_values("Rating", ascending=False)
    )
    overall_avg  = fdf["Rating"].mean()
    colors_sr    = [GREEN if r >= 4.3 else (CYAN if r >= 4.0 else ORANGE)
                    for r in state_rating["Rating"]]

    fig_sr = go.Figure(go.Bar(
        x=state_rating["State"],
        y=state_rating["Rating"],
        marker=dict(color=colors_sr),
        text=state_rating["Rating"].round(2),
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Avg Rating: %{y:.2f}<extra></extra>",
    ))
    fig_sr.add_hline(
        y=overall_avg, line_dash="dot", line_color="rgba(255,255,255,0.4)",
        annotation_text=f"Overall: {overall_avg:.2f}",
        annotation_font_color="#000000",
    )
    fig_sr.update_layout(
        **CHART_LAYOUT,
        title=ct("Average Rating by State"),
        height=300,
        yaxis=dict(range=[0, 5.5], showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
    )
    st.plotly_chart(fig_sr, use_container_width=True)

    st.divider()
    st.subheader("Key Insights")

    top_state        = df.groupby("State").size().idxmax()
    top_event        = df.groupby("Event Name").size().idxmax()
    top_college      = df.groupby("College").size().idxmax()
    best_rated_event = df.groupby("Event Name")["Rating"].mean().idxmax()
    pct_group        = len(df[df["Event Type"] == "Group"]) / len(df) * 100

    i1, i2, i3 = st.columns(3)
    with i1:
        st.info(f"**Top State:** {top_state} leads with {df[df['State']==top_state].shape[0]} participants.")
        st.info(f"**Most Popular Event:** {top_event} attracted the most registrations.")
    with i2:
        st.info(f"**Top College:** {top_college} sent the highest number of participants.")
        st.info(f"**Best Rated Event:** {best_rated_event} received the highest average rating.")
    with i3:
        st.info(f"**Group Events:** {pct_group:.1f}% of all registrations were group-based.")
        st.info(f"**Total Revenue:** Rs.{df['Amount Paid'].sum():,} collected across all events.")

#  TAB 5 — DASHBOARD

with tab_dash:
    st.header("GATEWAYS 2025 — Executive Dashboard")
    st.caption("All key participation, feedback, and revenue insights in one view")
    st.divider()


    st.subheader("Key Performance Indicators")
    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("Total Participants", f"{len(df):,}")
    d2.metric("States Represented", df["State"].nunique())
    d3.metric("Total Events", df["Event Name"].nunique())
    d4.metric("Avg Rating", f"{df['Rating'].mean():.2f} / 5")
    d5.metric("Total Revenue", f"Rs.{df['Amount Paid'].sum():,}")
    st.divider()

    
    st.subheader("Participation Trends")
    t1, t2 = st.columns(2)

    with t1:
        ev = df.groupby("Event Name")["Student Name"].count().reset_index()
        ev.columns = ["Event", "Participants"]
        ev = ev.sort_values("Participants", ascending=True)
        fig_ev = go.Figure(go.Bar(
            x=ev["Participants"], y=ev["Event"], orientation="h",
            marker=dict(color=ev["Participants"],
                        colorscale=[[0, "#1a3a7a"], [1, CYAN]]),
            text=ev["Participants"], textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x} participants<extra></extra>",
        ))
        fig_ev.update_layout(
            **CHART_LAYOUT,
            title=ct("Event-wise Participation"),
            height=320,
            xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig_ev, use_container_width=True)

    with t2:
        sv = df.groupby("State")["Student Name"].count().reset_index()
        sv.columns = ["State", "Participants"]
        sv = sv.sort_values("Participants", ascending=True)
        fig_sv = go.Figure(go.Bar(
            x=sv["Participants"], y=sv["State"], orientation="h",
            marker=dict(color=sv["Participants"],
                        colorscale=[[0, "#1a3a7a"], [1, PURPLE]]),
            text=sv["Participants"], textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x} participants<extra></extra>",
        ))
        fig_sv.update_layout(
            **CHART_LAYOUT,
            title=ct("State-wise Participation"),
            height=320,
            xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig_sv, use_container_width=True)

    st.subheader("College-wise Participation")
    coll = df.groupby("College").agg(
        Participants=("Student Name", "count"),
        Avg_Rating=("Rating", "mean"),
        Revenue=("Amount Paid", "sum"),
    ).reset_index().sort_values("Participants", ascending=False).head(10)

    fig_coll = go.Figure(go.Bar(
        x=coll["College"], y=coll["Participants"],
        marker=dict(
            color=coll["Avg_Rating"],
            colorscale=[[0, "#1a3a7a"], [0.5, CYAN], [1, GREEN]],
            colorbar=dict(
                title=dict(text="Avg Rating", font=dict(color="#000000")),
                tickfont=dict(color="#000000"),
            ),
        ),
        text=coll["Participants"], textposition="outside",
        hovertemplate="<b>%{x}</b><br>Participants: %{y}<extra></extra>",
    ))
    fig_coll.update_layout(
        **CHART_LAYOUT,
        title=ct("Top 10 Colleges (Color = Avg Rating)"),
        height=320,
        xaxis=dict(tickangle=-20, showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
    )
    st.plotly_chart(fig_coll, use_container_width=True)

    st.divider()


    st.subheader("State-wise Participation on India Map")
    map_col, rate_col = st.columns([3, 2])

    with map_col:
        st.subheader("India Participation Map")
        with st.spinner("⏳ Fetching India map data, please wait..."):
            geojson_d = fetch_india_geojson()  
        state_counts_d = df.groupby("State").agg(
            Participants=("Student Name", "count"),
            Avg_Rating=("Rating", "mean"),
            Revenue=("Amount Paid", "sum"),
        ).reset_index()
        state_counts_d["lat"] = state_counts_d["State"].map(
            lambda s: STATE_COORDS.get(s, (20, 78))[0]
        )
        state_counts_d["lon"] = state_counts_d["State"].map(
            lambda s: STATE_COORDS.get(s, (20, 78))[1]
        )
        state_counts_d["Avg_Rating"] = state_counts_d["Avg_Rating"].round(2)
        fig_dm = build_india_map(state_counts_d, geojson_d, height=420)
        st.plotly_chart(fig_dm, use_container_width=True)

    with rate_col:
        st.subheader("Rating Distribution")
        rc = df["Rating"].value_counts().sort_index()
        lm = {3: "3 - Good", 4: "4 - Great", 5: "5 - Excellent"}
        fig_rd = go.Figure(go.Bar(
            x=[lm.get(r, str(r)) for r in rc.index], y=rc.values,
            marker=dict(color=[ORANGE, CYAN, GREEN], line=dict(color="#111", width=2)),
            text=rc.values, textposition="outside",
            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
        ))
        fig_rd.update_layout(
            **CHART_LAYOUT,
            title=ct("Overall Rating Distribution"),
            height=200,
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
        )
        st.plotly_chart(fig_rd, use_container_width=True)

        st.subheader("Sentiment Split")
        fc = df["Feedback on Fest"].value_counts().reset_index()
        fc.columns = ["Feedback", "Count"]
        NEGATIVE_KW2 = ["improvement", "issue", "poor", "bad", "worst", "timing"]
        fc["Sentiment"] = fc["Feedback"].apply(
            lambda x: "Needs Improvement" if any(kw in x.lower() for kw in NEGATIVE_KW2) else "Positive"
        )
        pos_d = fc[fc["Sentiment"] == "Positive"]["Count"].sum()
        neg_d = fc[fc["Sentiment"] == "Needs Improvement"]["Count"].sum()
        tot_d = pos_d + neg_d
        fig_sd = go.Figure(go.Pie(
            labels=["Positive", "Needs Improvement"],
            values=[pos_d, neg_d],
            hole=0.5,
            marker=dict(colors=[CYAN, ORANGE], line=dict(color="#111", width=2)),
            textinfo="label+percent",
            hovertemplate="<b>%{label}</b><br>%{value} responses<extra></extra>",
        ))
        fig_sd.add_annotation(
            text=f"<b>{pos_d/tot_d*100:.0f}%</b><br>Positive",
            x=0.5, y=0.5, xref="paper", yref="paper",
            showarrow=False, font=dict(size=14, color=CYAN),
        )
        fig_sd.update_layout(
            **CHART_LAYOUT,
            title=ct("Feedback Sentiment"),
            height=220,
        )
        st.plotly_chart(fig_sd, use_container_width=True)

    st.divider()

    st.subheader("Event Type Breakdown & Ratings")
    eg1, eg2 = st.columns(2)

    with eg1:
        type_b = df.groupby(["Event Name", "Event Type"]).size().reset_index(name="Count")
        fig_tg = px.bar(
            type_b, x="Event Name", y="Count", color="Event Type",
            barmode="group",
            color_discrete_map={"Individual": CYAN, "Group": ORANGE},
            labels={"Count": "Participants", "Event Name": ""},
        )
        fig_tg.update_layout(
            **CHART_LAYOUT,
            title=ct("Individual vs Group Participation by Event"),
            height=320,
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
            xaxis=dict(tickangle=-15),
        )
        st.plotly_chart(fig_tg, use_container_width=True)

    with eg2:
        ev_r = df.groupby("Event Name")["Rating"].mean().reset_index()
        ev_r.columns = ["Event", "Avg Rating"]
        fig_er = go.Figure(go.Bar(
            x=ev_r["Event"], y=ev_r["Avg Rating"],
            marker=dict(
                color=ev_r["Avg Rating"],
                colorscale=[[0, ORANGE], [0.5, CYAN], [1, GREEN]],
            ),
            text=ev_r["Avg Rating"].round(2), textposition="outside",
            hovertemplate="<b>%{x}</b><br>Avg Rating: %{y:.2f}<extra></extra>",
        ))
        fig_er.add_hline(
            y=df["Rating"].mean(), line_dash="dash", line_color="rgba(255,255,255,0.4)",
            annotation_text=f"Overall: {df['Rating'].mean():.2f}",
            annotation_font_color="#000000",
        )
        fig_er.update_layout(
            **CHART_LAYOUT,
            title=ct("Average Rating per Event"),
            height=320,
            yaxis=dict(range=[0, 5.5], showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
            xaxis=dict(tickangle=-15, showgrid=False),
        )
        st.plotly_chart(fig_er, use_container_width=True)

    st.divider()

    st.subheader("Revenue & Feedback Insights")
    rev1, rev2 = st.columns(2)

    with rev1:
        rev_state = df.groupby("State")["Amount Paid"].sum().reset_index()
        rev_state.columns = ["State", "Revenue"]
        rev_state = rev_state.sort_values("Revenue", ascending=False)
        fig_rv = go.Figure(go.Bar(
            x=rev_state["State"], y=rev_state["Revenue"],
            marker=dict(
                color=rev_state["Revenue"],
                colorscale=[[0, "#1a3a7a"], [0.5, CYAN], [1.0, PURPLE]],
            ),
            text=[f"Rs.{v:,}" for v in rev_state["Revenue"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Revenue: Rs.%{y:,}<extra></extra>",
        ))
        fig_rv.update_layout(
            **{**CHART_LAYOUT, "margin": dict(t=60, b=20, l=10, r=10)},
            title=ct("Revenue by State"),
            height=420,
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.08)"),
        )
        st.plotly_chart(fig_rv, use_container_width=True)

    with rev2:
        all_text_d = " ".join(df["Feedback on Fest"].tolist())
        try:
            wc_d = WordCloud(
                width=600, height=280,
                background_color=None,
                mode="RGBA",
                colormap="cool",
                max_words=60,
                prefer_horizontal=0.7,
            ).generate(all_text_d)
            fig_wc_d, ax_d = plt.subplots(figsize=(7, 3))
            fig_wc_d.patch.set_alpha(0)
            ax_d.set_facecolor("none")
            ax_d.imshow(wc_d, interpolation="bilinear")
            ax_d.axis("off")
            ax_d.set_title("Feedback Word Cloud", color="#000000", fontsize=12)
            st.pyplot(fig_wc_d)
        except Exception as e:
            st.warning(f"Word cloud unavailable: {e}")

    st.divider()

    # ── Section 7: Summary Insights 
    st.subheader("Summary Insights")

    top_state_d        = df.groupby("State").size().idxmax()
    top_event_d        = df.groupby("Event Name").size().idxmax()
    top_college_d      = df.groupby("College").size().idxmax()
    best_rated_event_d = df.groupby("Event Name")["Rating"].mean().idxmax()
    pct_group_d        = len(df[df["Event Type"] == "Group"]) / len(df) * 100

    s1, s2, s3 = st.columns(3)
    with s1:
        st.success(f"**Top State:** {top_state_d} — {df[df['State']==top_state_d].shape[0]} participants")
        st.success(f"**Most Popular Event:** {top_event_d}")
    with s2:
        st.info(f"**Top College:** {top_college_d}")
        st.info(f"**Best Rated Event:** {best_rated_event_d}")
    with s3:
        st.warning(f"**Group Participation:** {pct_group_d:.1f}% of registrations")
        st.warning(f"**Total Revenue:** Rs.{df['Amount Paid'].sum():,}")

#  FOOTER
st.divider()
st.caption("GATEWAYS 2025 · National Level Fest · Analytics Platform · Built with Streamlit")