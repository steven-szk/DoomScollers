import mediapipe as mp
import cv2
import numpy as np

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, refine_landmarks=True)

# 3D model points of a generic face
MODEL_POINTS = np.array([
    (0.0,   0.0,    0.0),    # Nose tip (1)
    (0.0,  -330.0, -65.0),   # Chin (152)
    (-225.0, 170.0, -135.0), # Left eye corner (263)
    (225.0,  170.0, -135.0), # Right eye corner (33)
    (-150.0, -150.0, -125.0),# Left mouth corner (287)
    (150.0,  -150.0, -125.0) # Right mouth corner (57)
], dtype=np.float64)

LANDMARK_IDS = [1, 152, 263, 33, 287, 57]

def get_head_pose(face, img_w, img_h):
    image_points = np.array([
        (face.landmark[i].x * img_w, face.landmark[i].y * img_h)
        for i in LANDMARK_IDS
    ], dtype=np.float64)

    focal_length = img_w
    cam_matrix = np.array([
        [focal_length, 0, img_w / 2],
        [0, focal_length, img_h / 2],
        [0, 0, 1]
    ], dtype=np.float64)

    dist_coeffs = np.zeros((4, 1))

    _, rvec, _ = cv2.solvePnP(MODEL_POINTS, image_points, cam_matrix, dist_coeffs)
    rmat, _ = cv2.Rodrigues(rvec)
    angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)

    pitch, yaw, roll = angles
    return pitch, yaw, roll

def is_not_looking():
    status = []
    for i in range(5):
        image_path = f"captured_images/photo_{i}.jpg"
        img = cv2.imread(image_path)
        if img is None:
            status.append((True, "Image not found"))
            continue

        h, w = img.shape[:2]
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(rgb)

        if result.multi_face_landmarks:
            for face in result.multi_face_landmarks:
                pitch, yaw, roll = get_head_pose(face, w, h)

                if yaw > 15:
                    status.append((True, "Looking right"))
                elif yaw < -15:
                    status.append((True, "Looking left"))
                elif pitch > 15:
                    status.append((True, "Looking up"))
                elif pitch < -15:
                    status.append((False, "Looking down"))
                else:
                    status.append((False, "Locked in"))
        else:
            status.append((True, "Away from screen"))

    return status


print(is_not_looking())