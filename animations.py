import time
import pygame

class HeartbeatAnimation:
    def __init__(self, x, y, color=(0, 255, 0), duration=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.start_time = time.time()
        self.duration = duration
        self.max_radius = 100  # Maximum radius of the wave
        
    def draw(self, screen):
        current_time = time.time()
        age = current_time - self.start_time
        
        if age > self.duration:
            return False  # Animation is complete
        
        # Calculate current radius and alpha
        progress = age / self.duration
        current_radius = self.max_radius * progress
        alpha = int(255 * (1 - progress))  # Fade out as circle expands
        
        # Create a surface for the circle with transparency
        surface = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
        
        # Draw the circle with transparency
        pygame.draw.circle(surface, (*self.color, alpha), 
                         (current_radius, current_radius), 
                         current_radius, 2)  # Width of 2 pixels
        
        # Blit the surface onto the screen
        screen.blit(surface, 
                   (self.x - current_radius, 
                    self.y - current_radius))
        
        return True  # Animation still running
