import mediapipe as mp
import cv2


mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)  

def is_not_looking():
    status = []
    for i in range(0,5):
        image_path = f"captured_images/photo_{i}.jpg"

        img = cv2.imread(image_path)
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb)

        if result.multi_face_landmarks:
            for face in result.multi_face_landmarks:

                left_eye  = face.landmark[33]   # left eye outer corner
                right_eye = face.landmark[263]  # right eye outer corner
                nose      = face.landmark[1]    # nose tip

                # head direction check using nose vs eye midpoint
                eye_mid_x = (left_eye.x + right_eye.x) / 2
                offset = nose.x - eye_mid_x

                if offset > 0.05:
                    status.append((True, "Left distraction"))
                elif offset < -0.05:
                    status.append((True, "Right distraction"))
                else:
                    status.append((False, "Locked in"))
        else:
            print("No face detected")
            '''ARE we considering this as a distraction? I think we should, because it means the user is not looking at the screen at all.
            but may be doning other work on the desk, so we can say "Away from desk?" instead of "No face detected"
            status.append((True, "No face detected (Away from desk?)"))
            '''
            
    
    return status


