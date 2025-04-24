from typing import Dict, Optional, Any, List
from daemon_analysis_tools.datamodels.question import Question
import pandas as pd

def flatten_grouped_questions(
    grouped_questions: Dict[str, Dict[str, Dict[str, Question]]],
    publisher_metadata: Optional[Dict[str, Dict[str, Any]]] = None,
    journal_metadata: Optional[Dict[str, Dict[str, Any]]] = None
) -> pd.DataFrame:
    """
    Build a flat DataFrame with one row per individual answer.

    :param grouped_questions: nested dict: publisher -> journal -> question_id -> Question
    :param publisher_metadata: optional mapping publisher -> metadata dict
    :param journal_metadata: optional mapping journal -> metadata dict
    :return: pd.DataFrame
    """
    rows: List[Dict[str, Any]] = []

    for publisher_name, journals in grouped_questions.items():
        pub_meta = publisher_metadata.get(publisher_name, {}) if publisher_metadata else {}

        for journal_name, questions in journals.items():
            jour_meta = journal_metadata.get(journal_name, {}) if journal_metadata else {}

            for q_id, question in questions.items():
                for resp_idx, answer in enumerate(question.answers):
                    row: Dict[str, Any] = {
                        "publisher": publisher_name,
                        **pub_meta,
                        "journal": journal_name,
                        **jour_meta,
                        "question_id": q_id,
                        "question_text": question.text,
                        "is_open": question.is_open,
                        "respondent_id": resp_idx,
                        "answer_text": answer.text,
                        "answer_explanation": answer.explanation,
                        "correct_answer_id": question.correct_answer_encoder_id,
                        "is_correct_answer": (answer is question.correct_answer),
                        "has_discrepancies": question.has_discrepancies(),
                        "discrepancy_reason": question.discrepancy_reason
                    }
                    rows.append(row)

    df = pd.DataFrame(rows)
    # Order columns for readability (customize as needed)
    cols = [
        "publisher", *sorted(pub_meta.keys()),
        "journal", *sorted(jour_meta.keys()),
        "question_id", "question_text", "is_open",
        "respondent_id", "answer_text", "answer_explanation", "answer_score",
        "correct_answer_id", "is_correct_answer",
        "has_discrepancies", "discrepancy_reason"
    ]
    # keep only existing columns
    cols = [c for c in cols if c in df.columns]
    return df[cols]
