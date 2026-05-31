import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="WAG AA Dashboard",
    layout="wide"
)

st.title("🤸 Women's Artistic Gymnastics AA Final Dashboard")

# =========================
# Load Data
# =========================

df = pd.read_csv("wag_aa_finalgame_score.csv")

df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
df = df.dropna(how="all")
df = df.dropna(subset=["year", "competition", "name", "noc", "apparatus"])

df["year"] = df["year"].astype(int)

for col in ["rank_AA", "rotation", "D_score", "E_score", "final_score"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["athlete_id"] = df["name"].astype(str) + " | " + df["noc"].astype(str)

df["competition_id"] = (
    df["year"].astype(str)
    + " "
    + df["competition"].astype(str)
)

# =========================
# Sidebar Filters
# =========================

st.sidebar.header("Filters")

year_options = sorted(df["year"].dropna().unique())

selected_years = st.sidebar.multiselect(
    "Year",
    options=year_options,
    default=year_options
)

competition_options = sorted(df["competition"].dropna().unique())

selected_competitions = st.sidebar.multiselect(
    "Competition",
    options=competition_options,
    default=competition_options
)

country_options = sorted(df["noc"].dropna().unique())

selected_countries = st.sidebar.multiselect(
    "Country",
    options=country_options,
    default=country_options
)

apparatus_options = ["VT", "UB", "BB", "FX"]

selected_apparatus = st.sidebar.multiselect(
    "Apparatus",
    options=apparatus_options,
    default=apparatus_options
)

filtered = df[
    (df["year"].isin(selected_years))
    & (df["competition"].isin(selected_competitions))
    & (df["noc"].isin(selected_countries))
    & (df["apparatus"].isin(selected_apparatus))
]

# =========================
# Tabs
# =========================

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "📊 Overview",
        "👤 Athlete Analysis",
        "🌍 Country Analysis",
        "🔁 Rotation Analysis",
        "📋 Data Table",
    ]
)

# =========================
# Tab 1 Overview
# =========================

