import pygame
import os


def main():
    window = init_display("PyPong")
    
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            break
    

# returns a window for the game
def init_display(title):
    os.environ["SDL_VIDEO_CENTERED"] = "1"  # centers window in screen
    pygame.init()
    display_info = pygame.display.Info()    # object with display info
    pygame.display.set_caption(title)
    
    # load and set icon
    icon = pygame.image.load("pypong_icon.png")
    pygame.display.set_icon(icon)
    
    return pygame.display.set_mode((display_info.current_w, display_info.current_h))


class Ball:
    def __init__(self, speed, init_position, size):
        self.speed = speed                       # total speed
        self.x_spd = speed                       # x-component of total speed, initially equal to total speed
        self.y_spd = 0                           # y-component of total speed, initially 0
        self.init_position = init_position       # initial position, expressed as (int, int)
        self.position = init_position            # location of the ball on the screen, expressed as (int, int)
        self.size = size                         # ball is a square, and size is the length in px of each side
        set_rect()                               # rectangle representing the space occupied by the ball onscreen
        
    # updates the position and corresponding rect for the ball
    def step_position(self):
        current_x = self.position[0]
        current_y = self.position[1]
        self.position = current_x + self.x_spd, current_y + self.y_spd
        set_rect()
    
    # mirrors y_spd (for bounces off top & bottom walls, where x_spd doesn't change)
    def wall_bounce(self):
        self.y_spd = 0 - self.y_spd
    
    # changes x_spd & y_spd based on angle leaving the paddle
    def paddle_bounce(self, deflect_value):
        if x_spd > 0:
            self.x_spd = 0 - (self.speed * (1 - deflect_value))
        else:
            self.x_spd = self.speed * (1 - deflect_value)
        
        if y_spd > 0:
            self.y_spd = 0 - (self.speed * deflect_value)
        else:
            self.y_spd = self.speed * deflect_value
    
    # resets position and speed of ball to initial values
    def reset_ball(self):
        self.x_spd = self.speed
        self.y_spd = 0
        self.position = self.init_position
        self.rect = set_rect(self.init_position)
    
    # creates a Rect based on the size and position of the Ball
    def set_rect(self):
        self.rect = pygame.Rect(self.position[0] - (0.5 * self.size),
                                self.position[1] - (0.5 * self.size), 
                                self.position[0] + (0.5 * self.size), 
                                self.position[1] + (0.5 * self.size))


class Paddle:
    def __init__(self, init_position, height):
        self.position = init_position       # tuple to represent location of paddle
        self.init_position = init_position  # tuple that represents starting position of paddle
        self.height = height                # height of paddle
        self.width = height / 10            # width is 10% of height
        set_rect(self.position)
    
    # makes a Rect based on dimensions and position of Paddle
    def set_rect(self):
        self.rect = pygame.Rect(self.position[0] - (0.5 * self.width),
                                self.position[1] - (0.5 * self.height),
                                self.position[0] + (0.5 * self.width),
                                self.position[1] + (0.5 * self.height))


if __name__ == "__main__":
    main()
