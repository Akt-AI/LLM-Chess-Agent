import chess
import chess.engine
import time

# Path to the Stockfish engine (update this to your system's path)
STOCKFISH_PATH = "/usr/games/stockfish"

def autonomous_chess():
    board = chess.Board()
    
    # Start two Stockfish engines
    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine1, \
         chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine2:
        
        print("Autonomous chess game between two Stockfish engines!")
        time.sleep(1)
        
        while not board.is_game_over():
            print("\nCurrent board position:\n")
            print(board)
            print("\nThinking...\n")
            time.sleep(1)
            
            # Let engine 1 play
            result1 = engine1.play(board, chess.engine.Limit(time=0.5))  # 0.5-second time limit
            board.push(result1.move)
            print(f"Engine 1 plays: {result1.move.uci()}")
            
            if board.is_game_over():
                break
            
            # Let engine 2 play
            result2 = engine2.play(board, chess.engine.Limit(time=0.5))  # 0.5-second time limit
            board.push(result2.move)
            print(f"Engine 2 plays: {result2.move.uci()}")
        
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

if __name__ == "__main__":
    autonomous_chess()
