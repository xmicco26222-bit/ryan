import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 安全設定 ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        MY_API_KEY = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=MY_API_KEY)
    else:
        st.warning("🔑 尚未設定 API 金鑰。請前往 Streamlit Cloud 的 Secrets 設定 'GEMINI_API_KEY'。")
        st.stop()
except Exception as e:
    st.error(f"❌ 讀取金鑰時發生錯誤：{e}")
    st.stop()

st.set_page_config(page_title="亮知識 Lumi 7.9 - 萬用版", page_icon="💡", layout="wide")

# --- 2. 介面美化 ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; font-weight: bold; border: none; }
    .stCodeBlock { background-color: #0E1117 !important; border: 1px solid #FFD700 !important; }
    .stTextArea textarea { font-size: 16px !important; line-height: 1.6 !important; border: 2px solid #FFD700 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💡 亮知識 Lumi - 短影音腳本工具箱 7.9")
st.caption("自動選擇最穩定模型 | 支援 1.5 Flash")

# --- 3. 側邊欄與輸入 ---
with st.sidebar:
    st.header("✨ 創作設定")
    with st.form("lumi_form"):
        topic = st.text_input("影片主題", placeholder="例如：水豚的社交禮儀")
        animal = st.text_input("影片主角", placeholder="例如：水豚")
        st.divider()
        uploaded_file = st.file_uploader("上傳參考圖", type=["jpg", "jpeg", "png"])
        submit_button = st.form_submit_button("🚀 生成 20秒腳本")

# --- 4. 生成邏輯 ---
if submit_button:
    if not topic or not animal:
        st.error("⚠️ 請完整填寫主題與主角！")
    else:
        try:
            # --- 核心改動：萬用模型選擇邏輯 ---
            # 有些環境需要 "models/" 前綴，有些不需要，這裡直接嘗試最標準的寫法
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"你是導演，主題：{topic}，主角：{animal}。請產出標籤結構：[旁白]、[Grok指令]、[Imagen提示詞]。"
            
            with st.spinner("Lumi 正在精密連線中..."):
                if uploaded_file:
                    img = Image.open(uploaded_file)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                
                res_text = response.text
                st.success("✅ 生成成功！")

                # 顯示結果
                col1, col2 = st.columns([1, 1.2])
                with col1:
                    st.subheader("🎙️ 20秒旁白")
                    st.text_area("稿件內容：", value=res_text.split("[Grok指令]")[0].replace("[旁白]", "").strip(), height=400)
                with col2:
                    st.subheader("🎬 指令區")
                    st.code(res_text.split("[Grok指令]")[1].split("[Imagen提示詞]")[0].strip())
                    st.divider()
                    st.code(res_text.split("[Imagen提示詞]")[1].strip())

        except Exception as e:
            # 如果失敗，嘗試自動切換模型名稱 (有些舊版 SDK 需要加 models/)
            try:
                model = genai.GenerativeModel("models/gemini-1.5-flash")
                # 重試一次... (後面邏輯相同)
                st.info("🔄 正在嘗試備用路徑...")
                if uploaded_file:
                    img = Image.open(uploaded_file)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                st.success("✅ 備用路徑連結成功！")
                st.write(response.text)
            except:
                st.error(f"❌ 終極錯誤：{e}")