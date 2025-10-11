import cv2 as cv
import numpy as np
import chess
import chess.engine
from steare.utils import find2biggest, nextTurn, compare2images, whatMoveWasMade, getBoardMargins, drawBorders,setupBorders, cropImage, showChangedFields
import keyboard

#setup board
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"
board = chess.Board(fen)
engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-x86-64-avx2")
#---------------------

cap = cv.VideoCapture(1)

offset = setupBorders(cap)

flop = False
while True:
    ret, img1 = cap.read() 
    img1 = drawBorders(img1, offset)
    
    #zdj planszy 1
    while not keyboard.is_pressed('e'):
        cv.imshow("img1", img1)
        if cv.waitKey(1)==27:
            break
        flop = True
        continue
    #---------------------------
    cv.destroyAllWindows()
    if flop:
        ret, img2 = cap.read() 
        img1 = cropImage(img1, offset)
        img2 = cropImage(img2, offset)
        img1 = cv.flip(img1, 1)
        img2 = cv.flip(img2, 1)

       
    #sprawdzenie ruchu
        comp = compare2images(img1, img2, 20)
        no1, no2 = find2biggest(comp)
        print(f'from{no1}- to{no2}')
        img2 = showChangedFields(img2, no1, no2)
        cv.imshow('img2', img2)
        if cv.waitKey(1)==27:
            pass
        #chess part ----------------------------------------------------------
        player_move= whatMoveWasMade(no1, no2, board)
        print(player_move)
    #ruch komputera
        board = nextTurn(board, player_move)
        computer_move = engine.play(board, chess.engine.Limit(time=1.0))
        board = nextTurn(board, computer_move.move)
        print(board)
        flop = False