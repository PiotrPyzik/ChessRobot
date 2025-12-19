import cv2 as cv
import numpy as np
import chess
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity

class Field:
    def __init__(self, index):
        self.index = index
        self.x_pos = 0
        self.y_pos = 0
        self.a = 0
        self.chess_notation = self.getChessNotation()
        self.prev_img = None
        self.img = None
        self.now_value = 0.0
        self.just_color = 0.0
        self.offset = 5
        self.diff_img = None
    
    def __str__(self):
        return(str(int(self.now_value*100)))
    
    def setValue(self, t=1.5):
        if self.prev_img is not None and self.img is not None:
            first = self.img
            second = self.prev_img
            
            first_gray = cv.cvtColor(first, cv.COLOR_BGR2GRAY)
            second_gray = cv.cvtColor(second, cv.COLOR_BGR2GRAY)
            
            score, ssim_diff = structural_similarity(first_gray, second_gray, full=True)
            
            self.diff_img = ((1.0 - ssim_diff) * 255).astype("uint8")
            
            lab_prev = cv.cvtColor(self.prev_img, cv.COLOR_BGR2Lab).astype(np.float32)
            lab_curr = cv.cvtColor(self.img, cv.COLOR_BGR2Lab).astype(np.float32)

            L1, a1, b1 = cv.split(lab_prev)
            L2, a2, b2 = cv.split(lab_curr)

            dL = L1 - L2
            da = a1 - a2
            db = b1 - b2
            

            diff_map = np.sqrt(dL**2 + (t * da)**2 + (t * db)**2)
            
            self.just_color = float(np.mean(diff_map) / 255.0)
            
            ratio = self.just_color / (abs(1 - score) + 1e-6)
            
            self.now_value = ((self.just_color * (1/ratio)) + abs(1-score)) / 2

        else:
            self.now_value = 0.0
            self.just_color = 0.0
            self.diff_img = None

        self.prev_img = self.img.copy() if self.img is not None else None

    def getChessNotation(self):
        letters = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f', 6:'g', 7:'h'}
        return letters[self.index[1]] + str(self.index[0] + 1)

    def outlineField(self, img):
        """Rysuje prostokąt wokół pola."""
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
        if not ret: continue
        frame_copy = frame.copy()
        frame_copy = cv.rectangle(frame_copy, (ml, mt), (ml+size, mt+size), (0, 255, 0), 1)
        cv.imshow('Setup Board Borders (WASD + LK to resize, Q to confirm)', frame_copy)
        key = cv.waitKey(1) & 0xFF
        if keyboard.is_pressed('w'): mt -= 1
        elif keyboard.is_pressed('s'): mt += 1
        if keyboard.is_pressed('a'): ml -= 1
        elif keyboard.is_pressed('d'): ml += 1
        if keyboard.is_pressed('l'): size += 1
        elif keyboard.is_pressed('k'): size -= 1
        if key == ord('q'):
            offset = [mt, mt+size, ml, ml+size]
            cv.destroyAllWindows()
            return offset

def cropImage(frame, offset):
    return frame[offset[0]:offset[1], offset[2]:offset[3]]

def findTwoBiggest(board):
    first = (-float("inf"), -1, -1)
    second = (-float("inf"), -1, -1)
    
    # Do debugowania Castle (średnia wartość planszy)
    total_val = 0
    count = 0

    for x, row in enumerate(board):
        for y, cell in enumerate(row):
            val = cell.now_value
            total_val += val
            count += 1
            
            if val > first[0]:
                second = first
                first = (val, x, y)
            elif val > second[0] and (x, y) != (first[1], first[2]):
                second = (val, x, y)

    avg_field_value = total_val / count if count > 0 else 0
    return [(first[1], first[2]), (second[1], second[2])], avg_field_value

def checkForCastle(game_board, board_matrix, avg_val):
    if not game_board.piece_at(chess.parse_square('b1')) and \
       not game_board.piece_at(chess.parse_square('c1')) and \
       not game_board.piece_at(chess.parse_square('d1')):

        c1_val = board_matrix[0][2].now_value
        d1_val = board_matrix[0][3].now_value
        if c1_val + d1_val / 2 >= 0.7 * avg_val:
            return 2 
    if not game_board.piece_at(chess.parse_square('f1')) and \
       not game_board.piece_at(chess.parse_square('g1')):
        f1_val = board_matrix[0][5].now_value
        g1_val = board_matrix[0][6].now_value
        if f1_val + g1_val / 2 >= 0.7 * avg_val:
            return 1 # Short castle
            
    return 0

def whatMoveWasMade(f1, f2, board, castle):
    f1_not = f1.chess_notation
    f2_not = f2.chess_notation
    p1 = board.piece_at(chess.parse_square(f1_not))
    
    if castle == 1: return "e1g1"
    if castle == 2: return "e1c1"
    
    if p1:
        if board.turn == chess.WHITE:
            return f1_not + f2_not if str(p1).isupper() else f2_not + f1_not
        else:
            return f1_not + f2_not if str(p1).islower() else f2_not + f1_not
    else:
        return f2_not + f1_not

def plot_debug_graphs(board):
    matrix_now_value = np.zeros((8, 8))
    matrix_just_color = np.zeros((8, 8))

    for x, row in enumerate(board):
        for y, field in enumerate(row):
            matrix_now_value[y, x] = field.now_value
            matrix_just_color[y, x] = field.just_color

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    im1 = axes[0].imshow(matrix_now_value, cmap='viridis', vmin=0, vmax=1)
    axes[0].set_title('NOW_VALUE (Color + SSIM)')
    fig.colorbar(im1, ax=axes[0])
    for i in range(8):
        for j in range(8):
            axes[0].text(j, i, f"{matrix_now_value[i, j]:.2f}", ha="center", va="center", color="w", fontsize=7)

    im2 = axes[1].imshow(matrix_just_color, cmap='plasma', vmin=0, vmax=1)
    axes[1].set_title('JUST_COLOR (Lab Diff Only)')
    fig.colorbar(im2, ax=axes[1])
    for i in range(8):
        for j in range(8):
            axes[1].text(j, i, f"{matrix_just_color[i, j]:.2f}", ha="center", va="center", color="w", fontsize=7)

    plt.tight_layout()
    print("Wyświetlam wykresy. Zamknij okno wykresu aby kontynuować...")
    plt.show()