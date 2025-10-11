import cv2 as cv
import numpy as np
import chess
import chess.engine
from utils2 import Field, setupBorders, drawBorders, cropImage, whatMoveWasMade
import keyboard

#setup board
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"
game_board = chess.Board(fen)
engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-x86-64-avx2")
#---------------------

changed_fields = [0,0]

board = []
for y in range(8):
    row = []
    for x in range(8):
        field = Field([x,y])
        field.getChessNotation()
        row.append(field)
    board.append(row)
    

cap = cv.VideoCapture(1)

offset = setupBorders(cap)

flop = False
while True:
    ret, img1 = cap.read() 
    img1 = cropImage(img1, offset)
    img1 = cv.flip(img1, 0)
    #oczekiwanie na wykonanie ruchu
    while not keyboard.is_pressed('e'):
        cv.imshow("img1", img1)
        if cv.waitKey(1)==27:
            break
        continue
    cv.destroyAllWindows()
    while keyboard.is_pressed('e'):
        pass
    #wykonano ruch - czas na analizę
    
    #wstępne właściwosci pola
    a=int(img1.shape[0]/8)
    for x in range(8):
        for y in range(8):
            board[x][y].x_pos = x*a
            board[x][y].y_pos = y*a
            board[x][y].a = a
            board[x][y].img = img1[x*a : x*a+a, y*a: y*a+a]
            board[x][y].setValue()
            if cv.waitKey(0)==27:
                break
            
    ret, img2 = cap.read() 
    img2 = cropImage(img2, offset)
    img2 = cv.flip(img2, 0)
    #find 2 fields that changed the most
    no1 = [0,0]
    no2 = [0,0]
    for x in range(8):
        for y in range(8):
            board[x][y].img = img2[x*a : x*a+a, y*a: y*a+a]
            board[x][y].setValue()
            if board[x][y].diff>no1[0]:
                no1[0] = board[x][y].diff
                no1[1] = board[x][y].index
            elif board[x][y].diff>no2[0]:
                no2[0] = board[x][y].diff
                no2[1] = board[x][y].index
    print("dupsko", no1, no2)
    #-------------------------------------
    print(no1[1][0],no1[1][1],"dupa", no2[1][0],no2[1][1])
    f1 = board[no1[1][0]][no1[1][1]]
    f2 = board[no2[1][0]][no2[1][1]]
    img1 = f1.outlineField(img1)
    img1 = f2.outlineField(img1)

    move = whatMoveWasMade(f1, f2, game_board)
    print(move)
    cv.imshow("img", img1)
    if cv.waitKey(1)==27:
            break
    
        


       