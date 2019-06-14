import sys
sys.path.append("..")
from face_dlib.FaceAlignment import FaceAlignment

import cv2

fa=FaceAlignment()
img=cv2.imread("1.jpeg")
#cv2.rectangle(img,(220,201),(418,425),(0,0,255))
cv2.imshow("r",img);
res=fa.faceAlignment(img,face_rectangles=[[206,187,423,435]])

cv2.imshow("r1",res[0]);
cv2.imwrite("res.jpg",res[0])
cv2.waitKey(0);