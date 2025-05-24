import streamlit as st
from src.utils import get_available_models, load_model, get_available_devices
from src.image_processing import process_image
from src.video_processing import process_video_file
import torch

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
    
    # Device selection
    available_devices = get_available_devices()
    selected_device = st.selectbox(
        "Inference Device",
        options=available_devices,
        index=0,
        help="Select GPU (CUDA) for faster inference if available"
    )
    
    # Add GPU memory info if GPU is selected
    if "cuda" in selected_device and torch.cuda.is_available():
        gpu_id = int(selected_device.split(":")[-1])
        total_mem = torch.cuda.get_device_properties(gpu_id).total_memory / 1024**3
        used_mem = torch.cuda.memory_allocated(gpu_id) / 1024**3
        st.info(f"GPU Memory: {used_mem:.2f}GB used / {total_mem:.2f}GB total")
    
    # In the sidebar, when GPU is selected
    if "cuda" in selected_device:
        use_half_precision = st.checkbox(
            "Use half precision (FP16)", 
            value=True,
            help="Faster inference with slightly lower precision"
        )
        
        # Update model loading
        with st.spinner("Loading model..."):
            try:
                model = load_model(model_path, device=selected_device)
                
                # Handle half precision
                if use_half_precision:
                    # Convert model to half precision
                    if hasattr(model, 'model'):
                        model.model.half()
                        # Set a flag to indicate half precision is being used
                        model.model.fp16 = True
                        
                        # Force a small inference to ensure model is properly converted
                        import numpy as np
                        dummy = np.zeros((100, 100, 3), dtype=np.uint8)
                        with torch.no_grad():
                            model(dummy, half=True)
                else:
                    # Ensure model is in full precision
                    if hasattr(model, 'model'):
                        # Set flag to indicate full precision
                        model.model.fp16 = False
                
                st.success(f"Model loaded successfully on {selected_device}" + 
                          (" with half precision" if use_half_precision else ""))
            except Exception as e:
                st.error(f"Error loading model: {e}")
                st.stop()
    else:
        # CPU model loading
        with st.spinner("Loading model..."):
            try:
                model = load_model(model_path, device=selected_device)
                st.success(f"Model loaded successfully on {selected_device}")
            except Exception as e:
                st.error(f"Error loading model: {e}")
                st.stop()
    
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
