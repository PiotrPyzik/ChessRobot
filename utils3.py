import cv2 as cv
import numpy as np
import chess

class Field:
    def __init__(self, index):
        self.index = index  # (row, col)
        self.x_pos = 0
        self.y_pos = 0
        self.a = 0
        self.chess_notation = self.getChessNotation()
        self.prev_img = None
        self.img = None
        self.now_value = 0.0
        self.offset = 5

    def setValue(self, t=1.5):
        from skimage.metrics import structural_similarity
        from skimage import color

        if self.prev_img is not None and self.img is not None:
            # --- Convert to Lab color space for perceptual difference ---
            lab_prev = cv.cvtColor(self.prev_img, cv.COLOR_BGR2Lab)
            lab_curr = cv.cvtColor(self.img, cv.COLOR_BGR2Lab)

            # Convert to float for safe math
            lab_prev = lab_prev.astype(np.float32)
            lab_curr = lab_curr.astype(np.float32)

            # Separate channels
            L1, a1, b1 = cv.split(lab_prev)
            L2, a2, b2 = cv.split(lab_curr)

            # --- Compute per-channel differences ---
            dL = L1 - L2
            da = a1 - a2
            db = b1 - b2

            # --- Apply color bias (t) to chroma channels ---
            diff_map = np.sqrt(dL**2 + (t * da)**2 + (t * db)**2)

            # Average difference → normalized metric (0–1)
            self.now_value = float(np.mean(diff_map) / 255.0)

        else:
            self.now_value = 0.0

        # Update previous frame
        self.prev_img = self.img.copy() if self.img is not None else None

        

    def getChessNotation(self):
        letters = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'}
        return letters[self.index[1]] + str(self.index[0] + 1)

    def outlineField(self, img):
        """Draw a rectangle around the field."""
        return cv.rectangle(
            img,
            (self.y_pos + self.offset, self.x_pos + self.offset),
            (self.y_pos + self.a - self.offset, self.x_pos + self.a - self.offset),
            (0, 255, 0),
            3
        )

def setupBorders(cap):
    import keyboard
    mt, ml, size = 0, 0, 500
    while True:
        ret, frame = cap.read()
        frame_copy = frame.copy()
        frame_copy = cv.rectangle(frame_copy, (ml, mt), (ml+size, mt+size), (0, 255, 0), 1)
        cv.imshow('Setup Board Borders', frame_copy)
        key = cv.waitKey(1) & 0xFF
        if keyboard.is_pressed('w'): mt -= 1
        elif keyboard.is_pressed('s'): mt += 1
        if keyboard.is_pressed('a'): ml -= 1
        elif keyboard.is_pressed('d'): ml += 1
        if keyboard.is_pressed('l'): size += 1
        elif keyboard.is_pressed('k'): size -= 1
        if key == ord('q'):  # Done
            offset = [mt, mt+size, ml, ml+size]
            cv.destroyAllWindows()
            return offset


def cropImage(frame, offset):
    return frame[offset[0]:offset[1], offset[2]:offset[3]]

def find_two_biggest(board):
    first = (-float("inf"), -1, -1)
    second = (-float("inf"), -1, -1)
    board_table = [[0 for i in range(8)] for j in range(8)]
    for x, row in enumerate(board):
        for y, cell in enumerate(row):
            val = cell.now_value
            board_table[y][x] = int(cell.now_value*100)
            if val > first[0]:
                second = first
                first = (val, x, y)
            elif val > second[0] and (x, y) != (first[1], first[2]):
                second = (val, x, y)
    print(board_table)
    return [(first[1], first[2]), (second[1], second[2])]

def whatMoveWasMade(f1, f2, board):
    f1_not = f1.chess_notation
    f2_not = f2.chess_notation
    p1 = board.piece_at(chess.parse_square(f1_not))
    p2 = board.piece_at(chess.parse_square(f2_not))

    if p1:
        if board.turn == chess.WHITE:
            return f1_not + f2_not if str(p1).isupper() else f2_not + f1_not
        else:
            return f1_not + f2_not if str(p1).islower() else f2_not + f1_not
    else:
        return f2_not + f1_not