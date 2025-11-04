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
    
    def __str__(self):
        return(str(int(self.now_value*100)))
    
    def setValue(self, t=1.5):
        from skimage.metrics import structural_similarity
        from skimage import color
        # if self.prev_img is not None and self.img is not None:
        #     lab1 = cv.cvtColor(self.prev_img, cv.COLOR_BGR2Lab)
        #     lab2 = cv.cvtColor(self.img, cv.COLOR_BGR2Lab)
        #     diff_map = np.linalg.norm(lab1.astype(np.float32) - lab2.astype(np.float32), axis=2)
        #     self.now_value = float(np.mean(diff_map))
        # else:
        #     self.now_value = 0.0
        # self.prev_img = self.img.copy() if self.img is not None else None

            #----------------------
            # if score < 0.7:
            #     diff = (diff * 255).astype("uint8")

            #     # Threshold the difference image, followed by finding contours to
            #     # obtain the regions that differ between the two images
            #     thresh = cv.threshold(diff, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)[1]
            #     contours = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            #     contours = contours[0] if len(contours) == 2 else contours[1]

            #     # Highlight differences
            #     mask = np.zeros(first.shape, dtype='uint8')
            #     filled = second.copy()

            #     for c in contours:
            #         area = cv.contourArea(c)
            #         if area > 100:
            #             x,y,w,h = cv.boundingRect(c)
            #             cv.rectangle(first, (x, y), (x + w, y + h), (36,255,12), 2)
            #             cv.rectangle(second, (x, y), (x + w, y + h), (36,255,12), 2)
            #             cv.drawContours(mask, [c], 0, (0,255,0), -1)
            #             cv.drawContours(filled, [c], 0, (0,255,0), -1)

            #     cv.imshow('first', first)
            #     cv.imshow('second', second)
            #     cv.imshow('diff', diff)
            #     cv.imshow('mask', mask)
            #     cv.imshow('filled', filled)
            #     cv.waitKey()
        
        if self.prev_img is not None and self.img is not None:
            first = self.img
            second = self.prev_img
            first_gray = cv.cvtColor(first, cv.COLOR_BGR2GRAY)
            second_gray = cv.cvtColor(second, cv.COLOR_BGR2GRAY)
            score, diff = structural_similarity(first_gray, second_gray, full=True)
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
            diff_map = np.sqrt(dL**2 + (t * da)**2 + (t * db)**2)
            ratio = float(np.mean(diff_map) / 255.0)/abs(1-score)
            self.now_value = ((float(np.mean(diff_map) / 255.0)*1/ratio)+abs(1-score))/2

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


def findTwoBiggest(board):
    first = (-float("inf"), -1, -1)
    second = (-float("inf"), -1, -1)
    board_table = [[0 for i in range(8)] for j in range(8)]
    for x, row in enumerate(board):
        for y, cell in enumerate(row):
            val = cell.now_value
            board_table[y][x] = int(cell.now_value)
            if val > first[0]:
                second = first
                first = (val, x, y)
            elif val > second[0] and (x, y) != (first[1], first[2]):
                second = (val, x, y)

    # print("------test---------------------------")
    # find_four_biggest(board)
    # print("--------/test-------------------------")
    return [(first[1], first[2]), (second[1], second[2])], (first[0]+second[0])/2


# def find_four_biggest(board):
#     top = [(-float("inf"), -1, -1)] * 4
#     board_table = [[0 for _ in range(8)] for _ in range(8)]
#     avg = 0
#     for x, row in enumerate(board):
#         for y, cell in enumerate(row):
#             val = cell.now_value
#             avg += int(val*100)
#             board_table[y][x] = int(val * 100)

#             # Insert this value into the correct place in `top`
#             if val > top[-1][0]:
#                 top.append((val, x, y))
#                 top.sort(reverse=True, key=lambda t: t[0])
#                 top = top[:5]  # keep only top 4
#     for i in range(0,4):
#         diff = int((top[i][0]-top[i+1][0])*100)
#         print(diff,"\n----\n")
    
#     print(board_table)
#     print(top)

def checkForCastle(board, board_table, avg):
    print(board_table[0][5].now_value, board_table[7][5].now_value)
    if not board.piece_at(chess.parse_square('b1')) and not board.piece_at(chess.parse_square('c1')) and not board.piece_at(chess.parse_square('d1')):
        if board_table[2][0].now_value+board_table[3][0].now_value/2>=0.7*avg:
            return(2)#long castle
    if not board.piece_at(chess.parse_square('f1')) and not board.piece_at(chess.parse_square('g1')):
        if board_table[5][0].now_value+board_table[6][0].now_value/2>=0.7*avg:
            return(1)#short castle
        print("dupako")
    return(0)#no castle

def whatMoveWasMade(f1, f2, board, castle):
    f1_not = f1.chess_notation
    f2_not = f2.chess_notation
    p1 = board.piece_at(chess.parse_square(f1_not))
    p2 = board.piece_at(chess.parse_square(f2_not))
    if castle == 1:
        return("e1g1")
    if castle == 2:
        return("e1c1")
    if p1:
        if board.turn == chess.WHITE:
            return f1_not + f2_not if str(p1).isupper() else f2_not + f1_not
        else:
            return f1_not + f2_not if str(p1).islower() else f2_not + f1_not
    else:
        return f2_not + f1_not
    
