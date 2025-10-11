import cv2 as cv
import chess
import chess.engine
import keyboard
from utils3 import Field, setupBorders, cropImage, find_two_biggest, whatMoveWasMade
import cnc

def create_board():
    board = []
    for y in range(8):
        row = []
        for x in range(8):
            row.append(Field([x, y]))
        board.append(row)
    return board

def capture_board_frame(cap, offset):
    ret, frame = cap.read()
    frame = cropImage(frame, offset)
    return frame

def update_board_images(board, frame):
    a = frame.shape[0] // 8
    for x in range(8):
        for y in range(8):
            field = board[x][y]
            field.x_pos = x * a
            field.y_pos = y * a
            field.a = a
            field.img = frame[x*a : x*a + a, y*a : y*a + a]
            field.setValue()

def wait_for_key(key_char):
    while not keyboard.is_pressed(key_char):
        if cv.waitKey(1) == 27:
            return False
    while keyboard.is_pressed(key_char):
        pass
    return True

def main():
    #setup cnc
    cnc.goToCamera()
    
    # Setup chess engine & board
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    game_board = chess.Board(fen)
    engine = chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows-x86-64-avx2")

    # Camera & borders
    cap = cv.VideoCapture(1)
    offset = setupBorders(cap)

    board = create_board()

    while True:
        # Before move
        frame_before = capture_board_frame(cap, offset)
        # frame_before = cv.flip(capture_board_frame(cap, offset), 0)
        # frame_before = cv.flip(capture_board_frame(cap, offset), 1)
        
        cv.imshow("Before", frame_before)
        wait_for_key('e')
        cv.destroyAllWindows()
        update_board_images(board, frame_before)

        # After move
        frame_after = capture_board_frame(cap, offset)
        # frame_after = cv.flip(capture_board_frame(cap, offset), 0)
        # frame_after = cv.flip(capture_board_frame(cap, offset), 1)
        update_board_images(board, frame_after)

        # Find changed fields
        coords = find_two_biggest(board)
        f1 = board[coords[0][0]][coords[0][1]]
        f2 = board[coords[1][0]][coords[1][1]]

        # Draw & determine move
        frame_with_move = f1.outlineField(frame_after)
        frame_with_move = f2.outlineField(frame_with_move)
        move = whatMoveWasMade(f1, f2, game_board)
        #player_move = chess.Move.from_uci(move)
        
        player_move = chess.Move.from_uci(move)
        game_board.push_uci(move)
        print(game_board)
        
        computer_move = engine.play(game_board, chess.engine.Limit(time = 1)).move
        moved_piece = game_board.piece_at(computer_move.from_square)
        is_capture = game_board.is_capture(computer_move)
        game_board.push(computer_move)
        print(game_board)
        print(f'player: {move}, computer: {computer_move}')
        if is_capture:
            cnc.removePiece(str(game_board.piece_at(computer_move.to_square)).lower(), str(computer_move)[2:4])
        cnc.movePiece(str(computer_move)+str(moved_piece).lower())
        cnc.goToCamera()
        cv.imshow("Detected Move", frame_with_move)
        if cv.waitKey(1) == 27:
            break
        while not keyboard.is_pressed('d'):
            pass
        print("computer move has finished")

if __name__ == "__main__":
    main()