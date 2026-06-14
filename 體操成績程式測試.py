import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="競技體操成績系統",
    layout="wide"
)

SHEET_ID = "1k7AH73cR9GJWmWt0sh4Xz8tDRrykzDqrq6wM4vroyXs"

csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.title("🤸 競技體操成績系統")

st_autorefresh(
    interval=10000,
    key="refresh"
)

st.caption("每 10 秒自動更新一次")

try:
    df = pd.read_csv(csv_url)
except Exception as e:
    st.error("讀取 Google Sheets 失敗，請確認試算表是否已設定為知道連結的人可以檢視。")
    st.stop()

if df.empty:
    st.info("目前尚無成績")
else:
    required_columns = [
        "選手",
        "組別",
        "項目",
        "D分",
        "E分平均",
        "P分",
        "總分"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        st.error(f"試算表缺少欄位：{missing_columns}")
        st.stop()

    df["總分"] = pd.to_numeric(df["總分"], errors="coerce")
    df["D分"] = pd.to_numeric(df["D分"], errors="coerce")
    df["E分平均"] = pd.to_numeric(df["E分平均"], errors="coerce")
    df["P分"] = pd.to_numeric(df["P分"], errors="coerce")

    df = df.dropna(subset=["組別", "項目", "總分"])

    groups = (
        df[["組別", "項目"]]
        .drop_duplicates()
        .sort_values(["組別", "項目"])
    )

    for _, row in groups.iterrows():
        group = row["組別"]
        apparatus = row["項目"]

        st.subheader(f"{group}－{apparatus}")

        item_df = df[
            (df["組別"] == group) &
            (df["項目"] == apparatus)
        ]

        public_df = item_df[
            [
                "選手",
                "D分",
                "E分平均",
                "P分",
                "總分"
            ]
        ].copy()

        public_df = public_df.sort_values(
            by="總分",
            ascending=False
        ).reset_index(drop=True)

        public_df.insert(
            0,
            "排名",
            range(1, len(public_df) + 1)
        )

        st.dataframe(
            public_df,
            use_container_width=True,
            hide_index=True
        )