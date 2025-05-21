import streamlit as st
import time
import os
import tempfile
from io import BytesIO

# Import from our modules
from src.video_compression import compress_video
from src.video_detection import process_video
from src.video_utils import (
    initialize_session_state, 
    reset_session_state, 
    get_video_bytes_from_session,
    create_temp_file_from_upload,
    clean_up_temp_file
)
from src.video_ui import (
    render_video_upload_section,
    render_video_options_section,
    render_processing_buttons,
    render_processing_progress,
    render_video_comparison_section,
    render_video_players,
    render_detection_stats,
    render_download_options,
    render_reset_button
)

def process_video_file(model, conf_threshold, show_labels, show_conf, process_every_nth_frame):
    """
    Main function to handle video file upload and processing
    
    Args:
        model: YOLO model
        conf_threshold: Confidence threshold
        show_labels: Whether to show labels
        show_conf: Whether to show confidence scores
        process_every_nth_frame: Process every Nth frame to speed up inference
    """
    # Initialize session state
    initialize_session_state()
    
    # Render video upload section
    uploaded_file = render_video_upload_section()
    
    # Store uploaded file in session state
    if uploaded_file is not None:
        if st.session_state.uploaded_file_data is None:
            st.session_state.uploaded_file_data = uploaded_file.getvalue()
    
    # If we have an uploaded file (either from this run or stored in session state)
    if uploaded_file is not None or st.session_state.uploaded_file_data is not None:
        # Create a temporary file to save the uploaded video if needed
        video_path = None
        if uploaded_file is not None:
            video_path = create_temp_file_from_upload(uploaded_file)
        
        # Render video options section
        use_compression, target_resolution, target_fps, quality = render_video_options_section()
        
        # Only show processing buttons if we haven't processed a video yet
        if st.session_state.output_video_path is None:
            # Render processing buttons
            start_processing, stop_processing = render_processing_buttons()
            
            # Handle stop button click
            if stop_processing and st.session_state.processing:
                st.session_state.processing = False
                st.warning("Processing stopped by user")
                st.stop()  # This stops execution of the script
            
            # Process video when start button is clicked
            if start_processing or st.session_state.processing:
                # Set processing state to true
                st.session_state.processing = True
                
                process_video_path = video_path
                
                # Compress video if option is selected
                if use_compression and video_path:
                    with st.spinner("Compressing video..."):
                        compressed_video_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
                        compression_success = compress_video(
                            video_path, 
                            compressed_video_path, 
                            resolution=target_resolution,
                            quality=quality,
                            fps=target_fps
                        )
                        
                        if compression_success:
                            # Use the compressed video for processing
                            process_video_path = compressed_video_path
                            st.success("Video compressed successfully!")
                        else:
                            # Fall back to original if compression fails
                            st.warning("Video compression failed. Using original video.")
                
                # Run inference on video
                with st.spinner("Processing video... This may take a while depending on the video length"):
                    # Create a progress placeholder
                    progress_placeholder = render_processing_progress("Starting video processing...")
                    
                    start_time = time.time()
                    
                    # Check if processing should continue
                    if not st.session_state.processing:
                        st.warning("Processing stopped by user")
                        st.stop()
                    
                    # Process the video
                    output_video_path, detection_stats = process_video(
                        process_video_path, model, conf_threshold, show_labels, show_conf, process_every_nth_frame
                    )
                    
                    # Store results in session state
                    st.session_state.output_video_path = output_video_path
                    st.session_state.detection_stats = detection_stats
                    st.session_state.processing_time = time.time() - start_time
                    
                    # Reset processing state
                    st.session_state.processing = False
                    
                    # Display processing information
                    progress_placeholder.success(f"Processing completed in {st.session_state.processing_time:.2f} seconds")
                
                # Clean up temporary files
                if use_compression and 'compressed_video_path' in locals() and os.path.exists(compressed_video_path):
                    clean_up_temp_file(compressed_video_path)
                
                # Clean up the original video file
                if video_path and os.path.exists(video_path):
                    clean_up_temp_file(video_path)
        
        # Display results if we have processed a video (either in this run or a previous one)
        if st.session_state.output_video_path is not None and os.path.exists(st.session_state.output_video_path):
            # Render video comparison section
            sync_play = render_video_comparison_section(st.session_state.processing_time)
            
            # Get video bytes from session state
            original_video_bytes = get_video_bytes_from_session()
            
            # Render video players
            render_video_players(
                original_video_bytes, 
                st.session_state.output_video_path, 
                st.session_state.sync_time
            )
            
            # Render detection statistics
            render_detection_stats(
                st.session_state.detection_stats, 
                st.session_state.processing_time
            )
            
            # Render download options
            render_download_options(
                st.session_state.output_video_path,
                st.session_state.detection_stats
            )
            
            # Render reset button
            if render_reset_button():
                # Reset session state
                reset_session_state()
                st.experimental_rerun()
                
        elif st.session_state.output_video_path is not None:
            st.error("Video processing completed but the output file is no longer available. Please try again.")
            # Reset the output path since the file is no longer available
            st.session_state.output_video_path = None
    else:
        st.info("Please upload a video to get started.")
