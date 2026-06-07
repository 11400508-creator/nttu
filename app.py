import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64

def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

st.set_page_config(
    page_title="WAG AA Final Dashboard",
    layout="wide"
)
img = get_base64("picture.png")
st.markdown(f"""
<style>
.hero {{
    background-image:
        linear-gradient(
            rgba(0,0,0,0.45),
            rgba(0,0,0,0.45)
        ),
        url("data:image/jpg;base64,{img}");

    background-size: cover;
    background-position: center;

    height: 500px;

    border-radius: 20px;

    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;

    margin-bottom:20px;

    color:white;
}}

.hero h1 {{
    font-size:55px;
    font-weight:bold;
}}

.hero p {{
    font-size:24px;
}}
</style>

<div class="hero">
    <h1>Women's Artistic Gymnastics</h1>
    <p>All-Around Final Dashboard</p>
    <p>Data Visualization Project</p>
</div>

""", unsafe_allow_html=True)

st.header("林宸妤：女子競技體操個人全能決賽成績視覺化分析")
st.subheader("114-2 運動大數據與視覺化分析專題研究／林宸妤")
st.write("""
本專題以女子競技體操個人全能決賽成績為分析對象，
透過 Streamlit 建立互動式資料視覺化平台，
探討不同賽事、國家、選手、器械項目與出場順序之間的成績差異。
""")

with st.expander("資料來源與變項說明"):
    st.write("""
    本資料包含女子競技體操個人全能決賽資料。

    主要變項包含：
    - year：年份
    - competition：賽事名稱
    - name：選手姓名
    - noc：國家代碼
    - rank_AA：個人全能排名
    - apparatus：器械項目，包含 VT、UB、BB、FX
    - rotation：決賽出場順序
    - D_score：難度分
    - E_score：完成分
    - final_score：單項最終分數
    """)

# =========================
# Load Data
# =========================

df = pd.read_csv("wag_aa_finalgame_score.csv")

df = df.dropna(how="all")
df = df.dropna(subset=["year", "competition", "name", "noc", "apparatus"])

df["name"] = df["name"].astype(str).str.strip()
df["noc"] = df["noc"].astype(str).str.strip()
df["competition"] = df["competition"].astype(str).str.strip()
df["apparatus"] = df["apparatus"].astype(str).str.strip()

df["year"] = pd.to_numeric(df["year"], errors="coerce")
df = df.dropna(subset=["year"])
df["year"] = df["year"].astype(int)

for col in ["rank_AA", "rotation", "D_score", "E_score", "final_score"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["competition_id"] = (
    df["year"].astype(str) + " " + df["competition"].astype(str)
)

# =========================
# Sidebar Filter
# =========================

st.sidebar.header("篩選條件")

year_options = sorted(df["year"].dropna().unique())
selected_years = st.sidebar.multiselect(
    "選擇年份",
    options=year_options,
    default=year_options
)

competition_options = sorted(df["competition"].dropna().unique())
selected_competitions = st.sidebar.multiselect(
    "選擇賽事",
    options=competition_options,
    default=competition_options
)

country_options = sorted(df["noc"].dropna().unique())
selected_countries = st.sidebar.multiselect(
    "選擇國家",
    options=country_options,
    default=country_options
)

apparatus_options = ["VT", "UB", "BB", "FX"]
selected_apparatus = st.sidebar.multiselect(
    "選擇器械項目",
    options=apparatus_options,
    default=apparatus_options
)

search_name = st.sidebar.text_input("搜尋選手姓名")

filtered = df[
    (df["year"].isin(selected_years))
    & (df["competition"].isin(selected_competitions))
    & (df["noc"].isin(selected_countries))
    & (df["apparatus"].isin(selected_apparatus))
]

if search_name:
    filtered = filtered[
        filtered["name"].str.contains(search_name, case=False, na=False)
    ]

# =========================
# Tabs
# =========================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "📊 總覽分析",
        "👤 選手分析",
        "🌍 國家分析",
        "🏅 賽事比較",
        "🔁 出場順序分析",
        "📉 冠軍差距分析",
        "📋 資料表",
    ]
)

# =========================
# Tab 1 Overview
# =========================

