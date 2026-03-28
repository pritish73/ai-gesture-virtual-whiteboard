import cv2
import numpy as np
import mediapipe as mp
import time
import os

# ===== COLOR PALETTE =====
def create_color_palette(width=400, height=100):
    palette = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(width):
        hue = int(180 * i / width)
        color = np.array([[[hue, 255, 255]]], dtype=np.uint8)
        bgr = cv2.cvtColor(color, cv2.COLOR_HSV2BGR)[0][0]
        palette[:, i] = bgr
    return palette

# ===== CREATE SAVE FOLDER =====
save_folder = "drawings"
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Camera
camera = cv2.VideoCapture(0)
camera.set(3, 1280)
camera.set(4, 720)

# Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
drawer = mp.solutions.drawing_utils

# Canvas
board = np.zeros((720, 1280, 3), dtype=np.uint8)

last_x, last_y = 0, 0
pen_size = 10
eraser_size = 50

# FPS
prev_time = 0

# Save message
save_msg = ""
save_time = 0

# Palette
palette = create_color_palette()
pen_color = (255, 0, 255)

def check_fingers(points):
    fingers = []
    fingers.append(points[4][1] > points[3][1])
    for tip in [8, 12, 16, 20]:
        fingers.append(points[tip][2] < points[tip - 2][2])
    return fingers


while True:
    ret, frame = camera.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    # FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if curr_time != prev_time else 0
    prev_time = curr_time

    # ===== TOOLBAR =====
    cv2.rectangle(frame, (0, 0), (1280, 100), (40, 40, 40), -1)

    # Palette
    frame[0:100, 100:500] = palette

    # Color preview
    cv2.rectangle(frame, (520, 10), (600, 90), pen_color, -1)
    cv2.putText(frame, "COLOR", (520, 105),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

    # Title (top-right for better UI)
    cv2.putText(frame, "AI WHITEBOARD",
                (900, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200,200,200), 2)

    if result.multi_hand_landmarks:
        hand = result.multi_hand_landmarks[0]
        h, w, _ = frame.shape
        landmarks = []

        for idx, lm in enumerate(hand.landmark):
            x, y = int(lm.x * w), int(lm.y * h)
            landmarks.append((idx, x, y))

        drawer.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        fingers = check_fingers(landmarks)
        x, y = landmarks[8][1], landmarks[8][2]

        # ===== COLOR PICK =====
        if y < 100 and 100 < x < 500:
            selected = palette[y, x - 100]
            pen_color = tuple(int(c) for c in selected)
            last_x, last_y = 0, 0

        # ===== DRAW =====
        elif fingers[1] and not fingers[2] and not fingers[3]:

            cv2.circle(frame, (x, y), pen_size, pen_color, 2)

            if last_x == 0 and last_y == 0:
                last_x, last_y = x, y

            # Smooth drawing
            mid_x = (last_x + x) // 2
            mid_y = (last_y + y) // 2

            cv2.line(board, (last_x, last_y), (mid_x, mid_y), pen_color, pen_size)

            last_x, last_y = x, y

        # ===== ERASE =====
        elif fingers[1] and fingers[2] and fingers[3]:

            cv2.circle(frame, (x, y), eraser_size // 2, (0,0,0), 2)

            if last_x == 0 and last_y == 0:
                last_x, last_y = x, y

            cv2.line(board, (last_x, last_y), (x, y), (0,0,0), eraser_size)

            last_x, last_y = x, y

        # ===== CLEAR =====
        elif all(fingers):
            board[:] = 0

        else:
            last_x, last_y = 0, 0

    # Blend
    frame = cv2.addWeighted(frame, 0.7, board, 0.3, 0)

    # Text
    cv2.putText(frame, "INDEX: DRAW | THREE: ERASE | ALL: CLEAR",
                (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    cv2.putText(frame, "Press S to Save | ESC to Exit",
                (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 1)

    # FPS
    cv2.putText(frame, f'FPS: {int(fps)}',
                (1100, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

    # ===== SHOW SAVE MESSAGE =====
    if time.time() - save_time < 2:
        cv2.putText(frame, save_msg, (550, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("AI Gesture-Controlled Virtual Whiteboard", frame)

    key = cv2.waitKey(1)

    # ===== SAVE IMAGE =====
    if key == ord('s'):
        count = len(os.listdir(save_folder))
        filename = os.path.join(save_folder, f"drawing_{count+1}.png")
        cv2.imwrite(filename, board)
        save_msg = "Saved!"
        save_time = time.time()
        print(f"Saved: {filename}")

    if key == 27:
        break

camera.release()
cv2.destroyAllWindows()
