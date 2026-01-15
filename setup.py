"""Setup script for Facial Detection application."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="facial-detection",
    version="1.0.0",
    author="Facial Detection Team",
    description="Real-time facial detection and emotion analysis with deception detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.6.1",
        "opencv-python>=4.9.0",
        "mediapipe>=0.10.9",
        "deepface>=0.0.90",
        "fer>=22.5.1",
        "py-feat>=0.6.0",
        "Pillow>=10.2.0",
        "numpy>=1.26.3",
        "cryptography>=42.0.1",
        "PyYAML>=6.0.1",
        "colorlog>=6.8.2",
        "psutil>=5.9.8",
        "mss>=9.0.1",
    ],
    entry_points={
        "console_scripts": [
            "facial-detection=src.main:main",
        ],
    },
)
