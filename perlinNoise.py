import pygame
import sys
import random
import math

pygame.init()
canvas = pygame.display.set_mode((1600, 1000))

# settings
TOTAL_CELLS = 150
SAMPLING_RATE = 15
GRID_CELLS = TOTAL_CELLS // SAMPLING_RATE
SEED = None 
if SEED:
    random.seed(SEED)

CELL_OFFSET = 0.70710678118 / SAMPLING_RATE

# window settings
CELL_SIZE = 5
GRID_CELL_SIZE = SAMPLING_RATE * CELL_SIZE
MARGIN = 100

ARROW_THICK = 2
ARROW_LENGTH = 40

SCALEX_MARGIN = 1000

# colors
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
darkBlue = (0, 0, 128)
white = (255, 255, 255)
black = (0, 0, 0)
pink = (255, 200, 200)
lightGrey = (200, 200, 200)


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def getColorVal(a):  # a = float from -1 to 1
    i = a * 255
    return (
        (255 - i / 2, 255 - i, 255 - i / 2)
        if a > 0
        else (255 + i, 255 + i / 2, 255 + i)
    )


def drawArrow(a, b):
    pygame.draw.line(canvas, red, a, b, width=ARROW_THICK)
    pygame.draw.circle(canvas, red, b, ARROW_THICK)

def getOffsetVector(x, y, gridx, gridy):
    # get offset vector by cell units
    cellx = x - (gridx * SAMPLING_RATE)
    celly = y - (gridy * SAMPLING_RATE)
    # scale offset vector
    return (cellx * CELL_OFFSET, celly * CELL_OFFSET)

# using linear interpolation i think
def interpolate(a, b, w):
    if 0.0 > w:
        return a

    if 1.0 < w:
        return b 

    return (b - a) * w + a

# generate grid of gradient vectors; 2d array of vector objs
n = GRID_CELLS + 1
gradient_vectors = [[None] * n for i in range(n)]
for i in range(n):
    for j in range(n):
        dir = random.random() * 2 * math.pi  # rad clockwise from north
        gradient_vectors[i][j] = Vector(math.cos(dir), math.sin(dir))

dot_products = [[[0 for _ in range(4)] for _ in range(TOTAL_CELLS)] for _ in range(TOTAL_CELLS)]
cell_values = [[0 for _ in range(TOTAL_CELLS)] for _ in range(TOTAL_CELLS)]
for x in range(TOTAL_CELLS):
    for y in range(TOTAL_CELLS):
        # for each corner; x // sampling rate is one corner, x // sampling rate + 1 is other
        gridx = [math.floor(float(x) / SAMPLING_RATE), math.ceil(float(x) / SAMPLING_RATE)]
        gridy = [math.floor(float(y) / SAMPLING_RATE), math.ceil(float(y) / SAMPLING_RATE)]

        for i in range(2):
            for j in range(2):
                OV = getOffsetVector(x, y, gridx[i], gridy[j])
                dot_products[x][y][i+j*2] = (
                    OV[0] * gradient_vectors[gridx[i]][gridy[j]].x
                    + OV[1] * gradient_vectors[gridx[i]][gridy[j]].y
                )
        
        # x y position inside sampling square
        sx = float(x - (gridx[0] * SAMPLING_RATE)) / SAMPLING_RATE 
        sy = float(y - (gridy[0] * SAMPLING_RATE)) / SAMPLING_RATE
        x1 = interpolate(dot_products[x][y][0], dot_products[x][y][1], sx)
        x2 = interpolate(dot_products[x][y][2], dot_products[x][y][3], sx)
        cell_values[x][y] = interpolate(x1, x2, sy)

        # nearest corner for now; x / sampling rate rounded
        """
        gridx = round(float(x+0.1) / SAMPLING_RATE)
        gridy = round(float(y+0.1) / SAMPLING_RATE)
        """
        # calculate offset vector
        """
        OV = getOffsetVector(x, y, gridx, gridy)
        """
        # calculate dot product and set value
        """
        cell_values[x][y] = (
            OV[0] * gradient_vectors[gridx][gridy].x
            + OV[1] * gradient_vectors[gridx][gridy].y
        )
        """


exit = False
while not exit:
    canvas.fill(white)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit = True

    # draw cell values
    for x in range(TOTAL_CELLS):
        for y in range(TOTAL_CELLS):
            pygame.draw.rect(
                canvas,
                getColorVal(cell_values[x][y]),
                pygame.Rect(
                    MARGIN + x * CELL_SIZE, MARGIN + y * CELL_SIZE, CELL_SIZE, CELL_SIZE
                ),
            )

    # draw vertical lines
    for i in range(TOTAL_CELLS + 1):
        pygame.draw.line(
            canvas,
            lightGrey,
            (MARGIN + i * CELL_SIZE, MARGIN),
            (MARGIN + i * CELL_SIZE, MARGIN + TOTAL_CELLS * CELL_SIZE),
        )
    # draw horizontal lines
    for i in range(TOTAL_CELLS + 1):
        pygame.draw.line(
            canvas,
            lightGrey,
            (MARGIN, MARGIN + i * CELL_SIZE),
            (MARGIN + TOTAL_CELLS * CELL_SIZE, MARGIN + i * CELL_SIZE),
        )

    # draw vertical lines
    for i in range(GRID_CELLS + 1):
        pygame.draw.line(
            canvas,
            blue,
            (MARGIN + i * GRID_CELL_SIZE, MARGIN),
            (MARGIN + i * GRID_CELL_SIZE, MARGIN + GRID_CELLS * GRID_CELL_SIZE),
        )
    # draw horizontal lines
    for i in range(GRID_CELLS + 1):
        pygame.draw.line(
            canvas,
            blue,
            (MARGIN, MARGIN + i * GRID_CELL_SIZE),
            (MARGIN + GRID_CELLS * GRID_CELL_SIZE, MARGIN + i * GRID_CELL_SIZE),
        )

    # draw gradient vectors
    for i in range(GRID_CELLS + 1):
        for j in range(GRID_CELLS + 1):
            x = MARGIN + i * GRID_CELL_SIZE
            y = MARGIN + j * GRID_CELL_SIZE

            drawArrow(
                (x, y),
                (
                    x + gradient_vectors[i][j].x * ARROW_LENGTH,
                    y + gradient_vectors[i][j].y * ARROW_LENGTH,
                ),
            )

    # draw scale
    for i in range(256):
        j = (i / 127.5) - 1.0
        pygame.draw.rect(
            canvas,
            getColorVal(j),
            pygame.Rect(
                SCALEX_MARGIN, MARGIN + i * ARROW_THICK, ARROW_THICK * 20, ARROW_THICK
            ),  # i * ARROW_THICK,
        )

    pygame.display.update()
