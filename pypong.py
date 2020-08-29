import pygame
from os import path, environ


running = True
width = None
height = None
fore_color = (200, 200, 0)
back_color = (0, 0, 0)
last_collision_time = 0 # to lock out collision detection for 100ms after a collision
collision_lockout = 100
assets = {}
score_dict = {0: "0", 1: "15", 2: "30", 3: "40"}
player1_score = 0
player2_score = 0


class Ball:
    def __init__(self, speed, init_position, size):
        self.speed = int(speed)                                             # total speed
        self.x_spd = self.speed                                             # x-component of total speed, initially equal to total speed
        self.y_spd = 0                                                      # y-component of total speed, initially 0
        self.init_position = int(init_position[0]) , int(init_position[1])  # initial position, expressed as (int, int)
        self.position = self.init_position                                  # tuple representing current position
        self.size = int(size)                                               # ball is a square, and size is the length in px of each side
        self.set_rect()                                                     # rectangle representing the space occupied by the ball onscreen
        
    # updates the position and corresponding rect for the ball
    def step_position(self):
        self.position = self.position[0] + self.x_spd, self.position[1] + self.y_spd
        self.set_rect()
    
    # mirrors y_spd (for bounces off top & bottom walls, where x_spd doesn't change)
    def wall_bounce(self):
        self.y_spd = 0 - self.y_spd
    
    # changes x_spd & y_spd based on angle leaving the paddle
    def paddle_bounce(self, deflect_value): # deflect_value should be a float > 0 and < 1
        if self.x_spd > 0:
            self.x_spd = 0 - (self.speed * (1 - deflect_value))
        else:
            self.x_spd = self.speed * (1 - deflect_value)
        
        if self.y_spd > 0:
            self.y_spd = self.speed * deflect_value
        else:
            self.y_spd = 0 - (self.speed * deflect_value)
    
    # resets position and speed of ball to initial values
    def reset_ball(self):
        self.x_spd = self.speed
        self.y_spd = 0
        self.position = self.init_position
        self.rect = self.set_rect()
    
    # creates a Rect based on the size and position of the Ball
    def set_rect(self):
        self.rect = pygame.Rect(int(self.position[0] - (0.5 * self.size)), int(self.position[1] - (0.5 * self.size)), self.size, self.size)
        

class Paddle:
    def __init__(self, init_position, paddle_height):
        self.init_position = int(init_position[0]), int(init_position[1])   # tuple that represents starting position of paddle
        self.position = self.init_position                                  # tuple that represents current position of paddle
        self.paddle_height = int(paddle_height)                             # height of paddle
        self.paddle_width = int(self.paddle_height * 0.15)                  # width is 15% of height
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


def main():
    load_assets()
    window = init_display("PyPong")
    play(window)
    

def play(window):
    global last_collision_time
    
    ball_speed = width * 0.012
    
    # create and draw ball and paddles
    ball = Ball(ball_speed, (width / 2, height * 0.5), height / 30)
    paddle1 = Paddle((width * 0.05, height * 0.5), height / 5)
    paddle2 = Paddle((width * 0.95, height * 0.5), height / 5)
    object_list = [ball, paddle1, paddle2]
        
    while running:
        pygame.time.wait(10)
        
        # erase everything
        draw_objects(window, object_list, back_color)
        
        # update ball position and check for collisions
        ball.step_position()
        check_collide(ball, paddle1)
        check_collide(ball, paddle2)
        if ball.position[1] - (ball.size / 2) <= 0 or ball.position[1] + (ball.size / 2) >= height: # check for collision w/ wall
            ball.wall_bounce()
        
        # check if any player has scored
        score_occurred = check_for_score(ball)
        if score_occurred:
            print(f"Player 1: {player1_score}\t Player 2: {player2_score}")
            score_animation(window, ball, paddle1, paddle2)
            
        handle_keypress(paddle1, paddle2)
        
        # check for quit events
        listen_for_quit()
                             
        # draw everything and update display
        draw_objects(window, object_list, fore_color)
        pygame.display.update()
        pygame.event.clear()
            

def check_collide(ball, paddle):
    global last_collision_time
    
    # if ball collides w/ paddle & not within 100ms of a collision
    if paddle.rect.colliderect(ball.rect) and pygame.time.get_ticks() - last_collision_time > collision_lockout: 
        # get position of ball and paddle in the y-axis, plus the height of the paddle
        ball_position_y = ball.position[1]
        paddle_position_y = paddle.position[1]
        paddle_height = paddle.paddle_height
        
        # calculate the difference between the y-axis position of ball and paddle, and use that to determine how much the ball will deflect
        offset = ball_position_y - paddle_position_y
        deflect_value = abs(offset / ((paddle_height / 2) * 1.5))
        ball.paddle_bounce(deflect_value)   # call the paddle_bounce() function to change the ball's direction based on the deflect_value
        
        last_collision_time = pygame.time.get_ticks() # last_collision_time is now
        

