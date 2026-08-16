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


# --------------------------------------------
# 프로젝트 디렉토리 / 로그 파일
# --------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
LOG_FILE = PROJECT_DIR / "memory_game_log.txt"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


# ============================================
# 게임 설정
# ============================================

def choose_item_count():
    """
    기억할 물건 개수 선택
    """

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

            print()
            print(
                f"{MIN_ITEMS} 이상 "
                f"{MAX_ITEMS} 이하로 입력하세요."
            )

        except ValueError:
            print()
            print("숫자를 입력하세요.")

        time.sleep(1.5)


def choose_round_count():
    """
    연속 플레이 횟수 선택

    아무것도 입력하지 않고 Enter:
    기본값 10회
    """

    while True:
        clear_screen()

        print("=" * 50)
        print("             플레이 횟수 설정")
        print("=" * 50)
        print()

        print("몇 번 연속으로 플레이하시겠습니까?")
        print()
        print(
            f"그냥 Enter를 누르면 기본값 "
            f"{DEFAULT_ROUNDS}회입니다."
        )
        print()

        value = input(
            f"횟수 ({MIN_ROUNDS} ~ {MAX_ROUNDS}): "
        ).strip()

        # 아무것도 입력하지 않은 경우
        if value == "":
            return DEFAULT_ROUNDS

        try:
            count = int(value)

            if MIN_ROUNDS <= count <= MAX_ROUNDS:
                return count

            print()
            print(
                f"{MIN_ROUNDS} 이상 "
                f"{MAX_ROUNDS} 이하로 입력하세요."
            )

        except ValueError:
            print()
            print("숫자를 입력하세요.")

        time.sleep(1.5)


# ============================================
# 기억 단계
# ============================================

def show_memory_items(memory_items, round_number, total_rounds):
    """
    외워야 할 물건을 보여준다.
    """

    clear_screen()

    print("=" * 50)
    print(
        f"       {round_number} / {total_rounds} 회"
    )
    print("=" * 50)
    print()
    print("기억하세요!")
    print()

    for i, item in enumerate(memory_items, start=1):
        print(f"{i:2}. {item}")

    print()
    print(f"{SHOW_TIME}초 후 사라집니다.")

    time.sleep(SHOW_TIME)

    clear_screen()


# ============================================
# 선택지 생성
# ============================================

def make_choices(memory_items):
    """
    정답 물건 수만큼 오답을 추가한다.

    예:
    5개 기억
    -> 정답 5개 + 오답 5개
    -> 총 10개
    """

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
    """
    선택지 표시
    """

    print("=" * 50)
    print(
        f"       {round_number} / {total_rounds} 회"
    )
    print("=" * 50)
    print()

    print("방금 본 물건을 모두 고르세요.")
    print()

    for i, item in enumerate(choices, start=1):
        print(f"{i:2}. {item}")

    print()
    print(
        f"기억한 {memory_count}개의 번호를 "
        f"공백으로 구분해서 입력하세요."
    )
    print()
    print("예: 1 3 5 7")
    print()


# ============================================
# 플레이어 입력
# ============================================

def get_player_choices(choices, memory_count):

    while True:

        raw = input(
            f"{memory_count}개 선택: "
        ).strip()

        parts = raw.split()

        if len(parts) != memory_count:
            print()
            print(
                f"정확히 {memory_count}개의 번호를 "
                "선택해야 합니다."
            )
            print()
            continue

        try:
            numbers = [
                int(number)
                for number in parts
            ]

        except ValueError:
            print()
            print("숫자만 입력하세요.")
            print()
            continue

        # 번호 범위 검사
        if any(
            number < 1 or number > len(choices)
            for number in numbers
        ):
            print()
            print(
                f"1 ~ {len(choices)} 사이의 "
                "번호를 입력하세요."
            )
            print()
            continue

        # 중복 선택 검사
        if len(set(numbers)) != len(numbers):
            print()
            print(
                "같은 번호를 두 번 선택할 수 없습니다."
            )
            print()
            continue

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
# 한 판 결과 표시
# ============================================

def show_round_result(
    result,
    memory_count,
    round_number,
    total_rounds
):

    correct = result["correct_count"]

    accuracy = (
        correct / memory_count
    ) * 100

    print()
    print("-" * 50)

    print(
        f"{round_number}회 결과: "
        f"{correct} / {memory_count}"
    )

    print(
        f"정답률: {accuracy:.1f}%"
    )

    if correct == memory_count:
        print("완벽!")

    print("-" * 50)
    print()

    if round_number < total_rounds:
        input(
            "Enter를 누르면 다음 문제로 넘어갑니다..."
        )


# ============================================
# 전체 결과
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
    print("              최종 결과")
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
    """
    한 세션의 결과를 한꺼번에 기록한다.

    물건 이름은 저장하지 않는다.
    """

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

    # 게임 시작 설정
    item_count = choose_item_count()
    total_rounds = choose_round_count()

    round_results = []

    # 연속 플레이
    for round_number in range(
        1,
        total_rounds + 1
    ):

        clear_screen()

        print("=" * 50)
        print(
            f"       {round_number} / "
            f"{total_rounds} 회"
        )
        print("=" * 50)
        print()

        print(
            f"{item_count}개 기억하기"
        )
        print()

        input(
            "Enter를 누르면 시작합니다..."
        )

        # 이번 회차 기억 대상
        memory_items = random.sample(
            ITEMS,
            item_count
        )

        # 기억 단계
        show_memory_items(
            memory_items,
            round_number,
            total_rounds
        )

        # 선택지 생성
        choices = make_choices(
            memory_items
        )

        # 선택지 표시
        show_choices(
            choices,
            item_count,
            round_number,
            total_rounds
        )

        # 플레이어 선택
        selected_items = get_player_choices(
            choices,
            item_count
        )

        # 결과 계산
        result = calculate_result(
            memory_items,
            selected_items
        )

        round_results.append(result)

        # 이번 회차 결과
        show_round_result(
            result,
            item_count,
            round_number,
            total_rounds
        )

    # 전체 결과
    show_final_result(
        item_count,
        round_results
    )

    # 로그 기록
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