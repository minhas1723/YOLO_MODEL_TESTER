import cv2
import tempfile
import os
import pandas as pd
import streamlit as st
from stqdm import stqdm
import subprocess

def process_video(video_path, model, conf_threshold, show_labels, show_conf, process_every_nth_frame=1, batch_size=1):
    """
    Process video file with object detection
    
    Args:
        video_path: Path to video file
        model: YOLO model
        conf_threshold: Confidence threshold
        show_labels: Whether to show labels
        show_conf: Whether to show confidence scores
        process_every_nth_frame: Process every Nth frame to speed up inference
        batch_size: Number of frames to process in a batch (for GPU acceleration)
        
    Returns:
        tuple: (output_path, detection_stats)
    """
    # Create a temporary file for the output video
    temp_output_path = tempfile.NamedTemporaryFile(delete=False, suffix='_temp.mp4').name
    final_output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
    
    # Get video properties
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("Could not open video file")
        return None, None
        
    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Create VideoWriter with mp4v codec (we'll convert it later)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_output_path, fourcc, fps, (frame_width, frame_height))
    
    if not out.isOpened():
        st.error("Failed to create output video writer")
        return None, None
    
    # Process the results
    all_detections = []
    
    # Create a progress bar
    progress_bar = stqdm(total=total_frames, desc="Processing video")
    
    # Process frame by frame
    frame_count = 0
    last_result = None
    
    # Check if model is using half precision
    is_half_precision = False
    if hasattr(model, 'model'):
        if hasattr(model.model, 'fp16'):
            is_half_precision = model.model.fp16
        # Check if any parameter is in half precision
        elif next(model.model.parameters()).dtype == torch.float16:
            is_half_precision = True
    
    # If using half precision, ensure the model knows it
    if is_half_precision and hasattr(model, 'model'):
        model.model.fp16 = True
    
    # Check if processing should continue (for stop button functionality)
    while cap.isOpened() and st.session_state.get('processing', True):
        ret, frame = cap.read()
        if not ret:
            break
            
        # Only process every Nth frame to speed up inference
        if frame_count % process_every_nth_frame == 0:
            try:
                # Run detection on the frame with appropriate precision
                if is_half_precision:
                    # For half precision models, explicitly set half=True
                    results = model(frame, conf=conf_threshold, half=True)
                else:
                    # For full precision models
                    results = model(frame, conf=conf_threshold)
                
                last_result = results[0]  # Store the result for reuse
                
                # Collect detection stats
                if len(last_result.boxes) > 0:
                    boxes = last_result.boxes.cpu().numpy()
                    
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        class_name = model.names.get(cls_id, f"Class {cls_id}") if hasattr(model, 'names') else f"Class {cls_id}"
                        conf = float(box.conf[0])
                        
                        # Add to all detections
                        all_detections.append({
                            "Class": class_name,
                            "Confidence": conf,
                            "Frame": frame_count,
                            "Time": frame_count / fps  # Add timestamp in seconds
                        })
            except Exception as e:
                st.error(f"Error processing frame {frame_count}: {e}")
                # Continue with last result if there's an error
        
        # Plot the results on the current frame
        try:
            if last_result is not None:
                # Update the result's image to the current frame before plotting
                original_img = last_result.orig_img  # Save the original image
                last_result.orig_img = frame  # Replace with current frame
                annotated_frame = last_result.plot(conf=show_conf, labels=show_labels, line_width=2)
                last_result.orig_img = original_img  # Restore the original image
            else:
                # If we don't have any results yet, just use the current frame
                annotated_frame = frame
            
            # Write the annotated frame to the output video
            out.write(annotated_frame)
        except Exception as e:
            st.error(f"Error annotating frame {frame_count}: {e}")
            # Write the original frame if annotation fails
            out.write(frame)
        
        # Update progress bar
        progress_bar.update(1)
        frame_count += 1
    
    # Close progress bar
    progress_bar.close()
    
    # Release resources
    cap.release()
    out.release()
    
    # Convert the video to a web-compatible format using FFmpeg
    try:
        with st.spinner("Converting video to web-compatible format..."):
            # Command to convert video to H.264 with reasonable bitrate and web compatibility
            cmd = [
                'ffmpeg',
                '-i', temp_output_path,  # Input file
                '-c:v', 'libx264',       # H.264 codec
                '-preset', 'fast',       # Encoding speed/compression tradeoff
                '-crf', '23',            # Constant Rate Factor (quality) - lower is better
                '-pix_fmt', 'yuv420p',   # Pixel format for maximum compatibility
                '-movflags', '+faststart', # Optimize for web streaming
                '-y',                    # Overwrite output file if it exists
                final_output_path        # Output file
            ]
            
            # Run the FFmpeg command
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            _, stderr = process.communicate()
            
            # Check if conversion was successful
            if process.returncode != 0:
                st.error(f"Error converting video: {stderr}")
                # Fall back to the original output if conversion fails
                final_output_path = temp_output_path
            else:
                # Clean up the temporary file
                try:
                    os.unlink(temp_output_path)
                except Exception as e:
                    st.warning(f"Could not remove temporary file: {e}")
    except Exception as e:
        st.error(f"Error during video conversion: {e}")
        # Fall back to the original output if conversion fails
        final_output_path = temp_output_path
    
    # Convert detection statistics to DataFrame for display
    if all_detections:
        # Group by class and calculate average confidence
        stats_df = pd.DataFrame(all_detections)
        
        # Add more detailed statistics
        class_stats = stats_df.groupby('Class').agg(
            Count=('Class', 'count'),
            Avg_Confidence=('Confidence', 'mean'),
            Min_Confidence=('Confidence', 'min'),
            Max_Confidence=('Confidence', 'max'),
            First_Seen=('Time', 'min'),
            Last_Seen=('Time', 'max')
        ).reset_index()
        
        # Format the values
        class_stats['Avg_Confidence'] = class_stats['Avg_Confidence'].apply(lambda x: f"{x:.2f}")
        class_stats['Min_Confidence'] = class_stats['Min_Confidence'].apply(lambda x: f"{x:.2f}")
        class_stats['Max_Confidence'] = class_stats['Max_Confidence'].apply(lambda x: f"{x:.2f}")
        class_stats['First_Seen'] = class_stats['First_Seen'].apply(lambda x: f"{x:.1f}s")
        class_stats['Last_Seen'] = class_stats['Last_Seen'].apply(lambda x: f"{x:.1f}s")
    else:
        class_stats = pd.DataFrame(columns=['Class', 'Count', 'Avg_Confidence', 'Min_Confidence', 'Max_Confidence', 'First_Seen', 'Last_Seen'])
    
    return final_output_path, class_stats
