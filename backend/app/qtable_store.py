"""
Q-Table Store - Manages loading and persisting the Q-table.
Loads baseline Q-table from the root q_table.py file.
"""

import sys
import random
from pathlib import Path

ACTIONS = ("LEFT", "RIGHT", "UP", "DOWN")


def get_baseline_qtable():
    """
    Load the baseline Q-table from q_table.py in the project root.
    
    Returns:
        dict: Q-table with state-action values
    """
    try:
        # Add project root to path
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        from q_table import Q_TABLE
        
        return Q_TABLE.copy()
    except ImportError as e:
        print(f"Warning: Could not load Q-table from q_table.py: {e}")
        return {}


def load_baseline():
    """
    Load and return a copy of the baseline Q-table, adapted to 4-tuple states:
    (bone_direction, human_direction, bone_picked, is_near_boundary).
    """
    baseline = get_baseline_qtable()
    q_table = {}
    
    for state, actions in baseline.items():
        if len(state) == 3:
            b_dir, h_dir, picked = state
            q_table[(b_dir, h_dir, picked, False)] = actions.copy()
            q_table[(b_dir, h_dir, picked, True)] = {
                a: v - 1.0 for a, v in actions.items()
            }
        else:
            q_table[state] = actions.copy()
            
    return q_table


def save_qtable(q_table, filepath=None):
    """
    Save Q-table to a file for persistence.
    
    Args:
        q_table (dict): Q-table to save
        filepath (str, optional): Path to save. Defaults to root q_table.py
    """
    if filepath is None:
        project_root = Path(__file__).parent.parent.parent
        filepath = project_root / "q_table_trained.py"
    
    with open(filepath, "w") as f:
        f.write("Q_TABLE = ")
        f.write(repr(q_table))
    
    print(f"Q-table saved to {filepath}")


def get_q_value(q_table, state, action, default=0.0):
    """
    Get Q-value for a state-action pair.
    
    Args:
        q_table (dict): Q-table
        state (tuple): State representation
        action (str): Action name
        default (float): Default value if not found
    
    Returns:
        float: Q-value
    """
    if state not in q_table:
        q_table[state] = {a: 0.0 for a in ACTIONS}
    
    return q_table[state].get(action, default)


def set_q_value(q_table, state, action, value):
    """
    Set Q-value for a state-action pair.
    
    Args:
        q_table (dict): Q-table (modified in-place)
        state (tuple): State representation
        action (str): Action name
        value (float): New Q-value
    """
    if state not in q_table:
        q_table[state] = {a: 0.0 for a in ACTIONS}
    
    q_table[state][action] = value


def get_valid_actions(pos=None):
    """Get list of valid actions for a position inside 5x5 grid."""
    if pos is None:
        return list(ACTIONS)
    r, c = pos
    valid = []
    if r > 0: valid.append("UP")
    if r < 4: valid.append("DOWN")
    if c > 0: valid.append("LEFT")
    if c < 4: valid.append("RIGHT")
    return valid if valid else list(ACTIONS)


def default_q_values_for_state(state):
    """Create useful initial Q-values for a previously unseen state."""
    q_vals = {action: 0.0 for action in ACTIONS}

    if not isinstance(state, (tuple, list)) or len(state) < 3:
        return q_vals

    bone_dir = state[0]
    human_dir = state[1]
    bone_picked = state[2]
    near_boundary = bool(state[3]) if len(state) > 3 else False

    target_dir = human_dir if bone_picked else bone_dir
    if target_dir in q_vals:
        q_vals[target_dir] = 5.0

    if near_boundary:
        q_vals = {action: value - 0.5 for action, value in q_vals.items()}

    return q_vals


def get_best_action(q_table, state, pos=None, forbidden_pos=None):
    """
    Get the best valid action for a state based on Q-values.
    Uses target direction heuristic for unvisited states and filters out invalid wall moves.
    Optional forbidden_pos excludes the action that leads back to that position (anti-backtrack).
    """
    if state is None:
        return "UP"

    if state not in q_table:
        q_table[state] = default_q_values_for_state(state)
    
    valid_actions = get_valid_actions(pos)

    # If forbidden_pos is set, compute which action leads to it and exclude it (unless it's the only option)
    if forbidden_pos is not None and pos is not None:
        r, c = pos
        fr, fc = forbidden_pos
        dr, dc = fr - r, fc - c
        forbidden_action = None
        if dr == -1 and dc == 0: forbidden_action = "UP"
        elif dr == 1 and dc == 0: forbidden_action = "DOWN"
        elif dr == 0 and dc == -1: forbidden_action = "LEFT"
        elif dr == 0 and dc == 1: forbidden_action = "RIGHT"
        if forbidden_action and len(valid_actions) > 1:
            valid_actions = [a for a in valid_actions if a != forbidden_action]

    valid_q_vals = {a: q_table[state][a] for a in valid_actions if a in q_table[state]}
    if not valid_q_vals:
        valid_q_vals = q_table[state]

    # Return valid action with highest Q-value, breaking ties randomly
    max_val = max(valid_q_vals.values())
    best_actions = [a for a, v in valid_q_vals.items() if v == max_val]
    return random.choice(best_actions)
