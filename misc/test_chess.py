import chess
import chess.engine
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler, SingleThreadedAgentRuntime
from dataclasses import dataclass
import asyncio

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
        else:
            print(f"Illegal move: {message.move}")

# Register and run the runtime
async def main():
    runtime = SingleThreadedAgentRuntime()
    await ChessAgent.register(runtime, "chess_agent", lambda: ChessAgent("chess_agent"))

    runtime.start()
    await runtime.send_message(GetLegalMovesMessage(fen=chess.Board().fen()), AgentId("chess_agent", "default"))
    await runtime.send_message(ChessMoveMessage(fen=chess.Board().fen(), move="e2e4"), AgentId("chess_agent", "default"))
    await runtime.stop()

if __name__ == "__main__":
    asyncio.run(main())
