import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 安全設定：從 Streamlit Secrets 讀取金鑰 ---
# 注意：部署後請在 Streamlit Cloud 的 Settings > Secrets 裡設定 GEMINI_API_KEY
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

st.set_page_config(page_title="亮知識 Lumi 7.5 - 安全部署版", page_icon="💡", layout="wide")

# --- 2. 介面美化 ---
st.markdown("""
    <style>
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em; 
        background: linear-gradient(45deg, #FFD700, #FFA500); 
        color: black; 
        font-weight: bold; 
        border: none; 
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0px 4px 15px rgba(255, 215, 0, 0.4);
    }
    .stCodeBlock { background-color: #0E1117 !important; border: 1px solid #FFD700 !important; }
    .stTextArea textarea { font-size: 16px !important; line-height: 1.6 !important; border: 2px solid #FFD700 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("💡 亮知識 Lumi - 短影音腳本工具箱 7.5")
st.caption("分秒對時旁白 | Grok 電影級全域指令 | 安全防護版本")

# --- 3. 側邊欄與輸入 ---
with st.sidebar:
    st.header("✨ 創作設定")
    with st.form("lumi_form"):
        topic = st.text_input("影片主題", placeholder="例如：水豚的游泳速度")
        animal = st.text_input("影片主角 / 物體", placeholder="例如：水豚、iPhone 15、富士山")
        st.divider()
        uploaded_file = st.file_uploader("上傳參考圖 (AI 將模仿其光影與細節)", type=["jpg", "jpeg", "png"])
        
        submit_button = st.form_submit_button("🚀 生成/更新 20秒腳本")
    
    st.info("💡 提示：重複點擊按鈕可重新生成不同內容。")

# --- 4. 生成邏輯 ---
if submit_button:
    if not topic or not animal:
        st.error("⚠️ 請完整填寫主題與主角名稱！")
    else:
        try:
            # 自動選擇模型
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            你是一位視覺特效導演與短影音專家，頻道名稱『亮知識』。
            
            主題：{topic}
            主角：{animal}
            
            請嚴格依照以下結構生成內容：
            
            1. [旁白]：20秒中文腳本，分為 (0-5s), (5-10s), (10-15s), (15-20s) 四個區間。
               - 每區間約 25-30 字，語氣要專業且吸引人。
            
            2. [Grok指令]：一段極其詳細、具有電影感的中文影片指令（約 300 字）。
               - 包含：4K 畫質、攝影機環繞運鏡、黃金時刻光影、寫實的細節紋理。
            
            3. [Imagen提示詞]：一段高品質英文繪圖提示詞 (Prompt)。
            
            格式請務必用標籤區分：[旁白]、[Grok指令]、[Imagen提示詞]。
            """
            
            with st.spinner("Lumi 正在精密建構電影級畫面描述..."):
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
                        st.write("旁白解析失敗，請確認 AI 回傳格式。")

                with col2:
                    st.subheader("🎬 Grok 極致詳細影片指令")
                    try:
                        grok_script = res_text.split("[Grok指令]")[1].split("[Imagen提示詞]")[0].strip()
                        st.code(grok_script, language="text")
                    except:
                        st.write("Grok 指令解析失敗。")

                    st.divider()
                    st.subheader("🖼️ 劇照英文提示詞")
                    try:
                        img_prompt = res_text.split("[Imagen提示詞]")[1].strip()
                        st.code(img_prompt, language="text")
                    except:
                        st.write("提示詞解析失敗。")

        except Exception as e:
            st.error(f"❌ 發生錯誤：{e}")