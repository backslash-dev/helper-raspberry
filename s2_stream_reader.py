import cv2

cap = cv2.VideoCapture("http://203.252.161.105:8000/stream.mjpg")

while(cap.isOpened()):
    ret, frame = cap.read()
    if(ret):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('frame', gray)
        k = cv2.waitKey(1) & 0xFF
    if k == 27 :
        break

cap.release()
cv2.destroyAllWindows()