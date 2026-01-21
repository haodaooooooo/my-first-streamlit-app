import streamlit as st
import random

st.title("🧪 亂數猜測實驗")

# 初始化 session_state，這是網頁記住變數的關鍵技術
# 原理：Streamlit 每次互動都會從頭執行程式，若無此設定，答案會一直重置
if 'target' not in st.session_state:
    st.session_state.target = random.randint(1, 100)

st.write("目標：猜測一個 1 到 100 之間的整數。")

# 接收使用者輸入
guess = st.number_input("請輸入參數", min_value=1, max_value=100, step=1)

if st.button("提交驗證"):
    if guess == st.session_state.target:
        st.success(f"實驗成功！目標數值確實為 {st.session_state.target}")
        # 重置遊戲
        del st.session_state.target
    elif guess < st.session_state.target:
        st.warning("數值偏差：過低")
    else:
        st.warning("數值偏差：過高")