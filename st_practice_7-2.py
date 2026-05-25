# 教學模板 B：側邊欄元件
# 學習重點：st.sidebar.radio()、multiselect()、slider()、selectbox()、checkbox()

import streamlit as st
import pandas as pd

# ==========================================
# 頁面設定
# ==========================================
st.set_page_config(page_title="側邊欄教學", page_icon="🔧")

# 載入資料
df = pd.read_csv("practice_8_1.csv")

# ==========================================
# 綜合練習：設計一個完整的側邊欄
# ==========================================
st.title("✏️ 綜合練習：設計一個側邊欄")
st.markdown("請完成以下 TODO，設計一個功能完整的側邊欄")

st.markdown("---")

# 顯示練習題目
st.write('''
請複製以下code到你的程式中，並完成TODO部分！

記得拿掉 #
'''
)

# 請在側邊欄完成以下元件

# TODO 1：側邊欄標題（含圖標）
st.sidebar.title("側邊欄設計練習")

# TODO 2：radio 單選按鈕（選擇頁面，3個選項，含圖標）
page = st.sidebar.radio(
    "選擇頁面",
    ["分頁1", "分頁2", "分頁3"]
)

# TODO 3：分隔線
st.sidebar.divider()

# TODO 4：multiselect 多選框（選擇運動項目）
# 提示：先用 df["sport"].unique() 取得所有選項
all_sports = df["sport"].unique()
selected_sports = st.sidebar.multiselect(
    "選擇運動項目",
    options=all_sports,
    default=all_sports
)

# TODO 5：slider 滑桿（選擇年級範圍）
grade_range = st.sidebar.slider(
    "選擇年級範圍",
    min_value=1,
    max_value=4,
    value=(1, 4)
)

# TODO 6：selectbox 下拉選單（選擇性別）
selected_gender = st.sidebar.selectbox(
    "選擇性別",
    ["全部", "M", "F"]
)

# TODO 7：checkbox 核取方塊（是否只顯示受傷學生）
show_injured = st.sidebar.checkbox(
    "只顯示受傷學生",
    value=False
)

# TODO 8：顯示篩選後的資料筆數
st.sidebar.markdown("---")
st.sidebar.write("📊 篩選結果：___ 位學生")

st.code("""
# 請在側邊欄完成以下元件

# TODO 1：側邊欄標題（含圖標）
st.sidebar.title("___")

# TODO 2：radio 單選按鈕（選擇頁面，3個選項，含圖標）
page = st.sidebar.radio(
    "選擇頁面",
    ["___", "___", "___"]
)

# TODO 3：分隔線
st.sidebar.divider()

# TODO 4：multiselect 多選框（選擇運動項目）
# 提示：先用 df["sport"].unique() 取得所有選項
all_sports = df["sport"].unique()
selected_sports = st.sidebar.multiselect(
    "選擇運動項目",
    options=___,
    default=___
)

# TODO 5：slider 滑桿（選擇年級範圍）
grade_range = st.sidebar.slider(
    "選擇年級範圍",
    min_value=___,
    max_value=___,
    value=(___, ___)
)

# TODO 6：selectbox 下拉選單（選擇性別）
selected_gender = st.sidebar.selectbox(
    "選擇性別",
    ["___", "___", "___"]
)

# TODO 7：checkbox 核取方塊（是否只顯示受傷學生）
show_injured = st.sidebar.checkbox(
    "___",
    value=___
)

# TODO 8：顯示篩選後的資料筆數
st.sidebar.markdown("---")
st.sidebar.write("📊 篩選結果：___ 位學生")
""")

# ==========================================
# 解答區
# ==========================================
with st.expander("🔽 點我看解答"):
    st.code("""
# 解答：完整的側邊欄

# 側邊欄標題
st.sidebar.title("🔧 控制面板")

# radio 單選按鈕
page = st.sidebar.radio(
    "選擇頁面",
    ["🏠 首頁", "📊 分析", "⚙️ 設定"]
)

# 分隔線
st.sidebar.divider()

# multiselect 多選框
all_sports = df["sport"].unique()
selected_sports = st.sidebar.multiselect(
    "選擇運動項目",
    options=all_sports,
    default=all_sports
)

# slider 滑桿
grade_range = st.sidebar.slider(
    "選擇年級範圍",
    min_value=1,
    max_value=4,
    value=(1, 4)
)

# selectbox 下拉選單
selected_gender = st.sidebar.selectbox(
    "選擇性別",
    ["全部", "M", "F"]
)

# checkbox 核取方塊
show_injured = st.sidebar.checkbox(
    "只顯示受傷學生",
    value=False
)

# 顯示篩選結果
st.sidebar.markdown("---")
st.sidebar.write(f"📊 篩選結果：{len(df)} 位學生")
    """)
    
    # 加上過濾邏輯的補充說明
    st.info("💡 進階提示：篩選後，可以用以下程式碼過濾資料：")
    st.code("""
# 過濾資料的邏輯
filtered_df = df.copy()

# 套用運動項目篩選
filtered_df = filtered_df[filtered_df["sport"].isin(selected_sports)]

# 套用年級篩選
filtered_df = filtered_df[
    (filtered_df["grade"] >= grade_range[0]) & 
    (filtered_df["grade"] <= grade_range[1])
]

# 套用性別篩選
if selected_gender != "全部":
    filtered_df = filtered_df[filtered_df["gender"] == selected_gender]

# 套用受傷篩選
if show_injured:
    filtered_df = filtered_df[filtered_df["injury_history"] == "Yes"]
    """)

st.success("✅ 完成後，試試看每個篩選器是否都能正常運作！")