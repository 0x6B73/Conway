import pygame
import random
import os
import ctypes
import numpy as np
import tkinter as tk
from tkinter import messagebox, filedialog

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
CELL_SIZE = 10  # Adjusted cell size for easier visibility

# Grid dimensions
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE
MENU_HEIGHT = 60

# Colors
GREY = (30, 30, 30)
LIGHT_GREY = (100, 100, 100)
BLUE_SHADES = [
    (30, 144, 255),
    (70, 130, 180),
    (135, 206, 235),
    (173, 216, 230)
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

# Game speed
game_speed = 10

# Hotkeys
hotkeys = [
    ("Space", "Pause/Unpause the simulation"),
    ("+", "Increase game speed"),
    ("-", "Decrease game speed"),
    ("O", "Open RLE file"),
    ("C", "Clear the grid"),
]

# Function to show hotkeys in a popup window
def show_hotkeys():
    root = tk.Tk()
    root.withdraw()
    hotkey_text = "\n".join(f"{key}: {desc}" for key, desc in hotkeys)
    messagebox.showinfo("Hotkeys", hotkey_text)

# Function to parse RLE files
import tkinter as tk
from tkinter import messagebox
import os  # Ensure os is imported if not already done

def parse_rle(filename, grid):
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Remove comments and extract dimensions
    data = ''
    width = height = 0
    for line in lines:
        if line.startswith('x'):
            parts = line.split(',')
            width = int(parts[0].split('=')[1].strip())
            height = int(parts[1].split('=')[1].strip())
        elif not line.startswith('#'):
            data += line.strip()

    # Check if the pattern is too large for the current grid
    if width > GRID_WIDTH or height > GRID_HEIGHT:
        root = tk.Tk()
        root.withdraw()  # Hide the main Tk window
        proceed = messagebox.askyesno(
            "Pattern Too Large",
            f"The selected pattern is larger than the current grid size.\n"
            f"Pattern size: {width} x {height}\n"
            f"Current grid size: {GRID_WIDTH} x {GRID_HEIGHT}\n\n"
            "Would you like to proceed anyway?"
        )
        if not proceed:
            return  # Exit the function if the user chooses not to proceed

    # Calculate starting position to center the pattern
    start_x = (GRID_WIDTH - width) // 2
    start_y = (GRID_HEIGHT - height) // 2

    x = y = 0
    count = ''
    for char in data:
        if char.isdigit():
            count += char
        else:
            if count == '':
                count = '1'
            count = int(count)
            if char == 'o':
                for _ in range(count):
                    grid_x = x + start_x
                    grid_y = y + start_y
                    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                        grid[grid_x, grid_y] = 1
                    x += 1
            elif char == 'b':
                x += count
            elif char == '$':
                y += count
                x = 0
            elif char == '!':
                break
            count = ''

# Function to open a file dialog and load an RLE file
def open_rle_file():
    root = tk.Tk()
    root.withdraw()  # Hide the main Tk window
    file_path = filedialog.askopenfilename(filetypes=[("RLE files", "*.rle"), ("All files", "*.*")])
    if file_path:
        parse_rle(file_path, grid)
    
    # Bring the Pygame window to the foreground on Windows
    if ctypes and os.name == 'nt':  # Check if running on Windows
        hwnd = pygame.display.get_wm_info()['window']
        ctypes.windll.user32.SetForegroundWindow(hwnd)


# Button class for menu interaction
class Button:
    def __init__(self, x, y, text, action):
        # Adjust button width based on text
        width = font.size(text)[0] + 20
        height = 40
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
    Button(10, SCREEN_HEIGHT + 10, "Start", lambda: start_simulation()),
    Button(90, SCREEN_HEIGHT + 10, "Open RLE", open_rle_file),
    Button(220, SCREEN_HEIGHT + 10, "Clear", lambda: grid.fill(0)),
    Button(310, SCREEN_HEIGHT + 10, "Hotkeys", show_hotkeys),
]

# Start simulation function
def start_simulation():
    global paused
    paused = False

# Function to update grid based on Conway's Game of Life rules
def update_grid(grid):
    new_grid = np.copy(grid)
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            alive_neighbors = np.sum(grid[max(x - 1, 0):min(x + 2, GRID_WIDTH), max(y - 1, 0):min(y + 2, GRID_HEIGHT)]) - grid[x, y]
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
    global grid, dragging, toggle_target, paused, game_speed
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
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    game_speed += 1
                elif event.key == pygame.K_MINUS:
                    game_speed = max(1, game_speed - 1)
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if pos[1] > SCREEN_HEIGHT:
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
        clock.tick(game_speed)

    pygame.quit()

if __name__ == "__main__":
    main()
