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

# 암기 시간은 고정
MEMORY_TIME = 5

# 자동 답변 시간:
# 기억 개수 + 아래 값
AUTO_ANSWER_EXTRA_TIME = 3

# 자동 답변 시간의 최소값
MIN_AUTO_ANSWER_TIME = 5

# 수동 답변 시간 범위
MIN_MANUAL_ANSWER_TIME = 1
MAX_MANUAL_ANSWER_TIME = 120

# 한 문제 결과를 보여주는 시간(ms)
RESULT_SHOW_TIME = 1200

# 타이머 갱신 간격(ms)
TIMER_UPDATE_INTERVAL = 50


ITEMS = [
    "사과", "열쇠", "고양이", "촛불",
    "보석", "책", "검", "장미",
    "빵", "시계", "모자", "신발",
    "컵", "나무", "별", "달",
    "물고기", "우산", "의자", "연필",
    "가방", "동전", "안경", "병",
    "망치", "공", "나비", "토끼",
    "자동차", "반지", "바나나", "포도",
    "카메라", "전화기", "기타", "숟가락",
    "포크", "접시", "자전거", "꽃",
    "개", "새", "구름", "해",
    "문", "창문", "침대", "탁자",
    "거울", "상자", "지도", "주전자",
    "수건", "비누", "벨트", "양말",
    "종", "배", "기차", "비행기"
]


# =========================================================
# 로그 파일 위치
# =========================================================

if "__file__" in globals():
    PROJECT_DIR = Path(__file__).resolve().parent
else:
    PROJECT_DIR = Path.cwd()

LOG_FILE = PROJECT_DIR / "memory_game_log.txt"


# =========================================================
# 게임 클래스
# =========================================================

