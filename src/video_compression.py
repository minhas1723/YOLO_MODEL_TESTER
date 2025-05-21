import cv2
import os
from stqdm import stqdm
import streamlit as st

def compress_video(input_path, output_path, resolution=480, quality=23, fps=None):
    """
    Compress video to reduce processing time
    
    Args:
        input_path: Path to input video
        output_path: Path to output compressed video
        resolution: Target height (width will be calculated to maintain aspect ratio)
        quality: FFmpeg CRF value (0-51, lower means better quality, 23 is default)
        fps: Target FPS (None means keep original)
    
    Returns:
        bool: Success or failure
    """
    try:
        # Open the video
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            return False
            
        # Get original video properties
        orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        orig_fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate new dimensions while maintaining aspect ratio
        if orig_height > resolution:
            scale_factor = resolution / orig_height
            new_width = int(orig_width * scale_factor)
            new_height = resolution
        else:
            new_width = orig_width
            new_height = orig_height
        
        # Use original fps if not specified
        target_fps = fps if fps is not None else orig_fps
        
        # Create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, target_fps, (new_width, new_height))
        
        # Process frames with progress bar
        for _ in stqdm(range(total_frames), desc="Compressing video"):
            ret, frame = cap.read()
            if not ret:
                break
                
            # Resize frame
            resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Write frame
            out.write(resized_frame)
        
        # Release resources
        cap.release()
        out.release()
        
        return True
    except Exception as e:
        st.error(f"Error compressing video: {e}")
        return False