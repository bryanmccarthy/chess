from const import *
from square import Square
from piece import *
from move import Move

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
    piece.moved = True
    piece.clear_moves()
    self.last_move = move

  def valid_move(self, piece, move):
    return move in piece.moves

  def calc_moves(self, piece, row, col):
    def pawn_moves():
      # TODO: En passant and promotion
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
            final = Square(possible_move_row, possible_move_col)
            move = Move(initial, final)
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

      for move in posible_moves:
        move_row, move_col = move
        if Square.in_range(move_row, move_col):
          if self.squares[move_row][move_col].is_empty_or_enemy(piece.color):
            initial = Square(row, col)
            final = Square(move_row, move_col)
            move = Move(initial, final)
            piece.add_move(move)
    
    def incremental_moves(incrs):
      for incr in incrs:
        row_incr, col_incr = incr
        possible_move_row = row + row_incr
        possible_move_col = col + col_incr

        while True:
          if Square.in_range(possible_move_row, possible_move_col):
            initial = Square(row, col)
            final = Square(possible_move_row, possible_move_col)
            move = Move(initial, final)

            if self.squares[possible_move_row][possible_move_col].is_empty():
              piece.add_move(move)

            if self.squares[possible_move_row][possible_move_col].has_enemy(piece.color):
              piece.add_move(move)
              break # Enemy piece in the way

            if self.squares[possible_move_row][possible_move_col].has_team_piece(piece.color):
              break # Piece in the way
          else:
            break # Out of range
              
          possible_move_row, possible_move_col = possible_move_row + row_incr, possible_move_col + col_incr

    def king_moves():
      # TODO: Castling
      adjacent_squares = [(row - 1, col - 1), (row - 1, col), (row - 1, col + 1), (row, col - 1), (row, col + 1), (row + 1, col - 1), (row + 1, col), (row + 1, col + 1)]

      for possible_move in adjacent_squares:
        possible_move_row, possible_move_col = possible_move

        if Square.in_range(possible_move_row, possible_move_col):
          if self.squares[possible_move_row][possible_move_col].is_empty_or_enemy(piece.color):
            initial = Square(row, col)
            final = Square(possible_move_row, possible_move_col)
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