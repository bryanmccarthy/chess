import pygame

from const import *
from board import Board
from dragger import Dragger

class Game:
  def __init__(self):
    self.next_turn = 'white'
    self.board = Board()
    self.dragger = Dragger(self)
    
  def show_bg(self, surface):
    for row in range(ROWS):
      for col in range(COLS):
        if (row + col) % 2 == 0:
          color = (234, 235, 200) # light green
        else:
          color = (119, 154, 88) # dark green
                
        rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
        pygame.draw.rect(surface, color, rect)
  
  def show_pieces(self, surface):
    for row in range(ROWS):
      for col in range(COLS):
        if self.board.squares[row][col].has_piece():
          piece = self.board.squares[row][col].piece

          if piece is not self.dragger.piece:
            piece.set_texture(size=80)
            img = pygame.image.load(piece.texture)
            img_center = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
            piece.texture_rect = img.get_rect(center=img_center)
            surface.blit(img, piece.texture_rect)
  
  def show_moves(self, surface):
    if self.dragger.dragging:
      piece = self.dragger.piece

      for move in piece.moves:
        color = '#fabf5a' if (move.final.row + move.final.col) % 2 != 0 else '#f7d078'
        rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
        pygame.draw.rect(surface, color, rect)

  def show_last_move(self, surface):
    if self.board.last_move:
      initial = self.board.last_move.initial
      final = self.board.last_move.final
      
      for pos in [initial, final]:
        color = '#fabf5a' if (pos.row + pos.col) % 2 != 0 else '#f7d078'
        rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
        pygame.draw.rect(surface, color, rect)
  
  def switch_turn(self):
    self.next_turn = 'black' if self.next_turn == 'white' else 'white'

  def reset(self):
    self.__init__()