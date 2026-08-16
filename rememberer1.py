import tkinter as tk
from tkinter import messagebox
import random
import time
from pathlib import Path
from datetime import datetime


# =========================================================
# 1단계 기억력 게임
# =========================================================

MIN_ITEMS = 2
MAX_ITEMS = 12

DEFAULT_ROUNDS = 10
MIN_ROUNDS = 1
MAX_ROUNDS = 100

MEMORY_TIME = 5

AUTO_ANSWER_EXTRA_TIME = 3
MIN_AUTO_ANSWER_TIME = 5

MIN_MANUAL_ANSWER_TIME = 1
MAX_MANUAL_ANSWER_TIME = 120

RESULT_SHOW_TIME = 1200
TIMER_UPDATE_INTERVAL = 50

# 암기 화면의 단어 크기
MEMORY_WORD_FONT_SIZE = 27

# 선택지 단어 크기
CHOICE_WORD_FONT_SIZE = 14


# =========================================================
# 프로젝트 경로 / 공용 데이터
# =========================================================

if "__file__" in globals():
    PROJECT_DIR = Path(__file__).resolve().parent
else:
    PROJECT_DIR = Path.cwd()

WORD_FILE = PROJECT_DIR / "data" / "memory_words.txt"
LOG_FILE = PROJECT_DIR / "memory_game_log.txt"


def load_word_bank():
    """
    공용 단어집을 읽는다.

    규칙:
    - UTF-8 텍스트 파일
    - 한 줄에 단어 하나
    - 빈 줄 무시
    - #으로 시작하는 줄 무시
    - 중복 단어 자동 제거
    """
    if not WORD_FILE.exists():
        raise FileNotFoundError(
            f"단어집 파일을 찾을 수 없습니다.\n\n{WORD_FILE}"
        )

    words = []
    seen = set()

    with open(WORD_FILE, "r", encoding="utf-8-sig") as file:
        for line in file:
            word = line.strip()

            if not word:
                continue

            if word.startswith("#"):
                continue

            if word in seen:
                continue

            seen.add(word)
            words.append(word)

    if len(words) < MAX_ITEMS * 2:
        raise ValueError(
            "단어집의 단어 수가 너무 적습니다.\n"
            f"최소 {MAX_ITEMS * 2}개 이상 필요하지만 "
            f"현재 {len(words)}개입니다."
        )

    return words


