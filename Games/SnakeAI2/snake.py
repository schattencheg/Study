import pygame
import math
import random
import time

class SnakeAI:
    def __init__(self, reaction_distance=500, turn_speed=15, bonus_timeout=300, evasion_duration=60):
        self.enabled = True
        self.reaction_distance = reaction_distance
        self.turn_speed = turn_speed
        self.bonus_timeout = bonus_timeout
        self.evasion_duration = evasion_duration
        
        self.bonus_timer = 0
        self.is_evading = False
        self.evasion_timer = 0
    
    def reset(self):
        self.bonus_timer = 0
        self.is_evading = False
        self.evasion_timer = 0
    
    def calculate_turn(self, current_angle, target_pos, snake_pos):
        # Calculate distance and angle to target
        dx = target_pos[0] - snake_pos[0]
        dy = target_pos[1] - snake_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if not self.enabled:
            return 0
            
        # Update bonus timer
        if distance < self.reaction_distance:
            self.bonus_timer += 1
        else:
            self.bonus_timer = 0
        
        # Check for evasion
        if self.bonus_timer >= self.bonus_timeout and not self.is_evading:
            self.is_evading = True
            self.evasion_timer = self.evasion_duration
        
        # Handle movement
        if self.is_evading:
            self.evasion_timer -= 1
            if self.evasion_timer <= 0:
                self.is_evading = False
                self.bonus_timer = 0
            # Get angle away from target
            target_angle = (math.degrees(math.atan2(dy, dx)) + 180) % 360
        elif distance < self.reaction_distance:
            # Get angle towards target
            target_angle = math.degrees(math.atan2(dy, dx))
            if target_angle < 0:
                target_angle += 360
        else:
            return 0
            
        # Calculate turn amount
        angle_diff = (target_angle - current_angle) % 360
        if angle_diff > 180:
            angle_diff -= 360
            
        return min(self.turn_speed, max(-self.turn_speed, angle_diff))

