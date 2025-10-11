import numpy as np
import chess
import cv2 as cv
import keyboard


def compare2images(img1, img2, comp_thresh): 
    a=int(img1.shape[0]/8)
    val1=0
    val2=0
    comp = np.zeros((8,8))
    for x in range(8):
        for y in range(8):
            region1 = img1[x*a : x*a+a, y*a: y*a+a]
            val1= np.mean(region1)
            region2 = img2[x*a : x*a+a, y*a: y*a+a]
            val2 = np.mean(region2)
            comp[x][y] = abs(val1-val2)
    return comp


def find2biggest(comp):
    no1 = [float('-inf'), -1, -1]
    no2 = [float('-inf'), -1, -1]
    for x in range(8):
        for y in range(8):
            val = comp[x][y]
            if val > no1[0]:
                no2 = no1[:]  
                no1 = [val, x, y]
            elif val > no2[0] and (x != no1[1] or y != no1[2]):
                no2 = [val, x, y]
    return no1, no2


def toChessNotation(col, row):
    letters = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'}
    return letters[row] + str(col+1)


def whatMoveWasMade(no1, no2, board):
    f1 = toChessNotation(no1[1], no1[2])
    f2 = toChessNotation(no2[1], no2[2])
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
    if keyboard.is_pressed("e"):
        done = True
    return ml, mt, size, done

def drawBorders(frame, offset):
    frame = cv.rectangle(frame, (offset[2],offset[0]), (offset[3], offset[1]), (0,255,0), 1)
    return frame

def cropImage(frame, offset):
    frame = frame[offset[0]+5:offset[1]-5, offset[2]+5:offset[3]-5]
    return frame

def showChangedFields(frame, no1, no2):
    width, height, channels = frame.shape
    center_x1 = int(int(no2[2]) * width / 8-width/16)
    center_y1 = int(int(no2[1]) * width / 8-width/16)
    center_x2 = int(int(no1[2]) * width / 8-width/16)
    center_y2 = int(int(no1[1]) * width / 8-width/16)
    radius = int(width / 12)
    frame = cv.circle(frame, (center_x1, center_y1), radius, (0, 0, 255), 5)
    frame = cv.circle(frame, (center_x2, center_y2), radius, (0, 0, 255), 5)
    return frame

def nextTurn(board, move):
    move = chess.Move.from_uci(str(move))
    board.push(move)
    board.turn=not board.turn
    return board