class MemoryGame:

    def __init__(self, root):
        self.root = root

        self.root.title("1단계 기억력 게임")
        self.root.geometry("1050x800")
        self.root.minsize(900, 700)
        self.root.configure(bg="#f4f4f4")

        try:
            self.words = load_word_bank()
        except Exception as error:
            messagebox.showerror(
                "단어집 오류",
                str(error)
            )
            self.root.destroy()
            return

        self.item_count = 0
        self.total_rounds = 0

        self.answer_time = 0
        self.answer_time_mode = "자동"

        self.current_round = 0
        self.memory_items = []
        self.choices = []

        self.selected_indices = set()
        self.choice_buttons = []

        self.round_results = []

        self.timer_job = None
        self.deadline = None
        self.answer_submitted = False

        self.main_frame = tk.Frame(
            self.root,
            bg="#f4f4f4"
        )

        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25
        )

        self.show_start_screen()


    # =====================================================
    # 화면 / 타이머 관리
    # =====================================================

    def clear_screen(self):
        self.cancel_timer()

        for widget in self.main_frame.winfo_children():
            widget.destroy()


    def cancel_timer(self):
        if self.timer_job is not None:
            try:
                self.root.after_cancel(self.timer_job)
            except Exception:
                pass

            self.timer_job = None


    # =====================================================
    # 시작 화면
    # =====================================================

    def show_start_screen(self):
        self.clear_screen()
        self.root.unbind("<Return>")

        title = tk.Label(
            self.main_frame,
            text="1단계 기억력 게임",
            font=("맑은 고딕", 30, "bold"),
            bg="#f4f4f4"
        )
        title.pack(pady=(30, 12))

        description = tk.Label(
            self.main_frame,
            text=(
                "잠시 나타나는 단어들을 기억한 뒤\n"
                "방금 보았던 단어를 모두 찾아보세요."
            ),
            font=("맑은 고딕", 14),
            justify="center",
            bg="#f4f4f4"
        )
        description.pack(pady=(0, 8))

        word_info = tk.Label(
            self.main_frame,
            text=f"공용 단어집: {len(self.words)}개 단어",
            font=("맑은 고딕", 10),
            fg="#666666",
            bg="#f4f4f4"
        )
        word_info.pack(pady=(0, 18))

        settings_frame = tk.Frame(
            self.main_frame,
            bg="#f4f4f4"
        )
        settings_frame.pack(pady=10)

        item_label = tk.Label(
            settings_frame,
            text=f"기억할 단어 수 ({MIN_ITEMS}~{MAX_ITEMS})",
            font=("맑은 고딕", 13),
            bg="#f4f4f4"
        )
        item_label.grid(
            row=0,
            column=0,
            padx=15,
            pady=12,
            sticky="e"
        )

        self.item_entry = tk.Entry(
            settings_frame,
            width=10,
            font=("맑은 고딕", 14),
            justify="center"
        )
        self.item_entry.grid(
            row=0,
            column=1,
            padx=15,
            pady=12
        )
        self.item_entry.insert(0, "5")

        round_label = tk.Label(
            settings_frame,
            text="연속 플레이 횟수",
            font=("맑은 고딕", 13),
            bg="#f4f4f4"
        )
        round_label.grid(
            row=1,
            column=0,
            padx=15,
            pady=12,
            sticky="e"
        )

        self.round_entry = tk.Entry(
            settings_frame,
            width=10,
            font=("맑은 고딕", 14),
            justify="center"
        )
        self.round_entry.grid(
            row=1,
            column=1,
            padx=15,
            pady=12
        )

        default_round_label = tk.Label(
            settings_frame,
            text="비워두면 10회",
            font=("맑은 고딕", 10),
            fg="#555555",
            bg="#f4f4f4"
        )
        default_round_label.grid(
            row=2,
            column=1,
            pady=(0, 12)
        )

        answer_title = tk.Label(
            self.main_frame,
            text="답변 시간",
            font=("맑은 고딕", 15, "bold"),
            bg="#f4f4f4"
        )
        answer_title.pack(pady=(12, 8))

        self.answer_mode_var = tk.StringVar(
            value="auto"
        )

        answer_frame = tk.Frame(
            self.main_frame,
            bg="#f4f4f4"
        )
        answer_frame.pack()

        auto_radio = tk.Radiobutton(
            answer_frame,
            text="자동",
            variable=self.answer_mode_var,
            value="auto",
            font=("맑은 고딕", 12),
            bg="#f4f4f4",
            command=self.update_answer_time_preview
        )
        auto_radio.grid(
            row=0,
            column=0,
            padx=10,
            pady=5,
            sticky="w"
        )

        self.auto_preview_label = tk.Label(
            answer_frame,
            text="",
            font=("맑은 고딕", 11),
            fg="#555555",
            bg="#f4f4f4"
        )
        self.auto_preview_label.grid(
            row=0,
            column=1,
            padx=10,
            sticky="w"
        )

        manual_radio = tk.Radiobutton(
            answer_frame,
            text="직접 지정",
            variable=self.answer_mode_var,
            value="manual",
            font=("맑은 고딕", 12),
            bg="#f4f4f4",
            command=self.update_answer_time_preview
        )
        manual_radio.grid(
            row=1,
            column=0,
            padx=10,
            pady=5,
            sticky="w"
        )

        self.manual_answer_entry = tk.Entry(
            answer_frame,
            width=8,
            font=("맑은 고딕", 12),
            justify="center"
        )
        self.manual_answer_entry.grid(
            row=1,
            column=1,
            padx=(10, 3),
            pady=5,
            sticky="w"
        )

        manual_seconds_label = tk.Label(
            answer_frame,
            text="초",
            font=("맑은 고딕", 12),
            bg="#f4f4f4"
        )
        manual_seconds_label.grid(
            row=1,
            column=2,
            sticky="w"
        )

        memory_info = tk.Label(
            self.main_frame,
            text=f"암기 시간은 항상 {MEMORY_TIME}초",
            font=("맑은 고딕", 11),
            fg="#555555",
            bg="#f4f4f4"
        )
        memory_info.pack(pady=(15, 5))

        start_button = tk.Button(
            self.main_frame,
            text="게임 시작",
            font=("맑은 고딕", 16, "bold"),
            width=15,
            height=2,
            command=self.start_game
        )
        start_button.pack(pady=22)

        self.item_entry.bind(
            "<KeyRelease>",
            self.update_answer_time_preview
        )

        self.update_answer_time_preview()
        self.item_entry.focus_set()

        self.root.bind(
            "<Return>",
            self.start_game_event
        )


    def start_game_event(self, event=None):
        self.start_game()


    def calculate_auto_answer_time(self, item_count):
        return max(
            MIN_AUTO_ANSWER_TIME,
            item_count + AUTO_ANSWER_EXTRA_TIME
        )


    def update_answer_time_preview(self, event=None):
        try:
            item_count = int(
                self.item_entry.get().strip()
            )

            if MIN_ITEMS <= item_count <= MAX_ITEMS:
                auto_time = self.calculate_auto_answer_time(
                    item_count
                )

                self.auto_preview_label.config(
                    text=f"현재 설정에서는 {auto_time}초"
                )
            else:
                self.auto_preview_label.config(text="")

        except ValueError:
            self.auto_preview_label.config(text="")


    # =====================================================
    # 설정 검증
    # =====================================================

    def start_game(self):
        try:
            item_count = int(
                self.item_entry.get().strip()
            )
        except ValueError:
            messagebox.showerror(
                "입력 오류",
                "기억할 단어 수를 숫자로 입력하세요."
            )
            return

        if not MIN_ITEMS <= item_count <= MAX_ITEMS:
            messagebox.showerror(
                "입력 오류",
                f"기억할 단어 수는 {MIN_ITEMS}~{MAX_ITEMS} 사이로 입력하세요."
            )
            return

        # 한 문제에서 정답 N개 + 오답 N개가 필요
        if len(self.words) < item_count * 2:
            messagebox.showerror(
                "단어집 부족",
                f"{item_count}개 문제에는 최소 {item_count * 2}개의 "
                f"서로 다른 단어가 필요합니다."
            )
            return

        round_text = self.round_entry.get().strip()

        if round_text == "":
            round_count = DEFAULT_ROUNDS
        else:
            try:
                round_count = int(round_text)
            except ValueError:
                messagebox.showerror(
                    "입력 오류",
                    "플레이 횟수를 숫자로 입력하세요."
                )
                return

        if not MIN_ROUNDS <= round_count <= MAX_ROUNDS:
            messagebox.showerror(
                "입력 오류",
                f"플레이 횟수는 {MIN_ROUNDS}~{MAX_ROUNDS}회로 입력하세요."
            )
            return

        answer_mode = self.answer_mode_var.get()

        if answer_mode == "auto":
            answer_time = self.calculate_auto_answer_time(
                item_count
            )
            answer_time_mode = "자동"

        else:
            manual_text = (
                self.manual_answer_entry
                .get()
                .strip()
            )

            try:
                answer_time = int(manual_text)
            except ValueError:
                messagebox.showerror(
                    "입력 오류",
                    "직접 지정할 답변 시간을 입력하세요."
                )
                return

            if not (
                MIN_MANUAL_ANSWER_TIME
                <= answer_time
                <= MAX_MANUAL_ANSWER_TIME
            ):
                messagebox.showerror(
                    "입력 오류",
                    f"답변 시간은 {MIN_MANUAL_ANSWER_TIME}~"
                    f"{MAX_MANUAL_ANSWER_TIME}초 사이로 지정하세요."
                )
                return

            answer_time_mode = "수동"

        self.item_count = item_count
        self.total_rounds = round_count
        self.answer_time = answer_time
        self.answer_time_mode = answer_time_mode

        self.current_round = 0
        self.round_results = []

        self.root.unbind("<Return>")

        self.start_next_round()


    # =====================================================
    # 문제 진행
    # =====================================================

    def start_next_round(self):
        self.current_round += 1

        self.memory_items = random.sample(
            self.words,
            self.item_count
        )

        self.show_memory_screen()


    # =====================================================
    # 진행 바
    # =====================================================

    def create_timer_bar(self, parent):
        frame = tk.Frame(
            parent,
            bg="#f4f4f4"
        )
        frame.pack(
            fill="x",
            padx=80,
            pady=(10, 22)
        )

        self.timer_text_label = tk.Label(
            frame,
            text="",
            font=("맑은 고딕", 13, "bold"),
            bg="#f4f4f4"
        )
        self.timer_text_label.pack(
            pady=(0, 7)
        )

        self.timer_canvas = tk.Canvas(
            frame,
            height=26,
            bg="#dddddd",
            highlightthickness=0
        )
        self.timer_canvas.pack(
            fill="x",
            expand=True
        )

        self.timer_canvas.update_idletasks()

        self.timer_bar_rectangle = (
            self.timer_canvas.create_rectangle(
                0,
                0,
                0,
                26,
                fill="#43a047",
                outline=""
            )
        )


    def update_timer_bar(self, remaining, total):
        if total <= 0:
            ratio = 0
        else:
            ratio = max(
                0,
                min(1, remaining / total)
            )

        width = self.timer_canvas.winfo_width()
        bar_width = width * ratio

        if ratio > 0.60:
            color = "#43a047"
        elif ratio > 0.30:
            color = "#f9a825"
        else:
            color = "#e53935"

        self.timer_canvas.coords(
            self.timer_bar_rectangle,
            0,
            0,
            bar_width,
            26
        )

        self.timer_canvas.itemconfig(
            self.timer_bar_rectangle,
            fill=color
        )

        self.timer_text_label.config(
            text=f"{max(remaining, 0):.1f}초"
        )


    # =====================================================
    # 암기 화면
    # =====================================================

    def show_memory_screen(self):
        self.clear_screen()

        top_label = tk.Label(
            self.main_frame,
            text=f"{self.current_round} / {self.total_rounds}",
            font=("맑은 고딕", 13),
            bg="#f4f4f4"
        )
        top_label.pack(pady=(5, 5))

        title = tk.Label(
            self.main_frame,
            text="기억하세요!",
            font=("맑은 고딕", 29, "bold"),
            bg="#f4f4f4"
        )
        title.pack(pady=(8, 18))

        words_frame = tk.Frame(
            self.main_frame,
            bg="#f4f4f4"
        )
        words_frame.pack(
            expand=True,
            pady=8
        )

        if self.item_count <= 4:
            columns = 2
        elif self.item_count <= 9:
            columns = 3
        else:
            columns = 4

        for index, item in enumerate(
            self.memory_items
        ):
            row = index // columns
            column = index % columns

            label = tk.Label(
                words_frame,
                text=item,
                font=(
                    "맑은 고딕",
                    MEMORY_WORD_FONT_SIZE,
                    "bold"
                ),
                width=11,
                height=2,
                relief="groove",
                bg="white"
            )

            label.grid(
                row=row,
                column=column,
                padx=11,
                pady=11,
                ipadx=5,
                ipady=4
            )

        self.create_timer_bar(
            self.main_frame
        )

        self.deadline = (
            time.monotonic()
            + MEMORY_TIME
        )

        self.update_memory_timer()


    def update_memory_timer(self):
        remaining = (
            self.deadline
            - time.monotonic()
        )

        self.update_timer_bar(
            remaining,
            MEMORY_TIME
        )

        if remaining <= 0:
            self.timer_job = None
            self.show_choice_screen()
            return

        self.timer_job = self.root.after(
            TIMER_UPDATE_INTERVAL,
            self.update_memory_timer
        )


    # =====================================================
    # 선택지
    # =====================================================

    def make_choices(self):
        memory_set = set(
            self.memory_items
        )

        wrong_pool = [
            item
            for item in self.words
            if item not in memory_set
        ]

        wrong_items = random.sample(
            wrong_pool,
            self.item_count
        )

        self.choices = (
            self.memory_items
            + wrong_items
        )

        random.shuffle(
            self.choices
        )


    def show_choice_screen(self):
        self.clear_screen()

        self.make_choices()

        self.selected_indices = set()
        self.choice_buttons = []
        self.answer_submitted = False

        top_label = tk.Label(
            self.main_frame,
            text=f"{self.current_round} / {self.total_rounds}",
            font=("맑은 고딕", 13),
            bg="#f4f4f4"
        )
        top_label.pack(pady=(4, 3))

        title = tk.Label(
            self.main_frame,
            text="방금 본 단어를 모두 고르세요",
            font=("맑은 고딕", 22, "bold"),
            bg="#f4f4f4"
        )
        title.pack(pady=(4, 5))

        self.selection_label = tk.Label(
            self.main_frame,
            text=f"선택: 0 / {self.item_count}",
            font=("맑은 고딕", 12),
            bg="#f4f4f4"
        )
        self.selection_label.pack(
            pady=(0, 7)
        )

        choices_frame = tk.Frame(
            self.main_frame,
            bg="#f4f4f4"
        )
        choices_frame.pack(
            expand=True,
            pady=3
        )

        total_choices = len(
            self.choices
        )

        if total_choices <= 8:
            columns = 2
        elif total_choices <= 16:
            columns = 4
        else:
            columns = 6

        for index, item in enumerate(
            self.choices
        ):
            row = index // columns
            column = index % columns

            button = tk.Button(
                choices_frame,
                text=item,
                font=(
                    "맑은 고딕",
                    CHOICE_WORD_FONT_SIZE
                ),
                width=12,
                height=2,
                bg="white",
                activebackground="#dddddd",
                command=lambda i=index:
                    self.toggle_choice(i)
            )

            button.grid(
                row=row,
                column=column,
                padx=6,
                pady=6
            )

            self.choice_buttons.append(
                button
            )

        self.submit_button = tk.Button(
            self.main_frame,
            text="제출",
            font=("맑은 고딕", 14, "bold"),
            width=12,
            command=self.submit_answer,
            state="disabled"
        )
        self.submit_button.pack(
            pady=(8, 4)
        )

        self.create_timer_bar(
            self.main_frame
        )

        self.deadline = (
            time.monotonic()
            + self.answer_time
        )

        self.update_answer_timer()


    def toggle_choice(self, index):
        if self.answer_submitted:
            return

        if index in self.selected_indices:
            self.selected_indices.remove(index)

            self.choice_buttons[
                index
            ].config(
                bg="white",
                relief="raised"
            )

        else:
            if (
                len(self.selected_indices)
                >= self.item_count
            ):
                return

            self.selected_indices.add(index)

            self.choice_buttons[
                index
            ].config(
                bg="#b3e5fc",
                relief="sunken"
            )

        selected_count = len(
            self.selected_indices
        )

        self.selection_label.config(
            text=(
                f"선택: {selected_count} / "
                f"{self.item_count}"
            )
        )

        if selected_count == self.item_count:
            self.submit_button.config(
                state="normal"
            )
        else:
            self.submit_button.config(
                state="disabled"
            )


    # =====================================================
    # 답변 타이머 / 채점
    # =====================================================

    def update_answer_timer(self):
        if self.answer_submitted:
            return

        remaining = (
            self.deadline
            - time.monotonic()
        )

        self.update_timer_bar(
            remaining,
            self.answer_time
        )

        if remaining <= 0:
            self.timer_job = None

            self.submit_answer(
                time_out=True
            )
            return

        self.timer_job = self.root.after(
            TIMER_UPDATE_INTERVAL,
            self.update_answer_timer
        )


    def submit_answer(self, time_out=False):
        if self.answer_submitted:
            return

        if (
            not time_out
            and len(self.selected_indices)
            != self.item_count
        ):
            return

        self.answer_submitted = True
        self.cancel_timer()

        selected_items = [
            self.choices[index]
            for index
            in self.selected_indices
        ]

        memory_set = set(
            self.memory_items
        )

        selected_set = set(
            selected_items
        )

        correct_count = len(
            memory_set & selected_set
        )

        result = {
            "correct_count": correct_count,
            "selected_count": len(selected_items),
            "time_out": time_out
        }

        self.round_results.append(
            result
        )

        self.show_round_result(
            correct_count,
            time_out
        )


    # =====================================================
    # 회차 결과
    # =====================================================

    def show_round_result(
        self,
        correct_count,
        time_out
    ):
        self.clear_screen()

        title = tk.Label(
            self.main_frame,
            text=f"{self.current_round}회 결과",
            font=("맑은 고딕", 22, "bold"),
            bg="#f4f4f4"
        )
        title.pack(
            pady=(150, 15)
        )

        result_label = tk.Label(
            self.main_frame,
            text=(
                f"{correct_count} / "
                f"{self.item_count}"
            ),
            font=("맑은 고딕", 38, "bold"),
            bg="#f4f4f4"
        )
        result_label.pack(
            pady=15
        )

        if correct_count == self.item_count:
            message = "완벽!"
        elif time_out:
            message = "시간 종료"
        else:
            message = ""

        message_label = tk.Label(
            self.main_frame,
            text=message,
            font=("맑은 고딕", 16),
            bg="#f4f4f4"
        )
        message_label.pack(pady=5)

        if self.current_round < self.total_rounds:
            self.timer_job = self.root.after(
                RESULT_SHOW_TIME,
                self.start_next_round
            )
        else:
            self.timer_job = self.root.after(
                RESULT_SHOW_TIME,
                self.finish_game
            )


    # =====================================================
    # 종료 / 로그
    # =====================================================

    def finish_game(self):
        self.clear_screen()

        total_correct = sum(
            result["correct_count"]
            for result
            in self.round_results
        )

        total_possible = (
            self.item_count
            * self.total_rounds
        )

        accuracy = (
            total_correct
            / total_possible
            * 100
        )

        perfect_rounds = sum(
            1
            for result
            in self.round_results
            if (
                result["correct_count"]
                == self.item_count
            )
        )

        timeout_rounds = sum(
            1
            for result
            in self.round_results
            if result["time_out"]
        )

        self.save_log(
            total_correct,
            total_possible,
            accuracy,
            perfect_rounds,
            timeout_rounds
        )

        title = tk.Label(
            self.main_frame,
            text="게임 종료",
            font=("맑은 고딕", 28, "bold"),
            bg="#f4f4f4"
        )
        title.pack(
            pady=(45, 25)
        )

        result_text = (
            f"기억 개수: {self.item_count}개\n\n"
            f"플레이 횟수: {self.total_rounds}회\n\n"
            f"암기 시간: {MEMORY_TIME}초\n\n"
            f"답변 시간: {self.answer_time}초 "
            f"({self.answer_time_mode})\n\n"
            f"총 정답: {total_correct} / {total_possible}\n\n"
            f"전체 정답률: {accuracy:.1f}%\n\n"
            f"완벽 성공: {perfect_rounds} / "
            f"{self.total_rounds}회\n\n"
            f"시간 초과: {timeout_rounds}회"
        )

        result_label = tk.Label(
            self.main_frame,
            text=result_text,
            font=("맑은 고딕", 15),
            justify="center",
            bg="#f4f4f4"
        )
        result_label.pack(pady=10)

        score_text = ", ".join(
            f"{result['correct_count']}/"
            f"{self.item_count}"
            for result
            in self.round_results
        )

        rounds_label = tk.Label(
            self.main_frame,
            text=(
                "회차별 결과\n"
                + score_text
            ),
            font=("맑은 고딕", 11),
            wraplength=850,
            justify="center",
            bg="#f4f4f4"
        )
        rounds_label.pack(pady=20)

        button_frame = tk.Frame(
            self.main_frame,
            bg="#f4f4f4"
        )
        button_frame.pack(pady=15)

        retry_button = tk.Button(
            button_frame,
            text="새 게임",
            font=("맑은 고딕", 14),
            width=12,
            command=self.show_start_screen
        )
        retry_button.pack(
            side="left",
            padx=15
        )

        quit_button = tk.Button(
            button_frame,
            text="종료",
            font=("맑은 고딕", 14),
            width=12,
            command=self.root.destroy
        )
        quit_button.pack(
            side="left",
            padx=15
        )


    def save_log(
        self,
        total_correct,
        total_possible,
        accuracy,
        perfect_rounds,
        timeout_rounds
    ):
        now = datetime.now()

        round_scores = ", ".join(
            f"{result['correct_count']}/"
            f"{self.item_count}"
            for result
            in self.round_results
        )

        log_text = (
            "\n"
            "========================================\n"
            f"날짜/시간   : "
            f"{now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"게임        : 1단계 기억력 게임\n"
            f"단어집      : {WORD_FILE.name}\n"
            f"단어집 크기 : {len(self.words)}개\n"
            f"기억 개수   : {self.item_count}개\n"
            f"플레이 횟수 : {self.total_rounds}회\n"
            f"암기 시간   : {MEMORY_TIME}초\n"
            f"답변 방식   : {self.answer_time_mode}\n"
            f"답변 제한   : {self.answer_time}초\n"
            f"총 정답     : {total_correct}/{total_possible}\n"
            f"전체 정답률 : {accuracy:.1f}%\n"
            f"완벽 성공   : "
            f"{perfect_rounds}/{self.total_rounds}회\n"
            f"시간 초과   : {timeout_rounds}회\n"
            f"회차별 결과 : {round_scores}\n"
            "========================================\n"
        )

        with open(
            LOG_FILE,
            "a",
            encoding="utf-8"
        ) as file:
            file.write(log_text)


def main():
    root = tk.Tk()
    MemoryGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()