import pygame
from os import path, environ
#import os


running = True
width = None
height = None
fore_color = (200, 200, 0)
back_color = (0, 0, 0)
last_collision_time = 0 # to lock out collision detection for 100ms after a collision
collision_lockout = 100


def main():
    window = init_display("PyPong")
    play(window)
    

def play(window):
    global running
    global last_collision_time
    
    # create and draw ball and paddles
    ball = Ball(int(width / 100), (int(width / 2), int(height / 2)), int(height / 30))
    paddle1 = Paddle((int(width * 0.05), int(height / 2)), int(height / 5))
    paddle2 = Paddle((int(width * 0.95), int(height / 2)), int(height / 5))
        
    while running:
        pygame.time.wait(10)
        
        # erase everything
        window.fill(back_color, rect=ball.rect)
        window.fill(back_color, rect=paddle1.rect)
        window.fill(back_color, rect=paddle2.rect)
        
        # update ball position and check for collisions
        ball.step_position()
        check_collide(ball, paddle1)
        check_collide(ball, paddle2)
        if ball.position[1] - (ball.size / 2) <= 0 or ball.position[1] + (ball.size / 2) >= height:
            ball.wall_bounce()
        
        # check for quit events
        quit_events = pygame.event.get(pygame.QUIT)
        if len(quit_events) > 0:
            running = False
        
        # handle key presses
        keys = pygame.key.get_pressed()
        
        # paddle1 keys
        if keys[pygame.K_w] and paddle1.position[1] - (paddle1.paddle_height / 2) >= 0:         # move up
            paddle1.move(0 - (width / 150))
        if keys[pygame.K_s] and paddle1.position[1] + (paddle1.paddle_height / 2) <= height:    # move down
            paddle1.move(width / 150)

        # paddle2 keys
        if keys[pygame.K_UP] and paddle2.position[1] - (paddle2.paddle_height / 2) >= 0:        # move up
            paddle2.move(0 - (width / 150))
        if keys[pygame.K_DOWN] and paddle2.position[1] + (paddle2.paddle_height / 2) <= height: # move down
            paddle2.move(width / 150)
                             
        # draw everything and update display
        window.fill(fore_color, rect=ball.rect)
        window.fill(fore_color, rect=paddle1.rect)
        window.fill(fore_color, rect=paddle2.rect)
        pygame.display.update()
            

def check_collide(ball, paddle):
    global last_collision_time
    
    if paddle.rect.colliderect(ball.rect) and pygame.time.get_ticks() - last_collision_time > collision_lockout:
        # get position of ball and paddle in the y-axis, plus the height of the paddle
        ball_position_y = ball.position[1]
        paddle_position_y = paddle.position[1]
        paddle_height = paddle.paddle_height
        
        # calculate the difference between the y-axis position of ball and paddle, and use that to determine how much the ball will deflect
        offset = ball_position_y - paddle_position_y
        deflect_value = offset / ((paddle_height / 2) * 1.5)
        ball.paddle_bounce(deflect_value)   # call the paddle_bounce() function to change the ball's direction based on the deflect_value
        
        last_collision_time = pygame.time.get_ticks() # last_collision_time is now
        

# returns a window for the game
def init_display(title):
    global width
    global height
    
    environ["SDL_VIDEO_CENTERED"] = "1"  # centers window in screen
    pygame.init()
    display_info = pygame.display.Info()    # object with display info
    pygame.display.set_caption(title)       # set title
    
    # load and set icon
    icon = pygame.image.load(path.join("assets", "pypong_icon.png"))
    pygame.display.set_icon(icon)
    
    # set window size w/ info from display_info
    width = int(display_info.current_w * 0.8)
    height = int(display_info.current_h * 0.8)
    
    return pygame.display.set_mode((width, height))


class Ball:
    def __init__(self, speed, init_position, size):
        self.speed = speed                  # total speed
        self.x_spd = speed                  # x-component of total speed, initially equal to total speed
        self.y_spd = 0                      # y-component of total speed, initially 0
        self.init_position = init_position  # initial position, expressed as (int, int)
        self.position = init_position       # tuple representing current position
        self.size = int(size)               # ball is a square, and size is the length in px of each side
        self.set_rect()                     # rectangle representing the space occupied by the ball onscreen
        
    # updates the position and corresponding rect for the ball
    def step_position(self):
        self.position = self.position[0] + self.x_spd, self.position[1] + self.y_spd
        self.set_rect()
    
    # mirrors y_spd (for bounces off top & bottom walls, where x_spd doesn't change)
    def wall_bounce(self):
        self.y_spd = 0 - self.y_spd
    
    # changes x_spd & y_spd based on angle leaving the paddle
    def paddle_bounce(self, deflect_value):
        if self.x_spd > 0:
            self.x_spd = 0 - (self.speed * (1 - abs(deflect_value)))
        else:
            self.x_spd = self.speed * (1 - abs(deflect_value))
        
        if self.y_spd > 0:
            self.y_spd = 0 - (self.speed * deflect_value)
        else:
            self.y_spd = self.speed * deflect_value
    
    # resets position and speed of ball to initial values
    def reset_ball(self):
        self.x_spd = self.speed
        self.y_spd = 0
        self.rect = self.set_rect()
    
    # creates a Rect based on the size and position of the Ball
    def set_rect(self):
        self.rect = pygame.Rect(int(self.position[0] - (0.5 * self.size)), int(self.position[1] - (0.5 * self.size)), self.size, self.size)
        

class Paddle:
    def __init__(self, init_position, paddle_height):
        self.init_position = init_position                  # tuple that represents starting position of paddle
        self.position = init_position                       # tuple that represents current position of paddle
        self.paddle_height = int(paddle_height)             # height of paddle
        self.paddle_width = int(self.paddle_height * 0.15)  # width is 15% of height
        self.set_rect()
        
    def move(self, distance):
        self.position = self.position[0], self.position[1] + distance
        self.set_rect()
    
    def reset_paddle(self):
        self.position = self.init_position
        self.set_rect()
    
    # makes a Rect based on dimensions and position of Paddle
    def set_rect(self):
        self.rect = pygame.Rect(int(self.position[0] - (0.5 * self.paddle_width)), 
                                int(self.position[1] - (0.5 * self.paddle_height)), 
                                self.paddle_width, self.paddle_height)


if __name__ == "__main__":
    main()
