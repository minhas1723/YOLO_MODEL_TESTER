# Contributing to YOLO Object Detection App

Thank you for considering contributing to this project! Here's how you can help.

## Code of Conduct

Please be respectful and considerate of others when contributing to this project.

## Branch Naming Conventions

Please follow these naming conventions for branches:
* `feature/short-description` - For new features
* `bugfix/issue-number-description` - For bug fixes
* `docs/what-you-changed` - For documentation changes
* `refactor/component-name` - For code refactoring

Examples:
* `feature/add-yolov9-support`
* `bugfix/42-fix-video-processing`
* `docs/update-installation-guide`
* `refactor/image-processing-module`

## How to Contribute

1. Fork the repository
2. Create a new branch following the naming convention above
3. Make your changes
4. Run tests if applicable
5. Commit your changes with meaningful commit messages
6. Push to your branch
7. Open a Pull Request with a clear description of the changes

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

## Code Style

* Follow PEP 8 guidelines
* Include docstrings for functions and classes
* Write meaningful commit messages