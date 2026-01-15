#!/usr/bin/env python3
"""Download FER2013 dataset samples and convert to images for testing."""

import os
import sys
import csv
import numpy as np
from PIL import Image
from pathlib import Path

# FER2013 emotion labels
EMOTIONS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']

def download_dataset():
    """Download FER2013 dataset from Kaggle."""
    try:
        import kagglehub
        print("Downloading FER2013 dataset from Kaggle...")
        path = kagglehub.dataset_download("msambare/fer2013")
        print(f"Dataset downloaded to: {path}")
        return path
    except Exception as e:
        print(f"Error downloading from Kaggle: {e}")
        print("\nNote: You may need to authenticate with Kaggle.")
        print("Visit https://www.kaggle.com/settings to get your API token.")
        return None

def find_csv_file(dataset_path):
    """Find the FER2013 CSV file in the downloaded dataset."""
    dataset_path = Path(dataset_path)

    # Try common locations
    possible_files = [
        dataset_path / "fer2013.csv",
        dataset_path / "fer2013" / "fer2013.csv",
        dataset_path / "train.csv",
    ]

    for f in possible_files:
        if f.exists():
            return f

    # Search recursively
    for f in dataset_path.rglob("*.csv"):
        return f

    return None

def extract_samples(csv_path, output_dir, samples_per_emotion=3):
    """Extract sample images from FER2013 CSV and save as PNG files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Track samples per emotion
    emotion_counts = {i: 0 for i in range(len(EMOTIONS))}
    extracted = {i: [] for i in range(len(EMOTIONS))}

    print(f"Reading dataset from: {csv_path}")

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # Skip header

        # Find column indices
        emotion_col = header.index('emotion') if 'emotion' in header else 0
        pixels_col = header.index('pixels') if 'pixels' in header else 1

        for row in reader:
            try:
                emotion_idx = int(row[emotion_col])
                pixels = row[pixels_col]

                # Skip if we have enough samples for this emotion
                if emotion_counts[emotion_idx] >= samples_per_emotion:
                    continue

                # Convert pixel string to numpy array
                pixel_values = np.array([int(p) for p in pixels.split()], dtype=np.uint8)

                # Reshape to 48x48 image
                img_array = pixel_values.reshape(48, 48)

                # Create PIL image
                img = Image.fromarray(img_array, mode='L')

                # Upscale to 192x192 for better visibility
                img = img.resize((192, 192), Image.Resampling.LANCZOS)

                # Save image
                emotion_name = EMOTIONS[emotion_idx]
                count = emotion_counts[emotion_idx]
                filename = f"{emotion_name}_{count + 1}.png"
                img_path = output_path / filename
                img.save(img_path)

                emotion_counts[emotion_idx] += 1
                extracted[emotion_idx].append(filename)

                print(f"  Saved: {filename}")

                # Check if we have enough samples
                if all(c >= samples_per_emotion for c in emotion_counts.values()):
                    break

            except Exception as e:
                continue

    print(f"\nExtracted {sum(emotion_counts.values())} sample images")
    return extracted

def try_alternative_source():
    """Try to get FER2013 from alternative sources."""
    # The FER2013 dataset is also available in some Python packages
    try:
        # Try tensorflow datasets
        import tensorflow_datasets as tfds
        ds = tfds.load('fer2013', split='train', as_supervised=True)
        # Process...
    except ImportError:
        pass

    return None

def main():
    # Output directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_dir = project_root / "tests" / "fer2013_samples"

    print("=" * 60)
    print("FER2013 Dataset Sample Extractor")
    print("=" * 60)

    # Try to download from Kaggle
    dataset_path = download_dataset()

    if dataset_path:
        csv_file = find_csv_file(dataset_path)
        if csv_file:
            print(f"\nFound CSV file: {csv_file}")
            extracted = extract_samples(csv_file, output_dir, samples_per_emotion=2)

            print(f"\nSample images saved to: {output_dir}")
            print("\nExtracted emotions:")
            for emotion_idx, files in extracted.items():
                emotion = EMOTIONS[emotion_idx]
                print(f"  {emotion}: {len(files)} samples")

            return True

    print("\nCould not download FER2013 dataset.")
    print("Please download manually from: https://www.kaggle.com/datasets/msambare/fer2013")
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
