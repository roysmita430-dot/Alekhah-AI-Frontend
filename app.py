import streamlit as st
from streamlit_drawable_canvas import st_canvas
import numpy as np
import pandas as pd
import requests
import matplotlib.pyplot as plt

st.set_page_config(page_title="Reverse Desmos AI", layout="wide")

st.title("🎨 Reverse Desmos AI — Draw and Get Equation")

st.write("Draw a curve below and let the AI guess its mathematical form!")

# Sidebar configuration
st.sidebar.header("Canvas Settings")
stroke_width = st.sidebar.slider("Stroke width", 1, 5, 2)
stroke_color = st.sidebar.color_picker("Stroke color", "#000000")

# Draw canvas
canvas_result = st_canvas(
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color="#FFFFFF",
    width=600,
    height=400,
    drawing_mode="freedraw",
    key="canvas"
)

if st.button("Analyze Graph"):
    if canvas_result.json_data is not None:
        # Extract points from JSON data
        points = []
        for obj in canvas_result.json_data["objects"]:
            if obj["type"] == "path":
                for pt in obj["path"]:
                    if len(pt) >= 3:
                        x, y = pt[1], pt[2]
                        points.append((x, y))
        
        if len(points) > 10:
            data = np.array(points)
            df = pd.DataFrame(data, columns=["x", "y"])
            
            st.subheader("🧮 Sending data to AI backend...")
            try:
                response = requests.post(
                    "https://alekhah-ai.onrender.com/predict",
                    json={"x": df["x"].tolist(), "y": df["y"].tolist()},
                    timeout=30
                )
                result = response.json()
                st.success(f"Predicted Equation: {result['equation']}")
                
                # Show fitted curve
                fig, ax = plt.subplots()
                ax.scatter(df["x"], df["y"], label="Drawn Points", s=10)
                ax.plot(result["fitted_x"], result["fitted_y"], 'r-', label="Predicted Fit")
                ax.legend()
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error contacting backend: {e}")
        else:
            st.warning("Please draw a bigger curve.")
    else:
        st.warning("Please draw something first.")
