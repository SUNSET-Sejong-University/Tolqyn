import asyncio
import json
from spoon_ai.agents.base import BaseAgent
from spoon_ai.chat import ChatBot

# --------------------------------------------------
# Spoon Agent Definition
# --------------------------------------------------

class RotationDirectorAgent(BaseAgent):
    name: str = "rotation_director"
    description: str = "Controls expressive rotation gains for generative 3D art"

    system_prompt: str = """
    You are an AI creative director for a generative 3D audiovisual artwork.

    You do NOT control raw sensor data.
    You ONLY output expressive multipliers for rotation.

    Rules:
    - Output calm values when motion is low
    - Amplify X and Z for dramatic motion
    - Keep Y subtle and stabilizing
    - Never exceed safe ranges
    - ALWAYS respond with valid JSON only
    """

# --------------------------------------------------
# Agent lifecycle helpers
# --------------------------------------------------

async def _create_agent():
    return RotationDirectorAgent(
        llm=ChatBot(
            llm_provider="openrouter",
            model_name="gpt-5.1-chat-latest"
        )
    )

async def _ask_agent(agent, ax, ay, az):
    prompt = f"""
    Current motion state:
    angleX = {ax}
    angleY = {ay}
    angleZ = {az}

    Return ONLY valid JSON:
    {{
      "mode": "calm | reactive | intense",
      "rotationGainX": 0.1-1.0,
      "rotationGainY": 0.1-1.0,
      "rotationGainZ": 0.1-1.0
    }}
    """
    return await agent.run(prompt)

# --------------------------------------------------
# Public synchronous wrapper
# --------------------------------------------------

class SpoonRotationController:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.agent = self.loop.run_until_complete(_create_agent())

    def get_rotation_gains(self, ax, ay, az):
        try:
            text = self.loop.run_until_complete(
                _ask_agent(self.agent, ax, ay, az)
            )
            return json.loads(text)
        except Exception as e:
            print("[Spoon Agent error]", e)
            return None
