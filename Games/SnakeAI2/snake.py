import pygame
import math
import random
import time

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH = 800
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Snake properties
snake_pos = [WIDTH//2, HEIGHT//2]
snake_body = [[snake_pos[0], snake_pos[1]]]
snake_length = 1
snake_speed = 5
snake_angle = 0
TURN_SPEED = 13

# Bonus properties
# AI properties
ai_enabled = True
ai_reaction_distance = 500  # Distance at which AI starts targeting bonus
ai_turn_speed = 25  # How quickly AI turns towards target

def get_angle_to_bonus():
    dx = bonus_pos[0] - snake_pos[0]
    dy = bonus_pos[1] - snake_pos[1] 
    angle = math.degrees(math.atan2(dy, dx))
    if angle < 0:
        angle += 360
    return angle

def get_distance_to_bonus():
    dx = bonus_pos[0] - snake_pos[0]
    dy = bonus_pos[1] - snake_pos[1]
    return math.sqrt(dx*dx + dy*dy)

bonus_pos = [random.randrange(0, WIDTH-20), random.randrange(0, HEIGHT-20)]
bonus_type = random.choice(['speed', 'points'])
bonus_colors = {'speed': BLUE, 'points': RED}

# Game variables
score = 0
game_over = False
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

def spawn_bonus():
    return [random.randrange(0, WIDTH-20), random.randrange(0, HEIGHT-20)], random.choice(['speed', 'points'])

def draw_snake():
    # Draw body segments
    segment_radius = 10
    for segment in snake_body[1:]:
        center = (segment[0] + 10, segment[1] + 10)
        pygame.draw.circle(window, GREEN, (int(center[0]), int(center[1])), segment_radius)
    
    # Draw head
    head = snake_body[0]
    
    # Calculate head direction points based on snake_angle
    head_radius = 12
    head_center = (head[0] + 10, head[1] + 10)
    
    # Calculate triangle points for head
    front_point = (
        head_center[0] + head_radius * math.cos(math.radians(snake_angle)),
        head_center[1] + head_radius * math.sin(math.radians(snake_angle))
    )
    left_point = (
        head_center[0] + head_radius * math.cos(math.radians(snake_angle - 140)),
        head_center[1] + head_radius * math.sin(math.radians(snake_angle - 140))
    )
    right_point = (
        head_center[0] + head_radius * math.cos(math.radians(snake_angle + 140)),
        head_center[1] + head_radius * math.sin(math.radians(snake_angle + 140))
    )
    
    # Draw triangular head
    pygame.draw.polygon(window, GREEN, [front_point, left_point, right_point])
    
    # Draw eyes
    eye_distance = 6
    eye_size = 4
    left_eye_pos = (
        head_center[0] + eye_distance * math.cos(math.radians(snake_angle - 30)),
        head_center[1] + eye_distance * math.sin(math.radians(snake_angle - 30))
    )
    right_eye_pos = (
        head_center[0] + eye_distance * math.cos(math.radians(snake_angle + 30)),
        head_center[1] + eye_distance * math.sin(math.radians(snake_angle + 30))
    )
    
    pygame.draw.circle(window, WHITE, (int(left_eye_pos[0]), int(left_eye_pos[1])), eye_size)
    pygame.draw.circle(window, WHITE, (int(right_eye_pos[0]), int(right_eye_pos[1])), eye_size)
    pygame.draw.circle(window, BLACK, (int(left_eye_pos[0]), int(left_eye_pos[1])), eye_size - 2)
    pygame.draw.circle(window, BLACK, (int(right_eye_pos[0]), int(right_eye_pos[1])), eye_size - 2)

def draw_bonus():
    pygame.draw.rect(window, bonus_colors[bonus_type], (bonus_pos[0], bonus_pos[1], 20, 20))

def check_collision():
    if (abs(snake_pos[0] - bonus_pos[0]) < 20 and 
        abs(snake_pos[1] - bonus_pos[1]) < 20):
        return True
    return False

def check_self_collision():
    # Check if head collides with any body segment (skip the first few segments to prevent false collisions)
    head = snake_body[0]
    for segment in snake_body[3:]:
        if (abs(head[0] - segment[0]) < 15 and 
            abs(head[1] - segment[1]) < 15):
            return True
    return False

def reset_game():
    global snake_pos, snake_body, snake_length, snake_speed, snake_angle, score, bonus_pos, bonus_type
    snake_pos = [WIDTH//2, HEIGHT//2]
    snake_body = [[snake_pos[0], snake_pos[1]]]
    snake_length = 1
    snake_speed = 5
    snake_angle = 0
    score = 0
    bonus_pos, bonus_type = spawn_bonus()

def draw_game_over():
    game_over_text = font.render("GAME OVER!", True, WHITE)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    restart_text = font.render("Press SPACE to restart", True, WHITE)
    
    text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
    score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
    
    window.blit(game_over_text, text_rect)
    window.blit(score_text, score_rect)
    window.blit(restart_text, restart_rect)

# Game loop
game_running = True
while game_running:
    game_over = False
    reset_game()
    
    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                game_running = False

        # Handle key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            snake_angle -= TURN_SPEED
        if keys[pygame.K_RIGHT]:
            snake_angle += TURN_SPEED
        if keys[pygame.K_a]:  # Toggle AI with 'A' key
            ai_enabled = not ai_enabled

        # AI movement
        if ai_enabled:
            distance_to_bonus = get_distance_to_bonus()
            if distance_to_bonus < ai_reaction_distance:
                target_angle = get_angle_to_bonus()
                angle_diff = (target_angle - snake_angle) % 360
                if angle_diff > 180:
                    angle_diff -= 360
                snake_angle += min(ai_turn_speed, max(-ai_turn_speed, angle_diff))

        # Move snake
        dx = snake_speed * math.cos(math.radians(snake_angle))
        dy = snake_speed * math.sin(math.radians(snake_angle))
        snake_pos[0] += dx
        snake_pos[1] += dy

        # Check boundaries
        if snake_pos[0] < 0:
            snake_pos[0] = WIDTH
        elif snake_pos[0] > WIDTH:
            snake_pos[0] = 0
        if snake_pos[1] < 0:
            snake_pos[1] = HEIGHT
        elif snake_pos[1] > HEIGHT:
            snake_pos[1] = 0

        # Update snake body
        snake_body.insert(0, list(snake_pos))
        if len(snake_body) > snake_length:
            snake_body.pop()

        # Check bonus collision
        if check_collision():
            if bonus_type == 'speed':
                snake_speed += 1
            else:  # points
                score += 10
                snake_length += 1
            bonus_pos, bonus_type = spawn_bonus()

        # Check for self collision
        if check_self_collision():
            game_over = True
            continue

        # Draw everything
        window.fill(BLACK)
        draw_snake()
        draw_bonus()
        
        # Draw score, speed and AI status
        speed_text = font.render(f"Speed: {snake_speed}", True, WHITE)
        score_text = font.render(f"Score: {score}", True, WHITE)
        ai_text = font.render(f"AI: {'ON' if ai_enabled else 'OFF'}", True, WHITE)
        window.blit(speed_text, (10, 10))
        window.blit(score_text, (10, 50))
        window.blit(ai_text, (10, 90))

        pygame.display.update()
        clock.tick(30)

    # Game over screen loop
    while game_over and game_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_over = False

        window.fill(BLACK)
        draw_game_over()
        pygame.display.update()
        clock.tick(30)

pygame.quit()
