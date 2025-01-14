import chess
import chess.svg
import asyncio
from autogen_core import AgentId, MessageContext, RoutedAgent, message_handler, SingleThreadedAgentRuntime
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage  # Correctly import the message class
from autogen_ext.models.openai import OpenAIChatCompletionClient
import os

from collections import defaultdict
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

@dataclass
class UserMessage:
    content: str

def get_model_client() -> OpenAIChatCompletionClient:
    """Mimic OpenAI API using Local LLM Server."""
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

sys_msg = """You are an AI-powered chess board agent.
You translate the user's natural language input into a legal UCI move.
You should only reply with the move in UCI format, consisting of exactly four or five characters (e.g., e2e4, e7e8q), without any extra text or explanation."""

class CustomAssistant:
    def __init__(self, name: str):
        self.assistant = AssistantAgent(name=name, system_message=sys_msg, model_client=get_model_client())

    async def handle_message(self, message: str) -> str:
        """Send a message to the AssistantAgent and get the response."""
        reply = await self.assistant.on_messages(
            [TextMessage(content=message, source="user")],  # Use TextMessage instead of raw dict
            cancellation_token=None
        )
        uci_move = reply.chat_message.content.strip().replace("-", "").lower()
        return uci_move

class UmpireAgentWrapper(RoutedAgent):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.assistant = CustomAssistant(name="UmpireAgent")
        self.board = chess.Board()
        self.correct_move_messages = defaultdict(list)

    def save_board_svg(self, filename="current_board.svg"):
        """Save the current board state as an SVG file."""
        board_svg = chess.svg.board(self.board)
        with open(filename, "w") as f:
            f.write(board_svg)

    @message_handler
    async def handle_message(self, message: UserMessage, ctx: MessageContext) -> None:
        reply = await self.assistant.handle_message(message.content)
        print(f"Assistant reply: {reply}")
        try:
            self.board.push_uci(reply)
            print(f"Move applied: {reply}")
            self.save_board_svg()
        except ValueError as e:
            print(f"Illegal move: {reply}. Error: {e}")

# Define a runtime and register the agent
async def main():
    runtime = SingleThreadedAgentRuntime()
    await UmpireAgentWrapper.register(runtime, "umpire_agent", lambda: UmpireAgentWrapper("umpire_agent"))

    runtime.start()
    agent_id = AgentId("umpire_agent", "default")

    # Send a sample message
    test_message = UserMessage(content="Play e2e4")
    await runtime.send_message(test_message, agent_id)

    await runtime.stop()

if __name__ == "__main__":
    asyncio.run(main())
