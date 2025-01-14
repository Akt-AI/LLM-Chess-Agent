import chess
import chess.svg
import asyncio
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler, SingleThreadedAgentRuntime
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from collections import defaultdict
from typing import List, Optional
from dataclasses import dataclass
import os

@dataclass
class UserMessage:
    """Represents a user message with text content."""
    content: str
    player: str  # Identifies the player ("Player 1" or "Player 2")

def get_model_client() -> OpenAIChatCompletionClient:
    """
    Returns a mock OpenAI API client configured for a local LLM server.
    """
    return OpenAIChatCompletionClient(
        model="llama3.2-vision:latest",
        api_key="NotRequiredSinceWeAreLocal",
        base_url="http://0.0.0.0:4000",
        model_capabilities={
            "json_output": False,
            "vision": False,
            "function_calling": True,
        },
    )

# System message for the AI agent
sys_msg = """You are an AI-powered chess board agent.
You translate the user's natural language input into a legal UCI move.
You should only reply with the move in UCI format, consisting of exactly four or five characters (e.g., e2e4, e7e8q), without any extra text or explanation."""

class CustomAssistant:
    """
    A custom wrapper around AssistantAgent to handle chess-specific messaging.
    """
    def __init__(self, name: str):
        self.assistant = AssistantAgent(name=name, system_message=sys_msg, model_client=get_model_client())

    async def handle_message(self, message: str) -> str:
        """
        Sends a message to the AssistantAgent and retrieves the UCI move response.
        """
        reply = await self.assistant.on_messages(
            [TextMessage(content=message, source="user")],
            cancellation_token=None
        )
        return reply.chat_message.content.strip().replace("-", "").lower()

class MultiplayerUmpireAgent(RoutedAgent):
    """
    An agent that manages a multiplayer chess game by alternating turns between players and validating moves.
    """
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.assistant = CustomAssistant(name="UmpireAgent")
        self.board = chess.Board()
        self.current_player = "Player 1"  # Tracks whose turn it is
        self.move_log: List[str] = []

    def save_board_svg(self, filename="current_board.svg", last_move: Optional[str] = None):
        """
        Saves the current chessboard state as an SVG file, highlighting the last move.
        """
        if last_move:
            move = chess.Move.from_uci(last_move)
            board_svg = chess.svg.board(self.board, lastmove=move, size=600)
        else:
            board_svg = chess.svg.board(self.board, size=600)
        with open(filename, "w") as f:
            f.write(board_svg)

    def log_move(self, move: str):
        """
        Logs the move and prints the move history.
        """
        self.move_log.append(move)
        print("Move Log:")
        for i, mv in enumerate(self.move_log, 1):
            print(f"{i}. {mv}")

    def check_game_status(self) -> Optional[str]:
        """
        Checks the current status of the game (checkmate, stalemate, or draw).
        """
        if self.board.is_checkmate():
            return f"Checkmate! {self.current_player} loses."
        if self.board.is_stalemate():
            return "Stalemate! It's a draw."
        if self.board.is_insufficient_material():
            return "Draw due to insufficient material."
        if self.board.is_seventyfive_moves():
            return "Draw due to 75-move rule."
        return None

    @message_handler
    async def handle_message(self, message: UserMessage, ctx: MessageContext) -> None:
        """
        Handles incoming messages and alternates turns between players.
        """
        if message.player != self.current_player:
            print(f"It's not {message.player}'s turn. It's {self.current_player}'s turn.")
            return

        reply = await self.assistant.handle_message(message.content)
        print(f"{message.player}'s move: {reply}")

        try:
            self.board.push_uci(reply)
            self.log_move(reply)
            self.save_board_svg(last_move=reply)

            game_status = self.check_game_status()
            if game_status:
                print(game_status)
                return

            # Switch player turn
            self.current_player = "Player 2" if self.current_player == "Player 1" else "Player 1"
            print(f"Next turn: {self.current_player}")

        except ValueError as e:
            print(f"Illegal move by {message.player}: {reply}. Error: {e}")
        except Exception as ex:
            print(f"Unexpected error: {ex}")

# Define a runtime and register the agent
async def main():
    """
    Main function to initialize the runtime, register the agent, and send a test message.
    """
    runtime = SingleThreadedAgentRuntime()
    await MultiplayerUmpireAgent.register(runtime, "multiplayer_umpire_agent", lambda: MultiplayerUmpireAgent("multiplayer_umpire_agent"))

    runtime.start()
    agent_id = AgentId("multiplayer_umpire_agent", "default")

    # Simulated gameplay messages
    test_messages = [
        UserMessage(content="Play e2e4", player="Player 1"),
        UserMessage(content="Play e7e5", player="Player 2"),
        UserMessage(content="Play g1f3", player="Player 1"),
        UserMessage(content="Play b8c6", player="Player 2")
    ]

    for msg in test_messages:
        await runtime.send_message(msg, agent_id)

    await runtime.stop()

if __name__ == "__main__":
    asyncio.run(main())
