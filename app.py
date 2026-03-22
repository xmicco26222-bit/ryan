import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 設定金鑰 ---
MY_API_KEY = "AIzaSyD49o_iWpqQzRHL1t8NZoDxwJUkNs6xvgI"
genai.configure(api_key=MY_API_KEY)

st.set_page_config(page_title="亮知識 Lumi 7.0 - Grok 影像大師", page_icon="💡", layout="wide")

# --- 2. 介面美化 ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(45deg, #FFD700, #FFA500); color: black; font-weight: bold; border: none; }
    .stCodeBlock { background-color: #0E1117 !important; border: 1px solid #FFD700 !important; }
    .stTextArea textarea { font-size: 16px !important; line-height: 1.6 !important; border: 2px solid #FFD700 !important; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💡 亮知識 Lumi - 短影音腳本工具箱 7.0")
st.caption("分秒對時旁白 | Grok 電影級全域指令 | 視覺細節強化")

# --- 3. 側邊欄與輸入 ---
with st.sidebar:
    st.header("✨ 創作設定")
    with st.form("lumi_form"):
        topic = st.text_input("影片主題", placeholder="例如：水豚為什麼是動物界外交官？")
        animal = st.text_input("主角動物", placeholder="例如：水豚")
        st.divider()
        uploaded_file = st.file_uploader("上傳參考圖 (AI 將模仿其光影與細節)", type=["jpg", "jpeg", "png"])
        
        # 這裡就是你的生成按鈕，重複按就是重新生成
        submit_button = st.form_submit_button("🚀 生成/更新 20秒腳本")
    
    st.info("💡 提示：Grok 指令已針對 20 秒連貫影片優化，包含攝影機運動與光影細節。")

# --- 4. 生成邏輯 ---
if submit_button:
    if not topic or not animal:
        st.error("⚠️ 請完整填寫主題與動物名稱！")
    else:
        try:
            # 自動偵測模型
            all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target_model = next((n for n in ["models/gemini-1.5-flash", "gemini-1.5-flash", "models/gemini-pro"] if n in all_models), all_models[0])
            model = genai.GenerativeModel(target_model)
            
            # --- 極致詳細的 Prompt 設計 ---
            prompt = f"""
            你是一位視覺特效導演與短影音專家，頻道名稱『亮知識』。
            
            主題：{topic}
            主角動物：{animal}
            
            請嚴格依照以下結構生成：
            
            1. [旁白]：20秒中文腳本，分為 (0-5s), (5-10s), (10-15s), (15-20s) 四個區間。
               - 每區間約 25-30 字，語氣要活潑、有梗、充滿知識性。
            
            2. [Grok全域指令]：請寫一段『極其詳細、具有電影感』的中文影片指令（約 300 字）。
               - 必須包含：
                 * 攝影機運動：緩慢滑動、微距特寫(Macro)、平滑的拉遠(Pull back)或環繞軌道攝影。
                 * 光影氣氛：黃金時刻的側逆光、丁達爾效應、細微的水霧或塵埃動態、環境遮蔽(AO)陰影。
                 * 材質表現：極致寫實的毛髮根部、濕潤鼻頭、深邃的瞳孔反射、細膩的皮膚紋理。
                 * 畫質術語：4K, 8K, 120fps 高速攝影感, 專業調色。
                 * 動作描述：具體描述動物在 20 秒內的連貫自然動作。
            
            3. [Imagen提示詞]：一段對應主題的高品質英文劇照提示詞。
            
            格式請用標籤區分：[旁白]、[Grok指令]、[Imagen提示詞]。
            """
            
            with st.spinner("Lumi 正在精密建構電影級畫面描述..."):
                if uploaded_file:
                    img = Image.open(uploaded_file)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                
                res_text = response.text
                st.success("✅ 腳本與 Grok 詳細指令生成成功！")

                col1, col2 = st.columns([1, 1.3])

                with col1:
                    st.subheader("🎙️ 20秒分秒對位旁白")
                    # 抓取旁白
                    narration = res_text.split("[Grok指令]")[0].replace("[旁白]", "").strip()
                    st.text_area("錄音稿 (已按秒數分段)：", value=narration, height=450)

                with col2:
                    st.subheader("🎬 Grok 極致詳細影片指令")
                    # 抓取指令
                    try:
                        grok_script = res_text.split("[Grok指令]")[1].split("[Imagen提示詞]")[0].strip()
                        st.code(grok_script, language="text")
                        st.caption("💡 提示：將上方整段中文複製給 Grok，它會理解這是一段長達 20 秒的連貫運鏡。")
                    except:
                        st.write("格式解析異常，請看下方完整內容。")

                    st.divider()
                    st.subheader("🖼️ 劇照英文提示詞 (可選)")
                    try:
                        img_prompt = res_text.split("[Imagen提示詞]")[1].strip()
                        st.code(img_prompt, language="text")
                    except:
                        st.write("未產出提示詞。")

        except Exception as e:
            st.error(f"❌ 發生錯誤：{e}")