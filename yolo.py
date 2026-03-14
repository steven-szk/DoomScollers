from ultralytics import YOLO

model = YOLO("yolov8n.pt")  

PERSON = 0
PHONE  = 67

image_path = "captured_images/photo_4.jpg"


def is_on_phone(result):
    boxes = result.boxes
    persons = boxes[boxes.cls == PERSON].xyxy
    phones  = boxes[boxes.cls == PHONE].xyxy

    for person in persons:
        for phone in phones:
            # check if the phone object overlaps the person object
            overlap_x = (phone[0] < person[2]) and (phone[2] > person[0])
            overlap_y = (phone[1] < person[3]) and (phone[3] > person[1])
            if overlap_x and overlap_y:
                return True 
    return False  

for result in model(image_path):
    status = "Doomscrolling" if is_on_phone(result) else "Locked in"
    print(status)


