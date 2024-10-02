from typing import Optional, Union

from daemon_analysis_tools.scoring import jaccard_similarity


class Answer:
    def __init__(self, text: str, explanation: str = "") -> None:
        """
        Initialize an Answer instance.

        :param text: The text of the answer.
        :param explanation: The explanation text provided by the user, if any.
        """
        self.text = text
        self.explanation = explanation

    def __repr__(self) -> str:
        return f"Answer(text={self.text}, explanation={self.explanation})"


class Question:
    def __init__(self, text: str, is_open: Optional[bool] = False) -> None:
        """
        Initialize a Question instance.

        :param text: The text of the question.
        :param is_open: Whether the question admits open-text answers or not.
        """
        self.text = text
        self.answers = []
        self.is_open = is_open
        self.correct_answer = None
        self.correct_answer_encoder_id = None
        self.discrepancy_reason = None

    def add_answer(self, answer: str, explanation: str = "") -> None:
        """
        Add an answer given by a respondent, along with an optional explanation.

        :param answer: The answer given by a respondent.
        :param explanation: The explanation text provided by the user, if any.
        """
        self.answers.append(Answer(answer, explanation))

    def has_discrepancies(self) -> bool:
        """
        Check if there are discrepancies in the answers.

        :return: True if there are discrepancies, False otherwise.
        """
        answer_texts = [answer.text for answer in self.answers]
        if not self.is_open:
            return len(set(answer_texts)) > 1
        else:
            return jaccard_similarity(answer_texts) > 0.55

    def resolve_discrepancy(
        self,
        correct_answer: Optional[Union[str, int]] = None,
        discrepancy_reason: Optional[str] = None,
    ) -> None:
        """
        Resolve the discrepancy by choosing the correct answer.

        :param correct_answer: The correct answer to resolve the discrepancy.
        :param discrepancy_reason: The reason for the discrepancy, if any.
        Select one of Text missing
                    Language understanding
                    Difficulty in matching information and question
                    Other: free text
        """
        if self.has_discrepancies():
            if correct_answer is not None:
                if isinstance(correct_answer, str):
                    for answer in self.answers:
                        if answer.text == correct_answer:
                            self.correct_answer = answer
                            break
                elif isinstance(correct_answer, int):
                    assert 0 <= correct_answer <= len(self.answers) - 1, (
                        "If `correct_answer` in an `int`, it is must be the respondant "
                        "number as reported in `self.print_qa()`"
                    )
                    self.correct_answer_encoder_id = correct_answer
                    self.correct_answer = self.answers[correct_answer]
            else:
                raise ValueError(
                    "You must provide `correct_answer` to resolve discrepancies."
                )
            if discrepancy_reason is not None:
                print(discrepancy_reason)
                self.discrepancy_reason = discrepancy_reason
            else:
                raise ValueError(
                    "You must provide `discrepancy_reason` to resolve discrepancies."
                )
        else:
            self.correct_answer_encoder_id = 0
            self.correct_answer = self.answers[0]
            self.discrepancy_reason = discrepancy_reason

    def get_final_answer(self) -> Union[Answer, None]:
        """
        Get the final resolved answer.

        :return: The resolved Answer object.
        """
        if self.correct_answer is None:
            raise ValueError(
                "Correct answer is unknown. Resolve discrepancies, if present."
            )
        else:
            return self.correct_answer

    def print_qa(self):
        print(self.text)
        for i, a in enumerate(self.answers):
            print(f"  Resp. {i}:")
            print(f"    Answer: {a.text}")
            print(f"    Explanation: {a.explanation}")

    def __repr__(self):
        return f"Question(text={self.text}, answers={self.answers})"
