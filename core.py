DEFAULT_BOARD_SIZE = 8
BOARD_SIZE_OPTIONS = (6, 8, 10, 12)
EMPTY = 0
BLACK = 1
WHITE = 2

APP_NAME = "V家翻转棋"
BLACK_PIECE_NAME = "言和棋"
WHITE_PIECE_NAME = "天依棋"

AI_EASY = "easy"
AI_MEDIUM = "medium"
AI_HARD = "hard"

AI_DIFFICULTY_TEXT = {
    AI_EASY: "简单",
    AI_MEDIUM: "中等",
    AI_HARD: "高难",
}

GAME_MODE_SINGLE = "single_player"
GAME_MODE_TWO_PLAYER = "two_player"
GAME_MODE_NETWORK = "network_placeholder"

GAME_MODE_TEXT = {
    GAME_MODE_SINGLE: "单人模式",
    GAME_MODE_TWO_PLAYER: "双人模式",
    GAME_MODE_NETWORK: "联机模式",
}

DIRECTIONS = (
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
)

PIECE_TEXT = {
    BLACK: BLACK_PIECE_NAME,
    WHITE: WHITE_PIECE_NAME,
}

BASE_POSITION_WEIGHTS = (
    (120, -35, 20, 5, 5, 20, -35, 120),
    (-35, -60, -5, -5, -5, -5, -60, -35),
    (20, -5, 15, 3, 3, 15, -5, 20),
    (5, -5, 3, 3, 3, 3, -5, 5),
    (5, -5, 3, 3, 3, 3, -5, 5),
    (20, -5, 15, 3, 3, 15, -5, 20),
    (-35, -60, -5, -5, -5, -5, -60, -35),
    (120, -35, 20, 5, 5, 20, -35, 120),
)


def normalize_board_size(size):
    try:
        size = int(size)
    except (TypeError, ValueError):
        return DEFAULT_BOARD_SIZE
    if size in BOARD_SIZE_OPTIONS:
        return size
    return DEFAULT_BOARD_SIZE


def corners(size):
    return {(0, 0), (0, size - 1), (size - 1, 0), (size - 1, size - 1)}


def corner_adjacent(size):
    return {
        (0, 0): {(0, 1), (1, 0), (1, 1)},
        (0, size - 1): {(0, size - 2), (1, size - 2), (1, size - 1)},
        (size - 1, 0): {(size - 2, 0), (size - 2, 1), (size - 1, 1)},
        (size - 1, size - 1): {
            (size - 2, size - 2),
            (size - 2, size - 1),
            (size - 1, size - 2),
        },
    }


class ReversiGame:
    def __init__(self, size=DEFAULT_BOARD_SIZE):
        self.size = normalize_board_size(size)
        self.board = [[EMPTY for _ in range(self.size)] for _ in range(self.size)]
        self.current = BLACK
        self.reset(self.size)

    def reset(self, size=None):
        if size is not None:
            self.size = normalize_board_size(size)
        self.board = [[EMPTY for _ in range(self.size)] for _ in range(self.size)]
        mid = self.size // 2
        self.board[mid - 1][mid - 1] = WHITE
        self.board[mid][mid] = WHITE
        self.board[mid - 1][mid] = BLACK
        self.board[mid][mid - 1] = BLACK
        self.current = BLACK

    def copy(self):
        copied = ReversiGame(self.size)
        copied.board = [row[:] for row in self.board]
        copied.current = self.current
        return copied

    @staticmethod
    def opponent(player):
        return WHITE if player == BLACK else BLACK

    def in_bounds(self, row, col):
        return 0 <= row < self.size and 0 <= col < self.size

    def flips_for_move(self, row, col, player):
        if not self.in_bounds(row, col) or self.board[row][col] != EMPTY:
            return []

        opponent = self.opponent(player)
        flips = []

        for row_step, col_step in DIRECTIONS:
            path = []
            next_row = row + row_step
            next_col = col + col_step

            while self.in_bounds(next_row, next_col) and self.board[next_row][next_col] == opponent:
                path.append((next_row, next_col))
                next_row += row_step
                next_col += col_step

            if (
                path
                and self.in_bounds(next_row, next_col)
                and self.board[next_row][next_col] == player
            ):
                flips.extend(path)

        return flips

    def legal_moves(self, player=None):
        player = self.current if player is None else player
        moves = {}
        for row in range(self.size):
            for col in range(self.size):
                flips = self.flips_for_move(row, col, player)
                if flips:
                    moves[(row, col)] = flips
        return moves

    def place(self, row, col):
        flips = self.flips_for_move(row, col, self.current)
        if not flips:
            return False

        self.board[row][col] = self.current
        for flip_row, flip_col in flips:
            self.board[flip_row][flip_col] = self.current
        self.current = self.opponent(self.current)
        return True

    def count(self):
        black = sum(cell == BLACK for row in self.board for cell in row)
        white = sum(cell == WHITE for row in self.board for cell in row)
        return black, white

    def game_over(self):
        return not self.legal_moves(BLACK) and not self.legal_moves(WHITE)


