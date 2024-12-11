import pygame
import sys
import copy
import pandas as pd
import tkinter as tk
from tkinter import filedialog

from Astar import AStar

# Constants
VIEW_HISTORY = True   # Set to True to visualize the algorithm's progress
FRAME_DELAY = 2     # Number of frames to wait before showing the next step

# Initialize Pygame
pygame.init()

# Grid parameters
GRID_WIDTH = 20    # Number of columns
GRID_HEIGHT = 20   # Number of rows
CELL_SIZE = 30     # Size of each cell in pixels

# Window dimensions
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE

# Set up the display
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("A* Simulation")

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Initialize the grid with zeros (open spaces)
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Agent's starting position (row, col)
agent_pos = [0, 0]

# Variable to keep track of the goal cell (None if no goal is set)
goal_pos = None

# Variable to store the path
path = []

# Variables for visualization
visualizing_history = False
history = []
history_index = 0
frames_since_last_update = 0

def get_cell_pos(pos):
    """Convert pixel position to grid coordinates."""
    x, y = pos
    col = x // CELL_SIZE
    row = y // CELL_SIZE
    return row, col

def draw_grid(path, current_history):
    """Draw the grid, walls, goal, path, and history."""
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)

            if (row, col) == goal_pos:
                color = (255, 0, 0)  # Goal cell in red
            elif visualizing_history and (col, row) in current_history:
                color = (255, 255, 0)  # Cells being considered in yellow
            elif (col, row) in path:
                color = (173, 216, 230)  # Final path in light blue
            elif grid[row][col] == 1:
                color = (50, 50, 50)  # Wall cells in dark gray
            else:
                color = (200, 200, 200)  # Open cells in light gray
            pygame.draw.rect(window, color, rect)
            # Draw grid lines
            pygame.draw.rect(window, (150, 150, 150), rect, 1)

def draw_agent():
    """Draw the agent on the grid."""
    row, col = agent_pos
    rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(window, (0, 255, 0), rect)  # Agent is green

def select_file():
    # Create a Tkinter root window (it won't be shown)
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    
    # Open a file dialog to select a file
    file_path = filedialog.askopenfilename(
        title="Select a World",  # Window title
        filetypes=(("World files", "*.world"), ("All files", "*.*"))  # File types to show
    )
    
    return file_path

def save_file():
    # Create a Tkinter root window (it won't be shown)
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    
    # Open a file dialog to save a file
    file_path = filedialog.asksaveasfilename(
        title="Save as",  # Window title
        defaultextension=".path",  # Default file extension
        filetypes=(("World files", "*.world"), ("All files", "*.*"))  # File types to show
    )
    
    return file_path

# Variable to track if the mouse button is pressed
mouse_pressed = False

# Main game loop
running = True
cells_clicked = []
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        # Handle mouse button down
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pressed = True
            mouse_pos = pygame.mouse.get_pos()
            row, col = get_cell_pos(mouse_pos)
            if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
                grid[row][col] = 1 - grid[row][col]  # Toggle between wall and open space
                cells_clicked.append((row, col))

        # Handle mouse button up
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_pressed = False
            cells_clicked = []

        # Handle mouse motion
        if event.type == pygame.MOUSEMOTION:
            if mouse_pressed:
                mouse_pos = pygame.mouse.get_pos()
                row, col = get_cell_pos(mouse_pos)
                if (0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH and
                    (row, col) not in cells_clicked):
                    if (row, col) != tuple(agent_pos) and (goal_pos is None or (row, col) != goal_pos):
                        grid[row][col] = 1 - grid[row][col]  # Toggle cell
                        cells_clicked.append((row, col))

        # Handle key presses
        if event.type == pygame.KEYDOWN:
            # Agent movement
            new_row, new_col = agent_pos
            if event.key == pygame.K_w:   # Move up
                new_row -= 1
            if event.key == pygame.K_s:   # Move down
                new_row += 1
            if event.key == pygame.K_a:   # Move left
                new_col -= 1
            if event.key == pygame.K_d:   # Move right
                new_col += 1

            # Check boundaries and collisions with walls
            if (0 <= new_row < GRID_HEIGHT and 0 <= new_col < GRID_WIDTH and
                grid[new_row][new_col] == 0):
                agent_pos = [new_row, new_col]

            # Set or unset the goal cell
            if event.key == pygame.K_g:
                mouse_pos = pygame.mouse.get_pos()
                row, col = get_cell_pos(mouse_pos)
                if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
                    if goal_pos == (row, col):
                        goal_pos = None  # Remove goal if same cell
                    else:
                        goal_pos = (row, col)  # Set new goal cell

            # Compute the path when 'R' is pressed
            if event.key == pygame.K_r:
                # Cancel and restart visualization if already in progress
                if visualizing_history:
                    visualizing_history = False

                # Reset visualization variables
                path = []
                history = []
                history_index = 0
                frames_since_last_update = 0

                if goal_pos is not None:
                    if VIEW_HISTORY:
                        visualizing_history = True

                    try:
                        # Run the A* algorithm to get the path and history
                        matrix = copy.deepcopy(grid)
                        pathfinder = AStar(matrix, agent_pos, goal_pos)
                        path, history = pathfinder.astar()
                        path = [(x, y) for y, x in path]
                        for i in range(len(history)):
                            history[i] = [(x, y) for y, x in history[i]]
                    except:
                        if not path:
                            print('No path could be found.')
                            path = []
                            visualizing_history = False  # No need to visualize if no path
                else:
                    print("Please set a goal position by pressing 'G' over a cell.")

            # Clear the path when 'C' is pressed
            if event.key == pygame.K_c:
                path = []
                history = []
                visualizing_history = False
                pygame.display.set_caption("A* Simulation")


            # Clear the path and blocked cells when 'X' is pressed
            if event.key == pygame.K_x:
                path = []
                history = []
                visualizing_history = False
                pygame.display.set_caption("A* Simulation")
                grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

            # Save blocked cells when 'J' is pressed
            if event.key == pygame.K_j:
                file_path = save_file()  # Use a separate variable for the file path
                if file_path is not None and file_path != '':
                    pd.DataFrame(grid).to_csv(file_path, index=False, header=False)
                    
            # Loads blocked cells when 'k' is pressed
            if event.key == pygame.K_k:
                file_path = select_file()  # Use a separate variable for the file path
                if file_path is not None and file_path != '':
                    grid = pd.read_csv(file_path, header=None).astype(dtype='int64').to_numpy().__array__()

    # Update visualization
    if visualizing_history:
        frames_since_last_update += 1
        if frames_since_last_update >= FRAME_DELAY:
            frames_since_last_update = 0
            if history_index < len(history) - 1:
                history_index += 1
            else:
                pygame.display.set_caption("You found the Goal")
                visualizing_history = False  # Visualization complete
    else:
        history_index = 0  # Reset when not visualizing

    # Set the current history step for drawing
    if visualizing_history:
        current_history = history[history_index]
    else:
        current_history = []

    # Drawing
    window.fill((255, 255, 255))  # Clear the screen
    draw_grid(path, current_history)
    draw_agent()
    pygame.display.flip()
    clock.tick(60)  # Limit the frame rate to 60 FPS
