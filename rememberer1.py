import tkinter as tk
from tkinter import messagebox
import random
import time
import math
from pathlib import Path
from datetime import datetime


# =========================================================
# 1단계 기억력 게임 - GUI 버전
# =========================================================

MIN_ITEMS = 2
MAX_ITEMS = 12

DEFAULT_ROUNDS = 10
MIN_ROUNDS = 1
MAX_ROUNDS = 100

SHOW_TIME = 5
ANSWER_TIME = 5

# 한 문제 결과 표시 시간(ms)
RESULT_SHOW_TIME = 1200


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
    "문", "창문", "침대", "탁자"
]


# =========================================================
# 로그 파일
# =========================================================

if "__file__" in globals():
    PROJECT_DIR = Path(__file__).resolve().parent
else:
    PROJECT_DIR = Path.cwd()

LOG_FILE = PROJECT_DIR / "memory_game_log.txt"


# =========================================================
# 메인 프로그램
# =========================================================

class MemoryGame:
    def __init__(self, root):
        self.root = root

        self.root.title("1단계 기억력 게임")
        self.root.geometry("900x700")
        self.root.minsize(750, 600)

        # 게임 상태
        self.item_count = 0
        self.total_rounds = 0
        self.current_round = 0

        self.memory_items = []
        self.choices = []

        self.selected_indices = set()
        self.choice_buttons = []

        self.round_results = []

        # 타이머 관련
        self.timer_job = None
        self.deadline = None
        self.answer_submitted = False

        # 화면 전체를 담는 프레임
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=30
        )

        self.show_start_screen()


    # =====================================================
    # 기본 화면 관리
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

        title = tk.Label(
            self.main_frame,
            text="1단계 기억력 게임",
            font=("맑은 고딕", 28, "bold")
        )
        title.pack(pady=(40, 30))

        description = tk.Label(
            self.main_frame,
            text=(
                "잠시 나타나는 단어들을 기억한 뒤\n"
                "방금 보았던 단어를 모두 찾아보세요."
            ),
            font=("맑은 고딕", 14),
            justify="center"
        )
        description.pack(pady=10)

        settings_frame = tk.Frame(self.main_frame)
        settings_frame.pack(pady=40)

        # 기억 개수
        item_label = tk.Label(
            settings_frame,
            text=f"기억할 단어 수 ({MIN_ITEMS}~{MAX_ITEMS})",
            font=("맑은 고딕", 13)
        )
        item_label.grid(
            row=0,
            column=0,
            padx=15,
            pady=15,
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
            pady=15
        )

        self.item_entry.insert(0, "5")

        # 플레이 횟수
        round_label = tk.Label(
            settings_frame,
            text="연속 플레이 횟수",
            font=("맑은 고딕", 13)
        )
        round_label.grid(
            row=1,
            column=0,
            padx=15,
            pady=15,
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
            pady=15
        )

        default_label = tk.Label(
            settings_frame,
            text="비워두면 10회",
            font=("맑은 고딕", 10)
        )
        default_label.grid(
            row=2,
            column=1
        )

        info = tk.Label(
            self.main_frame,
            text=(
                f"암기 시간: {SHOW_TIME}초\n"
                f"답변 시간: {ANSWER_TIME}초"
            ),
            font=("맑은 고딕", 12)
        )
        info.pack(pady=15)

        start_button = tk.Button(
            self.main_frame,
            text="게임 시작",
            font=("맑은 고딕", 16, "bold"),
            width=15,
            height=2,
            command=self.start_game
        )
        start_button.pack(pady=30)

        self.item_entry.focus_set()

        # Enter를 눌러도 시작 가능
        self.root.bind("<Return>", self.start_game_event)


    def start_game_event(self, event):
        self.start_game()


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
                f"{MIN_ITEMS}~{MAX_ITEMS} 사이로 입력하세요."
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
                f"{MIN_ROUNDS}~{MAX_ROUNDS}회 사이로 입력하세요."
            )
            return

        self.item_count = item_count
        self.total_rounds = round_count

        self.current_round = 0
        self.round_results = []

        # 게임 중에는 Enter 바인딩 제거
        self.root.unbind("<Return>")

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
            font=("맑은 고딕", 14)
        )
        top_label.pack(pady=5)

        title = tk.Label(
            self.main_frame,
            text="기억하세요!",
            font=("맑은 고딕", 26, "bold")
        )
        title.pack(pady=20)

        # 단어 표시 영역
        words_frame = tk.Frame(
            self.main_frame
        )
        words_frame.pack(
            expand=True,
            pady=20
        )

        # 3열로 표시
        columns = 3

        for index, item in enumerate(
            self.memory_items
        ):
            row = index // columns
            column = index % columns

            label = tk.Label(
                words_frame,
                text=item,
                font=("맑은 고딕", 20),
                width=15,
                height=2,
                relief="groove"
            )

            label.grid(
                row=row,
                column=column,
                padx=10,
                pady=10
            )

        self.timer_label = tk.Label(
            self.main_frame,
            text="",
            font=("맑은 고딕", 15, "bold")
        )
        self.timer_label.pack(pady=20)

        self.deadline = (
            time.monotonic() + SHOW_TIME
        )

        self.update_memory_timer()


    def update_memory_timer(self):
        remaining = (
            self.deadline - time.monotonic()
        )

        if remaining <= 0:
            self.timer_label.config(
                text="0초"
            )

            self.timer_job = None

            self.show_choice_screen()
            return

        seconds = math.ceil(remaining)

        self.timer_label.config(
            text=f"{seconds}초"
        )

        self.timer_job = self.root.after(
            100,
            self.update_memory_timer
        )


    # =====================================================
    # 선택지 화면
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
            self.memory_items + wrong_items
        )

        random.shuffle(self.choices)


    def show_choice_screen(self):
        self.clear_screen()

        self.make_choices()

        self.selected_indices = set()
        self.choice_buttons = []
        self.answer_submitted = False

        top_label = tk.Label(
            self.main_frame,
            text=(
                f"{self.current_round} / "
                f"{self.total_rounds}"
            ),
            font=("맑은 고딕", 14)
        )
        top_label.pack(pady=5)

        title = tk.Label(
            self.main_frame,
            text="방금 본 단어를 모두 고르세요",
            font=("맑은 고딕", 22, "bold")
        )
        title.pack(pady=10)

        self.selection_label = tk.Label(
            self.main_frame,
            text=(
                f"선택: 0 / {self.item_count}"
            ),
            font=("맑은 고딕", 13)
        )
        self.selection_label.pack(pady=5)

        choices_frame = tk.Frame(
            self.main_frame
        )
        choices_frame.pack(
            expand=True,
            pady=15
        )

        # 최대 24개까지 표시하므로 4열
        columns = 4

        for index, item in enumerate(
            self.choices
        ):
            row = index // columns
            column = index % columns

            button = tk.Button(
                choices_frame,
                text=item,
                font=("맑은 고딕", 14),
                width=14,
                height=2,
                command=lambda i=index:
                    self.toggle_choice(i)
            )

            button.grid(
                row=row,
                column=column,
                padx=7,
                pady=7
            )

            self.choice_buttons.append(
                button
            )

        bottom_frame = tk.Frame(
            self.main_frame
        )
        bottom_frame.pack(pady=15)

        self.timer_label = tk.Label(
            bottom_frame,
            text="",
            font=("맑은 고딕", 15, "bold")
        )
        self.timer_label.pack(
            side="left",
            padx=30
        )

        self.submit_button = tk.Button(
            bottom_frame,
            text="제출",
            font=("맑은 고딕", 15, "bold"),
            width=12,
            command=self.submit_answer,
            state="disabled"
        )

        self.submit_button.pack(
            side="left",
            padx=30
        )

        self.deadline = (
            time.monotonic() + ANSWER_TIME
        )

        self.update_answer_timer()


    # =====================================================
    # 답 선택
    # =====================================================

    def toggle_choice(self, index):
        if self.answer_submitted:
            return

        if index in self.selected_indices:
            # 선택 취소
            self.selected_indices.remove(
                index
            )

            self.choice_buttons[index].config(
                relief="raised"
            )

        else:
            # 정해진 개수보다 더 선택하지 못하게 함
            if (
                len(self.selected_indices)
                >= self.item_count
            ):
                return

            self.selected_indices.add(
                index
            )

            self.choice_buttons[index].config(
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

        # 정확한 개수를 선택했을 때만 제출 가능
        if selected_count == self.item_count:
            self.submit_button.config(
                state="normal"
            )
        else:
            self.submit_button.config(
                state="disabled"
            )


    # =====================================================
    # 답변 시간
    # =====================================================

    def update_answer_timer(self):
        if self.answer_submitted:
            return

        remaining = (
            self.deadline - time.monotonic()
        )

        if remaining <= 0:
            self.timer_label.config(
                text="시간 종료"
            )

            self.timer_job = None

            # 현재 선택 상태 그대로 자동 제출
            self.submit_answer(
                time_out=True
            )
            return

        seconds = math.ceil(remaining)

        self.timer_label.config(
            text=f"남은 시간: {seconds}초"
        )

        self.timer_job = self.root.after(
            100,
            self.update_answer_timer
        )


    # =====================================================
    # 채점
    # =====================================================

    def submit_answer(self, time_out=False):
        if self.answer_submitted:
            return

        # 수동 제출일 경우 정확한 개수를 골라야 함
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
            memory_set & selected_set
        )

        result = {
            "correct_count": correct_count,
            "selected_count":
                len(selected_items),
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
            text=(
                f"{self.current_round}회 결과"
            ),
            font=("맑은 고딕", 22, "bold")
        )
        title.pack(
            expand=True,
            pady=(100, 20)
        )

        result_label = tk.Label(
            self.main_frame,
            text=(
                f"{correct_count} / "
                f"{self.item_count}"
            ),
            font=("맑은 고딕", 36, "bold")
        )
        result_label.pack(pady=20)

        if correct_count == self.item_count:
            message = "완벽!"

        elif time_out:
            message = "시간 종료"

        else:
            message = ""

        message_label = tk.Label(
            self.main_frame,
            text=message,
            font=("맑은 고딕", 16)
        )
        message_label.pack(pady=10)

        if (
            self.current_round
            < self.total_rounds
        ):
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
    # 게임 종료
    # =====================================================

    def finish_game(self):
        self.clear_screen()

        total_correct = sum(
            result["correct_count"]
            for result in self.round_results
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
            for result in self.round_results
            if (
                result["correct_count"]
                == self.item_count
            )
        )

        timeout_rounds = sum(
            1
            for result in self.round_results
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
            font=("맑은 고딕", 28, "bold")
        )
        title.pack(pady=(50, 30))

        result_text = (
            f"기억 개수: {self.item_count}개\n\n"
            f"플레이 횟수: {self.total_rounds}회\n\n"
            f"총 정답: "
            f"{total_correct} / {total_possible}\n\n"
            f"전체 정답률: {accuracy:.1f}%\n\n"
            f"완벽 성공: "
            f"{perfect_rounds} / "
            f"{self.total_rounds}회\n\n"
            f"시간 초과: {timeout_rounds}회"
        )

        result_label = tk.Label(
            self.main_frame,
            text=result_text,
            font=("맑은 고딕", 16),
            justify="center"
        )
        result_label.pack(pady=20)

        score_text = ", ".join(
            f"{result['correct_count']}/"
            f"{self.item_count}"
            for result in self.round_results
        )

        rounds_label = tk.Label(
            self.main_frame,
            text=(
                "회차별 결과\n"
                + score_text
            ),
            font=("맑은 고딕", 11),
            wraplength=750,
            justify="center"
        )
        rounds_label.pack(pady=20)

        button_frame = tk.Frame(
            self.main_frame
        )
        button_frame.pack(pady=20)

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
            for result in self.round_results
        )

        log_text = (
            "\n"
            "========================================\n"
            f"날짜/시간   : "
            f"{now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"게임        : 1단계 기억력 게임\n"
            f"기억 개수   : {self.item_count}개\n"
            f"플레이 횟수 : {self.total_rounds}회\n"
            f"암기 시간   : {SHOW_TIME}초\n"
            f"답변 제한   : {ANSWER_TIME}초\n"
            f"총 정답     : "
            f"{total_correct}/{total_possible}\n"
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


# =========================================================
# 실행
# =========================================================

def main():
    root = tk.Tk()

    game = MemoryGame(root)

    root.mainloop()


if __name__ == "__main__":
    main()