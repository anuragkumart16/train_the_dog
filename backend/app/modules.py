from typing import Literal, Optional

from pydantic import BaseModel


# Reward request
class RewardRequest(BaseModel):
    value: Literal[1, -1]


# Reset request
class ResetRequest(BaseModel):
    type: Literal["all", "env", "train"]


# Position
class Position(BaseModel):
    x: int
    y: int


# Step response
class StepResponse(BaseModel):
    pos: Position
    action: Literal["up", "down", "left", "right"]
    reward: Optional[float] = None
    source: Literal["automatic", "human"]