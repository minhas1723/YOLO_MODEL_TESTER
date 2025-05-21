import streamlit as st
from src.utils import get_available_models, load_model
from src.image_processing import process_image
from src.video_processing import process_video_file

# Set page config
st.set_page_config(page_title="Object Detection", layout="wide")

# Title
st.title("YOLO Object Detection App")
st.write("Upload an image or video to detect objects using your YOLO model")

# Get available models
available_models = get_available_models()

# Sidebar for model selection
with st.sidebar:
    st.header("Model Configuration")
    
    if available_models:
        selected_model_name = st.selectbox(
            "Select Model",
            options=list(available_models.keys()),
            index=0
        )
        model_path = available_models[selected_model_name]
        st.write(f"Selected model: **{selected_model_name}**")
    else:
        st.error("No model files (.pt) found")
        st.stop()
    
    # Load the model
    with st.spinner("Loading model..."):
        try:
            model = load_model(model_path)
            st.success(f"Model loaded successfully")
            
            # Option to show class names
            if hasattr(model, 'names') and model.names and st.checkbox("Show class names"):
                # Display class names in a cleaner format
                class_dict = model.names
                class_list = [f"{idx}: {name}" for idx, name in class_dict.items()]
                st.write("**Classes:**")
                # Display in columns for better readability
                cols = st.columns(2)
                half = len(class_list) // 2 + len(class_list) % 2
                cols[0].write("\n".join(class_list[:half]))
                cols[1].write("\n".join(class_list[half:]) if len(class_list) > half else "")
                
        except Exception as e:
            st.error(f"Error loading model: {e}")
            st.stop()
    
    # Additional options
    conf_threshold = st.slider("Confidence threshold", 0.1, 1.0, 0.5, 0.05)
    show_labels = st.checkbox("Show labels on image/video", value=True)
    show_conf = st.checkbox("Show confidence scores", value=True)
    
    # Video processing options
    st.subheader("Video Options")
    process_every_nth_frame = st.slider(
        "Process every Nth frame", 
        1, 10, 1, 1, 
        help="Only run detection on every Nth frame to speed up processing. Higher values = faster processing but may miss fast-moving objects. The output video will maintain the original frame rate."
    )

# Input selection - choose between image and video
input_type = st.radio("Select input type", ["Image", "Video"])

if input_type == "Image":
    process_image(model, conf_threshold, show_labels, show_conf)
else:  # Video processing
    process_video_file(model, conf_threshold, show_labels, show_conf, process_every_nth_frame)

# Add footer
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p>YOLO Object Detection App - Image and Video Support</p>
</div>
""", unsafe_allow_html=True)
