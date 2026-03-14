import cv2
import os
import time
from datetime import datetime

save_folder = "captured_images"
os.makedirs(save_folder, exist_ok=True)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Could not open camera")

print("Camera started. Taking a picture every 5 seconds.")
print("Press q in the camera window to stop.")

last_capture_time = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture image")
        break

    cv2.imshow("Camera", frame)

    current_time = time.time()
    if current_time - last_capture_time >= 5:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(save_folder, f"photo_{timestamp}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Saved: {filename}")
        last_capture_time = current_time

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
