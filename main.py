import pygame
from game_logic import Game

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Initialize pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("State Shifter: Collapse and Rebirth")

# Set up the font
font = pygame.font.SysFont("Arial", 24)

# Main game loop
def main():
    game = Game(screen, font, WIDTH, HEIGHT)

    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update game logic
        game.update()

        # Draw everything
        game.draw()

        # Update the screen
        pygame.display.flip()

        # Maintain FPS
        pygame.time.Clock().tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()

