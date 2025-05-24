
import streamlit as st
import os
import glob
from ultralytics import YOLO
import torch

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

def get_available_devices():
    """
    Get available devices for inference
    
    Returns:
        list: List of available devices
    """
    devices = ["cpu"]
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            devices.append(f"cuda:{i}")
    return devices

def warmup_gpu(model):
    """
    Run a warmup inference to initialize GPU memory
    
    Args:
        model: YOLO model
    """
    if hasattr(model, 'device') and 'cuda' in str(model.device):
        import numpy as np
        # Create a dummy image (3 channels, 640x640)
        dummy_input = np.zeros((640, 640, 3), dtype=np.uint8)
        # Run inference to warm up GPU
        with torch.no_grad():
            model(dummy_input)

# Load the model
@st.cache_resource
def load_model(model_path, device='cpu'):
    """
    Load a YOLO model with caching
    
    Args:
        model_path: Path to the model file
        device: Device to run inference on ('cpu', 'cuda:0', etc.)
        
    Returns:
        YOLO: Loaded model
    """
    # Load model in full precision first
    model = YOLO(model_path).to(device)
    
    # Run a warmup inference in full precision
    warmup_gpu(model)
    
    return model

