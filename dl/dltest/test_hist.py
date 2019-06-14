import cv2
import numpy as np

def hisEqulColor(img):
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
    channels = cv2.split(ycrcb)
    cv2.equalizeHist(channels[0], channels[0])
    cv2.merge(channels, ycrcb)
    cv2.cvtColor(ycrcb, cv2.COLOR_YCR_CB2BGR, img)
    return img



#img=cv2.imread("jemma.png")
#cv2.imshow("r1",img)
#img=hisEqulColor(img)
#cv2.imshow("res",img)
#cv2.waitKey(0)

capture=cv2.VideoCapture(0)

capture.set(cv2.CAP_PROP_FRAME_WIDTH,480)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT,360)
while capture.isOpened():

    _,frame=capture.read()

    frame=cv2.filter2D(frame,-1,np.array([[0,-1,0],[-1,5,-1],[0,-1,0]]))

    cv2.imshow("r",frame)
#    cv2.imwrite("res.jpg",frame)
    #exit(0)

    cv2.waitKey(50)