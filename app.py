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

st.set_page_config(page_title="亮知識 Lumi 7.7 - 穩定版", page_icon="💡", layout="wide")

# --- 2. 介面美化 ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; font-weight: bold; border: none; }
    .stCodeBlock { background-color: #0E1117 !important; border: 1px solid #FFD700 !important; }
    .stTextArea textarea { font-size: 16px !important; line-height: 1.6 !important; border: 2px solid #FFD700 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💡 亮知識 Lumi - 短影音腳本工具箱 7.7")
st.caption("穩定模型路徑 | 電影級指令優化")

# --- 3. 側邊欄與輸入 ---
with st.sidebar:
    st.header("✨ 創作設定")
    with st.form("lumi_form"):
        topic = st.text_input("影片主題", placeholder="例如：水豚為什麼這麼受歡迎？")
        animal = st.text_input("影片主角 / 物體", placeholder="例如：水豚")
        st.divider()
        uploaded_file = st.file_uploader("上傳參考圖 (可選)", type=["jpg", "jpeg", "png"])
        submit_button = st.form_submit_button("🚀 生成/更新 20秒腳本")

# --- 4. 生成邏輯 ---
if submit_button:
    if not topic or not animal:
        st.error("⚠️ 請完整填寫主題與主角名稱！")
    else:
        try:
            # --- 核心修改：使用最標準的模型代碼 ---
            # 拿掉 -latest，直接使用標準名稱
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            你是一位視覺特效導演與短影音專家，頻道名稱『亮知識』。
            主題：{topic}，主角：{animal}。
            請嚴格依照標籤結構生成：[旁白]、[Grok指令]、[Imagen提示詞]。
            """
            
            with st.spinner("Lumi 正在精密構建中..."):
                if uploaded_file:
                    img = Image.open(uploaded_file)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                
                res_text = response.text
                st.success("✅ 生成成功！")

                col1, col2 = st.columns([1, 1.3])
                with col1:
                    st.subheader("🎙️ 20秒分秒對位旁白")
                    try:
                        narration = res_text.split("[Grok指令]")[0].replace("[旁白]", "").strip()
                        st.text_area("錄音稿：", value=narration, height=450)
                    except:
                        st.write(res_text) # 如果解析失敗，顯示原始文字

                with col2:
                    st.subheader("🎬 Grok 極致詳細影片指令")
                    try:
                        grok_parts = res_text.split("[Grok指令]")
                        grok_script = grok_parts[1].split("[Imagen提示詞]")[0].strip()
                        st.code(grok_script, language="text")
                    except:
                        st.write("請重新點擊生成。")

                    st.divider()
                    st.subheader("🖼️ 劇照英文提示詞")
                    try:
                        img_prompt = res_text.split("[Imagen提示詞]")[1].strip()
                        st.code(img_prompt, language="text")
                    except:
                        st.write("提示詞解析中...")

        except Exception as e:
            st.error(f"❌ 發生錯誤：{e}")