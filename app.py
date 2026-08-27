import os
import base64
import mimetypes

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from prompts import PROMPTS, ICONS

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_image_bytes(image_bytes: bytes, mime_type: str, prompt: str) -> str:
    """Analyze raw image bytes using a vision-capable model."""
    
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime_type};base64,{image_base64}",
                    },
                ],
            }
        ],
    )
    return response.output_text





# -------------- streamlit application -------------------

st.set_page_config(page_title="Medical Image Analysis", page_icon="🩺")
st.markdown(
    "<h1 style='text-align: center;'>🩺 Medical Image Analysis</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: gray;'>"
    "Select an image type, upload an image to get an automated analysis."
    "</p>",
    unsafe_allow_html=True,
)


if not os.getenv("OPENAI_API_KEY"):
    st.warning("OPENAI_API_KEY is not set.")

# 1. Select the type of medical image.
image_type = st.selectbox(
    "Select image type",
    options=list(PROMPTS.keys()),
    format_func=lambda name: f"{ICONS.get(name, '')} {name}".strip(),
)

# 2. Upload an image.
uploaded = st.file_uploader(
    f"Upload a {image_type} image",
    type=["jpg", "jpeg", "png", "webp"],
)

if uploaded is not None:
    # Center the preview image using three columns (empty sides, image in middle).
    left, middle, right = st.columns([1, 2, 1])
    with middle:
        st.image(uploaded, caption=uploaded.name, use_container_width=True)

    # 3. Analyze with the model. Center the button in a narrow middle column.
    btn_left, btn_middle, btn_right = st.columns([3, 1, 3])
    with btn_middle:
        analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)

    if analyze_clicked:
        mime_type = (
            uploaded.type
            or mimetypes.guess_type(uploaded.name)[0]
            or "image/jpeg"
        )
        prompt = PROMPTS[image_type]
        with st.spinner(f"Analyzing {image_type} image..."):
            try:
                result = analyze_image_bytes(uploaded.getvalue(), mime_type, prompt)
                st.markdown("### Result")
                st.markdown(result)
            except Exception as e:  # noqa: BLE001
                st.error(f"Analysis failed: {e}")
