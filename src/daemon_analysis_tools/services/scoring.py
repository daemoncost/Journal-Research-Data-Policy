import os
import string
from typing import Dict, List, Set

from daemon_analysis_tools.io.yaml_base_handler import load_yaml
from daemon_analysis_tools.processing.normalizer import _normalize_series


# Function to check if all elements in a series are the same and return differences
def all_equal(series):
    series = _normalize_series(series)
    unique_values = series.dropna().unique()
    if len(unique_values) == 1:
        return True, None, None
    else:
        differing_indices = series.index[~series.duplicated(keep=False)]
        differing_values = series[~series.duplicated(keep=False)].tolist()
        return False, differing_indices, differing_values


def sentence_to_words(sentence: str) -> Set[str]:
    sentence = str(sentence)

    # Create a translation table that maps punctuation to None
    translator = str.maketrans("", "", string.punctuation)

    # Convert each string to a set of words after removing punctuation
    set_of_words = set(sentence.lower().translate(translator).split())

    return set_of_words


def jaccard_similarity(sentences: List[str]) -> float:
    """Compute the Jaccard similarity coefficient between two sentences."""
    word_sets = [sentence_to_words(s) for s in sentences]
    intersection = set.intersection(*word_sets)
    union = set.union(*word_sets)
    return len(intersection) / len(union)


# Function to check if all open text answers are similar above a threshold
def all_similar(series, threshold=0.8):
    """Check if all open-text answers are similar above a threshold."""

    series = _normalize_series(series)
    texts = series.dropna().unique()
    differing_indices = []
    differing_values = []
    for i, text1 in enumerate(texts):
        for text2 in texts[i + 1 :]:
            if jaccard_similarity(text1, text2) < threshold:
                differing_indices.extend(series.index[series == text1])
                differing_indices.extend(series.index[series == text2])
                differing_values.extend([text1, text2])
                differing_indices = list(set(differing_indices))
                differing_values = list(set(differing_values))
    if differing_indices:
        return False, differing_indices, differing_values
    return True, None, None


def assign_score(question_num, answer, multiple_choice_scores):
    if question_num in multiple_choice_scores:
        return multiple_choice_scores[question_num].get(answer, 0)
    return 0


def calculate_scores(data_duplicated, question_num_to_text, multiple_choice_scores):
    for question_num, question_text in question_num_to_text.items():
        data_duplicated[question_text + "_score"] = data_duplicated[
            question_text
        ].apply(lambda x: assign_score(question_num, x, multiple_choice_scores))
    data_duplicated["total_score"] = data_duplicated[
        [question_text + "_score" for question_text in question_num_to_text.values()]
    ].sum(axis=1)
    return data_duplicated


def normalize_scores(average_scores):
    min_score = average_scores["total_score"].min()
    max_score = average_scores["total_score"].max()
    average_scores["normalized_score"] = (average_scores["total_score"] - min_score) / (
        max_score - min_score
    )
    return average_scores


def _get_question_type_lookup(multiple_choice_scores):
    question_number_lookup = {}

    for key, value in multiple_choice_scores.items():
        question_number_lookup[value["identifier"]] = key

    return question_number_lookup


def _get_maximum_possible_score(multiple_choice_scores: Dict) -> float:
    """
    Returns the maximum score a journal can reach, which is the number of all
    multiple choice questions.

    Parameters
    ----------
    multiple_choice_scores : TYPE
        Lookup dictionary for type of question.

    Returns
    -------
    float
        Maximum possible score.

    """

    return len(list(multiple_choice_scores.keys()))


def get_question_score(
    question: str,
    answer: str,
    multiple_choice_scores: Dict,
    question_type: Dict,
    question_number_lookup: Dict,
) -> float:
    """
    Returns a numerical value the reflects how strict the RDP is on a given
    question.

    Parameters
    ----------
    question : str
        Handle text of the question.
    answer : str
        Text of the answer.
    multiple_choice_scores : Dict
        Lookup dictionary for type of question.
    question_type : Dict
        Type of question: multiple choice/text answer.
    question_number_lookup : Dict
        Lookup of which number the question is.

    Returns
    -------
    float
        Sore of a singel question. Float between 0 and 1.

    """
    if question_type[question] == "open":
        return 0.0

    answer_text = answer.correct_answer.text.lower()

    question_number = question_number_lookup[question]
    return multiple_choice_scores[question_number]["answers"][answer_text]


def get_journal_score(journal: Dict) -> float:
    """
    Returns a numerical value the reflects how strict the RDP of a journal is.

    Parameters
    ----------
    journal : dict
        Dictionary containing the rdp encoding of a specific journal.

    Returns
    -------
    float
        Score of the journal normalised by the maximum possible score.

    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "..", "metadata")

    multiple_choice_scores = load_yaml(
        os.path.join(data_dir, "question_metadata_score.yaml")
    )
    question_type = load_yaml(os.path.join(data_dir, "question_type.yaml"))
    question_number_lookup = _get_question_type_lookup(multiple_choice_scores)

    score_norm = _get_maximum_possible_score(multiple_choice_scores)

    score = 0
    for question, answer in journal.items():
        score += get_question_score(
            question,
            answer,
            multiple_choice_scores,
            question_type,
            question_number_lookup,
        )

    return score / score_norm
