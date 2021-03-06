import pygame
import random
import time

WIDTH = 600
HEIGHT = 600
FONTSIZE = 30
SHOWTIME = 1000
SHRINKAGE = 9
TIMER = 60
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

normal_font = pygame.font.SysFont('Comic Sans MS', FONTSIZE)
big_font = pygame.font.Font('freesansbold.ttf', FONTSIZE+40)

timestamp = {'past':0, 'now':0, 'timer':0}
timer_paused = True
timer_up = False

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

def drawText(msg, x, y, color, title=False):
	font = big_font if title else normal_font
	text = font.render(msg, True, color)
	rect = text.get_rect()
	if x == 'center':	x = (WIDTH // 2) - (text.get_width() // 2)
	rect.topleft = x, y
	win.blit(text, rect)

def startScreen():
	win.fill(BLUE)
	drawText('Memory Matrix', 'center', 100, YELLOW, True)
	drawText('Press SPACE to start', 'center', 350, WHITE)
	pygame.display.update()

def gameOver():
	win.fill(RED)
	drawText("Time's Up!", 'center', 50, WHITE, True)
	drawText(f'Score: {score}', 'center', 150, WHITE, True)
	drawText(f'Best: {hi_score}', 'center', 250, WHITE, True)
	drawText('Press SPACE to play again', 'center', 350, WHITE)
	pygame.display.update()

def drawBoard():
	win.fill(BLUE)
	drawText(f'Score: {score}', 20, 10, WHITE)
	drawText(f'Level: {level-2}', 'center', 10, LIME)
	drawText(f'Best: {hi_score}', WIDTH-130, 10, WHITE)
	# Drawing Table
	for row in range(level):
		for col in range(level):
			left, top = getLeftTop(row, col)
			pygame.draw.rect(win, GREY, (left, top, tile_size - 3, tile_size - 3))
	# Drawing border
	board_size = tile_size * level
	left, top = getLeftTop(0, 0)
	pygame.draw.rect(win, RED, (left-5, top-5, board_size+7, board_size+7), 4)
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
	surface = pygame.Surface((tile_size-3, tile_size-3))
	surface.fill(color)
	win.blit(surface, (left, top))

def runTimer():
	global timestamp
	if not timer_paused and timestamp['past']:
		timestamp['now'] = time.time()
		timestamp['timer'] += (timestamp['now'] - timestamp['past'])
		timestamp['past'] = timestamp['now']


running = True
started = False
waiting_input = False
# Main gameloop
while running:
	# Checking input events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_SPACE:
				if not started:
					started = True
				# Restarting if timer is up
				if timer_up:
					timer_up = False
					waiting_input = False
					score = 0
					level = 3
					tile_size = 100
					timestamp = {key:0 for key in timestamp.keys()}
					new_pattern = []
					input_pattern = []
		# Getting tile clicked by player
		# & Adding into input pattern
		if event.type == pygame.MOUSEBUTTONUP:
			mousex, mousey = event.pos
			row, col = getClickedTile(mousex, mousey)
			if waiting_input and row is not None:
				if (row, col) not in input_pattern:
					input_pattern.append((row, col))

	if not started:
		startScreen()
		continue

	runTimer()
	drawBoard()

	if timestamp['timer'] > TIMER:
		timer_up = True
		gameOver()

	if waiting_input and not timer_up:
		# Displaying input pattern
		for (row, col) in input_pattern:
			if (row, col) in new_pattern:
				lightUp(row, col, YELLOW)
			else:
				lightUp(row, col, RED)
		drawText(f'Recalling the pattern ({len(new_pattern)-len(input_pattern)})...', 'center', HEIGHT-60, WHITE)
		pygame.display.update()
		# Checking if input sequence completed
		if len(input_pattern) == len(new_pattern):
			waiting_input = False
			timer_paused = True
			# Displaying the correct pattern (& wrong ones)
			for (row, col) in new_pattern:
				lightUp(row, col, YELLOW)
			# Checking patterns
			if sorted(input_pattern) == sorted(new_pattern):
				score += level-2
				if score > hi_score:
					hi_score = score
				if level < 8:
					level += 1
					tile_size = int(tile_size - tile_size / SHRINKAGE)
			else:
				if level > 3:
					if score > 0: 
						score -= 1
					level -= 1
					tile_size = int(tile_size + tile_size / SHRINKAGE)
			pygame.display.update()
			pygame.time.wait(SHOWTIME)
	# if not waiting then display new pattern
	elif not waiting_input and not timer_up:
		timer_paused = True
		# Displaying empty board
		new_pattern = []
		input_pattern = []
		pygame.display.update()
		pygame.time.wait(SHOWTIME)
		# Displaying new pattern
		new_pattern = generatePattern()
		for (row, col) in new_pattern:
			lightUp(row, col, YELLOW)
		drawText('Memorize this pattern.', 'center', HEIGHT-60, WHITE)
		pygame.display.update()
		pygame.time.wait(SHOWTIME)
		waiting_input = True
		timer_paused = False
		timestamp['past'] = time.time()

	pygame.display.update()
	clock.tick(FPS)
# Quit pygame when while-loop is over
pygame.quit()