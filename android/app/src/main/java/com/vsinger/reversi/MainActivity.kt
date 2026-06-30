package com.vsinger.reversi

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.delay

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                VsingerReversiApp()
            }
        }
    }
}

@Composable
fun VsingerReversiApp() {
    val game = remember { ReversiGame() }
    val network = remember { NetworkSession() }
    var mode by remember { mutableStateOf(GameMode.SINGLE) }
    var boardSize by remember { mutableIntStateOf(DEFAULT_BOARD_SIZE) }
    var playerPiece by remember { mutableStateOf(Piece.BLACK) }
    var difficulty by remember { mutableStateOf(Difficulty.MEDIUM) }
    var boardVersion by remember { mutableIntStateOf(0) }
    var statusNote by remember { mutableStateOf<String?>(null) }
    var networkMessage by remember { mutableStateOf("") }
    var resultMessage by remember { mutableStateOf<String?>(null) }

    fun refresh() {
        boardVersion += 1
    }

    fun aiPiece(): Piece = opponent(playerPiece)
    fun shouldAiMove(): Boolean = mode == GameMode.SINGLE && game.current == aiPiece()

    fun restart() {
        game.reset(boardSize)
        resultMessage = null
        statusNote = null
        refresh()
    }

    fun showResultIfFinished(): Boolean {
        if (!game.gameOver()) {
            return false
        }
        val (black, white) = game.count()
        val result = when {
            black > white -> "${Piece.BLACK.label}获胜"
            white > black -> "${Piece.WHITE.label}获胜"
            else -> "平局"
        }
        statusNote = "游戏结束：$result"
        resultMessage = "$result\n${Piece.BLACK.label} $black : ${Piece.WHITE.label} $white"
        refresh()
        return true
    }

    fun handleFinishedOrPass(): Boolean {
        if (showResultIfFinished()) {
            return true
        }
        if (game.legalMoves(game.current).isEmpty()) {
            val skipped = game.current
            game.current = opponent(game.current)
            statusNote = "${skipped.label}无子可下，自动跳过。"
            refresh()
            return true
        }
        return false
    }

    LaunchedEffect(boardVersion, mode, playerPiece, difficulty) {
        if (shouldAiMove() && !game.gameOver()) {
            delay(350)
            val move = chooseAiMove(game, aiPiece(), difficulty)
            if (move == null) {
                handleFinishedOrPass()
            } else {
                game.place(move.row, move.col)
                statusNote = null
                refresh()
                handleFinishedOrPass()
            }
        }
    }

    val (black, white) = game.count()
    val currentMoves = game.legalMoves(game.current)
    val status = statusNote ?: when (mode) {
        GameMode.SINGLE -> "${mode.label} / ${game.size}x${game.size} / ${difficulty.label}：你执${playerPiece.label}，电脑执${aiPiece().label}；轮到${game.current.label}，可落子 ${currentMoves.size} 处"
        GameMode.NETWORK -> "${mode.label} / ${game.size}x${game.size}：我方预选${playerPiece.label}；轮到${game.current.label}，可落子 ${currentMoves.size} 处"
        GameMode.TWO_PLAYER -> "${mode.label} / ${game.size}x${game.size}：轮到${game.current.label}，可落子 ${currentMoves.size} 处"
    }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = Color(0xFFF5F8F5),
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(14.dp),
        ) {
            Text(
                text = "V家翻转棋",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
                color = Color(0xFF20342E),
            )
            Spacer(Modifier.height(6.dp))
            Text(
                text = status,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.SemiBold,
                color = Color(0xFF223A34),
            )
            Spacer(Modifier.height(4.dp))
            Text(
                text = "${Piece.BLACK.label} $black  :  ${Piece.WHITE.label} $white",
                style = MaterialTheme.typography.bodyMedium,
                color = Color(0xFF3D4D49),
            )
            if (networkMessage.isNotEmpty()) {
                Spacer(Modifier.height(4.dp))
                Text(
                    text = networkMessage,
                    style = MaterialTheme.typography.bodySmall,
                    color = Color(0xFF687470),
                )
            }

            Spacer(Modifier.height(12.dp))
            ControlRows(
                mode = mode,
                boardSize = boardSize,
                playerPiece = playerPiece,
                difficulty = difficulty,
                onModeChange = {
                    mode = it
                    game.reset(boardSize)
                    if (mode == GameMode.NETWORK) {
                        network.configureLocalPiece(playerPiece)
                        networkMessage = network.lastMessage
                        statusNote = "联机模式骨架：已记录我方选棋，尚未同步远端落子。"
                    } else {
                        networkMessage = ""
                        statusNote = null
                    }
                    resultMessage = null
                    refresh()
                },
                onBoardSizeChange = {
                    boardSize = it
                    restart()
                },
                onPlayerPieceChange = {
                    playerPiece = it
                    game.reset(boardSize)
                    if (mode == GameMode.NETWORK) {
                        network.configureLocalPiece(playerPiece)
                        networkMessage = network.lastMessage
                    }
                    statusNote = null
                    resultMessage = null
                    refresh()
                },
                onDifficultyChange = { difficulty = it },
                onRestart = { restart() },
            )

            Spacer(Modifier.height(12.dp))
            ReversiBoard(
                game = game,
                legalMoves = currentMoves.keys,
                onCellClick = { row, col ->
                    if (shouldAiMove()) {
                        return@ReversiBoard
                    }
                    if (mode == GameMode.SINGLE && game.current != playerPiece) {
                        return@ReversiBoard
                    }
                    val player = game.current
                    if (game.place(row, col)) {
                        if (mode == GameMode.NETWORK) {
                            network.sendMove(row, col, player)
                            networkMessage = network.lastMessage
                        }
                        statusNote = null
                        refresh()
                        handleFinishedOrPass()
                    }
                },
            )
        }
    }

    if (resultMessage != null) {
        AlertDialog(
            onDismissRequest = { resultMessage = null },
            confirmButton = {
                TextButton(onClick = { resultMessage = null }) {
                    Text("确定")
                }
            },
            title = { Text("游戏结束") },
            text = { Text(resultMessage ?: "") },
        )
    }
}

