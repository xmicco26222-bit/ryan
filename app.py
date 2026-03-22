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

st.set_page_config(page_title="亮知識 Lumi 7.8 - 穩定修復版", page_icon="💡", layout="wide")

# --- 2. 介面美化 ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; font-weight: bold; border: none; }
    .stCodeBlock { background-color: #0E1117 !important; border: 1px solid #FFD700 !important; }
    .stTextArea textarea { font-size: 16px !important; line-height: 1.6 !important; border: 2px solid #FFD700 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💡 亮知識 Lumi - 短影音腳本工具箱 7.8")
st.caption("自動修正模型路徑 | 旁白分區優化")

# --- 3. 側邊欄與輸入 ---
with st.sidebar:
    st.header("✨ 創作設定")
    with st.form("lumi_form"):
        topic = st.text_input("影片主題", placeholder="例如：水豚為什麼愛泡溫泉？")
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
            # --- 修正重點：使用更通用的名稱 ---
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            
            prompt = f"""
            你是一位專業的短影音導演。
            主題：{topic}，主角：{animal}。
            請產出：
            1. [旁白]：20秒中文腳本（分四段）。
            2. [Grok指令]：300字電影級中文影片生成指令。
            3. [Imagen提示詞]：英文繪圖提示詞。
            格式：請務必包含標籤 [旁白]、[Grok指令]、[Imagen提示詞]。
            """
            
            with st.spinner("Lumi 正在精密運算中..."):
                if uploaded_file:
                    img = Image.open(uploaded_file)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                
                res_text = response.text
                st.success("✅ 生成成功！")

                # 分欄顯示
                col1, col2 = st.columns([1, 1.2])
                
                with col1:
                    st.subheader("🎙️ 20秒旁白稿")
                    if "[旁白]" in res_text:
                        narration = res_text.split("[旁白]")[1].split("[Grok指令]")[0].strip()
                        st.text_area("錄音用：", value=narration, height=400)
                    else:
                        st.write(res_text)

                with col2:
                    st.subheader("🎬 Grok 影片指令")
                    if "[Grok指令]" in res_text:
                        grok_script = res_text.split("[Grok指令]")[1].split("[Imagen提示詞]")[0].strip()
                        st.code(grok_script, language="text")
                    
                    st.divider()
                    st.subheader("🖼️ Imagen 提示詞")
                    if "[Imagen提示詞]" in res_text:
                        img_p = res_text.split("[Imagen提示詞]")[1].strip()
                        st.code(img_p, language="text")

        except Exception as e:
            # 如果還是報錯，給出具體建議
            st.error(f"❌ 偵測到環境異常：{e}")
            st.info("💡 提示：這通常是 API 版本同步問題，請稍候 1 分鐘重試，或檢查 Secrets 是否填寫正確。")