import streamlit as st
import tempfile
import os
import cv2
import pandas as pd
from PIL import Image

def process_image(model, conf_threshold, show_labels, show_conf):
    """
    Process image with object detection
    
    Args:
        model: YOLO model
        conf_threshold: Confidence threshold
        show_labels: Whether to show labels
        show_conf: Whether to show confidence scores
    """
    # File uploader for images
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display original image
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Create a temporary file to save the uploaded image
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            img_path = tmp_file.name
        
        # Run inference
        with st.spinner("Detecting objects..."):
            # Load image with OpenCV (BGR format)
            cv_image = cv2.imread(img_path)
            # Convert to RGB for the model
            rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            # Run detection
            results = model(rgb_image, conf=conf_threshold)
        
        # Display results
        with col2:
            st.subheader("Detection Results")
            # Get the first result (only one image)
            result = results[0]
            # Plot the result (returns RGB image)
            res_plotted = result.plot(conf=show_conf, labels=show_labels, line_width=2)
            # Display the RGB image directly with Streamlit
            st.image(res_plotted, caption="Detection Result", use_column_width=True)
        
        # Display detection details
        st.subheader("Detection Details")
        
        if len(result.boxes) > 0:
            # Create a table with detection details
            boxes = result.boxes.cpu().numpy()
            
            # Create a DataFrame for better display
            detections_data = []
            
            for i, box in enumerate(boxes):
                cls_id = int(box.cls[0])
                # Get class name from model or use index if not available
                class_name = model.names.get(cls_id, f"Class {cls_id}") if hasattr(model, 'names') else f"Class {cls_id}"
                conf = float(box.conf[0])
                coords = box.xyxy[0].tolist()  # Get box coordinates [x1, y1, x2, y2]
                
                detections_data.append({
                    "ID": i+1,
                    "Class": class_name,
                    "Confidence": f"{conf:.2f}",
                    "Location": f"[{int(coords[0])}, {int(coords[1])}, {int(coords[2])}, {int(coords[3])}]"
                })
            
            # Display as a styled table
            if detections_data:
                df = pd.DataFrame(detections_data)
                st.dataframe(df, use_container_width=True)
                
                # Summary statistics
                st.subheader("Detection Summary")
                class_counts = {}
                for item in detections_data:
                    class_name = item["Class"]
                    class_counts[class_name] = class_counts.get(class_name, 0) + 1
                
                # Create metrics for each detected class
                cols = st.columns(min(len(class_counts), 4))  # Up to 4 columns
                for i, (cls_name, count) in enumerate(class_counts.items()):
                    col_idx = i % len(cols)
                    cols[col_idx].metric(f"Total {cls_name}s", count)
                
                # Export options
                st.download_button(
                    "Download Results as CSV",
                    df.to_csv(index=False).encode('utf-8'),
                    "detection_results.csv",
                    "text/csv",
                    key='download-csv'
                )
                
                # Display JSON option
                with st.expander("View Results as JSON"):
                    st.json(result.tojson())
        else:
            st.info("No objects detected in the image.")
        
        # Clean up the temporary file
        os.unlink(img_path)
    else:
        st.info("Please upload an image to get started.")