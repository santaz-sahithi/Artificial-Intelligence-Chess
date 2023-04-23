import pygame
from pygame.locals import *
import os
import pyautogui


SQUARE_SIZE = 80
SIDE_BAR_WIDTH = 0
TITLE_BAR_HEIGHT = 50


class BlackSquare(pygame.sprite.Sprite):
    def __init__(self):
        super(BlackSquare, self).__init__()
        self.surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        self.surf.fill((140, 55, 25))
        self.rect = self.surf.get_rect()


class WhiteSquare(pygame.sprite.Sprite):
    def __init__(self):
        super(WhiteSquare, self).__init__()
        self.surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
        self.surf.fill((245, 190, 120))
        self.rect = self.surf.get_rect()


class TitleBar(pygame.sprite.Sprite):
    def __init__(self):
        super(TitleBar, self).__init__()
        self.surf = pygame.Surface((8 * SQUARE_SIZE, TITLE_BAR_HEIGHT))
        self.surf.fill((255, 255, 255))
        self.rect = self.surf.get_rect()


class Render:

    def __init__(self, chess_gui):
        self.chess_gui = chess_gui
        self.sprites = {}
        self.load_sprites()

        pygame.init()
        self.screen = pygame.display.set_mode((SQUARE_SIZE * 8 + SIDE_BAR_WIDTH, TITLE_BAR_HEIGHT + SQUARE_SIZE * 8))
        pygame.display.set_caption('Chess AI')
        self.draw()

    def draw(self):
        self.draw_chess_table()
        if self.chess_gui.chess_board.selected():
            self.draw_selection_square()
            self.draw_available_moves()
        self.draw_chess_pieces()
        self.draw_titles()

        pygame.display.flip()

    def draw_titles(self):
        title_brd = TitleBar()
        self.screen.blit(title_brd.surf, (0, 0))
        font = pygame.font.Font('OpenSans.ttf', 32)
        text = font.render(self.chess_gui.chess_board.get_message(), True, (0, 0, 0), (255, 255, 255))

        self.screen.blit(text, (0, 0))

    def load_sprites_fldr(self, fldr):
        self.sprites[fldr] = {}

        for sprite in os.listdir(os.path.join("sprites", fldr)):
            s = sprite.find(".png")
            if s != -1:
                name = sprite[:sprite.find(".png")]
                self.sprites[fldr][name] = pygame.image.load(os.path.join("sprites", fldr, sprite))

    def load_sprites(self):
        self.load_sprites_fldr("white")
        self.load_sprites_fldr("black")
        self.load_sprites_fldr("etc")

    def draw_chess_table_row(self, row):
        white_square = WhiteSquare()
        black_square = BlackSquare()
        for i in range(8):
            if (row + i) % 2 == 0:
                self.screen.blit(white_square.surf, self.get_pos_table((row, i)))
            else:
                self.screen.blit(black_square.surf, self.get_pos_table((row, i)))

    def draw_chess_table(self):
        for i in range(8):
            self.draw_chess_table_row(i)

    def draw_selection_square(self):
        pos = self.get_pos_table(self.chess_gui.chess_board.selected_segment)
        self.screen.blit(self.sprites["etc"]["select_square"], pos)

    def draw_available_moves(self):
        for move in self.chess_gui.avail_moves:
            pos = self.get_pos_table(move)
            if self.chess_gui.chess_board.is_free(move):
                self.screen.blit(self.sprites["etc"]["select"], pos)
            else:
                self.screen.blit(self.sprites["etc"]["kill_square"], pos)

    def draw_chess_pieces(self):
        for row_number, board_row in enumerate(self.chess_gui.chess_board.get_chess_board()):
            for clm, piece in enumerate(board_row):
                if piece is not None:
                    piece = piece.split(":")
                    if len(piece) != 2:
                        raise ValueError()
                    self.screen.blit(self.sprites[piece[0]][piece[1]], self.get_pos_table((row_number, clm)))

    def get_pos_table(self, pos):
        row, clm = pos
        return clm * SQUARE_SIZE, TITLE_BAR_HEIGHT + row * SQUARE_SIZE

    def get_mouse_pos(self):
        x, y = pygame.mouse.get_pos()
        if x < 8 * SQUARE_SIZE and y > TITLE_BAR_HEIGHT:
            x = int(x / SQUARE_SIZE)
            y = int((y - TITLE_BAR_HEIGHT) / SQUARE_SIZE)
            return y, x
        else:
            return None


class ChessGUI:

    def __init__(self, chess_board, logger):
        self.avail_moves = []
        self.logger = logger
        self.chess_board = chess_board
        self.render = Render(self)

    def game_loop(self):
        if self.chess_board.checkmate is not None:
            self.render.draw()
            return
        pos = self.render.get_mouse_pos()
        self.logger.log(f"mouse button pressed at {pos}")
        if pos is not None:
            moved, pawn_promotion = self.chess_board.move_piece(pos)
            self.logger.log(f" move piece call moved:{moved} promotion:{pawn_promotion} ")
            if not moved:
                self.chess_board.select_piece(pos)
                self.avail_moves = self.chess_board.find_possible_moves()
                self.logger.log(f" {pos} selected ")
            if pawn_promotion:
                pawn_color = self.chess_board.get_piece(pos).split(":")[0]
                resp = pyautogui.confirm(text='Which piece would you like to promote the pawn?',
                                         title='Pawn Promotion', buttons=['Queen', 'Knight', 'Rook', 'Bishop'])
                resp = f"{pawn_color}:{resp.lower()}"
                self.chess_board.set_piece(pos, resp)

        else:
            self.chess_board.selected_segment = None
            self.avail_moves = []
        self.render.draw()

    def update(self):
        self.render.draw()

    def get_events(self):
        return pygame.event.get()
