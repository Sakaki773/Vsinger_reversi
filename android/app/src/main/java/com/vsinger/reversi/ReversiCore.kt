package com.vsinger.reversi

const val DEFAULT_BOARD_SIZE = 8
val BOARD_SIZE_OPTIONS = listOf(6, 8, 10, 12)

enum class Piece(val label: String) {
    EMPTY(""),
    BLACK("言和棋"),
    WHITE("天依棋");
}

enum class Difficulty(val label: String) {
    EASY("简单"),
    MEDIUM("中等"),
    HARD("高难");
}

enum class GameMode(val label: String) {
    SINGLE("单人模式"),
    TWO_PLAYER("双人模式"),
    NETWORK("联机模式");
}

data class Coord(val row: Int, val col: Int)

private val directions = listOf(
    Coord(-1, -1), Coord(-1, 0), Coord(-1, 1),
    Coord(0, -1), Coord(0, 1),
    Coord(1, -1), Coord(1, 0), Coord(1, 1),
)

private val basePositionWeights = arrayOf(
    intArrayOf(120, -35, 20, 5, 5, 20, -35, 120),
    intArrayOf(-35, -60, -5, -5, -5, -5, -60, -35),
    intArrayOf(20, -5, 15, 3, 3, 15, -5, 20),
    intArrayOf(5, -5, 3, 3, 3, 3, -5, 5),
    intArrayOf(5, -5, 3, 3, 3, 3, -5, 5),
    intArrayOf(20, -5, 15, 3, 3, 15, -5, 20),
    intArrayOf(-35, -60, -5, -5, -5, -5, -60, -35),
    intArrayOf(120, -35, 20, 5, 5, 20, -35, 120),
)

fun normalizeBoardSize(size: Int): Int {
    return if (size in BOARD_SIZE_OPTIONS) size else DEFAULT_BOARD_SIZE
}

fun opponent(piece: Piece): Piece {
    return if (piece == Piece.BLACK) Piece.WHITE else Piece.BLACK
}

fun corners(size: Int): Set<Coord> {
    return setOf(Coord(0, 0), Coord(0, size - 1), Coord(size - 1, 0), Coord(size - 1, size - 1))
}

fun cornerAdjacent(size: Int): Map<Coord, Set<Coord>> {
    return mapOf(
        Coord(0, 0) to setOf(Coord(0, 1), Coord(1, 0), Coord(1, 1)),
        Coord(0, size - 1) to setOf(Coord(0, size - 2), Coord(1, size - 2), Coord(1, size - 1)),
        Coord(size - 1, 0) to setOf(Coord(size - 2, 0), Coord(size - 2, 1), Coord(size - 1, 1)),
        Coord(size - 1, size - 1) to setOf(
            Coord(size - 2, size - 2),
            Coord(size - 2, size - 1),
            Coord(size - 1, size - 2),
        ),
    )
}

class ReversiGame(size: Int = DEFAULT_BOARD_SIZE) {
    var size: Int = normalizeBoardSize(size)
        private set
    var board: MutableList<MutableList<Piece>> = emptyBoard(this.size)
        private set
    var current: Piece = Piece.BLACK

    init {
        reset(this.size)
    }

    fun reset(nextSize: Int = size) {
        size = normalizeBoardSize(nextSize)
        board = emptyBoard(size)
        val mid = size / 2
        board[mid - 1][mid - 1] = Piece.WHITE
        board[mid][mid] = Piece.WHITE
        board[mid - 1][mid] = Piece.BLACK
        board[mid][mid - 1] = Piece.BLACK
        current = Piece.BLACK
    }

    fun copy(): ReversiGame {
        val copied = ReversiGame(size)
        copied.board = board.map { it.toMutableList() }.toMutableList()
        copied.current = current
        return copied
    }

    fun inBounds(row: Int, col: Int): Boolean {
        return row in 0 until size && col in 0 until size
    }

    fun flipsForMove(row: Int, col: Int, player: Piece): List<Coord> {
        if (!inBounds(row, col) || board[row][col] != Piece.EMPTY) {
            return emptyList()
        }

        val opponent = opponent(player)
        val flips = mutableListOf<Coord>()

        for (direction in directions) {
            val path = mutableListOf<Coord>()
            var nextRow = row + direction.row
            var nextCol = col + direction.col

            while (inBounds(nextRow, nextCol) && board[nextRow][nextCol] == opponent) {
                path.add(Coord(nextRow, nextCol))
                nextRow += direction.row
                nextCol += direction.col
            }

            if (path.isNotEmpty() && inBounds(nextRow, nextCol) && board[nextRow][nextCol] == player) {
                flips.addAll(path)
            }
        }

        return flips
    }

