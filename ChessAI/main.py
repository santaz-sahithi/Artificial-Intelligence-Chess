import os

import pygame
from pygame.locals import *

from chess_gui import ChessGUI
from chess_board import ChessBoard
from chess_ai import ChessAI
import datetime


class Logger:

    def __init__(self):
        time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H-%M")
        self.log_file_name = f"{time_stamp}.log"

        if not os.path.exists("log"):
            os.mkdir("log")

        count = 0
        while os.path.exists(os.path.join("log", self.log_file_name)):
            count += 1
            self.log_file_name = f"{time_stamp}_{count}.log"

        self.log_file_name = os.path.join("log", self.log_file_name)

        time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        with open(self.log_file_name, "w", encoding="UTF-8") as fp:
            fp.write(f"STARTING LOGGING {time_stamp}\n")

    def log(self, message):
        time_stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        with open(self.log_file_name, "a", encoding="UTF-8") as fp:
            fp.write(f"{time_stamp}:- {message}\n")


def main():
    gameOn = True
    logger = Logger()
    play_against_computer = True
    chess_board = ChessBoard()
    chess_ui = ChessGUI(chess_board, logger)
    chess_ai = ChessAI(chess_board, logger)
    chess_ui.update()

    while gameOn:
        for event in chess_ui.get_events():
            if event.type == QUIT:
                logger.log("quiting")
                gameOn = False
            elif event.type == MOUSEBUTTONDOWN:
                chess_ui.game_loop()
        chess_ui.update()
        if chess_board.turn == "black" and play_against_computer:
            chess_ai.play_next_move(chess_ui)
            chess_ui.update()


if __name__ == '__main__':
    main()
