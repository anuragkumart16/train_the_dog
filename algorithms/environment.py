import random

class Environment:
    def __init__(self, grid_size):
        self.grid_size = grid_size
        self.dog_position = [0, 0]
        self.bone_position = [1, 0]
        self.human_position = [grid_size - 1, grid_size - 1]
        self.bone_picked = False

    def init_grid(self):
        available_positions = [
            (row, col)
            for row in range(self.grid_size)
            for col in range(self.grid_size)
        ]

        # Random dog position
        dog_coordinates = random.choice(available_positions)
        available_positions.remove(dog_coordinates)
        self.dog_position = list(dog_coordinates)

        # Random bone position
        bone_coordinates = random.choice(available_positions)
        available_positions.remove(bone_coordinates)
        self.bone_position = list(bone_coordinates)

        # Human stays at the bottom-right corner
        self.human_position = [
            self.grid_size - 1,
            self.grid_size - 1
        ]

        self.bone_picked = False

        return self.get_grid()

    def get_dog_position(self):
        return self.dog_position

    def get_bone_position(self):
        return self.bone_position

    def get_human_position(self):
        return self.human_position

    def set_bone_picked(self):
        self.bone_picked = True
        return self.bone_picked

    def is_bone_picked(self):
        return self.bone_picked

    def get_grid(self):
        grid = [
            ["."] * self.grid_size
            for _ in range(self.grid_size)
        ]

        dog_x, dog_y = self.dog_position
        bone_x, bone_y = self.bone_position
        human_x, human_y = self.human_position

        grid[dog_y][dog_x] = "D"

        if not self.bone_picked:
            grid[bone_y][bone_x] = "B"

        grid[human_y][human_x] = "H"

        return grid

    def move_dog_up(self):
        if self.dog_position[1] + 1 >= self.grid_size:
            return False, self.get_grid()

        self.dog_position[1] += 1
        return True, self.get_grid()

    def move_dog_down(self):
        if self.dog_position[1] - 1 < 0:
            return False, self.get_grid()

        self.dog_position[1] -= 1
        return True, self.get_grid()

    def move_dog_right(self):
        if self.dog_position[0] + 1 >= self.grid_size:
            return False, self.get_grid()

        self.dog_position[0] += 1
        return True, self.get_grid()

    def move_dog_left(self):
        if self.dog_position[0] - 1 < 0:
            return False, self.get_grid()

        self.dog_position[0] -= 1
        return True, self.get_grid()