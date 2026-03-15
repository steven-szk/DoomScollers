import cv2
import os


def capture_image():
    
    save_folder = "captured_images"
    os.makedirs(save_folder, exist_ok=True) 
    # Checks/makes the folder

    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        raise RuntimeError("Could not open camera")

    try:
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture image")
            break
        
        filename = os.path.join(save_folder, f"photo.jpg")
        print(filename)
        cv2.imwrite(filename, frame)

    finally:
        cap.release()
        cv2.destroyAllWindows()