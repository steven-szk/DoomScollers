import cv2
import os

save_folder = "captured_images"
os.makedirs(save_folder, exist_ok=True) 

# Initialize the camera ONCE globally
cap = cv2.VideoCapture(0)

def capture_image():
    """Takes a single picture and saves it."""
    if not cap.isOpened():
        print("Error: Could not open camera")
        return False

    # Grab the frame from the webcam
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture image")
        return False # Use return instead of break!
        
    filename = os.path.join(save_folder, "photo.jpg")
    cv2.imwrite(filename, frame)
    print(f"Pic Saved: {filename}")
    
    return True

def release_camera():
    """Call this from main.py to shut cam down."""
    if cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    # For testing purposes, capture an image and then release the camera
    if capture_image():
        print("Image captured successfully.")
    else:
        print("Image capture failed.")
    
    release_camera()