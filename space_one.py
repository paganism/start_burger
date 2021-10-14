import time
import curses
import asyncio
import random
from fire_animation import fire
from curses_tools import draw_frame, read_controls
import os
from itertools import cycle


class EventLoopCommand():

    def __await__(self):
        return (yield self)


class Sleep(EventLoopCommand):

    def __init__(self, seconds):
        self.seconds = seconds

TIC_TIMEOUT = 0.1
STARS = '+*.:'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


async def blink(canvas, row, column, symbol='*'):
    
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for i in range(random.randint(1, 19)):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(2):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for i in range(4):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for i in range(2):
            await asyncio.sleep(0)


def read_file(path):
    with open(path, 'r') as file:
        return file.read()


async def animate_spaceship(canvas, row, column, frames):

    while True:
        for frame in frames:

            row_dir, col_dir, _ = read_controls(canvas)

            row += row_dir
            column += col_dir

            draw_frame(canvas, round(row), round(column), frame)
            await asyncio.sleep(0)
            draw_frame(canvas, round(row), round(column), frame, negative=True)


def draw(canvas):
    canvas.nodelay(True)
    rocket_frame_1 = read_file(os.path.join(BASE_DIR, 'frames/rocket_frame_1.txt'))
    rocket_frame_2 = read_file(os.path.join(BASE_DIR, 'frames/rocket_frame_2.txt'))
    rocket_frames = [rocket_frame_1, rocket_frame_2]
    max_row, max_column = canvas.getmaxyx()
    coroutines = [blink(canvas, random.randint(1, max_row-2), random.randint(1, max_column-2), random.choice(STARS)) for i in range(random.randint(1, max_column))]

    gun_fire = fire(canvas, max_row//2, max_column//2 )
    coroutines.append(gun_fire)

    spaceship = animate_spaceship(canvas, max_row//2, max_column//2-2, rocket_frames)
    coroutines.append(spaceship)

    while True:
        
        for coroutine in coroutines.copy():
            
            try:
                coroutine.send(None)
                canvas.border()
                
                canvas.refresh()
                curses.curs_set(False)                
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            continue
        time.sleep(TIC_TIMEOUT)
    
if __name__ == '__main__':
    
    curses.update_lines_cols()
    curses.wrapper(draw)

