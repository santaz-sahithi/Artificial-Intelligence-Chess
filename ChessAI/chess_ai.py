import random
import time

piece_scores = {
    "pawn": 1,
    "knight": 3,
    "bishop": 3,
    "rook": 5,
    "queen": 9,
    "king": 0,
}

opening_moves = {
    "black": [
        [(1, 6), (2, 6)],
        [(1, 1), (2, 1)],
        [(0, 2), (2, 0)],
        [(0, 6), (2, 5)],
        [(0, 5), (2, 7)],
        [(0, 1), (2, 2)],
        [(0, 4), (0, 6)],
        [(1, 3), (3, 3)],
        [(0, 3), (2, 3)],
    ],
    "white": [
        [(6, 1), (5, 1)],
        [(6, 6), (5, 6)],
        [(7, 5), (5, 7)],
        [(7, 1), (5, 2)],
        [(7, 2), (5, 0)],
        [(7, 6), (5, 5)],
        [(7, 4), (7, 6)],
        [(6, 4), (5, 4)],
        [(6, 3), (4, 3)],
        [(7, 3), (5, 3)],
        [(7, 0), (7, 3)],
    ]
}


def get_opp_side(side):
    if side == "white":
        return "black"
    return "white"


class ChessAI:

    def __init__(self, chess_board, logger, side="black"):
        self.logger = logger
        self.chess_board = chess_board
        self.playing_side = side
        self.other_side = "black"
        if self.playing_side == "black":
            self.other_side = "white"
        self.opening_moves = opening_moves[self.playing_side]
        pass

    def get_best_move(self, side, do_opening=True, n_moves=2):
        n_moves -= 1
        possible_moves = self.chess_board.get_all_possible_moves(side)
        k = list(possible_moves.keys())
        moves = []
        for key in k:
            for mov in possible_moves[key]:
                moves.append((key, mov))
        if len(moves) == 0:
            return None

        best_move = []

        cur_score = self.move_score(moves[0], side, n_moves=n_moves)
        min_score = cur_score

        for move in moves:
            move_score = self.move_score(move, side, n_moves=n_moves)
            if move_score == cur_score:
                best_move.append(move)
            if move_score > cur_score:
                cur_score = move_score
                best_move = [move]
            if move_score < min_score:
                min_score = move_score

        if do_opening:
            if (min_score == cur_score or (cur_score - min_score < 3)) and len(self.opening_moves) != 0:
                for move in self.opening_moves:
                    if self.is_valid_move(move):
                        best_move = [move]
                        self.opening_moves.remove(move)
                        break
        if len(best_move) > 2:
            best_move = random.choice(best_move)
        else:
            best_move = best_move[0]
        return best_move

    def play_next_move(self, ui):
        if self.chess_board.check_for_checkmate("black"):
            return

        best_move = self.get_best_move(self.playing_side)

        if best_move is not None:
            self.logger.log(f" AI moving {best_move[0]} to {best_move[1]}")
            time.sleep(1)
            self.chess_board.select_piece(best_move[0])
            ui.avail_moves = [best_move[1]]
            ui.update()
            time.sleep(1)
            self.chess_board.move_piece(best_move[1])

    def is_valid_move(self, move):
        start, end = move
        self.chess_board.save_state("AI_Valid_check")
        self.chess_board.select_piece(start)
        moved, pawn = self.chess_board.move_piece(end)
        self.chess_board.restore_state("AI_Valid_check")
        self.chess_board.destroy_state("AI_Valid_check")
        return moved

    def move_score(self, move, side, n_moves=1):
        start, end = move
        state = f"{time.time_ns()}{random.random()}"
        self.chess_board.save_state(state)

        self.chess_board.select_piece(start)
        moved, promotion = self.chess_board.move_piece(end)
        if promotion:
            resp = f"{side}:queen"
            self.chess_board.set_piece(end, resp)
        score = self.get_score(side)

        opp_side = get_opp_side(side)

        for i in range(n_moves):
            move = self.get_best_move(opp_side, do_opening=False, n_moves=n_moves)
            if move is None:
                score = self.get_score(side)
                break
            start, end = move
            self.chess_board.select_piece(start)
            self.chess_board.move_piece(end)

            move = self.get_best_move(side, do_opening=False, n_moves=n_moves)
            if move is None:
                score = self.get_score(side)
                break
            start, end = move
            self.chess_board.select_piece(start)
            self.chess_board.move_piece(end)

            score = self.get_score(side)

        self.chess_board.restore_state(state)
        self.chess_board.destroy_state(state)
        return score

    def get_score(self, side):
        check_score = 0
        other_side = get_opp_side(side)

        if self.chess_board.in_check(side):
            check_score -= 0
            if self.chess_board.check_for_checkmate(side):
                check_score -= 200
            elif self.chess_board.check_for_stalemate(side):
                check_score -= 20

        if self.chess_board.in_check(other_side):
            check_score += 0
            if self.chess_board.check_for_checkmate(other_side):
                check_score += 200
            elif self.chess_board.check_for_stalemate(other_side):
                check_score -= 200
        our_score = 0
        chess_board = self.chess_board.chess_board
        their_score = 0
        for row in chess_board:
            for piece in row:
                if piece is None:
                    continue
                piece = piece.split(":")
                if piece[0] == side:
                    our_score += piece_scores[piece[1]]
                else:
                    their_score += piece_scores[piece[1]]

        return our_score - their_score + check_score