@Composable
private fun ControlRows(
    mode: GameMode,
    boardSize: Int,
    playerPiece: Piece,
    difficulty: Difficulty,
    onModeChange: (GameMode) -> Unit,
    onBoardSizeChange: (Int) -> Unit,
    onPlayerPieceChange: (Piece) -> Unit,
    onDifficultyChange: (Difficulty) -> Unit,
    onRestart: () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
            OptionButton("模式", mode.label, GameMode.entries, { it.label }, onModeChange, Modifier.weight(1f))
            OptionButton("棋盘", "${boardSize} x $boardSize", BOARD_SIZE_OPTIONS, { "$it x $it" }, onBoardSizeChange, Modifier.weight(1f))
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
            OptionButton("我方棋子", playerPiece.label, listOf(Piece.BLACK, Piece.WHITE), { it.label }, onPlayerPieceChange, Modifier.weight(1f))
            OptionButton("难度", difficulty.label, Difficulty.entries, { it.label }, onDifficultyChange, Modifier.weight(1f))
        }
        Button(
            onClick = onRestart,
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF2F6554)),
            shape = RoundedCornerShape(8.dp),
        ) {
            Text("重新开始")
        }
    }
}

@Composable
private fun <T> OptionButton(
    title: String,
    value: String,
    options: List<T>,
    labelOf: (T) -> String,
    onSelect: (T) -> Unit,
    modifier: Modifier = Modifier,
) {
    var expanded by remember { mutableStateOf(false) }
    Box(modifier = modifier) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(8.dp))
                .background(Color.White)
                .border(1.dp, Color(0xFFD2DDD8), RoundedCornerShape(8.dp))
                .clickable { expanded = true }
                .padding(horizontal = 10.dp, vertical = 8.dp),
        ) {
            Text(title, style = MaterialTheme.typography.labelSmall, color = Color(0xFF66736F))
            Text(value, maxLines = 1, overflow = TextOverflow.Ellipsis, color = Color(0xFF20342E))
        }
        DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
            options.forEach { option ->
                DropdownMenuItem(
                    text = { Text(labelOf(option)) },
                    onClick = {
                        expanded = false
                        onSelect(option)
                    },
                )
            }
        }
    }
}

@Composable
private fun ReversiBoard(
    game: ReversiGame,
    legalMoves: Set<Coord>,
    onCellClick: (Int, Int) -> Unit,
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(1f)
            .clip(RoundedCornerShape(6.dp))
            .background(Color(0xFFEAF5EE)),
    ) {
        Image(
            painter = painterResource(R.drawable.background),
            contentDescription = null,
            contentScale = ContentScale.Crop,
            alpha = 0.42f,
            modifier = Modifier.fillMaxSize(),
        )
        Column(modifier = Modifier.fillMaxSize()) {
            for (row in 0 until game.size) {
                Row(modifier = Modifier.weight(1f)) {
                    for (col in 0 until game.size) {
                        BoardCell(
                            piece = game.board[row][col],
                            isHint = Coord(row, col) in legalMoves,
                            modifier = Modifier
                                .weight(1f)
                                .fillMaxSize()
                                .clickable { onCellClick(row, col) },
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun BoardCell(piece: Piece, isHint: Boolean, modifier: Modifier = Modifier) {
    Box(
        modifier = modifier.border(0.5.dp, Color(0xFF6F917D)),
        contentAlignment = Alignment.Center,
    ) {
        if (isHint) {
            Box(
                modifier = Modifier
                    .size(12.dp)
                    .clip(CircleShape)
                    .background(Color(0xFFFFD166))
                    .border(1.dp, Color(0xFF5B3B00), CircleShape),
            )
        }
        if (piece != Piece.EMPTY) {
            Canvas(modifier = Modifier.fillMaxSize()) {
                drawPieceBase(piece)
            }
            Image(
                painter = painterResource(if (piece == Piece.BLACK) R.drawable.qizi0 else R.drawable.qizi1),
                contentDescription = piece.label,
                modifier = Modifier
                    .fillMaxSize(0.82f)
                    .aspectRatio(1f),
            )
        }
    }
}

private fun DrawScope.drawPieceBase(piece: Piece) {
    val radiusX = size.width * 0.38f
    val radiusY = size.height * 0.32f
    val center = Offset(size.width / 2f, size.height / 2f + 4f)
    val color = if (piece == Piece.BLACK) Color(0xFF24342F) else Color(0xFFDCEEF8)
    drawOval(
        color = color,
        topLeft = Offset(center.x - radiusX, center.y - radiusY),
        size = Size(radiusX * 2f, radiusY * 2f),
    )
    drawOval(
        color = if (piece == Piece.BLACK) Color(0xFF121817) else Color(0xFFEAF6FB),
        topLeft = Offset(size.width * 0.12f, size.height * 0.12f),
        size = Size(size.width * 0.76f, size.height * 0.76f),
        style = Stroke(width = 2f),
    )
}
