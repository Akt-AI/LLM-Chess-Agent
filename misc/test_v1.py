import chess
import chess.engine
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler, SingleThreadedAgentRuntime
from dataclasses import dataclass
import asyncio
import pygame

# Define message types
@dataclass
class ChessMoveMessage:
    fen: str
    move: str

@dataclass
class GetLegalMovesMessage:
    fen: str

# Define the ChessAgent
class ChessAgent(RoutedAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    @message_handler
    async def handle_get_legal_moves(self, message: GetLegalMovesMessage, ctx: MessageContext) -> None:
        board = chess.Board(message.fen)
        legal_moves = [move.uci() for move in board.legal_moves]
        print(f"Legal moves for FEN {message.fen}: {legal_moves}")

    @message_handler
    async def handle_chess_move(self, message: ChessMoveMessage, ctx: MessageContext) -> None:
        board = chess.Board(message.fen)
        move = chess.Move.from_uci(message.move)
        if move in board.legal_moves:
            board.push(move)
            new_fen = board.fen()
            print(f"Move {message.move} applied. New FEN: {new_fen}")
            update_board_ui(board)
        else:
            print(f"Illegal move: {message.move}")

# Pygame UI for displaying the chess board
async def create_ui(runtime, agent_id):
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Chess Game")

    square_size = 50
    colors = [(255, 255, 255), (125, 135, 150)]

    def draw_board(board):
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(
                    screen, color, pygame.Rect(col * square_size, row * square_size, square_size, square_size)
                )
                piece = board.piece_at(row * 8 + col)
                if piece:
                    piece_text = str(piece).upper() if piece.color else str(piece).lower()
                    font = pygame.font.Font(None, 36)
                    text = font.render(piece_text, True, (0, 0, 0))
                    screen.blit(text, (col * square_size + 15, row * square_size + 10))
        pygame.display.flip()

    def update_board_ui(board):
        screen.fill((0, 0, 0))
        draw_board(board)

    async def autoplay_game():
        board = chess.Board()
        update_board_ui(board)  # Ensure the initial board state is drawn
        while not board.is_game_over():
            legal_moves = list(board.legal_moves)
            move = legal_moves[0]  # Just pick the first legal move
            board.push(move)
            update_board_ui(board)
            await asyncio.sleep(1)  # Pause to show the move
        print("Game over!")

    async def two_player_game():
        board = chess.Board()
        update_board_ui(board)
        while not board.is_game_over():
            if board.turn:  # White to move
                legal_moves = list(board.legal_moves)
                move = legal_moves[0]  # First legal move for White
                board.push(move)
                print(f"White plays: {move}")
            else:  # Black to move
                legal_moves = list(board.legal_moves)
                move = legal_moves[0]  # First legal move for Black
                board.push(move)
                print(f"Black plays: {move}")
            update_board_ui(board)
            await asyncio.sleep(1)
        print("Game over!")

    # Start two-player game in the background
    asyncio.create_task(two_player_game())

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        await asyncio.sleep(0.01)  # Allow event loop to run smoothly

    pygame.quit()

# Register and run the runtime
async def main():
    runtime = SingleThreadedAgentRuntime()
    await ChessAgent.register(runtime, "chess_agent", lambda: ChessAgent("chess_agent"))

    runtime.start()
    agent_id = AgentId("chess_agent", "default")
    await create_ui(runtime, agent_id)  # Await UI to integrate properly with asyncio
    await runtime.stop()

if __name__ == "__main__":
    asyncio.run(main())
