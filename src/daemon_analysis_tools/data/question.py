from typing import Union, Optional
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
    def __init__(self, question_text: str, is_open: Optional[bool] = False) -> None:
        """
        Initialize a Question instance.

        :param question_text: The text of the question.
        :param is_open: Whether the question admits open-text answers or not.
        """
        self.question_text = question_text
        self.answers = []
        self.is_open = is_open
        self.correct_answer = None

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

    def resolve_discrepancy(self, correct_answer: Optional[str] = None) -> None:
        """
        Resolve the discrepancy by choosing the correct answer.

        :param correct_answer: The correct answer to resolve the discrepancy.
        """
        if self.has_discrepancies():
            for answer in self.answers:
                if answer.text == correct_answer:
                    self.correct_answer = answer
                    break
            if len(self.answers) > 1:
                print(
                    (
                        "Warning: the correct answer is not among "
                        "those given by the respondents."
                    )
                )
                self.correct_answer = Answer(correct_answer, "Read again the RDP")
        else:
            self.correct_answer = self.answers[0]

    def get_final_answer(self) -> Union[Answer, None]:
        """
        Get the final resolved answer.

        :return: The resolved Answer object.
        """
        return self.correct_answer

    def print_qa(self):
        print(self.question_text)
        for i, a in enumerate(self.answers):
            print(f"  Resp. {i}:")
            print(f"    Answer: {a.text}")
            print(f"    Explanation: {a.explanation}")

    def __repr__(self):
        return f"Question(question_text={self.question_text}, answers={self.answers})"
