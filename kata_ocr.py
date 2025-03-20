import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import pandas as pd

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
        return None
    prompt = """この画像から、以下の情報を抽出して、Pythonの辞書形式で出力してください。
    抽出する情報:
    - 型番
    - 製造年
    - 冷房 定格能力 (単位も含む)
    - 暖房 定格能力 (標準、低温の区別と単位も含む)
    - 冷房 定格消費電力 (単位も含む)
    - 暖房 定格消費電力 (単位も含む)

    出力例:
    {
        "型番": "...",
        "製造年": "...",
        "冷房 定格能力": "...",
        "暖房 定格能力": "標準: ..., 低温: ...",
        "冷房 定格消費電力": "...",
        "暖房 定格消費電力": "..."
    }
    """
    response = model.generate_content(
        [prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
    )
    try:
        # Gemini の応答が Python の辞書形式であると期待して評価
        extracted_data = eval(response.text)
        return extracted_data
    except Exception as e:
        st.error(f"抽出結果の解析に失敗しました: {e}\n応答内容: {response.text}")
        return None

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

            extracted_info = extract_info_with_gemini(st.session_state["gemini_model"], image_bytes)

            if extracted_info:
                df = pd.DataFrame([extracted_info])
                st.subheader("抽出結果 (DataFrame)")
                st.dataframe(df)
        else:
            st.error("Gemini モデルの初期化に失敗しました。")

if __name__ == "__main__":
    main()