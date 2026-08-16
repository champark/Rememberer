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
# 프로젝트 디렉토리
# --------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent
LOG_FILE = PROJECT_DIR / "memory_game_log.txt"


def clear_screen():
    """
    콘솔 화면 지우기
    """
    os.system("cls" if os.name == "nt" else "clear")


def choose_item_count():
    """
    플레이어가 기억할 물건의 개수를 직접 선택한다.
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
                f"{MAX_ITEMS} 이하의 숫자를 입력하세요."
            )

        except ValueError:
            print()
            print("숫자를 입력하세요.")

        time.sleep(1.5)


def show_memory_items(memory_items):
    """
    외워야 할 물건을 일정 시간 보여준다.
    """

    clear_screen()

    print("=" * 50)
    print("                  기억하세요!")
    print("=" * 50)
    print()

    for i, item in enumerate(memory_items, start=1):
        print(f"{i:2}. {item}")

    print()
    print(f"{SHOW_TIME}초 후 사라집니다.")

    time.sleep(SHOW_TIME)

    clear_screen()


def make_choices(memory_items):
    """
    정답 물건과 가짜 물건을 섞어 선택지를 만든다.

    정답 개수만큼 오답을 추가한다.

    예:
    5개를 외우면
    정답 5 + 오답 5 = 총 10개
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


def show_choices(choices, memory_count):
    """
    선택지를 보여준다.
    """

    print("=" * 50)
    print("           방금 본 물건을 모두 고르세요")
    print("=" * 50)
    print()

    print(
        f"방금 {memory_count}개의 물건을 보았습니다."
    )

    print(
        "기억나는 물건의 번호를 "
        "공백으로 구분해서 입력하세요."
    )

    print()

    for i, item in enumerate(choices, start=1):
        print(f"{i:2}. {item}")

    print()

    print("예: 1 3 5 7")
    print()


def get_player_choices(choices, memory_count):
    """
    플레이어의 선택을 입력받는다.
    """

    while True:

        raw = input(
            f"{memory_count}개를 선택하세요: "
        ).strip()

        parts = raw.split()

        # 정확히 memory_count개를 고르게 함
        if len(parts) != memory_count:
            print()
            print(
                f"정확히 {memory_count}개의 번호를 "
                "선택해야 합니다."
            )
            print()
            continue

        try:
            numbers = [int(x) for x in parts]

        except ValueError:
            print()
            print("번호만 입력하세요.")
            print()
            continue

        # 범위 검사
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
            print("같은 번호를 두 번 선택할 수 없습니다.")
            print()
            continue

        selected_items = [
            choices[number - 1]
            for number in numbers
        ]

        return selected_items


def calculate_result(memory_items, selected_items):
    """
    결과를 계산한다.
    """

    memory_set = set(memory_items)
    selected_set = set(selected_items)

    correct_items = memory_set & selected_set

    missed_items = memory_set - selected_set

    wrong_items = selected_set - memory_set

    return {
        "correct_count": len(correct_items),
        "missed_count": len(missed_items),
        "wrong_count": len(wrong_items),

        "correct_items": sorted(correct_items),
        "missed_items": sorted(missed_items),
        "wrong_items": sorted(wrong_items)
    }


def show_result(memory_items, selected_items, result):
    """
    게임 결과를 화면에 보여준다.
    """

    clear_screen()

    total = len(memory_items)
    correct = result["correct_count"]

    accuracy = (correct / total) * 100

    print("=" * 50)
    print("                    결과")
    print("=" * 50)
    print()

    print(f"기억해야 했던 물건 : {total}개")
    print(f"맞힌 물건         : {correct}개")
    print(f"놓친 물건         : {result['missed_count']}개")
    print(f"잘못 고른 물건    : {result['wrong_count']}개")
    print(f"정답률            : {accuracy:.1f}%")

    print()
    print("-" * 50)

    print()
    print("실제 정답:")
    print(", ".join(memory_items))

    print()
    print("내가 선택한 것:")
    print(", ".join(selected_items))

    if result["missed_items"]:
        print()
        print("놓친 물건:")
        print(", ".join(result["missed_items"]))

    if result["wrong_items"]:
        print()
        print("잘못 선택한 물건:")
        print(", ".join(result["wrong_items"]))

    print()

    if correct == total:
        print("완벽하게 기억했습니다!")

    elif accuracy >= 80:
        print("거의 다 기억했습니다.")

    elif accuracy >= 60:
        print("절반 이상 잘 기억했습니다.")

    else:
        print("조금 더 연습해 봅시다.")

    print()


def save_log(memory_items, selected_items, result):
    """
    게임 결과를 프로젝트 폴더의
    memory_game_log.txt 파일에 추가한다.
    """

    now = datetime.now()

    total = len(memory_items)

    correct = result["correct_count"]

    accuracy = (correct / total) * 100

    log_text = (
        "\n"
        "========================================\n"
        f"날짜/시간 : {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"게임      : 1단계 기억력 게임\n"
        f"외운 개수 : {total}개\n"
        f"맞힌 개수 : {correct}개\n"
        f"놓친 개수 : {result['missed_count']}개\n"
        f"오답 선택 : {result['wrong_count']}개\n"
        f"정답률    : {accuracy:.1f}%\n"
        f"정답 목록 : {', '.join(memory_items)}\n"
        f"선택 목록 : {', '.join(selected_items)}\n"
        "========================================\n"
    )

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(log_text)


def play_game():

    item_count = choose_item_count()

    # 외울 물건 선택
    memory_items = random.sample(
        ITEMS,
        item_count
    )

    input(
        "\nEnter를 누르면 기억하기를 시작합니다..."
    )

    # 기억 단계
    show_memory_items(memory_items)

    # 선택지 생성
    choices = make_choices(memory_items)

    # 문제 표시
    show_choices(
        choices,
        item_count
    )

    # 플레이어 입력
    selected_items = get_player_choices(
        choices,
        item_count
    )

    # 결과 계산
    result = calculate_result(
        memory_items,
        selected_items
    )

    # 결과 표시
    show_result(
        memory_items,
        selected_items,
        result
    )

    # 로그 저장
    save_log(
        memory_items,
        selected_items,
        result
    )

    print(
        f"기록이 저장되었습니다:\n"
        f"{LOG_FILE}"
    )

    print()


def main():

    while True:

        play_game()

        again = input(
            "다시 플레이하시겠습니까? (y/n): "
        ).strip().lower()

        if again != "y":
            break

    print()
    print("게임을 종료합니다.")


if __name__ == "__main__":
    main()