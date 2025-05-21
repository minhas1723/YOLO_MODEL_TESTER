import streamlit as st
import time
import os
from io import BytesIO

def render_video_upload_section():
    """
    Render the video upload section
    
    Returns:
        object: Uploaded file object or None
    """
    return st.file_uploader("Choose a video...", type=["mp4", "avi", "mov", "mkv"])

def render_video_options_section():
    """
    Render the video processing options section
    
    Returns:
        tuple: (use_compression, target_resolution, target_fps, quality)
    """
    with st.expander("Video Processing Options", expanded=True):
        use_compression = st.checkbox("Compress video before processing (faster)", value=True)
        
        col1, col2 = st.columns(2)
        with col1:
            target_resolution = st.select_slider(
                "Target Resolution",
                options=[240, 360, 480, 720, 1080],
                value=480,
                help="Lower resolution = faster processing"
            )
        
        with col2:
            target_fps = st.slider(
                "Target FPS", 
                min_value=1, 
                max_value=30, 
                value=15,
                help="Lower FPS = faster processing"
            )
        
        quality = st.slider(
            "Video Quality", 
            min_value=18, 
            max_value=28, 
            value=23,
            help="Higher value = lower quality but smaller file (18-28 recommended)"
        )
    
    return use_compression, target_resolution, target_fps, quality

def render_processing_buttons():
    """
    Render the start and stop processing buttons
    
    Returns:
        tuple: (start_processing, stop_processing)
    """
    col1, col2 = st.columns(2)
    
    # Start button in the first column
    start_processing = col1.button("Start Processing", type="primary", key="start_video")
    
    # Stop button in the second column (only enabled during processing)
    stop_processing = col2.button(
        "Stop Processing", 
        disabled=not st.session_state.processing,
        key="stop_video"
    )
    
    return start_processing, stop_processing

def render_processing_progress(message):
    """
    Render a progress placeholder with a message
    
    Args:
        message: Message to display
        
    Returns:
        object: Streamlit empty placeholder
    """
    progress_placeholder = st.empty()
    progress_placeholder.info(message)
    return progress_placeholder

def render_video_comparison_section(processing_time):
    """
    Render the video comparison section
    
    Args:
        processing_time: Video processing time in seconds
    
    Returns:
        bool: Whether the sync button was clicked
    """
    st.subheader("Video Comparison")
    
    # Simple layout for the sync button
    st.write("Use this button to play both videos at the same time:")
    sync_play = st.button("▶️ Play Both Videos Simultaneously", type="primary", key="sync_play")
    start_time = st.slider(
        "Start Time (seconds)", 
        min_value=0.0, 
        max_value=float(processing_time) if processing_time > 0 else 100.0,
        value=0.0,
        step=1.0,
        key="sync_start_time"
    )
    
    # Update sync time when button is clicked
    if sync_play:
        st.session_state.sync_time = start_time
        st.success(f"Starting both videos at {start_time} seconds")
        # Add a countdown to help users synchronize manual clicking
        countdown_placeholder = st.empty()
        for i in range(3, 0, -1):
            countdown_placeholder.warning(f"Get ready to click play on both videos in {i}...")
            time.sleep(1)
        countdown_placeholder.success("Click play on both videos NOW!")
    
    return sync_play

def render_video_players(original_video_bytes, processed_video_path, sync_time):
    """
    Render the original and processed video players
    
    Args:
        original_video_bytes: BytesIO object containing original video
        processed_video_path: Path to processed video
        sync_time: Start time for videos in seconds
    """
    # Display the original and processed videos side by side
    result_col1, result_col2 = st.columns(2)
    
    with result_col1:
        st.subheader("Original Video")
        if original_video_bytes is not None:
            st.video(original_video_bytes, start_time=int(sync_time))
    
    with result_col2:
        st.subheader("Detection Results")
        st.video(processed_video_path, start_time=int(sync_time))
    
    # Add instructions for manual synchronization
    st.info("📝 **Note**: Due to browser security policies, videos can't be automatically played. "
            "The sync button positions both videos at the same timestamp, but you'll need to "
            "click play on each video manually. Try to click both play buttons at the same time for best synchronization.")

def render_detection_stats(detection_stats, processing_time):
    """
    Render the detection statistics section
    
    Args:
        detection_stats: DataFrame containing detection statistics
        processing_time: Video processing time in seconds
    """
    st.subheader("Detection Statistics")
    st.write(f"Processing time: {processing_time:.2f} seconds")
    
    if detection_stats is not None and not detection_stats.empty:
        # Create tabs for different views of the data
        basic_tab, detailed_tab = st.tabs(["Basic Stats", "Detailed Stats"])
        
        with basic_tab:
            # Display simplified statistics
            basic_stats = detection_stats[['Class', 'Count', 'Avg_Confidence']]
            st.dataframe(basic_stats, use_container_width=True)
            
            # Summary visualization
            st.subheader("Detection Summary")
            cols = st.columns(min(len(detection_stats), 4))
            for i, (_, row) in enumerate(detection_stats.iterrows()):
                col_idx = i % len(cols)
                cols[col_idx].metric(
                    f"Total {row['Class']}s", 
                    row['Count'],
                    f"Avg conf: {row['Avg_Confidence']}"
                )
        
        with detailed_tab:
            # Display all statistics
            st.dataframe(detection_stats, use_container_width=True)
            
            # Add a timeline visualization if there are enough detections
            if len(detection_stats) > 0:
                st.subheader("Object Timeline")
                st.write("When objects were first and last seen in the video:")
                
                # Create a simple timeline visualization
                for _, row in detection_stats.iterrows():
                    st.write(f"**{row['Class']}**: {row['First_Seen']} → {row['Last_Seen']}")
    else:
        st.info("No objects detected in the video.")

def render_download_options(processed_video_path, detection_stats):
    """
    Render download options for processed video and stats
    
    Args:
        processed_video_path: Path to processed video
        detection_stats: DataFrame containing detection statistics
    """
    # Option to download the processed video
    if processed_video_path and os.path.exists(processed_video_path):
        with open(processed_video_path, "rb") as file:
            st.download_button(
                label="Download Processed Video",
                data=file,
                file_name="processed_video.mp4",
                mime="video/mp4",
                key="download-video"
            )
    
    # Option to download detection stats as CSV
    if detection_stats is not None and not detection_stats.empty:
        st.download_button(
            "Download Results as CSV",
            detection_stats.to_csv(index=False).encode('utf-8'),
            "video_detection_results.csv",
            "text/csv",
            key='download-video-csv'
        )

def render_reset_button():
    """
    Render a button to reset the video processing state
    
    Returns:
        bool: Whether the reset button was clicked
    """
    return st.button("Process Another Video", key="reset_video")
