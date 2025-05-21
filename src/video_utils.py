
import os
import tempfile
import streamlit as st
from io import BytesIO

def create_temp_file_from_upload(uploaded_file):
    """
    Create a temporary file from an uploaded file
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        str: Path to temporary file
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name

def clean_up_temp_file(file_path):
    """
    Safely delete a temporary file
    
    Args:
        file_path: Path to file to delete
        
    Returns:
        bool: Success or failure
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
        return True
    except Exception as e:
        st.error(f"Error cleaning up temporary file: {e}")
        return False

def get_video_bytes_from_session():
    """
    Get video bytes from session state
    
    Returns:
        BytesIO: BytesIO object containing video data or None
    """
    if st.session_state.uploaded_file_data is not None:
        return BytesIO(st.session_state.uploaded_file_data)
    return None

def initialize_session_state():
    """
    Initialize session state variables for video processing
    """
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'sync_time' not in st.session_state:
        st.session_state.sync_time = 0
    if 'output_video_path' not in st.session_state:
        st.session_state.output_video_path = None
    if 'detection_stats' not in st.session_state:
        st.session_state.detection_stats = None
    if 'processing_time' not in st.session_state:
        st.session_state.processing_time = 0
    if 'uploaded_file_data' not in st.session_state:
        st.session_state.uploaded_file_data = None

def reset_session_state():
    """
    Reset session state variables for video processing
    """
    st.session_state.output_video_path = None
    st.session_state.detection_stats = None
    st.session_state.processing_time = 0
    st.session_state.uploaded_file_data = None
    st.session_state.sync_time = 0

