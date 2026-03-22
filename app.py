import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 安全設定 ---
if "GEMINI_API_KEY" in st.secrets:
    MY_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=MY_API_KEY)
else:
    st.error("❌ Secrets 裡找不到 GEMINI_API_KEY！")
    st.stop()

st.set_page_config(page_title="亮知識 Lumi 8.1", page_icon="💡", layout="wide")

# --- 2. 側邊欄 ---
with st.sidebar:
    st.header("✨ 創作設定")
    topic = st.text_input("影片主題", placeholder="例如：水豚的秘密")
    animal = st.text_input("主角", placeholder="水豚")
    submit = st.button("🚀 開始生成")

# --- 3. 生成邏輯 ---
if submit:
    if not topic or not animal:
        st.warning("請填寫主題與主角！")
    else:
        # 嘗試清單：從最新到最穩
        models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        success = False
        
        for m_name in models_to_try:
            try:
                model = genai.GenerativeModel(m_name)
                with st.spinner(f"正在嘗試連線 {m_name}..."):
                    response = model.generate_content(f"請用中文介紹{animal}的{topic}，並給出[旁白]、[Grok指令]、[Imagen提示詞]結構。")
                    st.success(f"✅ 連線成功！使用模型：{m_name}")
                    st.write(response.text)
                    success = True
                    break
            except Exception as e:
                last_error = str(e)
                continue
        
        if not success:
            st.error(f"❌ 嘗試所有模型均失敗。最後一個錯誤訊息：{last_error}")
            st.info("💡 如果訊息包含 'API key not found'，請檢查 Secrets 拼字；如果是 '403'，請重新申請金鑰。")