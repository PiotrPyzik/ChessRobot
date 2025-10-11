import numpy as np
import chess
import cv2 as cv
import keyboard


class Field:
    def __init__(self, index):
        self.index = index
        self.x_pos = 0
        self.y_pos = 0
        self.chess_notation = None
        self.piece = None
        self.a = 0
        self.prev_img = None
        self.img = None
        self.prev_value = 0
        self.now_value = 0
        diff = 0
        self.offset = 5
    
    def setValue(self):
        if self.prev_img is not None and self.img is not None:
            # Convert both to Lab color space
            lab1 = cv.cvtColor(self.prev_img, cv.COLOR_BGR2Lab)
            lab2 = cv.cvtColor(self.img, cv.COLOR_BGR2Lab)

            # Compute Euclidean distance per pixel in Lab
            diff_map = np.linalg.norm(lab1.astype(np.float32) - lab2.astype(np.float32), axis=2)

            # Mean difference across the whole square
            self.now_value = float(np.mean(diff_map))
        else:
            self.now_value = 0.0

        # Store the current image for next comparison
        self.prev_img = self.img.copy() if self.img is not None else None
    
    def getChessNotation(self):
        letters = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'}
        self.chess_notation = letters[self.index[1]] + str(self.index[0]+1)
        return self.chess_notation
        
    def outlineField(self, img):
        img = cv.rectangle(img, (self.x_pos+self.offset,self.y_pos+self.offset), (self.x_pos+self.a-self.offset, self.y_pos+self.a-self.offset), (0,255,0), 3)
        return img
    
        
def setupBorders(cap):
    mt, ml = 0,0
    size = 500
    while True:
        offset = [0,0,0,0]
        ret, frame = cap.read()
        ml, mt, size, done = getBoardMargins(frame, ml, mt, size)
        if done:
            offset[0] = mt
            offset[1] = size+mt
            offset[2] = ml
            offset[3] = size+ml
            cv.destroyAllWindows()
            break
        if cv.waitKey(1)==27:
            pass
    return offset
    
def getBoardMargins(frame, ml, mt, size):
    frame = cv.rectangle(frame, (ml,mt), (size+ml, size+mt), (0,255,0), 1)
    cv.imshow('frame', frame)
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
    if keyboard.is_pressed("q"):
        done = True
    return ml, mt, size, done

def drawBorders(frame, offset):
    frame = cv.rectangle(frame, (offset[2],offset[0]), (offset[3], offset[1]), (0,255,0), 1)
    return frame


def cropImage(frame, offset):
    frame = frame[offset[0]:offset[1], offset[2]:offset[3]]
    return frame

def find_two_biggest(board):
    first = (-float("inf"), -1, -1)
    second = (-float("inf"), -1, -1)

    for x, row in enumerate(board):
        for y, cell in enumerate(row):
            val = cell.now_value
            if val > first[0]:
                second = first
                first = (val, x, y)
            elif val > second[0] and (x, y) != (first[1], first[2]):
                second = (val, x, y)

    return [(first[1], first[2]), (second[1], second[2])]

def whatMoveWasMade(f1, f2, board):
    f1 = f1.getChessNotation()
    f2 = f2.getChessNotation()
    p1 = board.piece_at(chess.parse_square(f1))
    p2 = board.piece_at(chess.parse_square(f2))
    print(p1, p2)
    if p1:
        if board.turn == chess.WHITE:
            if str(p1).isupper():
                return(f1+f2)
            else:
                return(f2+f1)
        if board.turn == chess.BLACK:
            if str(p1).islower():
                return(f1+f2)
            else:
                return(f2+f1)
    else:
        return(f2+f1)