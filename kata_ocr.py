import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

def get_gemini_model():
    """Streamlit Cloud の Secrets から Gemini API キーを取得してモデルを初期化"""
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash')
    except KeyError:
        st.error("Gemini APIキーが Streamlit Cloud の Secrets に設定されていません。")
        return None

def extract_info_with_gemini(model, image_bytes):
    """Gemini API を使用して画像から情報を抽出する関数"""
    if model is None:
        return "Gemini モデルの初期化に失敗しました。"
    prompt = "この画像から、エアコンの定格能力、型番、冷房と暖房の定格消費電力を抽出してください。"
    response = model.generate_content(
        [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
    )
    return response.text if response.text else "Gemini APIからの応答がありませんでした。"

def main():
    st.title("エアコン情報抽出アプリ (Gemini API使用)")

    # Gemini モデルをセッションステートに保存 (初回のみロード)
    if "gemini_model" not in st.session_state:
        st.session_state["gemini_model"] = get_gemini_model()

    uploaded_file = st.file_uploader("エアコンの型番が写った画像をアップロードしてください", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        if st.session_state.get("gemini_model"):
            image = Image.open(uploaded_file)
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG')
            image_bytes = buffer.getvalue()

            st.image(image, caption="アップロードされた画像", use_column_width=True)
            st.write("解析中...")

            result = extract_info_with_gemini(st.session_state["gemini_model"], image_bytes)
            st.subheader("抽出結果")
            st.write(result)

if __name__ == "__main__":
    main()