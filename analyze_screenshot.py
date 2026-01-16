#!/usr/bin/env python3
"""
Analyze screenshot properties and quality for StructureScout bot.
This script helps validate screenshot captures without viewing the actual image.
"""

import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np

def analyze_screenshot(screenshot_path):
    """
    Analyze a screenshot file and provide detailed information.
    
    Args:
        screenshot_path: Path to the screenshot file
    """
    try:
        # Open the image
        img = Image.open(screenshot_path)
        
        # Get basic info
        width, height = img.size
        mode = img.mode
        format_name = img.format
        
        # Convert to numpy array for analysis
        img_array = np.array(img)
        
        # Calculate basic statistics
        mean_brightness = np.mean(img_array)
        std_brightness = np.std(img_array)
        
        # Check if image is mostly black (possible failed capture)
        black_threshold = 20
        black_pixels = np.sum(np.mean(img_array, axis=2) < black_threshold)
        black_percentage = (black_pixels / (width * height)) * 100
        
        # Check if image is mostly white (possible blank screen)
        white_threshold = 235
        white_pixels = np.sum(np.mean(img_array, axis=2) > white_threshold)
        white_percentage = (white_pixels / (width * height)) * 100
        
        # Color distribution analysis
        if len(img_array.shape) == 3:  # Color image
            r_mean = np.mean(img_array[:, :, 0])
            g_mean = np.mean(img_array[:, :, 1])
            b_mean = np.mean(img_array[:, :, 2])
        else:  # Grayscale
            r_mean = g_mean = b_mean = mean_brightness
        
        print("="*60)
        print("SCREENSHOT ANALYSIS REPORT")
        print("="*60)
        print(f"File: {os.path.basename(screenshot_path)}")
        print(f"Size: {width} x {height} pixels")
        print(f"Mode: {mode}")
        print(f"Format: {format_name}")
        print(f"File size: {os.path.getsize(screenshot_path):,} bytes")
        print()
        print("BRIGHTNESS ANALYSIS:")
        print(f"  Mean brightness: {mean_brightness:.1f} (0=black, 255=white)")
        print(f"  Brightness variation: {std_brightness:.1f}")
        print(f"  Black pixels: {black_percentage:.1f}%")
        print(f"  White pixels: {white_percentage:.1f}%")
        print()
        print("COLOR DISTRIBUTION:")
        print(f"  Red channel avg: {r_mean:.1f}")
        print(f"  Green channel avg: {g_mean:.1f}")
        print(f"  Blue channel avg: {b_mean:.1f}")
        print()
        
        # Quality assessment
        print("QUALITY ASSESSMENT:")
        if black_percentage > 80:
            print("  ⚠️  WARNING: Image is mostly black (possible failed capture)")
        elif white_percentage > 80:
            print("  ⚠️  WARNING: Image is mostly white (possible blank screen)")
        elif std_brightness < 10:
            print("  ⚠️  WARNING: Low brightness variation (possible uniform image)")
        else:
            print("  ✅ GOOD: Image has reasonable brightness variation")
        
        if width >= 1000 and height >= 600:
            print("  ✅ GOOD: Image size is adequate for analysis")
        else:
            print("  ⚠️  WARNING: Image size might be too small for detailed analysis")
        
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"Error analyzing screenshot: {e}")
        return False

def main():
    """Main function."""
    # Find the most recent screenshot
    screenshots_dir = Path("screenshots")
    
    if not screenshots_dir.exists():
        print("Screenshots directory not found!")
        return
    
    # Get all PNG files in screenshots directory and subdirectories
    screenshot_files = []
    for png_file in screenshots_dir.rglob("*.png"):
        screenshot_files.append(png_file)
    
    if not screenshot_files:
        print("No screenshot files found!")
        return
    
    # Sort by modification time (most recent first)
    screenshot_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    # Analyze the most recent screenshot
    latest_screenshot = screenshot_files[0]
    print(f"Analyzing latest screenshot: {latest_screenshot}")
    print()
    
    analyze_screenshot(latest_screenshot)

if __name__ == "__main__":
    main()
