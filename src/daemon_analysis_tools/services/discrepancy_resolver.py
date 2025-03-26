import numpy as np
from typing import Optional, Union

from daemon_analysis_tools.datamodels.question import Answer, Question


def _select_correct_answer(
    question: Question, correct_answer: Union[str, int]
) -> tuple[Answer, int]:
    """Select the correct answer from the available answers.

    :param question: The Question object.
    :param correct_answer: The correct answer (either text or index).
    :return: Tuple (selected Answer object, correct_index)
    """
    selected_answer = None
    correct_index = None

    if not isinstance(correct_answer, int):
        for idx, answer in enumerate(question.answers):
            if str(answer.text) == str(correct_answer):
                selected_answer = answer
                correct_index = idx
                break
    elif isinstance(correct_answer, int) and 0 <= correct_answer < len(
        question.answers
    ):
        selected_answer = question.answers[correct_answer]
        correct_index = correct_answer

    if selected_answer is None:
        raise ValueError(
            "Provided `correct_answer` does not match any available answers."
        )

    return selected_answer, correct_index


def _prompt_for_resolution(question: Question) -> tuple[int, str]:
    """Prompt the user to manually resolve discrepancies.

    :param question: The Question object.
    :return: Tuple (correct_answer_index, discrepancy_reason)
    """
    print(f"Discrepancy found in question: {question.text}")
    for idx, answer in enumerate(question.answers):
        print(f"  {idx}. {answer.text} \n {answer.explanation}")

    while True:
        try:
            correct_index = int(input("\nEnter the correct answer number: "))
            if 0 <= correct_index < len(question.answers):
                break
            else:
                print("Invalid selection. Please enter a valid index.")
        except ValueError:
            print("Please enter a number.")

    discrepancy_reason = input(
        "Enter the reason for selecting this answer: "
    ).strip()
    return correct_index, discrepancy_reason


def resolve_discrepancy(
    question: Question,
    correct_answer: Optional[Union[str, int]] = None,
    discrepancy_reason: Optional[str] = None,
    interactive: bool = False,
) -> None:
    """Resolve discrepancies in the question by selecting the correct answer.

    :param question: The Question object.
    :param correct_answer: The correct answer (string or index).
    :param discrepancy_reason: The reason for the discrepancy.
    :param interactive: If True, prompts user for input when `correct_answer` is not
        provided.
    """
    if not question.has_discrepancies():
        question._set_correct_answer(question.answers[0])
        print("No discrepancies detected.")
        return

    if interactive and correct_answer is None:
        correct_answer, discrepancy_reason = _prompt_for_resolution(question)

    selected_answer, correct_index = _select_correct_answer(
        question, correct_answer
    )

    if discrepancy_reason is None:
        raise ValueError(
            "You must provide `discrepancy_reason` to resolve discrepancies."
        )

    question._set_correct_answer(
        selected_answer, discrepancy_reason, correct_index
    )
