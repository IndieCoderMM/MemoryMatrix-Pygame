import pygame
import random
import time

WIDTH = 500
HEIGHT = 500
FONTSIZE = 20
SHOWTIME = 500
SHRINKAGE = 7
TIMER = 10
FPS = 30

WHITE = (255, 255, 255)
RED = (223, 32, 41)
YELLOW = (245, 242, 10)
BLUE = (0, 38, 97)
GREY = (96, 125, 139)
LIME = (205, 220, 57)

pygame.init()
clock = pygame.time.Clock()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Memtrix')
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)

normal_font = pygame.font.Font('freesansbold.ttf', FONTSIZE)
big_font = pygame.font.Font('freesansbold.ttf', FONTSIZE+30)

timestamp = {'past':0, 'now':0, 'timer':0}
timer_paused = True
timer_up =	False

level = 3
tile_size = 100
new_pattern = []
input_pattern = []
score = 0
hi_score = 0

def getLeftTop(row, col):
	board_size = tile_size * level
	left = (tile_size * col) + (WIDTH - board_size) // 2
	top = (tile_size * row) + (HEIGHT - board_size) // 2
	return left, top

def getClickedTile(x, y):
	for row in range(level):
		for col in range(level):
			left, top = getLeftTop(row, col)
			area = pygame.Rect(left, top, tile_size, tile_size)
			if area.collidepoint(x, y):
				return row, col 
	return None, None

def drawText(msg, x, y, large=False):
	font = big_font if large else normal_font
	text = font.render(msg, True, WHITE)
	rect = text.get_rect()
	if x == 'center':
		x = int(WIDTH/2 - text.get_width()/2)
	rect.topleft = (x, y)
	win.blit(text, rect)

def drawBoard():
	win.fill(BLUE)
	drawText(f'Score: {score}', 20, 10)
	drawText(f'Best: {hi_score}', WIDTH-100, 10)
	# Drawing Table
	for row in range(level):
		for col in range(level):
			left, top = getLeftTop(row, col)
			pygame.draw.rect(win, GREY, (left, top, tile_size - 3, tile_size - 3))
	# Drawing border
	board_size = tile_size * level
	left, top = getLeftTop(0, 0)
	pygame.draw.rect(win, RED, (left-5, top-5, board_size+6, board_size+6), 4)
	# Drawing timer
	time_ratio = timestamp['timer'] / TIMER		# e.g. if 30 / 60, length will be half of screen
	pygame.draw.rect(win, LIME, (0, HEIGHT-8, int(WIDTH*(1-time_ratio)), 8))

def generatePattern():
	pattern = []
	while len(pattern) < level:
		rand_row = random.randrange(level)
		rand_col = random.randrange(level)
		if (rand_row, rand_col) in pattern:	continue
		pattern.append((rand_row, rand_col))
	return pattern 

def lightUp(row, col, color):
	left, top = getLeftTop(row, col)
	surface = pygame.Surface((tile_size - 3, tile_size - 3))
	surface.fill(color)
	win.blit(surface, (left, top))

def startTimer():
	global timestamp
	if not timer_paused and timestamp['past']:
		timestamp['now'] = time.time()
		timestamp['timer'] += (timestamp['now'] - timestamp['past'])
		timestamp['past'] = timestamp['now']

def gameOver():
	win.fill(RED)
	drawText("Time's Up!", 'center', 50, True)
	drawText(f'Score: {score}', 'center', 150, True)
	drawText(f'Best: {hi_score}', 'center', 250, True)
	drawText('Press SPACE to play again', 'center', 350)
	pygame.display.update()

def startScreen():
	win.fill(BLUE)
	drawText('Memory Matrix', 'center', HEIGHT//2, True)
	drawText("Press SPACE to start", 'center', 350)
	pygame.display.update()

running = True
started = False
waiting_input = False


# Main Loop
while running:
	# Checking inputs
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		# Restart if times up
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_SPACE:
				if not started: started = True
				if timer_up:
					timer_up = False
					waiting_input = False
					score = 0
					level = 3
					tile_size = 100
					timestamp = {key:0 for key in timestamp.keys()}
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

	if not started:
		startScreen()
		continue

	startTimer()
	drawBoard()

	if timestamp['timer'] > TIMER:
		timer_up = True
		gameOver()

	if waiting_input and not timer_up:
		# Displaying tiles with color according to right/wrong
		for (row, col) in input_pattern:
			if (row, col) in new_pattern:
				lightUp(row, col, YELLOW)
			else:
				lightUp(row, col, RED)
		pygame.display.update()
		# Checking numbers of input
		if len(input_pattern) == len(new_pattern):
			waiting_input = False
			timer_paused = True
			# Display the correct pattern (& wrong ones)
			for (row, col) in new_pattern:
				lightUp(row, col, YELLOW)
			pygame.display.update()
			pygame.time.wait(SHOWTIME)
			# Checking patterns
			if sorted(input_pattern) == sorted(new_pattern):
				score += (level - 2)
				if score > hi_score:
					hi_score = score
				if level < 6:
					level += 1
					tile_size = int(tile_size - tile_size / SHRINKAGE)
			# Back to previous level if wrong pattern
			else:
				score -= 1
				if level > 3:
					level -= 1
					tile_size = int(tile_size + tile_size / SHRINKAGE)

	# if not waiting then display new pattern
	elif not waiting_input and not timer_up:
		timer_paused = True
		new_pattern = []
		input_pattern = []
		# Displaying empty board
		pygame.display.update()
		pygame.time.wait(SHOWTIME)
		# Display the new pattern 
		new_pattern = generatePattern()
		for (row, col) in new_pattern:
			lightUp(row, col, YELLOW)
		pygame.display.update()
		pygame.time.wait(SHOWTIME)

		waiting_input = True
		timer_paused = False
		timestamp['past'] = time.time()

	pygame.display.update()
	clock.tick(FPS)

pygame.quit()