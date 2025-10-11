import cv2 as cv
import numpy as np
import chess
import chess.engine
from steare.utils import find2biggest, compare2images, whatMoveWasMade




#--------------
offset = [0,0,0,0]#gora - dol - lewo - prawo
#--------------
img1 = cv.imread("0.png", 0)
img1 = cv.rotate(img1, cv.ROTATE_90_CLOCKWISE)
img2 = cv.imread("1.png", 0)
img2 = cv.rotate(img2, cv.ROTATE_90_CLOCKWISE)
img1 = img1[offset[0]:img1.shape[0]-offset[1], offset[2]:img1.shape[1]-offset[3]]#odcinanie brzegow


comp = compare2images(img1, img2, 20)
no1, no2 = find2biggest(comp)
print(no1, no2)

#chess part ----------------------------------------------------------
fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"
board = chess.Board(fen)
engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-x86-64-avx2")


player_move= whatMoveWasMade(no1, no2, board)

def nextTurn(board, move):
    move = chess.Move.from_uci(str(move))
    board.push(move)
    board.turn=not board.turn
    return board

board = nextTurn(board, player_move)
computer_move = engine.play(board, chess.engine.Limit(time=1.0))
board = nextTurn(board, computer_move.move)
print(board)