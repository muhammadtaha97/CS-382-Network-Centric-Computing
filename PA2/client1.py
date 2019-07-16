import socket
import sys
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_DOWN, KEY_UP
from random import randint
from _thread import *
import threading


WIDTH = 35
HEIGHT = 20
MAX_X = WIDTH - 2
MAX_Y = HEIGHT - 2
SNAKE_LENGTH = 5
SNAKE_X = SNAKE_LENGTH + 1
SNAKE_Y = 3
TIMEOUT = 500
result = " "





s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ## Connect to an IP with Port, could be a URL
s.connect(('10.130.49.183', 8080))
print(str(s.recv(50).decode("utf-8")))






def threaded_server(server):
    global result
    while True:
        data = server.recv(50)
        if not data: break
        reply = str(data.decode("utf8"))
        result = reply
    server.close()      

  

class Snake(object):
    REV_DIR_MAP = {
        KEY_UP: KEY_DOWN, KEY_DOWN: KEY_UP,
        KEY_LEFT: KEY_RIGHT, KEY_RIGHT: KEY_LEFT,
    }

    def __init__(self, x, y, window):
        self.body_list = []
        self.hit_score = 0
        self.timeout = TIMEOUT

        for i in range(SNAKE_LENGTH, 0, -1):
            self.body_list.append(Body(x - i, y))

        self.body_list.append(Body(x, y, '0'))
        self.window = window
        self.direction = KEY_RIGHT
        self.last_head_coor = (x, y)
        self.direction_map = {
            KEY_UP: self.move_up,
            KEY_DOWN: self.move_down,
            KEY_LEFT: self.move_left,
            KEY_RIGHT: self.move_right
        }

    @property
    def score(self):
        return 'Score : {}'.format(self.hit_score)

    def add_body(self, body_list):
        self.body_list.extend(body_list)

    def eat_food(self, food):
        food.reset()
        body = Body(self.last_head_coor[0], self.last_head_coor[1])
        self.body_list.insert(-1, body)
        self.hit_score += 1
        if self.hit_score % 3 == 0:
            self.timeout -= 5
            self.window.timeout(self.timeout)

    @property
    def collided(self):
        return any([body.coor == self.head.coor
                    for body in self.body_list[:-1]])

    def update(self):
        last_body = self.body_list.pop(0)
        last_body.x = self.body_list[-1].x
        last_body.y = self.body_list[-1].y
        self.body_list.insert(-1, last_body)
        self.last_head_coor = (self.head.x, self.head.y)
        self.direction_map[self.direction]()

    def change_direction(self, direction):
        if direction != Snake.REV_DIR_MAP[self.direction]:
            self.direction = direction

    def render(self):
        for body in self.body_list:
            self.window.addstr(body.y, body.x, body.char)

    @property
    def head(self):
        return self.body_list[-1]

    @property
    def coor(self):
        return self.head.x, self.head.y

    def move_up(self):
        self.head.y -= 1
        if self.head.y < 1:
            self.head.y = MAX_Y

    def move_down(self):
        self.head.y += 1
        if self.head.y > MAX_Y:
            self.head.y = 1

    def move_left(self):
        self.head.x -= 1
        if self.head.x < 1:
            self.head.x = MAX_X

    def move_right(self):
        self.head.x += 1
        if self.head.x > MAX_X:
            self.head.x = 1

class Body(object):
    def __init__(self, x, y, char='='):
        self.x = x
        self.y = y
        self.char = char

    @property
    def coor(self):
        return self.x, self.y

class Food(object):
    def __init__(self, window, char='&'):
        self.x = randint(1, MAX_X)
        self.y = randint(1, MAX_Y)
        self.char = char
        self.window = window

    def render(self):
        self.window.addstr(self.y, self.x, self.char)

    def reset(self):
        self.x = randint(1, MAX_X)
        self.y = randint(1, MAX_Y)





if __name__ == '__main__':

    curses.initscr()
    curses.beep()
    curses.beep()
    window = curses.newwin(HEIGHT, WIDTH, 0, 0)
    window.timeout(TIMEOUT)
    window.keypad(1)
    curses.noecho()
    curses.curs_set(0)
    window.border(0)
    snake = []
    snake.append(Snake(SNAKE_X, SNAKE_Y, window))
    snake.append(Snake(SNAKE_X, SNAKE_Y+3, window))
    food = Food(window, '*')

    start_new_thread(threaded_server, (s,)) 
    # global result
    while True:
        window.clear()
        window.border(0)
        snake[0].render()
        snake[1].render()
        food.render()
        ## Send some data, this method can be called multiple times

        window.addstr(0, 5, snake[1].score)
        event = window.getch()

        if event == 27:
            break

        if event in [KEY_UP]:
            message ="1:"+ "up"
            s.sendall(message.encode())


        if event in [KEY_DOWN]:
            message = "1:" + "down"
            s.sendall(message.encode())


        if event in [KEY_LEFT]:
            message = "1:"+"left"
            s.sendall(message.encode())

        if event in [KEY_RIGHT]:
            message = "1:"+ "right"
            s.sendall(message.encode()) 
                    



        
        if result != " ":   
            reply = result
            arr = reply.split(":")
            id = int(str(arr[0]))
        
            if arr[1] == "right":
                event = 261
                snake[id].change_direction(event)
            if arr[1] == "left":
                event = 260
                snake[id].change_direction(event)   
                
            if  arr[1] == "up":
                event = 259
                snake[id].change_direction(event)
            if arr[1] == "down":
                event = 258
                snake[id].change_direction(event)                   

        


        if snake[0].head.x == food.x and snake[0].head.y == food.y:
            snake[0].eat_food(food)
        if snake[1].head.x == food.x and snake[1].head.y == food.y:
            snake[1].eat_food(food)
    

        if event == 32:
            key = -1
            while key != 32:
                key = window.getch()

        snake[0].update()
        snake[1].update()


        checker =   False
        for body in snake[0].body_list[:-1]:
            if snake[1].head.coor == body.coor:
                checker = True

        if checker == True:
            break      


        
        if snake[1].head.x == snake[0].head.x and snake[1].head.y == snake[0].head.y:
            break
        
        if snake[1].head.coor == body.coor:
            break    

        if snake[1].head.x == MAX_X or snake[1].head.y == MAX_Y or snake[1].head.x == 0 or snake[1].head.y == 0:
            break
        if snake[1].collided:
            break

    curses.endwin()

s.close()
## Close the socket connection, no more data transmission


