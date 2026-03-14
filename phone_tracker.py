from ultralytics import YOLO
import threading

model = YOLO("yolov8s.pt")  

PERSON = 0
PHONE  = 67



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





def person_status():
    status = []
    for i in range(0,5):
        image_path = f"captured_images/photo_{i}.jpg"
        # verbose false just stops the model from printing specifics
        for result in model(image_path,verbose=False):
            status.append((True, "Doomscrolling")) if is_on_phone(result) else status.append((False, "Locked in"))
    return status


