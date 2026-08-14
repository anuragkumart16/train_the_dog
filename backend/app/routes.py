from fastapi import APIRouter

from .modules import ResetRequest, RewardRequest
from .state import (
    apply_reward,
    create_game_response,
    fetch_sequence,
    reset_response,
)


router = APIRouter(prefix="/game", tags=["game"])


@router.post("/new")
def new_game():
    return create_game_response()


@router.post("/fetch")
def fetch_moves():
    return fetch_sequence()


@router.post("/reward")
def reward(request: RewardRequest):
    return apply_reward(request.value)


@router.post("/reset")
def reset_game(request: ResetRequest):
    return reset_response(request.type)