class MemoryGame:

    def __init__(self, root):
        self.root = root

        self.root.title("1단계 기억력 게임")
        self.root.geometry("950x760")
        self.root.minsize(800, 650)

        # -------------------------------------------------
        # 게임 설정값
        # -------------------------------------------------

        self.item_count = 0
        self.total_rounds = 0

        self.answer_time = 0
        self.answer_time_mode = "자동"

        # -------------------------------------------------
        # 현재 게임 상태
        # -------------------------------------------------

        self.current_round = 0

        self.memory_items = []
        self.choices = []

        self.selected_indices = set()
        self.choice_buttons = []

        self.round_results = []

        # -------------------------------------------------
        # 타이머 상태
        # -------------------------------------------------

        self.timer_job = None
        self.deadline = None

        self.current_timer_duration = 0

        self.answer_submitted = False

        # -------------------------------------------------
        # 메인 화면 프레임
        # -------------------------------------------------

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

        self.root.configure(
            bg="#f4f4f4"
        )

        self.show_start_screen()


    # =====================================================
    # 공통 화면 관리
    # =====================================================

    def clear_screen(self):
        self.cancel_timer()

        for widget in self.main_frame.winfo_children():
            widget.destroy()


    def cancel_timer(self):

        if self.timer_job is not None:

            try:
                self.root.after_cancel(
                    self.timer_job
                )
            except Exception:
                pass

            self.timer_job = None


    # =====================================================
    # 시작 화면
    # =====================================================

    def show_start_screen(self):

        self.clear_screen()

        self.root.unbind("<Return>")

        # ---------------------------------------------
        # 제목
        # ---------------------------------------------

        title = tk.Label(
            self.main_frame,
            text="1단계 기억력 게임",
            font=("맑은 고딕", 28, "bold"),
            bg="#f4f4f4"
        )

        title.pack(
            pady=(35, 15)
        )

        description = tk.Label(
            self.main_frame,
            text=(
                "잠시 나타나는 단어들을 기억한 뒤\n"
                "방금 보았던 단어를 모두 찾아보세요."
            ),
            font=("맑은 고딕", 13),
            justify="center",
            bg="#f4f4f4"
        )

        description.pack(
            pady=(0, 25)
        )

        # ---------------------------------------------
        # 설정 프레임
        # ---------------------------------------------

        settings_frame = tk.Frame(
            self.main_frame,
            bg="#f4f4f4"
        )

        settings_frame.pack(
            pady=15
        )

        # ---------------------------------------------
        # 기억할 단어 수
        # ---------------------------------------------

        item_label = tk.Label(
            settings_frame,
            text=(
                f"기억할 단어 수 "
                f"({MIN_ITEMS}~{MAX_ITEMS})"
            ),
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

        self.item_entry.insert(
            0,
            "5"
        )

        # ---------------------------------------------
        # 연속 플레이 횟수
        # ---------------------------------------------

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

        # ---------------------------------------------
        # 답변 시간 설정
        # ---------------------------------------------

        answer_title = tk.Label(
            self.main_frame,
            text="답변 시간",
            font=("맑은 고딕", 15, "bold"),
            bg="#f4f4f4"
        )

        answer_title.pack(
            pady=(20, 10)
        )

        self.answer_mode_var = tk.StringVar(
            value="auto"
        )

        answer_frame = tk.Frame(
            self.main_frame,
            bg="#f4f4f4"
        )

        answer_frame.pack()

        # 자동
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

        # 직접 지정
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

        # ---------------------------------------------
        # 암기 시간 안내
        # ---------------------------------------------

        memory_info = tk.Label(
            self.main_frame,
            text=f"암기 시간은 항상 {MEMORY_TIME}초",
            font=("맑은 고딕", 11),
            fg="#555555",
            bg="#f4f4f4"
        )

        memory_info.pack(
            pady=(20, 5)
        )

        # ---------------------------------------------
        # 시작 버튼
        # ---------------------------------------------

        start_button = tk.Button(
            self.main_frame,
            text="게임 시작",
            font=("맑은 고딕", 16, "bold"),
            width=15,
            height=2,
            command=self.start_game
        )

        start_button.pack(
            pady=25
        )

        # 단어 수 변경 시 자동 시간 미리보기 갱신
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


    def start_game_event(
        self,
        event=None
    ):
        self.start_game()


    # =====================================================
    # 자동 답변 시간 계산
    # =====================================================

    def calculate_auto_answer_time(
        self,
        item_count
    ):

        return max(
            MIN_AUTO_ANSWER_TIME,
            item_count + AUTO_ANSWER_EXTRA_TIME
        )


    def update_answer_time_preview(
        self,
        event=None
    ):

        try:
            item_count = int(
                self.item_entry.get().strip()
            )

            if (
                MIN_ITEMS
                <= item_count
                <= MAX_ITEMS
            ):
                auto_time = (
                    self.calculate_auto_answer_time(
                        item_count
                    )
                )

                self.auto_preview_label.config(
                    text=(
                        f"현재 설정에서는 "
                        f"{auto_time}초"
                    )
                )

            else:
                self.auto_preview_label.config(
                    text=""
                )

        except ValueError:

            self.auto_preview_label.config(
                text=""
            )


    # =====================================================
    # 설정 검사 및 게임 시작
    # =====================================================

    def start_game(self):

        # ---------------------------------------------
        # 기억 개수
        # ---------------------------------------------

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

        if not (
            MIN_ITEMS
            <= item_count
            <= MAX_ITEMS
        ):

            messagebox.showerror(
                "입력 오류",
                (
                    f"기억할 단어 수는 "
                    f"{MIN_ITEMS}~{MAX_ITEMS} 사이로 "
                    f"입력하세요."
                )
            )

            return

        # ---------------------------------------------
        # 플레이 횟수
        # ---------------------------------------------

        round_text = (
            self.round_entry.get().strip()
        )

        if round_text == "":
            round_count = DEFAULT_ROUNDS

        else:

            try:
                round_count = int(
                    round_text
                )

            except ValueError:

                messagebox.showerror(
                    "입력 오류",
                    "플레이 횟수를 숫자로 입력하세요."
                )

                return

        if not (
            MIN_ROUNDS
            <= round_count
            <= MAX_ROUNDS
        ):

            messagebox.showerror(
                "입력 오류",
                (
                    f"플레이 횟수는 "
                    f"{MIN_ROUNDS}~{MAX_ROUNDS}회로 "
                    f"입력하세요."
                )
            )

            return

        # ---------------------------------------------
        # 답변 시간
        # ---------------------------------------------

        answer_mode = (
            self.answer_mode_var.get()
        )

        if answer_mode == "auto":

            answer_time = (
                self.calculate_auto_answer_time(
                    item_count
                )
            )

            answer_time_mode = "자동"

        else:

            manual_text = (
                self.manual_answer_entry
                .get()
                .strip()
            )

            try:
                answer_time = int(
                    manual_text
                )

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
                    (
                        f"답변 시간은 "
                        f"{MIN_MANUAL_ANSWER_TIME}~"
                        f"{MAX_MANUAL_ANSWER_TIME}초 "
                        f"사이로 지정하세요."
                    )
                )

                return

            answer_time_mode = "수동"

        # ---------------------------------------------
        # 설정 저장
        # ---------------------------------------------

        self.item_count = item_count
        self.total_rounds = round_count

        self.answer_time = answer_time
        self.answer_time_mode = (
            answer_time_mode
        )

        self.current_round = 0
        self.round_results = []

        self.root.unbind(
            "<Return>"
        )

        self.start_next_round()


    # =====================================================
    # 다음 문제
    # =====================================================

    def start_next_round(self):

        self.current_round += 1

        self.memory_items = random.sample(
            ITEMS,
            self.item_count
        )

        self.show_memory_screen()


    # =====================================================
    # 시간 바
    # =====================================================

    def create_timer_bar(
        self,
        parent
    ):

        frame = tk.Frame(
            parent,
            bg="#f4f4f4"
        )

        frame.pack(
            fill="x",
            padx=80,
            pady=(10, 25)
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
            height=24,
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
                24,
                fill="#43a047",
                outline=""
            )
        )


    def update_timer_bar(
        self,
        remaining,
        total
    ):

        if total <= 0:
            ratio = 0

        else:
            ratio = max(
                0,
                min(
                    1,
                    remaining / total
                )
            )

        width = (
            self.timer_canvas.winfo_width()
        )

        bar_width = width * ratio

        # ---------------------------------------------
        # 남은 비율에 따른 색 변경
        # ---------------------------------------------

        if ratio > 0.60:
            color = "#43a047"       # 초록

        elif ratio > 0.30:
            color = "#f9a825"       # 노랑/주황

        else:
            color = "#e53935"       # 빨강

        self.timer_canvas.coords(
            self.timer_bar_rectangle,
            0,
            0,
            bar_width,
            24
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
            text=(
                f"{self.current_round} / "
                f"{self.total_rounds}"
            ),
            font=("맑은 고딕", 13),
            bg="#f4f4f4"
        )

        top_label.pack(
            pady=(5, 5)
        )

        title = tk.Label(
            self.main_frame,
            text="기억하세요!",
            font=("맑은 고딕", 27, "bold"),
            bg="#f4f4f4"
        )

        title.pack(
            pady=(10, 20)
        )

        # ---------------------------------------------
        # 단어 영역
        # ---------------------------------------------

        words_frame = tk.Frame(
            self.main_frame,
            bg="#f4f4f4"
        )

        words_frame.pack(
            expand=True,
            pady=10
        )

        # 단어 수에 맞춰 열 개수 조절
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
                font=("맑은 고딕", 19, "bold"),
                width=13,
                height=2,
                relief="groove",
                bg="white"
            )

            label.grid(
                row=row,
                column=column,
                padx=9,
                pady=9
            )

        # ---------------------------------------------
        # 시간 바
        # ---------------------------------------------

        self.create_timer_bar(
            self.main_frame
        )

        self.current_timer_duration = (
            MEMORY_TIME
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
    # 선택지 생성
    # =====================================================

    def make_choices(self):

        wrong_pool = [
            item
            for item in ITEMS
            if item not in self.memory_items
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


    # =====================================================
    # 답변 화면
    # =====================================================

    def show_choice_screen(self):

        self.clear_screen()

        self.make_choices()

        self.selected_indices = set()
        self.choice_buttons = []

        self.answer_submitted = False

        # ---------------------------------------------
        # 회차
        # ---------------------------------------------

        top_label = tk.Label(
            self.main_frame,
            text=(
                f"{self.current_round} / "
                f"{self.total_rounds}"
            ),
            font=("맑은 고딕", 13),
            bg="#f4f4f4"
        )

        top_label.pack(
            pady=(5, 3)
        )

        # ---------------------------------------------
        # 제목
        # ---------------------------------------------

        title = tk.Label(
            self.main_frame,
            text="방금 본 단어를 모두 고르세요",
            font=("맑은 고딕", 21, "bold"),
            bg="#f4f4f4"
        )

        title.pack(
            pady=(5, 6)
        )

        self.selection_label = tk.Label(
            self.main_frame,
            text=(
                f"선택: 0 / "
                f"{self.item_count}"
            ),
            font=("맑은 고딕", 12),
            bg="#f4f4f4"
        )

        self.selection_label.pack(
            pady=(0, 8)
        )

        # ---------------------------------------------
        # 선택지 버튼
        # ---------------------------------------------

        choices_frame = tk.Frame(
            self.main_frame,
            bg="#f4f4f4"
        )

        choices_frame.pack(
            expand=True,
            pady=5
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
                font=("맑은 고딕", 13),
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

        # ---------------------------------------------
        # 제출 버튼
        # ---------------------------------------------

        self.submit_button = tk.Button(
            self.main_frame,
            text="제출",
            font=("맑은 고딕", 14, "bold"),
            width=12,
            command=self.submit_answer,
            state="disabled"
        )

        self.submit_button.pack(
            pady=(10, 5)
        )

        # ---------------------------------------------
        # 답변 시간 바
        # ---------------------------------------------

        self.create_timer_bar(
            self.main_frame
        )

        self.current_timer_duration = (
            self.answer_time
        )

        self.deadline = (
            time.monotonic()
            + self.answer_time
        )

        self.update_answer_timer()


    # =====================================================
    # 선택 버튼
    # =====================================================

    def toggle_choice(
        self,
        index
    ):

        if self.answer_submitted:
            return

        if index in self.selected_indices:

            self.selected_indices.remove(
                index
            )

            self.choice_buttons[
                index
            ].config(
                bg="white",
                relief="raised"
            )

        else:

            # 필요한 수 이상 선택 금지
            if (
                len(self.selected_indices)
                >= self.item_count
            ):
                return

            self.selected_indices.add(
                index
            )

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

        # 정확히 필요한 개수를 골라야 제출 활성화
        if (
            selected_count
            == self.item_count
        ):

            self.submit_button.config(
                state="normal"
            )

        else:

            self.submit_button.config(
                state="disabled"
            )


    # =====================================================
    # 답변 타이머
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

            # 지금까지 고른 것만으로 자동 제출
            self.submit_answer(
                time_out=True
            )

            return

        self.timer_job = self.root.after(
            TIMER_UPDATE_INTERVAL,
            self.update_answer_timer
        )


    # =====================================================
    # 답 제출
    # =====================================================

    def submit_answer(
        self,
        time_out=False
    ):

        if self.answer_submitted:
            return

        # 수동 제출은 정확히 N개 선택했을 때만 가능
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
            for index in self.selected_indices
        ]

        memory_set = set(
            self.memory_items
        )

        selected_set = set(
            selected_items
        )

        correct_count = len(
            memory_set
            & selected_set
        )

        result = {
            "correct_count":
                correct_count,

            "selected_count":
                len(selected_items),

            "time_out":
                time_out
        }

        self.round_results.append(
            result
        )

        self.show_round_result(
            correct_count,
            time_out
        )


    # =====================================================
    # 한 회차 결과
    # =====================================================

    def show_round_result(
        self,
        correct_count,
        time_out
    ):

        self.clear_screen()

        title = tk.Label(
            self.main_frame,
            text=(
                f"{self.current_round}회 결과"
            ),
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

        if (
            correct_count
            == self.item_count
        ):

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

        message_label.pack(
            pady=5
        )

        if (
            self.current_round
            < self.total_rounds
        ):

            self.timer_job = (
                self.root.after(
                    RESULT_SHOW_TIME,
                    self.start_next_round
                )
            )

        else:

            self.timer_job = (
                self.root.after(
                    RESULT_SHOW_TIME,
                    self.finish_game
                )
            )


    # =====================================================
    # 게임 종료
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

        # ---------------------------------------------
        # 결과 표시
        # ---------------------------------------------

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
            f"기억 개수: "
            f"{self.item_count}개\n\n"

            f"플레이 횟수: "
            f"{self.total_rounds}회\n\n"

            f"암기 시간: "
            f"{MEMORY_TIME}초\n\n"

            f"답변 시간: "
            f"{self.answer_time}초 "
            f"({self.answer_time_mode})\n\n"

            f"총 정답: "
            f"{total_correct} / "
            f"{total_possible}\n\n"

            f"전체 정답률: "
            f"{accuracy:.1f}%\n\n"

            f"완벽 성공: "
            f"{perfect_rounds} / "
            f"{self.total_rounds}회\n\n"

            f"시간 초과: "
            f"{timeout_rounds}회"
        )

        result_label = tk.Label(
            self.main_frame,
            text=result_text,
            font=("맑은 고딕", 15),
            justify="center",
            bg="#f4f4f4"
        )

        result_label.pack(
            pady=10
        )

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
            wraplength=800,
            justify="center",
            bg="#f4f4f4"
        )

        rounds_label.pack(
            pady=20
        )

        # ---------------------------------------------
        # 버튼
        # ---------------------------------------------

        button_frame = tk.Frame(
            self.main_frame,
            bg="#f4f4f4"
        )

        button_frame.pack(
            pady=15
        )

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


    # =====================================================
    # 로그 저장
    # =====================================================

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

            f"게임        : "
            f"1단계 기억력 게임\n"

            f"기억 개수   : "
            f"{self.item_count}개\n"

            f"플레이 횟수 : "
            f"{self.total_rounds}회\n"

            f"암기 시간   : "
            f"{MEMORY_TIME}초\n"

            f"답변 방식   : "
            f"{self.answer_time_mode}\n"

            f"답변 제한   : "
            f"{self.answer_time}초\n"

            f"총 정답     : "
            f"{total_correct}/"
            f"{total_possible}\n"

            f"전체 정답률 : "
            f"{accuracy:.1f}%\n"

            f"완벽 성공   : "
            f"{perfect_rounds}/"
            f"{self.total_rounds}회\n"

            f"시간 초과   : "
            f"{timeout_rounds}회\n"

            f"회차별 결과 : "
            f"{round_scores}\n"

            "========================================\n"
        )

        with open(
            LOG_FILE,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                log_text
            )


# =========================================================
# 프로그램 실행
# =========================================================

def main():

    root = tk.Tk()

    MemoryGame(root)

    root.mainloop()


if __name__ == "__main__":
    main()