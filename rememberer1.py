import random
import time
import os
from pathlib import Path
from datetime import datetime


# ============================================
# 1단계 기억력 게임
# ============================================

MIN_ITEMS = 2
MAX_ITEMS = 12

DEFAULT_ROUNDS = 10
MIN_ROUNDS = 1
MAX_ROUNDS = 100

SHOW_TIME = 5
ANSWER_TIME = 5

# 한 문제 결과를 보여주는 시간
RESULT_SHOW_TIME = 1.5


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


# ============================================
# 프로젝트 디렉토리 / 로그
# ============================================

PROJECT_DIR = Path(__file__).resolve().parent
LOG_FILE = PROJECT_DIR / "memory_game_log.txt"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# ============================================
# 게임 설정
# ============================================

def choose_item_count():

    while True:
        clear_screen()

        print("=" * 50)
        print("             1단계 기억력 게임")
        print("=" * 50)
        print()

        print(
            f"몇 개의 물건을 기억하시겠습니까?"
            f" ({MIN_ITEMS} ~ {MAX_ITEMS})"
        )
        print()

        value = input("개수: ").strip()

        try:
            count = int(value)

            if MIN_ITEMS <= count <= MAX_ITEMS:
                return count

        except ValueError:
            pass

        print()
        print(
            f"{MIN_ITEMS} 이상 "
            f"{MAX_ITEMS} 이하의 숫자를 입력하세요."
        )

        time.sleep(1)


def choose_round_count():

    while True:
        clear_screen()

        print("=" * 50)
        print("             플레이 횟수 설정")
        print("=" * 50)
        print()

        print("몇 번 연속으로 플레이하시겠습니까?")
        print()

        print(
            f"아무것도 입력하지 않으면 "
            f"{DEFAULT_ROUNDS}회입니다."
        )
        print()

        value = input(
            f"횟수 ({MIN_ROUNDS} ~ {MAX_ROUNDS}): "
        ).strip()

        if value == "":
            return DEFAULT_ROUNDS

        try:
            count = int(value)

            if MIN_ROUNDS <= count <= MAX_ROUNDS:
                return count

        except ValueError:
            pass

        print()
        print(
            f"{MIN_ROUNDS} 이상 "
            f"{MAX_ROUNDS} 이하의 숫자를 입력하세요."
        )

        time.sleep(1)


# ============================================
# 기억 단계
# ============================================

def show_memory_items(
    memory_items,
    round_number,
    total_rounds
):

    clear_screen()

    print("=" * 50)
    print(
        f"        {round_number} / {total_rounds} 회"
    )
    print("=" * 50)
    print()
    print("기억하세요!")
    print()

    for i, item in enumerate(
        memory_items,
        start=1
    ):
        print(f"{i:2}. {item}")

    print()
    print(
        f"{SHOW_TIME}초 후 자동으로 사라집니다."
    )

    time.sleep(SHOW_TIME)

    clear_screen()


# ============================================
# 선택지 생성
# ============================================

def make_choices(memory_items):

    memory_count = len(memory_items)

    wrong_pool = [
        item
        for item in ITEMS
        if item not in memory_items
    ]

    wrong_items = random.sample(
        wrong_pool,
        memory_count
    )

    choices = memory_items + wrong_items

    random.shuffle(choices)

    return choices


def show_choices(
    choices,
    memory_count,
    round_number,
    total_rounds
):

    clear_screen()

    print("=" * 50)
    print(
        f"        {round_number} / {total_rounds} 회"
    )
    print("=" * 50)
    print()

    print("방금 본 물건을 모두 고르세요.")
    print()

    for i, item in enumerate(
        choices,
        start=1
    ):
        print(f"{i:2}. {item}")

    print()
    print(
        f"{memory_count}개의 번호를 "
        "공백으로 구분해서 입력하세요."
    )

    print(
        f"답변 제한 시간: {ANSWER_TIME}초"
    )

    print()


# ============================================
# 플레이어 답변
# ============================================

def get_player_choices(choices, memory_count):
    """
    플레이어의 답변을 받는다.

    Enter를 누른 시점까지 걸린 시간을 측정하고,
    ANSWER_TIME을 넘겼으면 시간 초과로 처리한다.
    """

    start_time = time.time()

    raw = input("선택: ").strip()

    elapsed_time = time.time() - start_time

    # 제한시간 초과
    if elapsed_time > ANSWER_TIME:
        print()
        print(
            f"시간 종료! "
            f"({elapsed_time:.1f}초 / 제한 {ANSWER_TIME}초)"
        )
        time.sleep(0.8)
        return []

    if not raw:
        return []

    parts = raw.split()

    numbers = []

    for part in parts:

        try:
            number = int(part)

        except ValueError:
            continue

        # 유효한 번호이고 중복이 아닌 경우만 추가
        if (
            1 <= number <= len(choices)
            and number not in numbers
        ):
            numbers.append(number)

    # 필요한 개수보다 많이 입력했으면
    # 앞쪽 번호만 사용
    numbers = numbers[:memory_count]

    selected_items = [
        choices[number - 1]
        for number in numbers
    ]

    return selected_items


