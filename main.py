import mss
import cv2
import numpy as np
import easyocr
import csv
import time
import os
from datetime import datetime

# Load the regions of interest (ROIs) from the file
def load_rois():
    regions = []
    with open('rois.txt', 'r') as file:
        for line in file.readlines():
            top, left, width, height = map(int, line.strip().split(','))
            regions.append({'top': top, 'left': left, 'width': width, 'height': height})
    return regions

# Capture the screen based on a region (ROI)
def capture_roi(region):
    with mss.mss() as sct:
        monitor = {"top": region['top'], "left": region['left'], "width": region['width'], "height": region['height']}
        screen = sct.grab(monitor)
        img = np.array(screen)
        return img

# Extract text from an image using EasyOCR
def extract_text_from_image(img, reader):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    result = reader.readtext(gray_img)
    return result

# Save data to CSV
def save_to_csv(data, csv_filename='readings.csv'):
    file_exists = os.path.isfile(csv_filename)
    with open(csv_filename, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            # Write header only if the file does not exist
            writer.writerow(['Timestamp'] + [f"ROI {i+1} Text" for i in range(len(data))])
        writer.writerow([datetime.now()] + data)

# Main function to capture readings every 500ms and log them to CSV
def main():
    reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader for English language
    regions = load_rois()  # Load the regions of interest from file

    # Capture readings from ROIs every 500ms
    try:
        while True:
            # Check for stop logging flag
            if os.path.exists('stop_logging.txt'):
                with open('stop_logging.txt', 'r') as f:
                    if f.read().strip() == 'stop':
                        print("Stopping capture process.")
                        os.remove('stop_logging.txt')
                        break

            readings = []
            for region in regions:
                img = capture_roi(region)  # Capture the screen from the region
                text_data = extract_text_from_image(img, reader)  # Extract text from the image
                text_result = ' '.join([text[1] for text in text_data]) if text_data else ''
                readings.append(text_result)

            save_to_csv(readings)
            time.sleep(0.5)  # Pause for 500ms between readings

    except KeyboardInterrupt:
        print("Terminating due to keyboard interrupt.")

if __name__ == "__main__":
    main()
