import dlib
import cv2
import os
import numpy as np
import time


class FaceAlignment:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.predictor_path = os.path.join(BASE_DIR, "cfg", "shape_predictor_5_face_landmarks.dat")
        try:
            self.sp = dlib.shape_predictor(self.predictor_path)
        except:
            self.sp = None

    def faceAlignment(self, frame, face_rectangles=None):
        if isinstance(face_rectangles, list) and len(face_rectangles) == 0:
            return list()
        start = time.time()
        if self.sp is None:
            return None
        if face_rectangles is None:
            face_rectangles = []
            face_rectangles.append((0, 0, frame.shape[1], frame.shape[0]))

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faceslandmarks = dlib.full_object_detections()
        for (x1, y1, x2, y2) in face_rectangles:
            shape = self.sp(frame_rgb,
                            dlib.rectangle(int(x1), int(y1),
                                           int(x2), int(y2)))
            faceslandmarks.append(shape)

        face_rgb_aligned = dlib.get_face_chips(frame_rgb, faceslandmarks, size=112, padding=0.25)
        cv_bgr_images = []
        for face in face_rgb_aligned:
            # Convert to numpy array first
            cv_rgb_image = np.array(face).astype(np.uint8)

            # Convert to cv
            cv_bgr_image = cv2.cvtColor(cv_rgb_image, cv2.COLOR_RGB2BGR)

            cv_bgr_images.append(cv_bgr_image)

        end = time.time()
        # print(end-start)
        return cv_bgr_images