def check_for_score(ball):
    global player1_score
    global player2_score
    
    score_occurred = False
    
    # left side -- player 2 scored
    if ball.position[0] <= 0:
        player2_score += 1
        score_occurred = True
        
    # right side -- player 1 scored
    elif ball.position[0] >= width:
        player1_score += 1
        score_occurred = True
    
    return score_occurred


def score_animation(window, ball, paddle1, paddle2):
    object_list = [ball, paddle1, paddle2]
    
    # show negative image
    window.fill(fore_color)
    draw_objects(window, object_list, back_color)
    show_score(window, negative=True)
    pygame.display.update()
    pygame.time.wait(1000)

    # return objects to starting locations
    ball.reset_ball()
    paddle1.reset_paddle()
    paddle2.reset_paddle()
    
    # redraw objects in positive
    window.fill(back_color)
    draw_objects(window, object_list, fore_color)
    pygame.display.update()
    
    
# draws the current score on the screen
def show_score(window, negative=False):
    global running
    
    suffix = "_y"
    if negative:
        suffix = "_b"
        
    score_root = int(width * 0.45), int(height * 0.95)
    
    #TODO: comment on this mess
    if player1_score >= 3 and player2_score >= 3:
        img_dimensions = (int(width * 0.15), int(height * 0.05))
        
        if player1_score == player2_score:
            img = pygame.transform.scale(assets["deuce" + suffix], img_dimensions)
        elif player1_score - player2_score >= 2 or player2_score - player1_score >= 2:
            running = False
            return
        elif player1_score > player2_score:
            img = pygame.transform.scale(assets["adin" + suffix], img_dimensions)
        elif player2_score > player1_score:
            img = pygame.transform.scale(assets["adout" + suffix], img_dimensions)
        
        window.blit(img, pygame.Rect(score_root, img_dimensions))
    elif player1_score >= 4 or player2_score >= 4:
        running = False
    else:
        img_dimensions = (int(width * 0.05), int(height * 0.05))

        player1_img = pygame.transform.scale(assets[score_dict[player1_score] + suffix], img_dimensions)
        dash_img = pygame.transform.scale(assets["dash" + suffix], img_dimensions)
        player2_img = pygame.transform.scale(assets[score_dict[player2_score] + suffix], img_dimensions)
        
        window.blit(player1_img, pygame.Rect(score_root, img_dimensions))
        window.blit(dash_img, pygame.Rect(score_root[0] + int(width * 0.05), score_root[1], img_dimensions[0], img_dimensions[1]))
        window.blit(player2_img, pygame.Rect(score_root[0] + int(width * 0.1), score_root[1], img_dimensions[0], img_dimensions[1]))
        
        
def draw_objects(window, object_list, color):
    show_score(window)
    for obj in object_list:
        window.fill(color, rect=obj.rect)
    
    
def handle_keypress(paddle1, paddle2):
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
        

# returns a window for the game
def init_display(title):
    global width
    global height
    
    environ["SDL_VIDEO_CENTERED"] = "1"  # centers window in screen
    pygame.init()
    display_info = pygame.display.Info()    # object with display info
    pygame.display.set_caption(title)       # set title
    
    # load and set icon
    pygame.display.set_icon(assets["icon"])
    
    # set window size w/ info from display_info
    width = int(display_info.current_w * 0.8)
    height = int(display_info.current_h * 0.8)
    
    return pygame.display.set_mode((width, height))


# returns True if QUIT event is registered 
def listen_for_quit():
    global running
    
    quit_events = pygame.event.get(pygame.QUIT)
    if len(quit_events) > 0:
        running = False
        

def load_assets():
    global assets
    
    assets["icon"] = pygame.image.load(path.join("assets", "pypong_icon.png"))
    assets["0_b"] = pygame.image.load(path.join("assets", "0_b.png"))
    assets["0_y"] = pygame.image.load(path.join("assets", "0_y.png"))
    assets["15_b"] = pygame.image.load(path.join("assets", "15_b.png"))
    assets["15_y"] = pygame.image.load(path.join("assets", "15_y.png"))
    assets["30_b"] = pygame.image.load(path.join("assets", "30_b.png"))
    assets["30_y"] = pygame.image.load(path.join("assets", "30_y.png"))
    assets["40_b"] = pygame.image.load(path.join("assets", "40_b.png"))
    assets["40_y"] = pygame.image.load(path.join("assets", "40_y.png"))
    assets["deuce_b"] = pygame.image.load(path.join("assets", "deuce_b.png"))
    assets["deuce_y"] = pygame.image.load(path.join("assets", "deuce_y.png"))
    assets["adin_b"] = pygame.image.load(path.join("assets", "adin_b.png"))
    assets["adin_y"] = pygame.image.load(path.join("assets", "adin_y.png"))
    assets["adout_b"] = pygame.image.load(path.join("assets", "adout_b.png"))
    assets["adout_y"] = pygame.image.load(path.join("assets", "adout_y.png"))
    assets["dash_b"] = pygame.image.load(path.join("assets", "dash_b.png"))
    assets["dash_y"] = pygame.image.load(path.join("assets", "dash_y.png"))


if __name__ == "__main__":
    main()
