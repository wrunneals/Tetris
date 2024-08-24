from enum import Enum
import random
import pygame
from pygame.locals import *
import sys

class Tetris:

	def __init__(self):
		pygame.init()
		self.res_x = 320
		self.res_y = 640
		self.ui_x = 240
		self.grid_x = 10
		self.grid_y = 20
		self.grid_size_x = int(self.res_x / self.grid_x)
		self.grid_size_y = int(self.res_y / self.grid_y)
		print(self.grid_size_y)
		self.fps = 60
		self.frames_per_tick = 60
		self.score = 0
		self.board = [[0] * self.grid_y for i in range(self.grid_x)]
		self.background = (80, 80, 100)
		self.ui_background = (127, 127, 150)

	def drawBoard(self, display, board, offset_x, offset_y, size_x, size_y):
		for x in range(len(board)):
			for y in range(len(board[0])):
				if board[x][y] == 0:
					continue
				color = (0, 0, 0)
				match board[x][y]:
					case 1:
						color = (225, 20, 20)
					case 2:
						color = (20, 225, 20)
					case 3:
						color = (20, 20, 225)
					case 4:
						color = (20, 225, 225)
					case 5:
						color = (225, 20, 225)
					case 6:
						color = (225, 100, 20)

				pygame.draw.rect(display, color, pygame.Rect(offset_x + x * size_x, offset_y + y * size_y, size_x, size_y))
				pygame.draw.rect(display, (0, 0, 0), pygame.Rect(offset_x + x * size_x, offset_y + y * size_y, size_x, size_y), 2)

	def drawUI(self, display):
		big_font = pygame.font.SysFont("Times New Roman", 40)
		small_font = pygame.font.SysFont("Times New Roman", 22)
		pygame.draw.rect(display, self.ui_background, (self.res_x, 0, self.ui_x, self.res_y))
		pygame.draw.rect(display, (0, 0, 0), (0, 0, self.res_x, self.res_y), 2)
		pygame.draw.rect(display, (0, 0, 0), (self.res_x, 0, self.ui_x, self.res_y), 2)
		title_text = big_font.render("Tetris", True, "white")
		title_rect = title_text.get_rect()
		title_rect.center = (self.res_x + self.ui_x / 2, 20)
		display.blit(title_text, title_rect)

		next_text = small_font.render("Next Block:", True, "black")
		next_rect = next_text.get_rect()
		next_rect.center = (self.res_x + 65, 75)
		display.blit(next_text, next_rect)

		score_text = small_font.render("Score: %s      Level: %s" % (self.score, int(self.score / 100 + 1) ), True, "white")
		score_rect = score_text.get_rect()
		score_rect.center = (self.res_x + 110, 300)
		display.blit(score_text, score_rect)

	def checkRows(self):
		for y in range(self.grid_y):
			row_complete = True
			for x in range(self.grid_x):
				if self.board[x][y] == 0:
					row_complete = False
			if row_complete:
				self.score += 10
				if self.score % 100 == 0 and self.score > 0:
					#Speed up on level up
					if self.frames_per_tick > 1:
						self.frames_per_tick -= 1
				for ytemp in reversed(range(y + 1 )):
					for xtemp in range(self.grid_x):
						if ytemp == 0:
							self.board[xtemp][ytemp] = 0
						else:
							self.board[xtemp][ytemp] = self.board[xtemp][ytemp - 1]

	def redraw(self, display, player):
		display.fill(self.background)
		self.drawBoard(display, self.board, 0, 0, self.grid_size_x, self.grid_size_y)
		self.drawBoard(display, player.board, player.x, player.y, self.grid_size_x, self.grid_size_y)
		self.drawUI(display)
		self.drawBoard(display, player.next_block, self.res_x + self.ui_x / 2 - 60, 125, self.grid_size_x, self.grid_size_y)