with tab1:
    st.subheader("Overall Performance Overview")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Athletes", filtered["athlete_id"].nunique())
    col2.metric("Countries", filtered["noc"].nunique())
    col3.metric("Average D", round(filtered["D_score"].mean(), 2))
    col4.metric("Average E", round(filtered["E_score"].mean(), 2))
    col5.metric("Average Final", round(filtered["final_score"].mean(), 2))

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("D Score vs E Score")

        fig = px.scatter(
            filtered,
            x="D_score",
            y="E_score",
            color="apparatus",
            size="final_score",
            hover_data=[
                "year",
                "competition",
                "name",
                "noc",
                "rank_AA",
                "rotation",
            ],
            title="Difficulty and Execution Relationship",
        )

        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Average Final Score by Apparatus")

        event_mean = (
            filtered.groupby("apparatus")["final_score"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            event_mean,
            x="apparatus",
            y="final_score",
            text_auto=".2f",
            title="Average Final Score by Apparatus",
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Score Distribution")

    score_type = st.selectbox(
        "Choose score type",
        ["D_score", "E_score", "final_score"],
    )

    fig = px.box(
        filtered,
        x="apparatus",
        y=score_type,
        color="competition_id",
        points="all",
        title=f"{score_type} Distribution by Apparatus",
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# Tab 2 Athlete Analysis
# =========================

with tab2:
    st.subheader("Athlete Individual Analysis")

    athlete_options = sorted(filtered["athlete_id"].dropna().unique())

    if len(athlete_options) > 0:
        selected_athlete = st.selectbox(
            "Select Athlete",
            athlete_options,
        )

        athlete_df = filtered[filtered["athlete_id"] == selected_athlete]

        st.write("### Athlete Records")
        st.dataframe(athlete_df, use_container_width=True)

        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Apparatus Final Score Radar")

            radar_df = (
                athlete_df.groupby("apparatus")["final_score"]
                .mean()
                .reindex(["VT", "UB", "BB", "FX"])
                .reset_index()
            )

            fig = go.Figure()

            fig.add_trace(
                go.Scatterpolar(
                    r=radar_df["final_score"],
                    theta=radar_df["apparatus"],
                    fill="toself",
                    name=selected_athlete,
                )
            )

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                    )
                ),
                showlegend=True,
            )

            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("D / E / Final by Apparatus")

            score_long = athlete_df.melt(
                id_vars=[
                    "apparatus",
                    "competition_id",
                    "year",
                    "competition",
                ],
                value_vars=[
                    "D_score",
                    "E_score",
                    "final_score",
                ],
                var_name="score_type",
                value_name="score",
            )

            fig = px.bar(
                score_long,
                x="apparatus",
                y="score",
                color="score_type",
                barmode="group",
                hover_data=["competition_id"],
                title="Score Composition",
            )

            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Athlete Performance Across Competitions")

        fig = px.line(
            athlete_df,
            x="competition_id",
            y="final_score",
            color="apparatus",
            markers=True,
            hover_data=[
                "year",
                "competition",
                "rotation",
                "D_score",
                "E_score",
            ],
            title="Apparatus Scores Across Competitions",
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No athlete data available under current filters.")

# =========================
# Tab 3 Country Analysis
# =========================

with tab3:
    st.subheader("Country Performance Analysis")

    country_summary = (
        filtered.groupby("noc")
        .agg(
            athletes=("athlete_id", "nunique"),
            avg_rank=("rank_AA", "mean"),
            avg_D=("D_score", "mean"),
            avg_E=("E_score", "mean"),
            avg_final=("final_score", "mean"),
        )
        .reset_index()
        .sort_values("avg_final", ascending=False)
    )

    st.dataframe(country_summary, use_container_width=True)

    c1, c2 = st.columns(2)

    with c1:
        fig = px.bar(
            country_summary.head(15),
            x="noc",
            y="avg_final",
            text_auto=".2f",
            title="Top Countries by Average Final Score",
        )

        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.scatter(
            country_summary,
            x="avg_D",
            y="avg_E",
            size="athletes",
            color="noc",
            hover_data=["avg_rank", "avg_final"],
            title="Country D/E Profile",
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Country Strength by Apparatus")

    country_event = (
        filtered.groupby(["noc", "apparatus"])["final_score"]
        .mean()
        .reset_index()
    )

    fig = px.density_heatmap(
        country_event,
        x="apparatus",
        y="noc",
        z="final_score",
        histfunc="avg",
        title="Average Final Score Heatmap",
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# Tab 4 Rotation Analysis
# =========================

with tab4:
    st.subheader("Rotation / Starting Order Analysis")

    c1, c2 = st.columns(2)

    with c1:
        fig = px.box(
            filtered,
            x="rotation",
            y="E_score",
            color="apparatus",
            points="all",
            title="E Score by Rotation",
        )

        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.box(
            filtered,
            x="rotation",
            y="final_score",
            color="apparatus",
            points="all",
            title="Final Score by Rotation",
        )

        st.plotly_chart(fig, use_container_width=True)

    rotation_summary = (
        filtered.groupby("rotation")
        .agg(
            avg_D=("D_score", "mean"),
            avg_E=("E_score", "mean"),
            avg_final=("final_score", "mean"),
            count=("athlete_id", "count"),
        )
        .reset_index()
    )

    st.subheader("Rotation Summary")
    st.dataframe(rotation_summary, use_container_width=True)

    fig = px.line(
        rotation_summary,
        x="rotation",
        y=["avg_D", "avg_E", "avg_final"],
        markers=True,
        title="Average Score Trend by Rotation",
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# Tab 5 Data Table
# =========================

with tab5:
    st.subheader("Filtered Data")

    st.dataframe(filtered, use_container_width=True)

    csv = filtered.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name="filtered_wag_aa_data.csv",
        mime="text/csv",
    )