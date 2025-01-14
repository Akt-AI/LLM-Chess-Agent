import chess
import chess.engine
import chess.svg
import time
import os
import cv2
import numpy as np
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM

# Path to the Stockfish engine (update this to your system's path)
STOCKFISH_PATH = "/usr/games/stockfish"

# Ensure images folder exists
os.makedirs("images", exist_ok=True)

def save_board_image(board, move_number):
    """Save the current board as an SVG image without coordinates/labels."""
    svg_data = chess.svg.board(board, coordinates=False)
    with open(f"images/board_{move_number}.svg", "w") as f:
        f.write(svg_data)

def svg_to_cv2_image(svg_path):
    """Convert an SVG file to a format suitable for OpenCV (PNG)."""
    drawing = svg2rlg(svg_path)
    png_data = renderPM.drawToPIL(drawing)
    # Convert to NumPy array for OpenCV compatibility
    return cv2.cvtColor(np.array(png_data), cv2.COLOR_RGB2BGR)

def autonomous_chess():
    board = chess.Board()
    move_number = 0  # Track the number of moves
    
    # Initialize video writer
    video_writer = cv2.VideoWriter('chess_game.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 2, (800, 800))
    
    # Start two Stockfish engines
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine1, \
         chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine2:
        
        print("Autonomous chess game between two Stockfish engines!")
        time.sleep(1)
        
        while not board.is_game_over():
            move_number += 1
            
            # Save the current board position
            save_board_image(board, move_number)
            
            # Convert SVG to OpenCV-compatible format and display it
            frame = svg_to_cv2_image(f"images/board_{move_number}.svg")
            cv2.imshow("Chess Game", frame)
            video_writer.write(frame)  # Save frame to video
            
            if cv2.waitKey(500) & 0xFF == ord('q'):  # Press 'q' to quit
                break
            
            # Let engine 1 play
            result1 = engine1.play(board, chess.engine.Limit(time=0.5))  # 0.5-second time limit
            board.push(result1.move)
            print(f"Engine 1 plays: {result1.move.uci()}")
            
            if board.is_game_over():
                break
            
            move_number += 1
            
            # Save the current board position after engine 1's move
            save_board_image(board, move_number)
            
            # Convert SVG to OpenCV-compatible format and display it
            frame = svg_to_cv2_image(f"images/board_{move_number}.svg")
            cv2.imshow("Chess Game", frame)
            video_writer.write(frame)  # Save frame to video
            
            if cv2.waitKey(500) & 0xFF == ord('q'):  # Press 'q' to quit
                break
            
            # Let engine 2 play
            result2 = engine2.play(board, chess.engine.Limit(time=0.5))  # 0.5-second time limit
            board.push(result2.move)
            print(f"Engine 2 plays: {result2.move.uci()}")
        
        # Save the final board position
        save_board_image(board, move_number + 1)
        
        # Convert final SVG to OpenCV-compatible format and display it
        frame = svg_to_cv2_image(f"images/board_{move_number + 1}.svg")
        cv2.imshow("Chess Game", frame)
        video_writer.write(frame)  # Save final frame to video
        
        # Game over message
        print("\nGame Over!")
        print("Final board position:\n")
        print(board)
        if board.is_checkmate():
            print("Checkmate!")
        elif board.is_stalemate():
            print("Stalemate!")
        elif board.is_insufficient_material():
            print("Draw due to insufficient material!")
        else:
            print("Game result: Draw!")
    
    video_writer.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    autonomous_chess()


