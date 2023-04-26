from const import *
from square import Square
from piece import *
from move import Move
import copy

class Board:
  def __init__(self):
    self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
    self.last_move = None
    self._create()
    self._add_pieces('white')
    self._add_pieces('black')

  def move(self, piece, move):
    initial = move.initial
    final = move.final
    self.squares[initial.row][initial.col].piece = None
    self.squares[final.row][final.col].piece = piece

    if isinstance(piece, Pawn):
      self.check_promotion(piece, final)

    if isinstance(piece, King):
      if self.castle(initial, final):
        diff = final.col - initial.col

        if diff < 0:
          rook = piece.left_rook
        else:
          rook = piece.right_rook
        
        self.move(rook, rook.moves[-1])

    piece.moved = True
    piece.clear_moves()
    self.last_move = move

  def valid_move(self, piece, move):
    return move in piece.moves
  
  def check_promotion(self, piece, final):
    if final.row == 0 or final.row == 7:
      self.squares[final.row][final.col].piece = Queen(piece.color)

  def castle(self, initial, final):
    return abs(initial.col - final.col) == 2
  
  def in_check(self, piece, move):
    temp_piece = copy.deepcopy(piece)
    temp_board = copy.deepcopy(self)
    temp_board.move(temp_piece, move)

    for row in range(ROWS):
      for col in range(COLS):
        if temp_board.squares[row][col].has_enemy(piece.color):
          p = temp_board.squares[row][col].piece
          temp_board.calc_moves(p, row, col, bool=False)
          for m in p.moves:
            if isinstance(m.final.piece, King):
              return True
    
    return False

  def calc_moves(self, piece, row, col, bool=True):
    def pawn_moves():
      # TODO: En passant
      steps = 1 if piece.moved else 2
      
      # Vertical (move)
      start = row + piece.dir
      end = row + (piece.dir * (steps + 1))
      for possible_move_row in range(start, end, piece.dir):
        if Square.in_range(possible_move_row):
          if self.squares[possible_move_row][col].is_empty():
            initial = Square(row, col)
            final = Square(possible_move_row, col)
            move = Move(initial, final)

            if bool:
              if not self.in_check(piece, move):
                piece.add_move(move)
            else:
              piece.add_move(move)
          else:
            break # Piece in the way
        else:
          break # Out of range

      # Diagonal (capture)
      possible_move_row = row + piece.dir
      possible_move_cols = (col - 1, col + 1)
      for possible_move_col in possible_move_cols:
        if Square.in_range(possible_move_row, possible_move_col):
          if self.squares[possible_move_row][possible_move_col].has_enemy(piece.color):
            initial = Square(row, col)
            final_piece = self.squares[possible_move_row][possible_move_col].piece
            final = Square(possible_move_row, possible_move_col, final_piece)
            move = Move(initial, final)
            
            if bool:
              if not self.in_check(piece, move):
                piece.add_move(move)
            else:
              piece.add_move(move)

    def knight_moves():
      posible_moves = [
        (row - 2, col - 1),
        (row - 2, col + 1),
        (row - 1, col - 2),
        (row - 1, col + 2),
        (row + 1, col - 2),
        (row + 1, col + 2),
        (row + 2, col - 1),
        (row + 2, col + 1)
      ]

      for possible_move in posible_moves:
        possible_move_row, possible_move_col = possible_move
        if Square.in_range(possible_move_row, possible_move_col):
          if self.squares[possible_move_row][possible_move_col].is_empty_or_enemy(piece.color):
            initial = Square(row, col)
            final_piece = self.squares[possible_move_row][possible_move_col].piece
            final = Square(possible_move_row, possible_move_col, final_piece)
            move = Move(initial, final)
            
            if bool:
              if not self.in_check(piece, move):
                piece.add_move(move)
              else:
                break
            else:
              piece.add_move(move)
    
    def incremental_moves(incrs):
      for incr in incrs:
        row_incr, col_incr = incr
        possible_move_row = row + row_incr
        possible_move_col = col + col_incr

        while True:
          if Square.in_range(possible_move_row, possible_move_col):
            initial = Square(row, col)
            final_piece = self.squares[possible_move_row][possible_move_col].piece
            final = Square(possible_move_row, possible_move_col, final_piece)
            move = Move(initial, final)

            if self.squares[possible_move_row][possible_move_col].is_empty():
              if bool:
                if not self.in_check(piece, move):
                  piece.add_move(move)
              else:
                piece.add_move(move)

            elif self.squares[possible_move_row][possible_move_col].has_enemy(piece.color):
              if bool:
                if not self.in_check(piece, move):
                  piece.add_move(move)
              else:
                piece.add_move(move)
              break # Enemy piece in the way

            elif self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
              break # Piece in the way
          else:
            break # Out of range
              
          possible_move_row, possible_move_col = possible_move_row + row_incr, possible_move_col + col_incr

    def king_moves():
      # TODO: Prevent king from moving into check
      # TODO: Prevent King from castling if in check or if any square between king and rook is under attack
      adjacent_squares = [(row - 1, col - 1), (row - 1, col), (row - 1, col + 1), (row, col - 1), (row, col + 1), (row + 1, col - 1), (row + 1, col), (row + 1, col + 1)]

      for possible_move in adjacent_squares:
        possible_move_row, possible_move_col = possible_move

        if Square.in_range(possible_move_row, possible_move_col):
          if self.squares[possible_move_row][possible_move_col].is_empty_or_enemy(piece.color):
            initial = Square(row, col)
            final = Square(possible_move_row, possible_move_col)
            move = Move(initial, final)
            piece.add_move(move)
      
      if not piece.moved:
        left_rook = self.squares[row][0].piece
        right_rook = self.squares[row][7].piece

        if isinstance(left_rook, Rook) and not left_rook.moved:
          if self.squares[row][1].is_empty() and self.squares[row][2].is_empty() and self.squares[row][3].is_empty():
            piece.left_rook = left_rook

            # Rook move
            initial = Square(row, 0)
            final = Square(row, 3)
            move = Move(initial, final)
            left_rook.add_move(move)

            # King move
            initial = Square(row, col)
            final = Square(row, 2)
            move = Move(initial, final)
            piece.add_move(move)

        if isinstance(right_rook, Rook) and not right_rook.moved:
          if self.squares[row][5].is_empty() and self.squares[row][6].is_empty():
            piece.right_rook = right_rook

            # Rook move
            initial = Square(row, 7)
            final = Square(row, 5)
            move = Move(initial, final)
            right_rook.add_move(move)

            # King move
            initial = Square(row, col)
            final = Square(row, 6)
            move = Move(initial, final)
            piece.add_move(move)

    if isinstance(piece, Pawn): pawn_moves()
    elif isinstance(piece, Knight): knight_moves()
    elif isinstance(piece, Bishop): incremental_moves([(-1, -1), (-1, 1), (1, -1), (1, 1)])
    elif isinstance(piece, Rook): incremental_moves([(-1, 0), (0, -1), (0, 1), (1, 0)])
    elif isinstance(piece, Queen): incremental_moves([(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)])
    elif isinstance(piece, King): king_moves()

  def _create(self):
    for row in range(ROWS):
      for col in range(COLS):
        self.squares[row][col] = Square(row, col)

  def _add_pieces(self, color):
    row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

    # Pawns
    for col in range(COLS):
      self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

    # Knights
    self.squares[row_other][1] = Square(row_other, 1, Knight(color))
    self.squares[row_other][6] = Square(row_other, 6, Knight(color))

    # Bishops
    self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
    self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

    # Rooks
    self.squares[row_other][0] = Square(row_other, 0, Rook(color))
    self.squares[row_other][7] = Square(row_other, 7, Rook(color))

    # Queen
    self.squares[row_other][3] = Square(row_other, 3, Queen(color))

    # King
    self.squares[row_other][4] = Square(row_other, 4, King(color))