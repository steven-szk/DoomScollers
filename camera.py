import cv2
import os
import time

save_folder = "captured_images"
os.makedirs(save_folder, exist_ok=True)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Could not open camera")

print("Camera started. Taking a picture every 5 seconds.")
print("Only 5 files will be kept at once.")
print("Press Ctrl+C to stop.")

capture_count = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        file_index = capture_count % 5
        filename = os.path.join(save_folder, f"photo_{file_index}.jpg")

        cv2.imwrite(filename, frame)
        print(f"Saved: {filename}")

        capture_count += 1
        time.sleep(5)
        
        '''
        change sleep to non blocking code pls, so that we can capture images while the main.py is running and analyzing the images.
        we can use time.time() to check the elapsed time and capture images every 5 seconds
        '''

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    cap.release()
    cv2.destroyAllWindows()