from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

from core import (
    AI_DIFFICULTY_TEXT,
    AI_MEDIUM,
    APP_NAME,
    BLACK,
    BOARD_SIZE_OPTIONS,
    DEFAULT_BOARD_SIZE,
    EMPTY,
    GAME_MODE_NETWORK,
    GAME_MODE_SINGLE,
    GAME_MODE_TEXT,
    NetworkSession,
    PIECE_TEXT,
    ReversiGame,
    choose_ai_move,
    normalize_board_size,
    piece_from_label,
)


PROJECT_ROOT = Path(__file__).resolve().parent
PIC_DIR = PROJECT_ROOT / "pic"
BACKGROUND_PATH = PIC_DIR / "background.png"
BLACK_PIECE_PATH = PIC_DIR / "qizi0.png"
WHITE_PIECE_PATH = PIC_DIR / "qizi1.png"
BACKGROUND_FADE = 0.58
BOARD_PIXELS = 512
MIN_BOARD_PIXELS = 420


class ReversiApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.minsize(760, 720)

        self.game = ReversiGame(DEFAULT_BOARD_SIZE)
        self.network = NetworkSession()
        self.board_pixels = BOARD_PIXELS
        self.mode_var = tk.StringVar(value=GAME_MODE_TEXT[GAME_MODE_SINGLE])
        self.board_size_var = tk.StringVar(value=f"{DEFAULT_BOARD_SIZE} x {DEFAULT_BOARD_SIZE}")
        self.player_piece_var = tk.StringVar(value=PIECE_TEXT[BLACK])
        self.difficulty_var = tk.StringVar(value=AI_DIFFICULTY_TEXT[AI_MEDIUM])
        self.status_var = tk.StringVar()
        self.score_var = tk.StringVar()
        self.network_var = tk.StringVar(value="")
        self.background_image = None
        self.background_source = None
        self.piece_images = {}
        self.piece_image_size = None
        self.last_canvas_size = None

        self._load_background()
        self._load_piece_assets()
        self._build_ui()
        self._apply_dynamic_min_size()
        self._draw_board()
        self._refresh_status()

        if self._should_ai_move():
            self.after(350, self._ai_move)
        self.after_idle(self._redraw_after_layout)

    @property
    def cell_size(self):
        return self.board_pixels / self.game.size

    def _board_origin(self):
        if not hasattr(self, "canvas"):
            return 0, 0
        canvas_width = max(self.board_pixels, self.canvas.winfo_width())
        canvas_height = max(self.board_pixels, self.canvas.winfo_height())
        return (
            max(0, (canvas_width - self.board_pixels) / 2),
            max(0, (canvas_height - self.board_pixels) / 2),
        )

    def _load_background(self):
        if BACKGROUND_PATH.exists():
            self.background_source = Image.open(BACKGROUND_PATH).convert("RGB")
            self._refresh_background_image()

    def _refresh_background_image(self):
        if self.background_source is None:
            self.background_image = None
            return
        image = self.background_source.resize((self.board_pixels, self.board_pixels), Image.LANCZOS)
        veil = Image.new("RGB", image.size, "#edf7f1")
        image = Image.blend(image, veil, BACKGROUND_FADE)
        self.background_image = ImageTk.PhotoImage(image)

    def _load_piece_assets(self):
        piece_size = max(24, int(self.cell_size * 0.82))
        if self.piece_image_size == piece_size and self.piece_images:
            return
        self.piece_images = {}
        self.piece_image_size = piece_size
        for piece, path in {BLACK: BLACK_PIECE_PATH, self.game.opponent(BLACK): WHITE_PIECE_PATH}.items():
            if path.exists():
                image = Image.open(path).resize((piece_size, piece_size), Image.LANCZOS)
                self.piece_images[piece] = ImageTk.PhotoImage(image)

    def _build_ui(self):
        main = ttk.Frame(self, padding=14)
        main.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        main.columnconfigure(0, weight=1, minsize=MIN_BOARD_PIXELS)
        main.rowconfigure(1, weight=1, minsize=MIN_BOARD_PIXELS)

        self.main_frame = main
        self.top_bar = ttk.Frame(main)
        self.top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.top_bar.columnconfigure(0, weight=1)

        ttk.Label(self.top_bar, text=APP_NAME, font=("Microsoft YaHei UI", 16, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(self.top_bar, textvariable=self.status_var, font=("Microsoft YaHei UI", 11, "bold")).grid(
            row=1, column=0, sticky="w", pady=(4, 0)
        )
        ttk.Label(self.top_bar, textvariable=self.score_var).grid(row=2, column=0, sticky="w", pady=(4, 0))
        ttk.Label(self.top_bar, textvariable=self.network_var, foreground="#666666").grid(
            row=3, column=0, sticky="w", pady=(4, 0)
        )

        controls = ttk.Frame(self.top_bar)
        controls.grid(row=0, column=1, rowspan=4, sticky="e", padx=(24, 0))
        self._add_combo(controls, "模式", self.mode_var, list(GAME_MODE_TEXT.values()), 0, 12, self._after_mode_change)
        self._add_combo(
            controls,
            "棋盘",
            self.board_size_var,
            [f"{size} x {size}" for size in BOARD_SIZE_OPTIONS],
            1,
            8,
            self._after_board_size_change,
        )
        self._add_combo(
            controls,
            "我方棋子",
            self.player_piece_var,
            [PIECE_TEXT[BLACK], PIECE_TEXT[self.game.opponent(BLACK)]],
            2,
            8,
            self._after_player_piece_change,
        )
        self._add_combo(controls, "难度", self.difficulty_var, list(AI_DIFFICULTY_TEXT.values()), 3, 7, None)
        ttk.Button(controls, text="重新开始", command=self._restart).grid(row=1, column=4, pady=(2, 0))

        self.canvas = tk.Canvas(
            main,
            width=self.board_pixels,
            height=self.board_pixels,
            highlightthickness=0,
            bg="#edf7f1",
        )
        self.canvas.grid(row=1, column=0, sticky="nsew")
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Configure>", self._on_canvas_resize)

    def _apply_dynamic_min_size(self):
        self.update_idletasks()
        top_height = self.top_bar.winfo_reqheight()
        top_width = self.top_bar.winfo_reqwidth()
        min_width = max(760, top_width + 28, MIN_BOARD_PIXELS + 28)
        min_height = top_height + MIN_BOARD_PIXELS + 52
        self.minsize(min_width, min_height)

    def _add_combo(self, parent, label, variable, values, column, width, callback):
        ttk.Label(parent, text=label).grid(row=0, column=column, sticky="w", padx=(0, 8))
        box = ttk.Combobox(parent, textvariable=variable, values=values, width=width, state="readonly")
        box.grid(row=1, column=column, sticky="w", padx=(0, 10), pady=(2, 0))
        if callback is not None:
            box.bind("<<ComboboxSelected>>", callback)
        return box

    def _current_mode(self):
        reverse = {label: key for key, label in GAME_MODE_TEXT.items()}
        return reverse.get(self.mode_var.get(), GAME_MODE_SINGLE)

    def _current_difficulty(self):
        reverse = {label: key for key, label in AI_DIFFICULTY_TEXT.items()}
        return reverse.get(self.difficulty_var.get(), AI_MEDIUM)

    def _selected_board_size(self):
        return normalize_board_size(self.board_size_var.get().split()[0])

    def _on_canvas_resize(self, event):
        next_pixels = max(MIN_BOARD_PIXELS, min(max(event.width, 1), max(event.height, 1)))
        canvas_size = (event.width, event.height)
        size_changed = abs(next_pixels - self.board_pixels) >= 2
        canvas_changed = canvas_size != self.last_canvas_size

        if not size_changed and not canvas_changed:
            return

        self.last_canvas_size = canvas_size
        if size_changed:
            self.board_pixels = int(next_pixels)
            self._refresh_background_image()
            self._load_piece_assets()
        self._draw_board()

    def _redraw_after_layout(self):
        self.update_idletasks()
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        next_pixels = max(MIN_BOARD_PIXELS, min(width, height))
        if abs(next_pixels - self.board_pixels) >= 2:
            self.board_pixels = int(next_pixels)
            self._refresh_background_image()
            self._load_piece_assets()
        self.last_canvas_size = (width, height)
        self._draw_board()

    def _player_piece(self):
        return piece_from_label(self.player_piece_var.get(), BLACK)

    def _ai_piece(self):
        return self.game.opponent(self._player_piece())

    def _restart(self):
        self.game.reset(self._selected_board_size())
        self._load_piece_assets()
        self._draw_board()
        self._refresh_status()
        if self._should_ai_move():
            self.after(350, self._ai_move)

    def _after_board_size_change(self, _event=None):
        self._restart()

    def _after_mode_change(self, _event=None):
        self.game.reset(self._selected_board_size())
        if self._current_mode() == GAME_MODE_NETWORK:
            self.network.configure_local_piece(self._player_piece())
            self.network_var.set(self.network.last_message)
            self._refresh_status("联机模式骨架：已记录我方选棋，尚未同步远端落子。")
        else:
            self.network_var.set("")
            self._refresh_status()
        self._load_piece_assets()
        self._draw_board()
        if self._should_ai_move():
            self.after(350, self._ai_move)

    def _after_player_piece_change(self, _event=None):
        self.game.reset(self._selected_board_size())
        if self._current_mode() == GAME_MODE_NETWORK:
            self.network.configure_local_piece(self._player_piece())
            self.network_var.set(self.network.last_message)
        self._draw_board()
        self._refresh_status()
        if self._should_ai_move():
            self.after(350, self._ai_move)

    def _should_ai_move(self):
        return self._current_mode() == GAME_MODE_SINGLE and self.game.current == self._ai_piece()

    def _on_click(self, event):
        if self._should_ai_move():
            return
        if self._current_mode() == GAME_MODE_SINGLE and self.game.current != self._player_piece():
            return
        origin_x, origin_y = self._board_origin()
        board_x = event.x - origin_x
        board_y = event.y - origin_y
        if board_x < 0 or board_y < 0 or board_x >= self.board_pixels or board_y >= self.board_pixels:
            return
        row = int(board_y // self.cell_size)
        col = int(board_x // self.cell_size)
        if not self.game.in_bounds(row, col):
            return
        player = self.game.current
        if self.game.place(row, col):
            if self._current_mode() == GAME_MODE_NETWORK:
                self.network.send_move(row, col, player)
                self.network_var.set(self.network.last_message)
            self._advance_turn()

    def _advance_turn(self):
        self._draw_board()
        self._refresh_status()
        if self._handle_finished_or_pass():
            return
        if self._should_ai_move():
            self.after(350, self._ai_move)

    def _handle_finished_or_pass(self):
        if self.game.game_over():
            self._show_result()
            return True
        if not self.game.legal_moves(self.game.current):
            skipped = self.game.current
            self.game.current = self.game.opponent(self.game.current)
            self._draw_board()
            self._refresh_status(f"{PIECE_TEXT[skipped]}无子可下，自动跳过。")
            if self.game.game_over():
                self._show_result()
                return True
            if self._should_ai_move():
                self.after(350, self._ai_move)
            return True
        return False

    def _ai_move(self):
        if not self._should_ai_move() or self.game.game_over():
            return
        ai_piece = self._ai_piece()
        move = choose_ai_move(self.game, ai_piece, self._current_difficulty())
        if move is None:
            self._handle_finished_or_pass()
            return
        row, col = move
        self.game.place(row, col)
        self._advance_turn()

    def _draw_board(self):
        self.canvas.delete("all")
        size = self.cell_size
        origin_x, origin_y = self._board_origin()
        if self.background_image is not None:
            self.canvas.create_image(origin_x, origin_y, anchor="nw", image=self.background_image)
        else:
            self.canvas.create_rectangle(
                origin_x,
                origin_y,
                origin_x + self.board_pixels,
                origin_y + self.board_pixels,
                fill="#edf7f1",
                outline="",
            )
        for row in range(self.game.size):
            for col in range(self.game.size):
                x1 = origin_x + col * size
                y1 = origin_y + row * size
                self.canvas.create_rectangle(x1, y1, x1 + size, y1 + size, fill="", outline="#6f917d", width=1)
        hint_radius = max(4, int(size * 0.11))
        for row, col in self.game.legal_moves(self.game.current):
            cx = origin_x + col * size + size / 2
            cy = origin_y + row * size + size / 2
            self.canvas.create_oval(
                cx - hint_radius,
                cy - hint_radius,
                cx + hint_radius,
                cy + hint_radius,
                fill="#ffd166",
                outline="#5b3b00",
            )
        shadow_rx = size * 0.38
        shadow_ry = size * 0.32
        for row in range(self.game.size):
            for col in range(self.game.size):
                piece = self.game.board[row][col]
                if piece == 0:
                    continue
                cx = origin_x + col * size + size / 2
                cy = origin_y + row * size + size / 2
                shadow_fill = "#07100d" if piece == BLACK else "#cfeeff"
                base_fill = "#0d1b17" if piece == BLACK else "#fbfeff"
                base_outline = "#000000" if piece == BLACK else "#86c9e8"
                self.canvas.create_oval(
                    cx - shadow_rx,
                    cy - shadow_ry + 4,
                    cx + shadow_rx,
                    cy + shadow_ry + 6,
                    fill=shadow_fill,
                    outline="",
                )
                base_radius = size * 0.4
                self.canvas.create_oval(
                    cx - base_radius,
                    cy - base_radius,
                    cx + base_radius,
                    cy + base_radius,
                    fill=base_fill,
                    outline=base_outline,
                    width=2,
                )
                image = self.piece_images.get(piece)
                if image is not None:
                    self.canvas.create_image(cx, cy, image=image)

    def _refresh_status(self, note=None):
        black, white = self.game.count()
        moves = len(self.game.legal_moves(self.game.current))
        current = PIECE_TEXT[self.game.current]
        mode = self.mode_var.get()
        difficulty = self.difficulty_var.get()
        if note:
            self.status_var.set(note)
        elif self._current_mode() == GAME_MODE_SINGLE:
            player = PIECE_TEXT[self._player_piece()]
            ai = PIECE_TEXT[self._ai_piece()]
            self.status_var.set(
                f"{mode} / {self.game.size}x{self.game.size} / {difficulty}："
                f"你执{player}，电脑执{ai}；轮到{current}，可落子 {moves} 处"
            )
        elif self._current_mode() == GAME_MODE_NETWORK:
            self.status_var.set(
                f"{mode} / {self.game.size}x{self.game.size}："
                f"我方预选{PIECE_TEXT[self._player_piece()]}；轮到{current}，可落子 {moves} 处"
            )
        else:
            self.status_var.set(f"{mode} / {self.game.size}x{self.game.size}：轮到{current}，可落子 {moves} 处")
        self.score_var.set(f"{PIECE_TEXT[BLACK]} {black}  :  {PIECE_TEXT[self.game.opponent(BLACK)]} {white}")

    def _show_result(self):
        self._draw_board()
        black, white = self.game.count()
        if black > white:
            result = f"{PIECE_TEXT[BLACK]}获胜"
        elif white > black:
            result = f"{PIECE_TEXT[self.game.opponent(BLACK)]}获胜"
        else:
            result = "平局"
        self.status_var.set(f"游戏结束：{result}")
        self.score_var.set(f"{PIECE_TEXT[BLACK]} {black}  :  {PIECE_TEXT[self.game.opponent(BLACK)]} {white}")
        messagebox.showinfo("游戏结束", f"{result}\n{PIECE_TEXT[BLACK]} {black} : {PIECE_TEXT[self.game.opponent(BLACK)]} {white}")


def run_app():
    app = ReversiApp()
    app.mainloop()