with tab1:
    st.subheader("整體表現總覽")

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("選手數", filtered["name"].nunique())
    col2.metric("國家數", filtered["noc"].nunique())
    col3.metric("平均 D 分", round(filtered["D_score"].mean(), 2))
    col4.metric("平均 E 分", round(filtered["E_score"].mean(), 2))
    col5.metric("平均 Final 分", round(filtered["final_score"].mean(), 2))

    st.subheader("D-E 風險策略象限圖")

    avg_D = filtered["D_score"].mean()
    avg_E = filtered["E_score"].mean()

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
        title="D-E Strategy Map"
    )

    fig.add_vline(x=avg_D, line_dash="dash")
    fig.add_hline(y=avg_E, line_dash="dash")

    st.plotly_chart(fig, use_container_width=True)

    st.caption("""
    圖中右上角代表高難度且高完成度，右下角代表高難度但完成度較低；
    左上角代表難度較低但完成度穩定。
    """)

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("各器械平均 Final 分")

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
            title="Average Final Score by Apparatus"
        )

        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("各器械分數穩定性分析")

        fig = px.violin(
            filtered,
            x="apparatus",
            y="final_score",
            color="apparatus",
            box=True,
            points="all",
            hover_data=["name", "noc", "competition_id"],
            title="Score Stability by Apparatus"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("分數分布比較")

    score_type = st.selectbox(
        "選擇分數類型",
        ["D_score", "E_score", "final_score"]
    )

    fig = px.box(
        filtered,
        x="apparatus",
        y=score_type,
        color="competition_id",
        points="all",
        title=f"{score_type} Distribution by Apparatus"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# Tab 2 Athlete Analysis
# =========================

with tab2:
    st.subheader("選手個人分析")

    athlete_options = sorted(
        filtered["name"]
        .dropna()
        .astype(str)
        .str.strip()
        .drop_duplicates()
        .tolist()
    )

    if len(athlete_options) > 0:
        selected_athlete = st.selectbox(
            "選擇選手",
            athlete_options
        )

        athlete_df = filtered[
            filtered["name"].astype(str).str.strip() == selected_athlete
        ]

        athlete_country = athlete_df["noc"].iloc[0]

        st.write(f"### {selected_athlete} ({athlete_country})")

        col1, col2, col3 = st.columns(3)

        col1.metric("參賽場次", athlete_df["competition_id"].nunique())
        col2.metric("最佳 AA 排名", int(athlete_df["rank_AA"].min()))
        col3.metric("平均單項 Final", round(athlete_df["final_score"].mean(), 2))

        c1, c2 = st.columns(2)

        with c1:
            st.subheader("選手 vs 全體平均雷達圖")

            athlete_radar = (
                athlete_df.groupby("apparatus")["final_score"]
                .mean()
                .reindex(["VT", "UB", "BB", "FX"])
            )

            overall_radar = (
                filtered.groupby("apparatus")["final_score"]
                .mean()
                .reindex(["VT", "UB", "BB", "FX"])
            )

            fig = go.Figure()

            fig.add_trace(
                go.Scatterpolar(
                    r=athlete_radar,
                    theta=["VT", "UB", "BB", "FX"],
                    fill="toself",
                    name=selected_athlete
                )
            )

            fig.add_trace(
                go.Scatterpolar(
                    r=overall_radar,
                    theta=["VT", "UB", "BB", "FX"],
                    fill="toself",
                    name="All Athletes Average"
                )
            )

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True)
                ),
                showlegend=True
            )

            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("D / E / Final 分組成")

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
                value_name="score"
            )

            fig = px.bar(
                score_long,
                x="apparatus",
                y="score",
                color="score_type",
                barmode="group",
                hover_data=["competition_id"],
                title="Score Composition by Apparatus"
            )

            st.plotly_chart(fig, use_container_width=True)

        st.subheader("選手跨賽事單項表現")

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
            title="Apparatus Scores Across Competitions"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("選手跨賽事 AA 總分趨勢")

        aa_trend = (
            athlete_df.groupby(["competition_id", "year", "competition"])["final_score"]
            .sum()
            .reset_index()
            .rename(columns={"final_score": "AA_total"})
        )

        fig = px.line(
            aa_trend,
            x="competition_id",
            y="AA_total",
            markers=True,
            title="All-Around Total Score Trend"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("選手資料表")
        st.dataframe(athlete_df, use_container_width=True)

    else:
        st.warning("目前篩選條件下沒有選手資料。")

# =========================
# Tab 3 Country Analysis
# =========================

with tab3:
    st.subheader("國家表現分析")

    country_summary = (
        filtered.groupby("noc")
        .agg(
            athletes=("name", "nunique"),
            avg_rank=("rank_AA", "mean"),
            avg_D=("D_score", "mean"),
            avg_E=("E_score", "mean"),
            avg_final=("final_score", "mean")
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
            title="Top Countries by Average Final Score"
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
            title="Country D/E Profile"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("國家 × 器械強項熱力圖")

    country_event = (
        filtered.groupby(["noc", "apparatus"])["final_score"]
        .mean()
        .reset_index()
    )

    heatmap_data = country_event.pivot(
        index="noc",
        columns="apparatus",
        values="final_score"
    )

    fig = px.imshow(
        heatmap_data,
        text_auto=".2f",
        aspect="auto",
        title="Country Strength Heatmap"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# Tab 4 Competition Comparison
# =========================

with tab4:
    st.subheader("不同賽事比較")

    competition_summary = (
        filtered.groupby("competition_id")
        .agg(
            athletes=("name", "nunique"),
            countries=("noc", "nunique"),
            avg_D=("D_score", "mean"),
            avg_E=("E_score", "mean"),
            avg_final=("final_score", "mean")
        )
        .reset_index()
        .sort_values("competition_id")
    )

    st.dataframe(competition_summary, use_container_width=True)

    fig = px.bar(
        competition_summary,
        x="competition_id",
        y=["avg_D", "avg_E", "avg_final"],
        barmode="group",
        title="Competition Average Score Comparison"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("各賽事器械平均分")

    comp_event = (
        filtered.groupby(["competition_id", "apparatus"])["final_score"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        comp_event,
        x="apparatus",
        y="final_score",
        color="competition_id",
        barmode="group",
        text_auto=".2f",
        title="Average Final Score by Competition and Apparatus"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# Tab 5 Rotation Analysis
# =========================

with tab5:
    st.subheader("出場順序與成績分析")

    c1, c2 = st.columns(2)

    with c1:
        fig = px.box(
            filtered,
            x="rotation",
            y="E_score",
            color="apparatus",
            points="all",
            title="E Score by Rotation"
        )

        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.box(
            filtered,
            x="rotation",
            y="final_score",
            color="apparatus",
            points="all",
            title="Final Score by Rotation"
        )

        st.plotly_chart(fig, use_container_width=True)

    rotation_summary = (
        filtered.groupby("rotation")
        .agg(
            avg_D=("D_score", "mean"),
            avg_E=("E_score", "mean"),
            avg_final=("final_score", "mean"),
            count=("name", "count")
        )
        .reset_index()
    )

    st.subheader("出場順序統計摘要")
    st.dataframe(rotation_summary, use_container_width=True)

    fig = px.line(
        rotation_summary,
        x="rotation",
        y=["avg_D", "avg_E", "avg_final"],
        markers=True,
        title="Average Score Trend by Rotation"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# Tab 6 Gap from Winner
# =========================

with tab6:
    st.subheader("AA 排名與冠軍差距分析")

    aa_score = (
        filtered.groupby(["competition_id", "name", "noc", "rank_AA"])["final_score"]
        .sum()
        .reset_index()
        .rename(columns={"final_score": "AA_total"})
    )

    if len(aa_score) > 0:
        selected_comp_gap = st.selectbox(
            "選擇一場賽事",
            sorted(aa_score["competition_id"].unique())
        )

        comp_df = aa_score[
            aa_score["competition_id"] == selected_comp_gap
        ].sort_values("rank_AA")

        winner_score = comp_df["AA_total"].max()
        comp_df["gap_from_winner"] = winner_score - comp_df["AA_total"]

        fig = px.bar(
            comp_df,
            x="name",
            y="gap_from_winner",
            color="noc",
            hover_data=["rank_AA", "AA_total"],
            title="Gap from Winner"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(comp_df, use_container_width=True)

    else:
        st.warning("目前沒有足夠資料可進行冠軍差距分析。")

# =========================
# Tab 7 Data Table
# =========================

with tab7:
    st.subheader("篩選後資料表")

    st.dataframe(filtered, use_container_width=True)

    csv = filtered.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="下載篩選後資料 CSV",
        data=csv,
        file_name="filtered_wag_aa_data.csv",
        mime="text/csv"
    )

st.caption("""
資料來源為公開國際競技體操賽事成績資料。
本平台僅作為 114-2 運動大數據與視覺化分析課程之學習與期末專題展示用途，
不涉及個人隱私與敏感資料。
""")