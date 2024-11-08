import pygame
import random

# Colors
WHITE = (255, 255, 255)
GREEN_GAS_COLOR = (0, 255, 0)  # Alpha channel removed for compatibility
STABLE_COLOR = (34, 139, 34)
CHAOTIC_COLOR = (255, 0, 0)
RECOVERY_COLOR = (0, 0, 255)
PLAYER_COLOR = (200, 200, 0)  # Yellow for player
COLLAPSE_COLOR = (255, 0, 0)
BACKGROUND_COLOR = (30, 30, 30)
CATCHER_COLOR = (255, 215, 0)  # Gold for catcher

# Game Parameters
MAX_GREEN_GAS = 100
COLLAPSE_THRESHOLD = 80
GREEN_GAS_INCREASE_RATE = 0.5
GAS_EMIT_RATE = 1
OBJECT_COUNT = 10
CATCHER_COUNT = 3  # New catchers to catch green gas
RECOVERY_RATE = 0.1
GAS_DRAIN_RATE = 0.1
POWER_UP_CHANCE = 0.05
POWER_UP_EFFECT_TIME = 200

class Game:
    def __init__(self, screen, font, width, height):
        self.screen = screen
        self.font = font
        self.width = width
        self.height = height
        self.objects = []
        self.catchers = []
        self.green_gas_level = 0
        self.game_over = False
        self.score = 0
        self.power_up_active = False
        self.power_up_timer = 0
        self.player = Player(self.width // 2, self.height // 2, self)  # Pass game instance to player

        self.create_objects()
        self.create_catchers()

    def create_objects(self):
        for _ in range(OBJECT_COUNT):
            obj_type = random.choice(["stable", "chaotic", "gas", "recovery"])
            self.objects.append(GameObject(obj_type, random.randint(100, self.width - 100), random.randint(100, self.height - 100)))

    def create_catchers(self):
        for _ in range(CATCHER_COUNT):
            self.catchers.append(GasCatcher(random.randint(100, self.width - 100), random.randint(100, self.height - 100)))

    def update(self):
        if self.game_over:
            return
        
        self.player.update()
        for obj in self.objects:
            obj.update()
            if obj.state == "chaotic":
                self.green_gas_level += GAS_EMIT_RATE
                obj.emit_gas_particles(self.screen)  # Emit gas particles

            if self.player.collides_with(obj):
                if obj.state == "chaotic" and not self.power_up_active:
                    self.green_gas_level += 5  # Penalty for hitting chaotic objects
                elif obj.state == "recovery":
                    self.green_gas_level = max(0, self.green_gas_level - 5)  # Recovery effect

        if self.green_gas_level >= COLLAPSE_THRESHOLD:
            self.handle_world_collapse()

        if self.green_gas_level < MAX_GREEN_GAS:
            self.green_gas_level += GREEN_GAS_INCREASE_RATE

        for obj in self.objects:
            if obj.state == "recovery":
                self.green_gas_level = max(0, self.green_gas_level - RECOVERY_RATE)

        if self.green_gas_level > 0 and self.power_up_active:
            self.green_gas_level = max(0, self.green_gas_level - GAS_DRAIN_RATE)

        if self.power_up_active:
            self.power_up_timer -= 1
            if self.power_up_timer <= 0:
                self.deactivate_power_up()

        for catcher in self.catchers:
            catcher.update()
            catcher.catch_green_gas(self.objects, self)

        self.score += 1

    def draw(self):
        if self.game_over:
            return

        self.screen.fill(BACKGROUND_COLOR)

        for obj in self.objects:
            obj.draw(self.screen)
        for catcher in self.catchers:
            catcher.draw(self.screen)

        self.player.draw(self.screen)

        gas_text = self.font.render(f"Green Gas: {self.green_gas_level}/{MAX_GREEN_GAS}", True, WHITE)
        self.screen.blit(gas_text, (10, 10))

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (self.width - 150, 10))

        if self.power_up_active:
            power_up_text = self.font.render("Power-Up Active!", True, (0, 255, 255))
            self.screen.blit(power_up_text, (self.width // 2 - 100, 50))

    def handle_world_collapse(self):
        collapse_text = self.font.render("World Collapse! Green Gas has overtaken!", True, COLLAPSE_COLOR)
        self.screen.blit(collapse_text, (self.width // 4, self.height // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        self.game_over = True

    def activate_power_up(self):
        self.power_up_active = True
        self.power_up_timer = POWER_UP_EFFECT_TIME
        self.player.color = (0, 255, 255)  # Change player color during power-up

    def deactivate_power_up(self):
        self.power_up_active = False
        self.player.color = PLAYER_COLOR

class Player:
    def __init__(self, x, y, game):
        self.x = x
        self.y = y
        self.speed = 5
        self.color = PLAYER_COLOR
        self.size = 15
        self.game = game  # Reference to game

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > self.size:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < self.game.width - self.size:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > self.size:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < self.game.height - self.size:
            self.y += self.speed

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)
        if self.game.power_up_active:
            pygame.draw.circle(screen, (255, 255, 0), (self.x, self.y), self.size + 5, 2)

    def collides_with(self, obj):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2).colliderect(
            pygame.Rect(obj.x - 20, obj.y - 20, 40, 40))

class GameObject:
    def __init__(self, state, x, y):
        self.state = state
        self.x = x
        self.y = y
        self.color = self.get_color()

    def get_color(self):
        if self.state == "stable":
            return STABLE_COLOR
        elif self.state == "chaotic":
            return CHAOTIC_COLOR
        elif self.state == "gas":
            return GREEN_GAS_COLOR
        elif self.state == "recovery":
            return RECOVERY_COLOR

    def update(self):
        if self.state == "stable" and random.random() < 0.05:
            self.state = "chaotic"
        elif self.state == "chaotic" and random.random() < 0.02:
            self.state = "gas"
        elif self.state == "gas" and random.random() < 0.02:
            self.state = "recovery"

    def draw(self, screen):
        if self.state == "chaotic":
            pygame.draw.circle(screen, self.color, (self.x, self.y), 20)
        elif self.state == "gas":
            pygame.draw.circle(screen, self.color, (self.x, self.y), 15)
        elif self.state == "recovery":
            pygame.draw.rect(screen, self.color, (self.x - 20, self.y - 20, 40, 40))
        else:
            pygame.draw.rect(screen, self.color, (self.x - 20, self.y - 20, 40, 40))

    def emit_gas_particles(self, screen):
        for _ in range(5):  # Emit 5 particles
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-10, 10)
            particle_pos = (self.x + offset_x, self.y + offset_y)
            pygame.draw.circle(screen, GREEN_GAS_COLOR, particle_pos, 3)  # Small green particles

class GasCatcher:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 30

    def update(self):
        self.y += 1
        if self.y > 600:
            self.y = -self.size  # Reset to top

    def draw(self, screen):
        pygame.draw.circle(screen, CATCHER_COLOR, (self.x, self.y), self.size)

    def catch_green_gas(self, objects, game):
        for obj in objects:
            if obj.state == "gas" and self.collides_with(obj):
                game.green_gas_level = max(0, game.green_gas_level - 5)  # Catch and reduce gas level
                obj.state = "stable"  # Reset object state

    def collides_with(self, obj):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2).colliderect(
            pygame.Rect(obj.x - 20, obj.y - 20, 40, 40))

pygame.init()

# Game settings
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Green Gas Game")
font = pygame.font.SysFont("Arial", 20)

# Game Loop
clock = pygame.time.Clock()
game = Game(screen, font, WIDTH, HEIGHT)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    game.update()
    game.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

