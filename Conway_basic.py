import pygame
import numpy as np
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
CELL_SIZE = 20  # Larger cell size to make cells easier to see

# Grid dimensions
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE
MENU_HEIGHT = 60

# Colors
GREY = (30, 30, 30)  # Dark grey background color
LIGHT_GREY = (100, 100, 100)  # Color for grid lines
BLUE_SHADES = [
    (30, 144, 255),  # Dodger blue
    (70, 130, 180),  # Steel blue
    (135, 206, 235),  # Sky blue
    (173, 216, 230)  # Light blue
]
WHITE = (255, 255, 255)
BUTTON_COLOR = (60, 60, 60)
BUTTON_HOVER_COLOR = (90, 90, 90)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + MENU_HEIGHT))
pygame.display.set_caption("Conway's Game of Life")

# Initialize font
font = pygame.font.Font(None, 30)

# Start with an empty grid
grid = np.zeros((GRID_WIDTH, GRID_HEIGHT), dtype=int)

# Variables for drag toggle behavior
dragging = False
toggle_target = 1

# Define patterns
def set_glider(grid):
    glider = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]
    for x, y in glider:
        grid[x + GRID_WIDTH // 2, y + GRID_HEIGHT // 2] = 1

def set_lwss(grid):
    lwss = [(1, 0), (4, 0), (0, 1), (0, 2), (4, 2), (0, 3), (1, 3), (2, 3), (3, 3)]
    for x, y in lwss:
        grid[x + GRID_WIDTH // 2 - 2, y + GRID_HEIGHT // 2 - 2] = 1

def set_blinker(grid):
    blinker = [(1, 0), (1, 1), (1, 2)]
    for x, y in blinker:
        grid[x + GRID_WIDTH // 2, y + GRID_HEIGHT // 2] = 1

def set_mwss(grid):
    # Middleweight spaceship pattern
    mwss = [(1, 0), (2, 0), (3, 0), (4, 0), (0, 1), (4, 1), (4, 2), (0, 3), (3, 3)]
    for x, y in mwss:
        grid[x + GRID_WIDTH // 2 - 2, y + GRID_HEIGHT // 2 - 2] = 1

# Helper function to randomize grid
def randomize_grid():
    global grid
    grid = np.random.randint(2, size=(GRID_WIDTH, GRID_HEIGHT))

# Button class for menu interaction
class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = BUTTON_COLOR

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surface = font.render(self.text, True, WHITE)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.action()
            return True
        return False

    def update_color(self, pos):
        if self.rect.collidepoint(pos):
            self.color = BUTTON_HOVER_COLOR
        else:
            self.color = BUTTON_COLOR

# Create buttons for the menu
buttons = [
    Button(10, SCREEN_HEIGHT + 10, 100, 40, "Start", lambda: start_simulation()),
    Button(120, SCREEN_HEIGHT + 10, 100, 40, "Glider", lambda: set_glider(grid)),
    Button(230, SCREEN_HEIGHT + 10, 100, 40, "LWSS", lambda: set_lwss(grid)),
    Button(340, SCREEN_HEIGHT + 10, 100, 40, "Blinker", lambda: set_blinker(grid)),
    Button(450, SCREEN_HEIGHT + 10, 100, 40, "MWSS", lambda: set_mwss(grid)),
    Button(560, SCREEN_HEIGHT + 10, 100, 40, "Clear", lambda: grid.fill(0)),
    Button(670, SCREEN_HEIGHT + 10, 130, 40, "Randomize", randomize_grid),
]

# Start simulation function
def start_simulation():
    global paused
    paused = False  # Unpauses the game

# Function to update grid based on Conway's Game of Life rules
def update_grid(grid):
    new_grid = np.copy(grid)
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            alive_neighbors = np.sum(grid[x - 1:x + 2, y - 1:y + 2]) - grid[x, y]
            if grid[x, y] == 1:
                if alive_neighbors < 2 or alive_neighbors > 3:
                    new_grid[x, y] = 0
            else:
                if alive_neighbors == 3:
                    new_grid[x, y] = 1
    return new_grid

# Function to draw the grid and cells on the screen
def draw_grid(grid):
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            color = random.choice(BLUE_SHADES) if grid[x, y] == 1 else GREY
            pygame.draw.rect(screen, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, LIGHT_GREY, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, LIGHT_GREY, (0, y), (SCREEN_WIDTH, y))

# Draw the menu with buttons
def draw_menu():
    pygame.draw.rect(screen, GREY, (0, SCREEN_HEIGHT, SCREEN_WIDTH, MENU_HEIGHT))
    for button in buttons:
        button.draw(screen)

# Main game loop
def main():
    global grid, dragging, toggle_target, paused
    clock = pygame.time.Clock()
    running = True
    paused = True

    while running:
        screen.fill(GREY)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if pos[1] > SCREEN_HEIGHT:  # If click is in the menu
                    for button in buttons:
                        if button.check_click(pos):
                            break
                else:
                    cell_x, cell_y = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
                    grid[cell_x, cell_y] = 1 - grid[cell_x, cell_y]
                    dragging = True
                    toggle_target = grid[cell_x, cell_y]
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False

        if dragging:
            pos = pygame.mouse.get_pos()
            if pos[1] < SCREEN_HEIGHT:
                cell_x, cell_y = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
                grid[cell_x, cell_y] = toggle_target

        if not paused:
            grid = update_grid(grid)

        # Update button colors based on hover
        mouse_pos = pygame.mouse.get_pos()
        for button in buttons:
            button.update_color(mouse_pos)

        draw_grid(grid)
        draw_menu()
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    main()
