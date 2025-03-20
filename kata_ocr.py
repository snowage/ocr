import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import os

def extract_info_with_gemini(image_bytes):
    """Gemini API を使用して画像から情報を抽出する関数 (APIキーは環境変数から取得)"""
    api_key = st.secrets["GEMINI_API_KEY"]
    if not api_key:
        return "エラー: Gemini APIキーが環境変数に設定されていません。"

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = "この画像から、エアコンの定格能力、型番、冷房と暖房の定格消費電力を抽出してください。"
    response = model.generate_content(
        [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
    )
    return response.text if response.text else "Gemini APIからの応答がありませんでした。"

def main():
    st.title("エアコン情報抽出アプリ (Gemini API使用)")

    uploaded_file = st.file_uploader("エアコンの型番が写った画像をアップロードしてください", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG')
        image_bytes = buffer.getvalue()

        st.image(image, caption="アップロードされた画像", use_column_width=True)
        st.write("解析中...")

        result = extract_info_with_gemini(image_bytes)
        st.subheader("抽出結果")
        st.write(result)

if __name__ == "__main__":
    main()