    fun legalMoves(player: Piece = current): Map<Coord, List<Coord>> {
        val moves = linkedMapOf<Coord, List<Coord>>()
        for (row in 0 until size) {
            for (col in 0 until size) {
                val flips = flipsForMove(row, col, player)
                if (flips.isNotEmpty()) {
                    moves[Coord(row, col)] = flips
                }
            }
        }
        return moves
    }

    fun place(row: Int, col: Int): Boolean {
        val flips = flipsForMove(row, col, current)
        if (flips.isEmpty()) {
            return false
        }
        board[row][col] = current
        for (coord in flips) {
            board[coord.row][coord.col] = current
        }
        current = opponent(current)
        return true
    }

    fun count(): Pair<Int, Int> {
        var black = 0
        var white = 0
        for (row in board) {
            for (cell in row) {
                if (cell == Piece.BLACK) black += 1
                if (cell == Piece.WHITE) white += 1
            }
        }
        return black to white
    }

    fun gameOver(): Boolean {
        return legalMoves(Piece.BLACK).isEmpty() && legalMoves(Piece.WHITE).isEmpty()
    }
}

class NetworkSession {
    var connected: Boolean = false
        private set
    var localPiece: Piece = Piece.BLACK
        private set
    var lastMessage: String = "联机模式骨架已建立，尚未接入真实同步。"
        private set

    fun configureLocalPiece(piece: Piece) {
        localPiece = piece
        lastMessage = "联机模式预选我方为${piece.label}，等待后续接入联机同步。"
    }

    fun sendMove(row: Int, col: Int, player: Piece): Boolean {
        lastMessage = "预留发送落子：${player.label} (${row + 1}, ${col + 1})。"
        return false
    }
}

private fun emptyBoard(size: Int): MutableList<MutableList<Piece>> {
    return MutableList(size) { MutableList(size) { Piece.EMPTY } }
}

private fun emptyCorners(game: ReversiGame): Set<Coord> {
    return corners(game.size).filter { game.board[it.row][it.col] == Piece.EMPTY }.toSet()
}

private fun isRiskyCornerNeighbor(game: ReversiGame, move: Coord): Boolean {
    val adjacent = cornerAdjacent(game.size)
    for (corner in emptyCorners(game)) {
        if (move in adjacent.getValue(corner)) {
            return true
        }
    }
    return false
}

private fun simulateMove(game: ReversiGame, move: Coord, player: Piece): ReversiGame {
    val copied = game.copy()
    copied.current = player
    copied.place(move.row, move.col)
    return copied
}

private fun isAdjacentToCornerCoords(size: Int, row: Int, col: Int): Boolean {
    return cornerAdjacent(size).values.any { Coord(row, col) in it }
}

private fun positionWeight(size: Int, row: Int, col: Int): Int {
    if (size == 8) {
        return basePositionWeights[row][col]
    }
    if (Coord(row, col) in corners(size)) {
        return 120
    }
    if (isAdjacentToCornerCoords(size, row, col)) {
        return -45
    }
    if (row == 0 || row == size - 1 || col == 0 || col == size - 1) {
        return 22
    }
    val nearEdge = row == 1 || row == size - 2 || col == 1 || col == size - 2
    return if (nearEdge) -5 else 5
}

private fun scoreAiMove(
    game: ReversiGame,
    move: Coord,
    flips: List<Coord>,
    difficulty: Difficulty,
    player: Piece,
): Int {
    val boardCorners = corners(game.size)
    var score = flips.size

    if (difficulty == Difficulty.EASY) {
        return score
    }

    if (move in boardCorners) {
        score += 100
    } else if (move.row == 0 || move.row == game.size - 1 || move.col == 0 || move.col == game.size - 1) {
        score += 18
    }

    if (isRiskyCornerNeighbor(game, move)) {
        score -= 30
    }

    if (difficulty == Difficulty.MEDIUM) {
        return score
    }

    val after = simulateMove(game, move, player)
    val opponent = opponent(player)
    val opponentMoves = after.legalMoves(opponent)
    val ownFutureMoves = after.legalMoves(player)
    val opponentCornerMoves = opponentMoves.keys.count { it in boardCorners }

    score += positionWeight(game.size, move.row, move.col)
    score += ownFutureMoves.size * 3
    score -= opponentMoves.size * 5
    score -= opponentCornerMoves * 90

    val (black, white) = after.count()
    val pieceBalance = if (player == Piece.WHITE) white - black else black - white
    score += pieceBalance

    return score
}

fun chooseAiMove(game: ReversiGame, player: Piece = Piece.WHITE, difficulty: Difficulty = Difficulty.MEDIUM): Coord? {
    val moves = game.legalMoves(player)
    if (moves.isEmpty()) {
        return null
    }
    return moves.maxBy { (move, flips) -> scoreAiMove(game, move, flips, difficulty, player) }.key
}