#---------------------------------------------------------------------------------------------------------------------------
class Container:
	
	class Blocks(Enum):
		T = [[1, 1, 1],
			 [0, 1, 0],
			 [0, 0, 0]]

		I = [[0, 2, 0, 0],
			 [0, 2, 0, 0],
			 [0, 2, 0, 0],
			 [0, 2, 0, 0]]

		O = [[3, 3],
			 [3, 3]]

		L = [[4, 0, 0],
			 [4, 0, 0],
			 [4, 4, 0]]

		J = [[0, 0, 5],
			 [0, 0, 5],
			 [0, 5, 5]]

		#Mean ones
		#X = [[0, 6, 0],
		#	 [6, 6, 6],
		#	 [0, 6, 0]]

	def __init__(self, game):
		self.startY = -96
		self.startX = 128
		self.x = self.startX
		self.y = self.startY
		self.board = random.choice(list(self.Blocks)).value
		self.next_block = random.choice(list(self.Blocks)).value
		self.game = game

	def checkCollisionPoint(self, pointX, pointY) -> bool:
		for x in range(len(self.board)):
			for y in range(len(self.board[0])):
				bx = int(pointX / self.game.grid_size_x) + x
				by = int(pointY / self.game.grid_size_y) + y
				if by >= self.game.grid_y and self.board[x][y] != 0:
					#Hitting ground
					return True
				if bx < 0 and self.board[x][y] != 0:
					#Hitting left side
					return True
				if bx >= self.game.grid_x and self.board[x][y] != 0:
					#Hitting right side
					return True
				if by >= 0 and by < self.game.grid_y and bx < self.game.grid_x:
					if self.game.board[bx][by] != 0 and self.board[x][y] != 0:
						#Hitting block
						return True
		return False

	def rotate(self, anti=False):
		temp = [[]] * len(self.board)
		for y in range(len(self.board[0])):
			column = []
			for x in range(len(self.board)):
				column.append(self.board[x][y])
			if not anti:
				temp[(len(temp) - 1) - y] = column
			else:
				temp[y] = column
		self.board = temp


	def update(self):
		if not self.checkCollisionPoint(self.x, self.y + self.game.grid_size_y):
			self.y += self.game.grid_size_y
		else:
			self.writeToBoard()
			self.y = self.startY
			self.x = self.startX
			self.board = self.next_block
			self.next_block = random.choice(list(self.Blocks)).value
	
	def writeToBoard(self):
		for x in range(len(self.board)):
			for y in range(len(self.board[0])):
				bx = int(self.x / self.game.grid_size_x) + x
				by = int(self.y / self.game.grid_size_y) + y
				if by < 0 and self.board[x][y] != 0:
					print("Game Over")
					self.game.board = [[0] * self.game.grid_y for i in range(self.game.grid_x)]
					self.x = 0
					self.y = self.startY
					return
				if self.board[x][y] != 0:
					self.game.board[bx][by] = self.board[x][y]
#----------------------------------------------------------------------------------------------------------------------------
def main():
	game = Tetris()
	display = pygame.display.set_mode((game.res_x + game.ui_x, game.res_y))
	pygame.display.set_caption("Tetris")
	clock = pygame.time.Clock()
	player = Container(game)
	frames_count = 0
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT:
					if not player.checkCollisionPoint(player.x - game.grid_size_x, player.y):
						player.x -= game.grid_size_x
				if event.key == pygame.K_RIGHT:
					if not player.checkCollisionPoint(player.x + game.grid_size_x, player.y):
						player.x += game.grid_size_x
				if event.key == pygame.K_DOWN:
					if not player.checkCollisionPoint(player.x, player.y + game.grid_size_y):
						player.y += game.grid_size_y
				if event.key == pygame.K_UP:
					player.rotate()
					if player.checkCollisionPoint(player.x, player.y):
						player.rotate(True)
		game.redraw(display, player)
		if frames_count / game.frames_per_tick == 1:
			player.update()
			game.checkRows()
			frames_count = 0
		pygame.display.update()
		frames_count += 1
		clock.tick(game.fps)

if __name__ == "__main__":
	main()