class SnakeGame:
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    
    def __init__(self, width=800, height=600):
        # Initialize Pygame
        pygame.init()
        
        # Window setup
        self.WIDTH = width
        self.HEIGHT = height
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Snake Game")
        
        # Game constants
        self.TURN_SPEED = 15
        self.SEGMENT_SPACING = 25
        self.BONUS_TIMEOUT = 300
        self.EVASION_DURATION = 60
        
        # Snake properties
        self.snake_pos = [self.WIDTH//2, self.HEIGHT//2]
        self.snake_body = [[self.snake_pos[0], self.snake_pos[1]]]
        self.snake_length = 1
        self.snake_speed = 5
        self.snake_angle = 0
        
        # Replace AI properties with AI controller
        self.ai = SnakeAI()
        
        # Bonus properties
        self.bonus_colors = {'speed': self.BLUE, 'points': self.RED}
        self.bonus_pos, self.bonus_type = self.spawn_bonus()
        
        # Game state
        self.score = 0
        self.game_over = False
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
    
    def spawn_bonus(self):
        return [random.randrange(0, self.WIDTH-20), random.randrange(0, self.HEIGHT-20)], random.choice(['speed', 'points'])
    
    def get_angle_to_bonus(self):
        dx = self.bonus_pos[0] - self.snake_pos[0]
        dy = self.bonus_pos[1] - self.snake_pos[1] 
        angle = math.degrees(math.atan2(dy, dx))
        return angle + 360 if angle < 0 else angle
    
    def get_distance_to_bonus(self):
        dx = self.bonus_pos[0] - self.snake_pos[0]
        dy = self.bonus_pos[1] - self.snake_pos[1]
        return math.sqrt(dx*dx + dy*dy)
    
    def get_evasion_angle(self):
        return (self.get_angle_to_bonus() + 180) % 360
    
    def wrap_position(self, pos):
        x, y = pos
        if x < 0: x = self.WIDTH
        elif x > self.WIDTH: x = 0
        if y < 0: y = self.HEIGHT
        elif y > self.HEIGHT: y = 0
        return [x, y]
    
    def check_collision(self):
        return (abs(self.snake_pos[0] - self.bonus_pos[0]) < 20 and 
                abs(self.snake_pos[1] - self.bonus_pos[1]) < 20)
    
    def check_self_collision(self):
        head = self.snake_body[0]
        for segment in self.snake_body[3:]:
            if (abs(head[0] - segment[0]) < 15 and 
                abs(head[1] - segment[1]) < 15):
                return True
        return False
    
    def update_snake_body(self):
        self.snake_body[0] = list(self.snake_pos)
        
        for i in range(1, len(self.snake_body)):
            dx = self.snake_body[i-1][0] - self.snake_body[i][0]
            dy = self.snake_body[i-1][1] - self.snake_body[i][1]
            
            if abs(dx) > self.WIDTH/2:
                dx = -math.copysign(self.WIDTH - abs(dx), dx)
            if abs(dy) > self.HEIGHT/2:
                dy = -math.copysign(self.HEIGHT - abs(dy), dy)
                
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > self.SEGMENT_SPACING:
                angle = math.atan2(dy, dx)
                new_x = self.snake_body[i][0] + (distance - self.SEGMENT_SPACING) * math.cos(angle)
                new_y = self.snake_body[i][1] + (distance - self.SEGMENT_SPACING) * math.sin(angle)
                self.snake_body[i] = self.wrap_position([new_x, new_y])
    
    def draw_snake(self):
        # Draw body segments
        segment_radius = 10
        for segment in self.snake_body[1:]:
            center = (segment[0] + 10, segment[1] + 10)
            pygame.draw.circle(self.window, self.GREEN, (int(center[0]), int(center[1])), segment_radius)
        
        # Draw head
        head = self.snake_body[0]
        head_radius = 12
        head_center = (head[0] + 10, head[1] + 10)
        
        # Calculate head points
        front_point = (
            head_center[0] + head_radius * math.cos(math.radians(self.snake_angle)),
            head_center[1] + head_radius * math.sin(math.radians(self.snake_angle))
        )
        left_point = (
            head_center[0] + head_radius * math.cos(math.radians(self.snake_angle - 140)),
            head_center[1] + head_radius * math.sin(math.radians(self.snake_angle - 140))
        )
        right_point = (
            head_center[0] + head_radius * math.cos(math.radians(self.snake_angle + 140)),
            head_center[1] + head_radius * math.sin(math.radians(self.snake_angle + 140))
        )
        
        pygame.draw.polygon(self.window, self.GREEN, [front_point, left_point, right_point])
        
        # Draw eyes
        eye_distance = 6
        eye_size = 4
        left_eye_pos = (
            head_center[0] + eye_distance * math.cos(math.radians(self.snake_angle - 30)),
            head_center[1] + eye_distance * math.sin(math.radians(self.snake_angle - 30))
        )
        right_eye_pos = (
            head_center[0] + eye_distance * math.cos(math.radians(self.snake_angle + 30)),
            head_center[1] + eye_distance * math.sin(math.radians(self.snake_angle + 30))
        )
        
        for eye_pos in [left_eye_pos, right_eye_pos]:
            pygame.draw.circle(self.window, self.WHITE, (int(eye_pos[0]), int(eye_pos[1])), eye_size)
            pygame.draw.circle(self.window, self.BLACK, (int(eye_pos[0]), int(eye_pos[1])), eye_size - 2)
    
    def draw_bonus(self):
        pygame.draw.rect(self.window, self.bonus_colors[self.bonus_type], 
                        (self.bonus_pos[0], self.bonus_pos[1], 20, 20))
    
    def draw_game_over(self):
        game_over_text = self.font.render("GAME OVER!", True, self.WHITE)
        score_text = self.font.render(f"Final Score: {self.score}", True, self.WHITE)
        restart_text = self.font.render("Press SPACE to restart", True, self.WHITE)
        
        for text, offset in [(game_over_text, -50), (score_text, 0), (restart_text, 50)]:
            rect = text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 + offset))
            self.window.blit(text, rect)
    
    def reset_game(self):
        self.snake_pos = [self.WIDTH//2, self.HEIGHT//2]
        self.snake_body = [[self.snake_pos[0], self.snake_pos[1]]]
        self.snake_length = 1
        self.snake_speed = 5
        self.snake_angle = 0
        self.score = 0
        self.bonus_pos, self.bonus_type = self.spawn_bonus()
        self.ai.reset()
    
    def run(self):
        game_running = True
        while game_running:
            self.game_over = False
            self.reset_game()
            
            while not self.game_over:
                # Event handling
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                
                # Input handling
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    self.snake_angle -= self.TURN_SPEED
                if keys[pygame.K_RIGHT]:
                    self.snake_angle += self.TURN_SPEED
                if keys[pygame.K_a]:
                    self.ai.enabled = not self.ai.enabled
                
                # Replace AI movement section with:
                self.snake_angle += self.ai.calculate_turn(
                    self.snake_angle,
                    self.bonus_pos,
                    self.snake_pos
                )
                
                # Move snake
                dx = self.snake_speed * math.cos(math.radians(self.snake_angle))
                dy = self.snake_speed * math.sin(math.radians(self.snake_angle))
                self.snake_pos[0] += dx
                self.snake_pos[1] += dy
                
                # Update positions and check collisions
                self.snake_pos = self.wrap_position(self.snake_pos)
                self.update_snake_body()
                
                # Handle length changes
                while len(self.snake_body) < self.snake_length:
                    last = self.snake_body[-1]
                    second_last = self.snake_body[-2] if len(self.snake_body) > 1 else self.snake_body[0]
                    angle = math.atan2(last[1] - second_last[1], last[0] - second_last[0])
                    new_segment = [
                        last[0] + self.SEGMENT_SPACING * math.cos(angle),
                        last[1] + self.SEGMENT_SPACING * math.sin(angle)
                    ]
                    self.snake_body.append(new_segment)
                while len(self.snake_body) > self.snake_length:
                    self.snake_body.pop()
                
                # Check collisions
                if self.check_collision():
                    if self.bonus_type == 'speed':
                        self.snake_speed += 0.1
                    else:
                        self.score += 10
                        self.snake_length += 0.1
                    self.bonus_pos, self.bonus_type = self.spawn_bonus()
                
                if self.check_self_collision():
                    self.game_over = True
                    continue
                
                # Drawing
                self.window.fill(self.BLACK)
                self.draw_snake()
                self.draw_bonus()
                
                # Update HUD text
                for i, text in enumerate([
                    f"Speed: {self.snake_speed}",
                    f"Score: {self.score}",
                    f"AI: {'ON' if self.ai.enabled else 'OFF'}"
                ]):
                    surface = self.font.render(text, True, self.WHITE)
                    self.window.blit(surface, (10, 10 + i*40))
                
                pygame.display.update()
                self.clock.tick(30)
            
            # Game over screen
            while self.game_over:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        self.game_over = False
                
                self.window.fill(self.BLACK)
                self.draw_game_over()
                pygame.display.update()
                self.clock.tick(30)
        
        pygame.quit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
