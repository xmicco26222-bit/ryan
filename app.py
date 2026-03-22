import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 安全設定 ---
if "GEMINI_API_KEY" in st.secrets:
    # 這裡會讀取你在 Streamlit 後台設定的新金鑰
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("🔑 請在 Secrets 設定 GEMINI_API_KEY")
    st.stop()

st.set_page_config(page_title="亮知識 Lumi 8.2", page_icon="💡", layout="wide")

# --- 2. 介面美化 ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; font-weight: bold; border: none; }
    .stCodeBlock { background-color: #0E1117 !important; border: 1px solid #FFD700 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💡 亮知識 Lumi - 短影音腳本 8.2")
st.caption("強制模型更新版本 | 解決 404 報錯")

# --- 3. 側邊欄 ---
with st.sidebar:
    st.header("✨ 創作設定")
    with st.form("lumi_form"):
        topic = st.text_input("影片主題", placeholder="例如：水豚為什麼愛泡溫泉？")
        animal = st.text_input("主角名稱", placeholder="水豚")
        st.divider()
        uploaded_file = st.file_uploader("參考圖 (選填)", type=["jpg", "jpeg", "png"])
        submit_button = st.form_submit_button("🚀 生成腳本")

# --- 4. 生成邏輯 ---
if submit_button:
    if not topic or not animal:
        st.error("⚠️ 請填寫完整主題與主角！")
    else:
        # 強制使用目前最新且支援的 1.5 系列模型名稱
        # 不再使用舊的 gemini-pro (這是 404 的主因)
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            你是一位專業短影音導演，頻道『亮知識』。
            主題：{topic}，主角：{animal}。
            請產出標籤結構：[旁白]、[Grok指令]、[Imagen提示詞]。
            """
            
            with st.spinner("Lumi 正在連線最新 1.5 模型..."):
                if uploaded_file:
                    img = Image.open(uploaded_file)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                
                res_text = response.text
                st.success("✅ 1.5 模型連線成功！")

                # 顯示結果
                col1, col2 = st.columns([1, 1.3])
                with col1:
                    st.subheader("🎙️ 20秒旁白")
                    try:
                        narration = res_text.split("[Grok指令]")[0].replace("[旁白]", "").strip()
                        st.text_area("稿件：", value=narration, height=400)
                    except:
                        st.write(res_text)

                with col2:
                    st.subheader("🎬 生成指令")
                    try:
                        grok_script = res_text.split("[Grok指令]")[1].split("[Imagen提示詞]")[0].strip()
                        st.code(grok_script, language="text")
                        
                        st.divider()
                        img_prompt = res_text.split("[Imagen提示詞]")[1].strip()
                        st.code(img_prompt, language="text")
                    except:
                        st.info("格式解析稍有偏差，請參考左側完整內容。")

        except Exception as e:
            st.error(f"❌ 發生錯誤：{e}")
            st.info("如果還是報 404，請檢查 Google AI Studio 是否有產生一把『新的』金鑰。")