import cv2
import numpy as np
import keyboard


cap = cv2.VideoCapture(0)
mt, ml = 0,0
size = 500

def getBoardMargins(frame, ml, mt, size):
    frame = cv2.rectangle(frame, (ml,mt), (size+ml, size+mt), (0,255,0), 5)
    cv2.imshow('frame', frame)
    done = False
    
    if keyboard.is_pressed('w'):
        mt-=1
    elif keyboard.is_pressed('s'):
        mt+=1
    if keyboard.is_pressed('a'):
        ml-=1
    elif keyboard.is_pressed('d'):
        ml+=1
    if keyboard.is_pressed('l'):
        size+=1
    elif keyboard.is_pressed('k'):
        size-=1
    if keyboard.is_pressed("e"):
        done = True
    return ml, mt, size, done


while True:
    ret, frame = cap.read()
    width = int(cap.get(3))
    height=  int(cap.get(4))
    ml, mt, size, done = getBoardMargins(frame, ml, mt, size)
    
    
    if cv2.waitKey(1)==27:
        break

cap.release()
cv2.destroyAllWindows()


