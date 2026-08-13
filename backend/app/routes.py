from fastapi import APIRouter
from modules import RewardRequest

from state import (
    create_game,
    reset_environment,
    reset_training,
    reset_all,
    fetch_sequence,
    apply_reward,
)


router = APIRouter()


# 1. Create a new game
@router.post("/game/new")
def new_game():
    game = create_game()

    return {
        "dog_position": game["dog_position"],
        "bone_position": game["bone_position"],
        "home_position": game["home_position"],
        "has_bone": game["has_bone"],
        "score": game["score"],
        "move_count": game["move_count"],
    }


# 2. Reset environment
@router.post("/game/reset")
def reset_game():
    game = reset_environment()

    return {
        "dog_position": game["dog_position"],
        "bone_position": game["bone_position"],
        "home_position": game["home_position"],
        "has_bone": game["has_bone"],
        "score": game["score"],
        "move_count": game["move_count"],
    }


# 3. Reset training
@router.post("/training/reset")
def reset_training_route():
    game = reset_training()

    return {
        "message": "Training reset",
        "q_table_size": len(game["q_table"]),
    }


# 4. Reset everything
@router.post("/reset/all")
def reset_all_route():
    game = reset_all()

    return {
        "message": "Environment and training reset",
        "dog_position": game["dog_position"],
        "bone_position": game["bone_position"],
        "home_position": game["home_position"],
        "has_bone": game["has_bone"],
        "score": game["score"],
        "move_count": game["move_count"],
    }


# 5. Fetch sequence
@router.post("/game/fetch")
def game_fetch():
    return fetch_sequence()


# 6. Apply visitor reward
@router.post("/game/reward")
def game_reward(request: RewardRequest):
    return apply_reward(request.value)