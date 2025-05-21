
import streamlit as st
import os
import glob
from ultralytics import YOLO

def get_available_models():
    """
    Find available YOLO model files in the current directory and subdirectories
    
    Returns:
        dict: Dictionary with model name as key and path as value
    """
    # Look for .pt files in the current directory and subdirectories
    model_files = glob.glob("*.pt") + glob.glob("**/*.pt", recursive=True)
    
    # Filter out any checkpoint files
    model_files = [f for f in model_files if not "checkpoint" in f.lower()]
    
    # Create a dictionary with model name as key and path as value
    models_dict = {}
    for model_path in model_files:
        model_name = os.path.basename(model_path)
        models_dict[model_name] = model_path
    
    return models_dict

# Load the model
@st.cache_resource
def load_model(model_path):
    """
    Load a YOLO model with caching
    
    Args:
        model_path: Path to the model file
        
    Returns:
        YOLO: Loaded model
    """
    return YOLO(model_path)

