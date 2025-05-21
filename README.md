
# YOLO Object Detection App

A Streamlit-based application for object detection in images and videos using YOLO models.

## Features

- Support for multiple YOLO model variants
- Image and video processing
- Adjustable confidence thresholds
- Customizable display options

## Installation

This application was tested with Python 3.11. You can use conda to easily set up the correct Python version:

```bash
# Clone the repository
git clone https://github.com/yourusername/yolo-detection-app.git
cd yolo-detection-app

# Create and activate conda environment with Python 3.11
conda create -n yolo-app python=3.11
conda activate yolo-app

# Install dependencies
pip install -r requirements.txt
```

Alternatively, if you prefer using venv:

```bash
# Create and activate virtual environment (if you already have Python 3.11)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

## Adding Your Own Models

The application automatically detects and loads any YOLO model files (`.pt`) in the project directory:

1. Copy your trained YOLO model files anywhere in the project directory
   - Example locations: `models/mymodel.pt`, `yolov8_models/custom_model.pt`
2. Use descriptive filenames as they will appear in the model selection dropdown
3. Models are detected recursively, so you can organize them in subdirectories
4. Restart the application to see your new models in the selection menu

Example:
```
yolo-detection-app/
├── models/
│   ├── my_custom_model.pt       # Will appear as "my_custom_model" in dropdown
│   └── specialized/
│       └── face_detection.pt    # Will appear as "face_detection" in dropdown
├── app.py
└── ...
```

## Project Structure

- `app.py`: Main application file
- `src/`: Source code directory
  - `utils.py`: Utility functions
  - `image_processing.py`: Image processing functions
  - `video_processing.py`: Video processing functions
- `yolov8_models/`: Directory containing trained models

## Contributing

We welcome contributions to improve this project! Please follow these steps:

1. Check the [open issues](https://github.com/yourusername/yolo-detection-app/issues) or create a new one to discuss your ideas
2. Fork the repository and create a branch following our naming conventions
3. Make your changes following our code style guidelines
4. Submit a pull request with a clear description of the changes

For detailed instructions, please read our [contribution guidelines](CONTRIBUTING.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

