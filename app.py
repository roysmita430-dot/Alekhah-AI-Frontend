import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

# ----------------------------
# Canvas Configuration Function
# ----------------------------
def create_graph_paper(width, height, grid_size=25):
    """Generate a simple graph-paper-style background."""
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Light gray grid lines
    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill=(220, 220, 220), width=1)
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill=(220, 220, 220), width=1)

    # Darker X and Y axes at center
    draw.line([(width//2, 0), (width//2, height)], fill=(150, 150, 150), width=2)
    draw.line([(0, height//2), (width, height//2)], fill=(150, 150, 150), width=2)

    return img

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Alekhah AI — Reverse Desmos", layout="wide")

st.title("📈 Alekhah AI — Draw & Discover the Equation")

st.write("Draw your curve on the **graph paper** below. The AI will infer the most probable mathematical function behind it.")

# Sidebar
st.sidebar.header("Canvas Settings")
stroke_width = st.sidebar.slider("✏️ Stroke Width", 1, 5, 2)
stroke_color = st.sidebar.color_picker("🎨 Stroke Color", "#000000")
grid_size = st.sidebar.slider("🧮 Grid Size", 15, 50, 25)

# Create graph paper background
width, height = 600, 400
graph_paper = create_graph_paper(width, height, grid_size)
st.sidebar.image(graph_paper, caption="Graph Paper Preview", use_container_width=True)

# Draw canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 255, 255, 0)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_image=graph_paper,
    update_streamlit=True,
    height=height,
    width=width,
    drawing_mode="freedraw",
    key="canvas"
)

# ----------------------------
# Analysis
# ----------------------------
if st.button("🔍 Analyze Graph"):
    if canvas_result.json_data is not None:
        points = []
        for obj in canvas_result.json_data["objects"]:
            if obj["type"] == "path":
                for pt in obj["path"]:
                    if len(pt) >= 3:
                        x, y = pt[1], pt[2]
                        points.append((x, y))

        if len(points) > 10:
            df = pd.DataFrame(points, columns=["x", "y"])
            st.subheader("🧠 Alekhah AI having a chat with Guass and Fourier...")
            try:
                response = requests.post(
                    "https://alekhah-ai.onrender.com/predict",  # Replace with your actual backend URL
                    json={"x": df["x"].tolist(), "y": df["y"].tolist()},
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    st.success(f"**Predicted Equation:** {result['equation']}")
                    st.caption(f"Type: {result.get('function_type', 'Unknown')}")

                    # Plotting
                    fig, ax = plt.subplots(figsize=(7, 4))
                    ax.scatter(df["x"], df["y"], s=10, label="Drawn Curve")
                    ax.plot(result["fitted_x"], result["fitted_y"], "r-", label="AI Fit")
                    ax.axhline(0, color="gray", linewidth=0.8)
                    ax.axvline(0, color="gray", linewidth=0.8)
                    ax.legend()
                    st.pyplot(fig)
                else:
                    st.error(f"Backend Error: {response.text}")

            except Exception as e:
                st.error(f"Error contacting backend: {e}")
        else:
            st.warning("Please draw a bigger or clearer curve.")
    else:
        st.warning("Please draw something on the canvas first.")