# ============================================
# 결과 계산
# ============================================

def calculate_result(
    memory_items,
    selected_items
):

    memory_set = set(memory_items)
    selected_set = set(selected_items)

    correct_items = (
        memory_set & selected_set
    )

    missed_items = (
        memory_set - selected_set
    )

    wrong_items = (
        selected_set - memory_set
    )

    return {
        "correct_count": len(correct_items),
        "missed_count": len(missed_items),
        "wrong_count": len(wrong_items)
    }


# ============================================
# 한 문제 결과
# ============================================

def show_round_result(
    result,
    memory_count,
    round_number,
    total_rounds
):

    clear_screen()

    correct = result["correct_count"]

    accuracy = (
        correct / memory_count
    ) * 100

    print("=" * 50)
    print(
        f"        {round_number} / {total_rounds} 회"
    )
    print("=" * 50)
    print()

    print(
        f"결과: {correct} / {memory_count}"
    )

    print(
        f"정답률: {accuracy:.1f}%"
    )

    if correct == memory_count:
        print()
        print("완벽!")

    print()
    print("다음 문제로 넘어갑니다...")

    time.sleep(RESULT_SHOW_TIME)


# ============================================
# 최종 결과
# ============================================

def show_final_result(
    item_count,
    round_results
):

    clear_screen()

    total_rounds = len(round_results)

    total_correct = sum(
        result["correct_count"]
        for result in round_results
    )

    total_questions = (
        item_count * total_rounds
    )

    accuracy = (
        total_correct / total_questions
    ) * 100

    perfect_rounds = sum(
        1
        for result in round_results
        if result["correct_count"] == item_count
    )

    print("=" * 50)
    print("               최종 결과")
    print("=" * 50)
    print()

    print(
        f"기억 개수      : {item_count}개"
    )

    print(
        f"플레이 횟수    : {total_rounds}회"
    )

    print(
        f"총 정답        : "
        f"{total_correct} / {total_questions}"
    )

    print(
        f"전체 정답률    : {accuracy:.1f}%"
    )

    print(
        f"완벽 성공      : "
        f"{perfect_rounds} / {total_rounds}회"
    )

    print()
    print("회차별 결과")
    print("-" * 30)

    for i, result in enumerate(
        round_results,
        start=1
    ):
        print(
            f"{i:2}회 : "
            f"{result['correct_count']} / "
            f"{item_count}"
        )

    print()


# ============================================
# 로그 저장
# ============================================

def save_log(
    item_count,
    round_results
):

    now = datetime.now()

    total_rounds = len(round_results)

    total_correct = sum(
        result["correct_count"]
        for result in round_results
    )

    total_questions = (
        item_count * total_rounds
    )

    accuracy = (
        total_correct / total_questions
    ) * 100

    perfect_rounds = sum(
        1
        for result in round_results
        if result["correct_count"] == item_count
    )

    round_scores = ", ".join(
        f"{result['correct_count']}/{item_count}"
        for result in round_results
    )

    log_text = (
        "\n"
        "========================================\n"
        f"날짜/시간   : "
        f"{now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"게임        : 1단계 기억력 게임\n"
        f"기억 개수   : {item_count}개\n"
        f"플레이 횟수 : {total_rounds}회\n"
        f"암기 시간   : {SHOW_TIME}초\n"
        f"답변 제한   : {ANSWER_TIME}초\n"
        f"총 정답     : "
        f"{total_correct}/{total_questions}\n"
        f"전체 정답률 : {accuracy:.1f}%\n"
        f"완벽 성공   : "
        f"{perfect_rounds}/{total_rounds}회\n"
        f"회차별 결과 : {round_scores}\n"
        "========================================\n"
    )

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(log_text)


# ============================================
# 게임 실행
# ============================================

def play_game():

    item_count = choose_item_count()
    total_rounds = choose_round_count()

    round_results = []

    # 설정 직후 바로 첫 문제 시작
    for round_number in range(
        1,
        total_rounds + 1
    ):

        memory_items = random.sample(
            ITEMS,
            item_count
        )

        # 자동으로 암기 화면 시작
        show_memory_items(
            memory_items,
            round_number,
            total_rounds
        )

        choices = make_choices(
            memory_items
        )

        show_choices(
            choices,
            item_count,
            round_number,
            total_rounds
        )

        selected_items = get_player_choices(
            choices,
            item_count
        )

        result = calculate_result(
            memory_items,
            selected_items
        )

        round_results.append(result)

        # 결과를 잠깐 보여준 뒤
        # 자동으로 다음 문제
        show_round_result(
            result,
            item_count,
            round_number,
            total_rounds
        )

    show_final_result(
        item_count,
        round_results
    )

    save_log(
        item_count,
        round_results
    )

    print(
        f"기록 저장 완료:\n{LOG_FILE}"
    )

    print()


# ============================================
# 프로그램 시작
# ============================================

def main():

    while True:

        play_game()

        again = input(
            "새 게임을 시작하시겠습니까? "
            "(y/n): "
        ).strip().lower()

        if again != "y":
            break

    print()
    print("게임을 종료합니다.")


if __name__ == "__main__":
    main()