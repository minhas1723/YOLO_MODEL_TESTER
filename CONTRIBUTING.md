# Contributing to YOLO Object Detection App

Thank you for considering contributing to this project! Here's how you can help.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## How to Contribute

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Run tests if applicable
5. Commit your changes (`git commit -m 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature`)
7. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/yolo-detection-app.git
cd yolo-detection-app

# Set up development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Adding New Features

- For new model support, add implementation in `src/utils.py`
- For new processing capabilities, extend the appropriate files in `src/`

## Code Style

- Follow PEP 8 guidelines
- Include docstrings for functions and classes
- Write meaningful commit messages