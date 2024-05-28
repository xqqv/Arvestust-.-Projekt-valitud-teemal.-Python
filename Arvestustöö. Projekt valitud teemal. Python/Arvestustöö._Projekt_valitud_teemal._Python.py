import pygame
import random
import os

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jungle Maze Adventure")

# Colors
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)

class Maze:
    def __init__(self, width, height, grid_size):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.start_pos = (1, 1)
        self.end_pos = []
        self.coin_positions = []
        self.grid = self.generate_maze()

    def generate_maze(self):
        grid = [[1 for _ in range(self.width // self.grid_size)] for _ in range(self.height // self.grid_size)]
        
        def carve_passages_from(cx, cy, grid):
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            for direction in directions:
                nx, ny = cx + direction[0]*2, cy + direction[1]*2
                if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
                    if grid[ny][nx] == 1:
                        grid[cy + direction[1]][cx + direction[0]] = 0
                        grid[ny][nx] = 0
                        carve_passages_from(nx, ny, grid)

        # Generate multiple finish points
        for _ in range(2):  # Adjust number of finishes as needed
            x = random.randint(self.width // 2, self.width // self.grid_size - 2)
            y = random.randint(1, self.height // self.grid_size - 2)
            self.end_pos.append((x, y))
            grid[y][x] = 0  # Set finish point in the maze

        # Generate random coin positions
        for _ in range(10):  # Adjust number of coins as needed
            x = random.randint(1, self.width // self.grid_size - 2)
            y = random.randint(1, self.height // self.grid_size - 2)
            if grid[y][x] == 0:
                continue  # Skip if position overlaps with finish or start
            self.coin_positions.append((x, y))
            grid[y][x] = 2  # Set coin position in the maze

        carve_passages_from(1, 1, grid)
        grid[1][1] = 0  # Ensure start position is clear
        return grid

    def draw(self, screen):
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell == 1:
                    pygame.draw.rect(screen, BROWN, (j * self.grid_size, i * self.grid_size, self.grid_size, self.grid_size))

class Player:
    def __init__(self, start_pos, grid_size):
        self.pos = list(start_pos)
        self.size = grid_size
        self.color = RED
        self.score = 0  # Initialize player score
        self.coins_collected = 0

    def move(self, keys, maze):
        new_pos = self.pos.copy()
        if keys[pygame.K_LEFT]:
            new_pos[0] -= 1
        if keys[pygame.K_RIGHT]:
            new_pos[0] += 1
        if keys[pygame.K_UP]:
            new_pos[1] -= 1
        if keys[pygame.K_DOWN]:
            new_pos[1] += 1

        # Check collisions with walls
        if 0 <= new_pos[0] < len(maze.grid[0]) and 0 <= new_pos[1] < len(maze.grid):
            if maze.grid[new_pos[1]][new_pos[0]] == 0:
                self.pos = new_pos

        # Check if player collects coins
        if maze.grid[new_pos[1]][new_pos[0]] == 2:
            maze.grid[new_pos[1]][new_pos[0]] = 0  # Remove coin from maze
            self.score += 50
            self.coins_collected += 1

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.pos[0] * self.size, self.pos[1] * self.size, self.size, self.size))

    def reset_score(self):
        self.score = 0
        self.coins_collected = 0

class Score:
    def __init__(self):
        self.score = 0
        self.high_score = self.load_high_score()

    def load_high_score(self):
        if os.path.exists('data/high_score.txt'):
            with open('data/high_score.txt', 'r') as file:
                return int(file.read())
        return 0

    def save_high_score(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        with open('data/high_score.txt', 'w') as file:
            file.write(str(self.high_score))

    def add_points(self, points):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def draw(self, screen):
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        high_score_text = font.render(f'High Score: {self.high_score}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 50))

def main():
    clock = pygame.time.Clock()
    levels = [
        Maze(WIDTH, HEIGHT, GRID_SIZE),  # Level 1
        Maze(WIDTH, HEIGHT, GRID_SIZE)   # Level 2 (add more levels as needed)
    ]
    current_level = 0
    maze = levels[current_level]
    player = Player(maze.start_pos, GRID_SIZE)
    score = Score()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.move(keys, maze)

        # Check if player reaches any of the finish points
        for end_pos in maze.end_pos:
            if player.pos == list(end_pos):
                score.add_points(100)  # Adjust points as needed
                player.reset_score()
                current_level += 1
                if current_level < len(levels):
                    maze = levels[current_level]
                    player.pos = list(maze.start_pos)
                else:
                    # Game completed all levels (you can add game completion logic here)
                    running = False
                break

        screen.fill(GREEN)
        maze.draw(screen)
        player.draw(screen)
        score.draw(screen)

        # Draw coins in the maze
        for coin_pos in maze.coin_positions:
            pygame.draw.circle(screen, YELLOW, (coin_pos[0] * GRID_SIZE + GRID_SIZE // 2, coin_pos[1] * GRID_SIZE + GRID_SIZE // 2), 5)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
