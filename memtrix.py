import pygame
import random
import time

WIDTH = 500
HEIGHT = 500
FONTSIZE = 20
SHOWTIME = 500
SHRINKAGE = 7
TIMER = 30
FPS = 30

WHITE = (255, 255, 255)
RED = (223, 32, 41)
YELLOW = (245, 242, 10)
BLUE = (0, 38, 97)
GREY = (96, 125, 139)
CYAN = (0, 188, 212)
LIME = (205, 220, 57)



pygame.init()
clock = pygame.time.Clock()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Memtrix')
icon = pygame.image.load('icon1.png')
pygame.display.set_icon(icon)

normal_font = pygame.font.Font('freesansbold.ttf', FONTSIZE)
big_font = pygame.font.Font('freesansbold.ttf', FONTSIZE+10)

LEVEL = 3
TILESIZE = 100

new_pattern = []
input_pattern = []
score = 0
hi_score = 0
timestamp = {'past':0, 'now':0, 'timer':0}

timer_paused = True
timer_up =	False



def getLeftTop(row, col):
	left = (TILESIZE * col) + (WIDTH - TILESIZE * LEVEL) // 2
	top = (TILESIZE * row) + (HEIGHT - TILESIZE * LEVEL) // 2
	return left, top

def getClickedTile(x, y):
	for row in range(LEVEL):
		for col in range(LEVEL):
			left, top = getLeftTop(row, col)
			area = pygame.Rect(left, top, TILESIZE, TILESIZE)
			if area.collidepoint(x, y):
				return row, col 
	return None, None

def drawText(msg, x, y, large):
	if large:
		font = big_font
	else:
		font = normal_font
	text = font.render(msg, True, WHITE)
	rect = text.get_rect()
	rect.topleft = (x, y)
	win.blit(text, rect)

def displayScore():
	drawText(f'Score: {score}', 10, 10, False)
	drawText(f'Best: {hi_score}', WIDTH-100, 10, False)

def drawBoard():
	win.fill(BLUE)
	displayScore()
	# Drawing Table
	for row in range(LEVEL):
		for col in range(LEVEL):
			left, top = getLeftTop(row, col)
			pygame.draw.rect(win, GREY, (left, top, TILESIZE-3, TILESIZE-3))
	# Drawing border
	left, top = getLeftTop(0, 0)
	pygame.draw.rect(win, RED, (left-5, top-5, TILESIZE*LEVEL+6, TILESIZE*LEVEL+6), 4)

	# Drawing timer
	pygame.draw.rect(win, LIME, (0, HEIGHT-8, int(WIDTH*(1-(timestamp['timer']/TIMER))), 8))


def generatePattern():
	pattern = []
	while len(pattern) < LEVEL:
		rand_row = random.randrange(LEVEL)
		rand_col = random.randrange(LEVEL)
		if (rand_row, rand_col) not in pattern:
			pattern.append((rand_row, rand_col))
	return pattern 

def lightUp(row, col, color):
	left, top = getLeftTop(row, col)
	surface = pygame.Surface((TILESIZE-3, TILESIZE-3))
	surface.fill(color)
	win.blit(surface, (left, top))

def startTimer():
	global timestamp
	if not timer_paused and timestamp['past']:
		timestamp['now'] = time.time()
		timestamp['timer'] += (timestamp['now'] - timestamp['past'])
		timestamp['past'] = timestamp['now']

running = True
waiting_input = False

while running:
	startTimer()
	drawBoard()
	

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		# Restart if game is over
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_SPACE:
				if timer_up:
					timer_up = False
					waiting_input = False
					score = 0
					LEVEL = 3
					TILESIZE = 100
					timestamp = {'past':0, 'now':0, 'timer':0}
					new_pattern = []
					input_pattern = []
					drawBoard()
		# Get user-clicked tile & add to pattern
		if event.type == pygame.MOUSEBUTTONUP:
			mousex, mousey = event.pos
			row, col = getClickedTile(mousex, mousey)
			if waiting_input and row is not None:
				if (row, col) not in input_pattern:
					input_pattern.append((row, col))

	if timestamp['timer'] > TIMER:	timer_up = True

	if waiting_input and not timer_up:
		# Display tiles whether right or wrong
		for (row, col) in input_pattern:
			if (row, col) in new_pattern:
				lightUp(row, col, YELLOW)
			else:
				lightUp(row, col, RED)
		pygame.display.update()

		if len(input_pattern) == len(new_pattern):
			waiting_input = False
			timer_paused = True
			# Display the correct pattern (& wrong ones)
			for (row, col) in new_pattern:
				lightUp(row, col, YELLOW)
			pygame.display.update()
			pygame.time.wait(SHOWTIME)
			# Check if patterns are match
			if sorted(input_pattern) == sorted(new_pattern):
				score += (LEVEL - 2)
				if score > hi_score:
					hi_score = score 

				if LEVEL < 6:
					LEVEL += 1
					TILESIZE = int(TILESIZE - TILESIZE / SHRINKAGE) 
			else:
				if LEVEL > 3:
					LEVEL -= 1
					TILESIZE = int(TILESIZE + TILESIZE / SHRINKAGE)

	elif not waiting_input and not timer_up:
		waiting_input = True
		timer_paused = True
		new_pattern = []
		input_pattern = []

		pygame.display.update()
		pygame.time.wait(SHOWTIME)
		# Display the new pattern 
		new_pattern = generatePattern()
		for (row, col) in new_pattern:
			lightUp(row, col, YELLOW)
		pygame.display.update()
		pygame.time.wait(SHOWTIME)
		
		timer_paused = False
		timestamp['past'] = time.time()

		# 	if LEVEL > 3:
		# 		LEVEL -= 1
		
		# timer_paused = False
		# timestamp['past'] = time.time()

	pygame.display.update()
	clock.tick(FPS)

pygame.quit()


