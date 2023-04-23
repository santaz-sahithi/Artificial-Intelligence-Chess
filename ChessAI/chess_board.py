import json
import copy

available_colors = ["white", "black"]


def add_positions(pos, move):
    pos_x, pos_y = pos
    mov_x, mov_y = move
    return pos_x + mov_x, pos_y + mov_y


def get_pos_after_move(pos, move):
    out_x, out_y = add_positions(pos, move)
    if out_x > 7 or out_x < 0 or out_y > 7 or out_y < 0:
        return None
    return out_x, out_y


class ChessBoard:

    def __init__(self, chess_board=None):
        self.chess_board = chess_board
        self.chess_info = {}
        self.selected_segment = None
        self.turn = "white"
        self.checkmate = None
        self.castle_available = [
            # white
            # king side queen side
            [True, True],
            # black
            # king side queen side
            [True, True]
        ]

        self.saved_state = {}

        self.load_data()
        self.valid_moves = self.chess_info["valid_moves"]
        if self.chess_board is None:
            self.chess_board = self.chess_info["starting_position"]

    def get_all_possible_moves(self, side):
        avail_moves = {}
        for row in range(8):
            for clm in range(8):
                pos = (row, clm)
                piece = self.get_piece(pos)
                if piece is None:
                    continue
                piece = piece.split(":")
                if piece[0] != side:
                    continue

                avail_moves[(row, clm)] = self._possible_moves(pos)

        return avail_moves

    def check_for_checkmate(self, side):
        if self.checkmate is not None:
            return self.checkmate == side
        if not self.in_check(side):
            return False
        check_mate = self.check_for_stalemate(side)
        if check_mate:
            self.checkmate = side
        return check_mate

    def check_for_stalemate(self, side):
        for row in range(8):
            for clm in range(8):
                pos = (row, clm)
                piece = self.get_piece(pos)
                if piece is None:
                    continue

                piece = piece.split(":")
                if piece[0] != side:
                    continue

                avail_moves = self._possible_moves(pos)
                if len(avail_moves) != 0:
                    return False
        return True

    def set_piece(self, pos, piece):
        self.chess_board[pos[0]][pos[1]] = piece

    def get_selected_piece(self):
        if self.selected_segment is not None:
            return self.get_piece(self.selected_segment)
        return None

    def get_piece(self, pos):
        return self.chess_board[pos[0]][pos[1]]

    def get_chess_board(self):
        return self.chess_board

    def select_piece(self, pos):
        if self.get_piece(pos) is not None:
            self.selected_segment = pos
        else:
            self.selected_segment = None

    def selected(self):
        return self.selected_segment is not None

    def get_moves_row(self, delta, pos):
        moves = []
        m = delta
        side = self.get_piece(pos).split(":")[0]
        while self._is_valid_move(get_pos_after_move(pos, m), side):
            move = get_pos_after_move(pos, m)
            moves.append(move)
            if not self.is_free(move):
                break
            m = add_positions(m, delta)
        return moves

    def get_rook_moves(self, pos):
        moves = []
        moves.extend(self.get_moves_row((1, 0), pos))
        moves.extend(self.get_moves_row((-1, 0), pos))
        moves.extend(self.get_moves_row((0, -1), pos))
        moves.extend(self.get_moves_row((0, 1), pos))
        return moves

    def get_bishop_moves(self, pos):
        moves = []
        moves.extend(self.get_moves_row((1, 1), pos))
        moves.extend(self.get_moves_row((-1, -1), pos))
        moves.extend(self.get_moves_row((1, -1), pos))
        moves.extend(self.get_moves_row((-1, 1), pos))
        return moves

    def get_message(self):
        message = self.turn
        if self.in_check(self.turn):
            message += " check"
            if self.check_for_checkmate(self.turn):
                message += "mate"
        if self.checkmate is not None:
            m = "white"
            if self.checkmate == "white":
                m = "black"
            message += f" congrats {m} wins"
        return message

    def get_pawn_available_moves(self, pos, clr):
        moves = []
        if clr == "black":
            vm_1 = get_pos_after_move(pos, (1, 0))
            vm_2 = get_pos_after_move(pos, (2, 0))
            kill_1 = get_pos_after_move(pos, (1, -1))
            kill_2 = get_pos_after_move(pos, (1, 1))
            if pos[0] != 1:
                vm_2 = None
        else:
            vm_1 = get_pos_after_move(pos, (-1, 0))
            vm_2 = get_pos_after_move(pos, (-2, 0))
            kill_1 = get_pos_after_move(pos, (-1, -1))
            kill_2 = get_pos_after_move(pos, (-1, 1))
            if pos[0] != 6:
                vm_2 = None
        if self._is_valid_move(vm_1, clr):
            if self.is_free(vm_1):
                moves.append(vm_1)
                if self._is_valid_move(vm_2, clr):
                    if self.is_free(vm_2):
                        moves.append(vm_2)
        for km in (kill_2, kill_1):
            if self._is_valid_move(km, clr):
                if not self.is_free(km):
                    moves.append(km)
        return moves

    def find_piece(self, piece):
        pos = []
        for row in range(8):
            for clm in range(8):
                if self.chess_board[row][clm] == piece:
                    pos.append((row, clm))
        return pos

    def in_check(self, side):
        position_king = self.find_piece(f"{side}:king")[0]
        for row in range(8):
            for clm in range(8):
                pos = (row, clm)
                piece = self.get_piece(pos)
                if piece is None:
                    continue
                piece = piece.split(":")
                if piece[0] == side:
                    continue

                avail_moves = self._possible_moves(pos, prevent_check=False)
                if position_king in avail_moves:
                    return True
        return False

    def _possible_moves(self, pos, prevent_check=True):
        moves = []
        piece = self.get_piece(pos).split(":")

        if piece[1] == "pawn":
            # pawn special moves
            moves.extend(self.get_pawn_available_moves(pos, piece[0]))
        elif piece[1] == "knight" or piece[1] == "king":
            valid_moves = self.valid_moves[piece[1]]
            for mov in valid_moves:
                p = get_pos_after_move(pos, mov)
                if self._is_valid_move(p, piece[0]):
                    moves.append(p)
        else:
            if piece[1] == "rook" or piece[1] == "queen":
                moves.extend(self.get_rook_moves(pos))
            if piece[1] == "bishop" or piece[1] == "queen":
                moves.extend(self.get_bishop_moves(pos))

        # castling
        if piece[1] == "king":
            row = 0
            clr = 1
            if piece[0] == "white":
                clr = 0
                row = 7
            king_side, queen_side = self.castle_available[clr]

            if king_side and self.is_free((row, 5)) and self.is_free((row, 6)):
                moves.append((row, 6))
            if queen_side and self.is_free((row, 1)) and self.is_free((row, 2)) and self.is_free((row, 3)):
                moves.append((row, 2))
        if prevent_check:
            bad_moves = []
            for move in moves:
                # check if the move puts the current person in check ie it's not allowed
                temp = copy.deepcopy(self.chess_board)
                self._apply_move(pos, move)

                if self.in_check(self.turn):
                    bad_moves.append(move)
                self.chess_board = temp
            for move in bad_moves:
                moves.remove(move)
        return moves

    def find_possible_moves(self):
        moves = []
        pos = self.selected_segment
        if pos is not None:
            piece = self.get_selected_piece().split(":")
            if piece[0] == self.turn:
                moves.extend(self._possible_moves(pos))

        return moves

    def check_castle_allowed(self):

        for clr, row in [(0, 7), (1, 0)]:
            king_side, queen_side = self.castle_available[clr]
            color = available_colors[clr]
            if king_side:
                piece = self.get_piece((row, 7))
                if piece is None:
                    self.castle_available[clr][0] = False
                elif piece != f"{color}:rook":
                    self.castle_available[clr][0] = False

            if queen_side:
                piece = self.get_piece((row, 0))
                if piece is None:
                    self.castle_available[clr][1] = False
                elif piece != f"{color}:rook":
                    self.castle_available[clr][0] = False

            if king_side or queen_side:
                piece = self.get_piece((row, 4))
                if piece is None:
                    self.castle_available[clr][0] = False
                    self.castle_available[clr][1] = False
                elif piece != f"{color}:king":
                    self.castle_available[clr][0] = False
                    self.castle_available[clr][1] = False

    def _apply_move(self, piece_pos, pos):
        piece = self.get_piece(piece_pos)
        self.chess_board[piece_pos[0]][piece_pos[1]] = None
        self.chess_board[pos[0]][pos[1]] = piece
        piece = piece.split(":")

        # Check if moved piece is king and castle move
        if piece[1] == "king":
            row = 0
            clr = 1
            if piece[0] == "white":
                clr = 0
                row = 7
            king_side, queen_side = self.castle_available[clr]

            if king_side or queen_side:
                if pos[1] == 2:
                    self.chess_board[row][0] = None
                    self.chess_board[row][3] = f"{piece[0]}:rook"
                elif pos[1] == 6:
                    self.chess_board[row][7] = None
                    self.chess_board[row][5] = f"{piece[0]}:rook"

    def move_piece(self, pos):
        if not self.selected():
            return False, False

        possible_moves = self.find_possible_moves()
        start_pos = self.selected_segment

        moved_piece = False
        pawn_promotion = False
        if pos in possible_moves:

            moved_piece = True

            self._apply_move(start_pos, pos)
            piece = self.get_piece(pos).split(":")

            if piece[1] == "pawn":
                if piece[0] == "white":
                    pawn_promotion = (pos[0] == 0)
                else:
                    pawn_promotion = (pos[0] == 7)
            self.check_castle_allowed()

            if self.turn == "white":
                self.turn = "black"
            else:
                self.turn = "white"

        self.selected_segment = None
        return moved_piece, pawn_promotion

    def is_friendly(self, pos, side):
        pos_color = self.get_piece(pos)
        if pos_color is None:
            return None
        pos_color = pos_color.split(":")[0]
        return pos_color == side

    def is_free(self, pos):
        return self.get_piece(pos) is None

    def _is_valid_move(self, start_pos, side):
        if start_pos is None:
            return False
        if self.is_free(start_pos):
            return True
        # return not self.is_friendly()
        if not self.is_friendly(start_pos, side):
            return True
        return False

    def is_valid_move(self, pos):
        if pos is None:
            return False
        if self.is_free(pos):
            return True
        piece = self.get_selected_piece().split(":")[0]
        if not self.is_friendly(pos, piece):
            return True
        return False

    def load_data(self):
        with open("chess_info.json", "r", encoding="UTF-8") as fp:
            self.chess_info = json.load(fp)

    def save_state(self, name):
        turn = copy.deepcopy(self.turn)
        chess_board = copy.deepcopy(self.chess_board)
        checkmate = copy.deepcopy(self.checkmate)
        selected_segment = copy.deepcopy(self.selected_segment)
        castle_available = copy.deepcopy(self.castle_available)
        self.saved_state[name] = {
            "turn": turn,
            "chess_board": chess_board,
            "checkmate": checkmate,
            "selected_segment": selected_segment,
            "castle_available": castle_available,
        }

    def restore_state(self, name):
        state = self.saved_state[name]
        self.turn = state["turn"]
        self.chess_board = state["chess_board"]
        self.checkmate = state["checkmate"]
        self.selected_segment = state["selected_segment"]
        self.castle_available = state["castle_available"]

    def destroy_state(self, name):
        self.saved_state[name] = None
