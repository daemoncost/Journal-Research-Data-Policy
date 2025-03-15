from typing import List, Optional

from daemon_analysis_tools.services.scoring import jaccard_similarity


class Answer:
    """A class representing an answer with an optional explanation."""

    def __init__(self, text: str, explanation: str = "") -> None:
        """Initialize an Answer instance.

        :param text: The text of the answer.
        :param explanation: The explanation text provided by the respondent (optional).
        """
        self.text: str = text
        self.explanation: str = explanation

    def __repr__(self) -> str:
        """Return the string representation of the Answer instance.

        :return: A string representation of the Answer.
        """
        return f"Answer(\n\ttext='{self.text}',\n\texplanation={self.explanation}\n)"


class Question:
    """A class representing a question and its associated answers."""

    def __init__(self, question_id: str, text: str, is_open: bool) -> None:
        """Initialize a Question instance.

        :param question_id: Unique identifier of the question.
        :param text: The text of the question.
        :param is_open: Flag indicating whether the question accepts open-text answers.
        """

<<<<<<< HEAD
        self.question_id: str = question_id
        self.text: str = text
        self.is_open: bool = is_open
        self.answers: List[Answer] = []
        self.correct_answer: Optional[Answer] = None
        self.correct_answer_encoder_id: Optional[int] = None
        self.discrepancy_reason: Optional[str] = None

    def _set_correct_answer(
        self, correct_answer: Answer, reason: Optional[str] = None, encoder_id: Optional[int] = None
    ) -> None:
        """Set the correct answer after resolving discrepancies.

        :param correct_answer: The correct Answer object.
        :param reason: The reason for choosing this answer.
        :param encoder_id: An optional identifier for the correct answer encoder.
        """
        self.correct_answer = correct_answer
        self.correct_answer_encoder_id = encoder_id
        self.discrepancy_reason = reason

    def _add_answer(self, answer: str, explanation: str = "") -> None:
        """Add a respondent's answer along with an optional explanation.

        :param answer: The answer provided by a respondent.
        :param explanation: Additional explanation text provided by the respondent
            (optional).
        """
        self.answers.append(Answer(answer, explanation))

    def has_discrepancies(self) -> bool:
        """Determine whether discrepancies exist among the answers.

        If the question is not open-text, discrepancies exist if there is more than one
        unique answer. For open-text questions, a jaccard similarity threshold is used.

        :return: True if discrepancies exist; otherwise, False.
        """
        if self.discrepancy_reason is not None:
            return True

        if len(self.answers) < 2:
            print("Warning: This question has a single answer")

        answer_texts: List[str] = [answer.text for answer in self.answers]
        if not self.is_open:
            return len(set(answer_texts)) > 1
        else:
<<<<<<< HEAD
            return jaccard_similarity(answer_texts) > 0.55

    def get_final_answer(self) -> Answer:
        """Retrieve the final resolved answer.

        :return: The resolved Answer object.
        :raises ValueError: If the correct answer has not been determined.
        """
        if self.correct_answer is None:
            raise ValueError(
                "Correct answer is unknown. Resolve discrepancies, if present."
            )
        return self.correct_answer

    def print_qa(self) -> None:
        """Print the question along with each of the respondent's answers and
        explanations."""
        print(self.text)
        for i, answer in enumerate(self.answers):
            print(f"  Resp. {i}:")
            print(f"    Answer: {answer.text}")
            print(f"    Explanation: {answer.explanation}")

    def __repr__(self) -> str:
        """Return the string representation of the Question instance.

        :return: A string representation of the Question.
        """
<<<<<<< HEAD
        return f"Question(\n\tid='{self.question_id}'," f"\n\ttext='{self.text}',\n)"
=======
        return (
            f"Question(\n\tid='{self.question_id}',"
            f"\n\ttext='{self.text}',"
            f"\n\tis_open={self.is_open}\n)"
        )
>>>>>>> 3c89b3b... Add question_id to Question class