class NetworkSession:
    """联机对弈占位接口，后续可替换为 socket、HTTP 或 WebSocket 实现。"""

    def __init__(self):
        self.connected = False
        self.local_piece = BLACK
        self.last_message = "联机模式骨架已建立，尚未接入真实同步。"

    def configure_local_piece(self, piece):
        self.local_piece = piece
        self.last_message = f"联机模式预选我方为{PIECE_TEXT[piece]}，等待后续接入联机同步。"

    def connect(self, endpoint):
        self.connected = False
        self.last_message = f"预留连接入口：{endpoint or '未填写地址'}。当前版本不会发起联机连接。"
        return False

    def send_move(self, row, col, player):
        self.last_message = f"预留发送落子：{PIECE_TEXT[player]} ({row + 1}, {col + 1})。"
        return False

    def poll_remote_move(self):
        self.last_message = "预留接收远端落子入口。"
        return None


def piece_from_label(label, default=BLACK):
    reverse = {value: key for key, value in PIECE_TEXT.items()}
    return reverse.get(label, default)


def normalize_difficulty(difficulty):
    if difficulty in AI_DIFFICULTY_TEXT:
        return difficulty
    return AI_MEDIUM


def empty_corners(game):
    return {corner for corner in corners(game.size) if game.board[corner[0]][corner[1]] == EMPTY}


def is_risky_corner_neighbor(game, move):
    adjacent = corner_adjacent(game.size)
    for corner in empty_corners(game):
        if move in adjacent[corner]:
            return True
    return False


def simulate_move(game, move, player):
    copied = game.copy()
    copied.current = player
    copied.place(move[0], move[1])
    return copied


def position_weight(size, row, col):
    if size == 8:
        return BASE_POSITION_WEIGHTS[row][col]

    if (row, col) in corners(size):
        return 120
    if is_adjacent_to_empty_corner_coords(size, row, col):
        return -45
    if row in {0, size - 1} or col in {0, size - 1}:
        return 22
    near_edge = row in {1, size - 2} or col in {1, size - 2}
    return -5 if near_edge else 5


def is_adjacent_to_empty_corner_coords(size, row, col):
    for adjacent in corner_adjacent(size).values():
        if (row, col) in adjacent:
            return True
    return False


def score_ai_move(game, move, flips, difficulty=AI_MEDIUM, player=WHITE):
    difficulty = normalize_difficulty(difficulty)
    row, col = move
    board_corners = corners(game.size)

    if difficulty == AI_EASY:
        return len(flips)

    score = len(flips)

    if move in board_corners:
        score += 100
    elif row in {0, game.size - 1} or col in {0, game.size - 1}:
        score += 18

    if is_risky_corner_neighbor(game, move):
        score -= 30

    if difficulty == AI_MEDIUM:
        return score

    after = simulate_move(game, move, player)
    opponent = game.opponent(player)
    opponent_moves = after.legal_moves(opponent)
    own_future_moves = after.legal_moves(player)
    opponent_corner_moves = sum(1 for candidate in opponent_moves if candidate in board_corners)

    score += position_weight(game.size, row, col)
    score += len(own_future_moves) * 3
    score -= len(opponent_moves) * 5
    score -= opponent_corner_moves * 90

    black, white = after.count()
    piece_balance = white - black if player == WHITE else black - white
    score += piece_balance

    return score


def choose_ai_move(game, player=WHITE, difficulty=AI_MEDIUM):
    moves = game.legal_moves(player)
    if not moves:
        return None
    return max(moves, key=lambda move: score_ai_move(game, move, moves[move], difficulty, player))
