import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 安全設定 ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        MY_API_KEY = st.secrets["GEMINI_API_KEY"]
        # 強制使用 REST 傳輸協定，避免 v1beta 報錯
        genai.configure(api_key=MY_API_KEY, transport='rest')
    else:
        st.warning("🔑 尚未設定 API 金鑰。請前往 Streamlit Cloud 的 Secrets 設定 'GEMINI_API_KEY'。")
        st.stop()
except Exception as e:
    st.error(f"❌ 讀取金鑰時發生錯誤：{e}")
    st.stop()

st.set_page_config(page_title="亮知識 Lumi 8.0 - 終極修復", page_icon="💡", layout="wide")

# --- 2. 介面美化 ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; font-weight: bold; border: none; }
    .stCodeBlock { background-color: #0E1117 !important; border: 1px solid #FFD700 !important; }
    .stTextArea textarea { font-size: 16px !important; line-height: 1.6 !important; border: 2px solid #FFD700 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💡 亮知識 Lumi - 短影音腳本工具箱 8.0")
st.caption("REST 傳輸協定 | 多重模型偵測 | 創作必備")

# --- 3. 側邊欄與輸入 ---
with st.sidebar:
    st.header("✨ 創作設定")
    with st.form("lumi_form"):
        topic = st.text_input("影片主題", placeholder="例如：為什麼水豚不怕鱷魚？")
        animal = st.text_input("影片主角", placeholder="例如：水豚")
        st.divider()
        uploaded_file = st.file_uploader("上傳參考圖", type=["jpg", "jpeg", "png"])
        submit_button = st.form_submit_button("🚀 生成電影級腳本")

# --- 4. 生成邏輯 ---
if submit_button:
    if not topic or not animal:
        st.error("⚠️ 請完整填寫主題與主角！")
    else:
        # 定義可嘗試的模型列表，解決 404 問題
        model_names = ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-1.5-pro"]
        success = False
        
        prompt = f"你是一位短影音導演。主題：{topic}，主角：{animal}。請產出包含 [旁白]、[Grok指令]、[Imagen提示詞] 的腳本。"

        for m_name in model_names:
            if success: break
            try:
                model = genai.GenerativeModel(m_name)
                with st.spinner(f"正在嘗試與 {m_name} 建立通訊..."):
                    if uploaded_file:
                        img = Image.open(uploaded_file)
                        response = model.generate_content([prompt, img])
                    else:
                        response = model.generate_content(prompt)
                    
                    res_text = response.text
                    st.success(f"✅ 使用 {m_name} 成功產出！")
                    
                    # 顯示結果
                    col1, col2 = st.columns([1, 1.2])
                    with col1:
                        st.subheader("🎙️ 20秒旁白稿")
                        st.text_area("錄音用：", value=res_text.split("[Grok指令]")[0].replace("[旁白]", "").strip(), height=400)
                    with col2:
                        st.subheader("🎬 生成指令區")
                        st.code(res_text.split("[Grok指令]")[1].split("[Imagen提示詞]")[0].strip())
                        st.divider()
                        st.code(res_text.split("[Imagen提示詞]")[1].strip())
                    
                    success = True
            except Exception as e:
                continue # 嘗試下一個模型名稱

        if not success:
            st.error("❌ 所有模型嘗試均失敗。請確認：1. API Key 是否正確 2. 稍後再試。")