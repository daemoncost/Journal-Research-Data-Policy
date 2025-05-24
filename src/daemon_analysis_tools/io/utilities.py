from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, MutableMapping, Optional

import numpy as np
import pandas as pd
import yaml
from rapidfuzz import fuzz, process

from daemon_analysis_tools.datamodels.question import Question


def _read_yaml(path: Optional[Path | str]) -> Dict[str, Any]:
    """Load *one* YAML document. Return {} if path is None or file is missing."""
    if path is None:
        return {}
    p = Path(path)
    if not p.exists():
        print(f"[warning] metadata file not found → {p}")
        return {}
    with p.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, Mapping):
        raise yaml.YAMLError(f"Top level of {p} must be a mapping.")
    return dict(data)  # make it mutable


def _read_single_layer_metadata(
    path: Optional[Path | str],
) -> Dict[str, Dict[str, Any]]:
    """
    Format: <key>: {prop: value, …}
    Example keys → publisher names, journal names, question_id.
    """
    return _read_yaml(path)


def _read_double_layer_metadata(
    path: Optional[Path | str],
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Format:
        <question_id>:
            <answer_text>:
                prop: value
    """
    return _read_yaml(path)


def _create_table_from_grouped_questions(
    grouped_questions: Dict[str, Dict[str, Dict[str, Question]]]
) -> pd.DataFrame:
    """
    Flatten publisher → journal → Question into one row per question.

    Added column
    ------------
    num_encoders : int
        Number of individual answers recorded for this question
        (i.e. ``len(question.answers)``).
    """
    rows: List[Dict[str, Any]] = []

    for publisher, journals in grouped_questions.items():
        for journal, questions in journals.items():
            for q_id, q in questions.items():
                rows.append(
                    {
                        "publisher": publisher,
                        "journal": journal,
                        "question_id": q_id,
                        "question_text": q.text,
                        "has_discrepancy": q.has_discrepancies(),
                        "discrepancy_reason": q.discrepancy_reason,
                        "final_answer": (
                            q.correct_answer.text if q.correct_answer else None
                        ),
                        "num_encoders": len(q.answers),
                    }
                )

    return pd.DataFrame(rows)


def _merge_single_layer(
    df: pd.DataFrame, metadata: Dict[str, Dict[str, Any]], key: str
) -> pd.DataFrame:
    """Left-join single-layer metadata onto *df* using *key* column."""
    if not metadata:
        return df

    meta_df = pd.DataFrame.from_dict(metadata, orient="index")
    meta_df.index.name = key
    merged = df.merge(meta_df, left_on=key, right_index=True, how="left")
    return merged


def _normalize(txt: Any) -> str | None:
    """
    Lower-case, trim, collapse whitespace, strip trailing period.
    Returns None if *txt* is not a real string.
    """
    if not isinstance(txt, str):  # ← handles NaN / floats / None
        return None
    txt = re.sub(r"\s+", " ", txt).strip().casefold()
    return txt.rstrip(".")


def _merge_answers_metadata(
    df: pd.DataFrame,
    answers_meta: Dict[str, Dict[str, Dict[str, Any]]],
) -> pd.DataFrame:
    """
    Join double-layer answer metadata on (question_id, final_answer).

    Uses a *normalised* version of the answer text so that differences
    in capitalisation, extra spaces, or a trailing full stop do not
    block the match.
    """
    if not answers_meta:
        return df

    # ------------------------------------------------------------------
    # 1 / build a flat metadata frame with normalised answer text
    # ------------------------------------------------------------------
    flat: List[MutableMapping[str, Any]] = []
    for qid, answers in answers_meta.items():
        for answer_text, props in answers.items():
            flat.append(
                {
                    "question_id": qid,
                    "final_answer_norm": _normalize(answer_text),
                    **props,
                }
            )

    meta_df = pd.DataFrame(flat)

    # ------------------------------------------------------------------
    # 2 / add a normalised column to the main DF and merge
    # ------------------------------------------------------------------
    df = df.copy()
    df["final_answer_norm"] = df["final_answer"].apply(_normalize)

    merged = df.merge(  # ← join on normalised keys
        meta_df,
        on=["question_id", "final_answer_norm"],
        how="left",
        validate="m:1",  # optional: safety check
    ).drop(
        columns="final_answer_norm"
    )  # tidy up helper column
    return merged


def _fill_answer_metadata_fuzzy(
    df: pd.DataFrame,
    answers_meta: Dict[str, Dict[str, Dict[str, Any]]],
    threshold: int = 90,
) -> pd.DataFrame:
    """
    Copy every YAML property into rows whose exact merge failed,
    using fuzzy matching on *normalised* answer text.
    """
    if not answers_meta:
        return df

    # discover YAML property columns once
    sample_props = next(iter(next(iter(answers_meta.values())).values()), {})
    yaml_cols = list(sample_props.keys())

    needs_patch = df[yaml_cols].isna().any(axis=1)

    for idx, row in df[needs_patch].iterrows():
        qid = row["question_id"]
        ans_norm = _normalize(row["final_answer"])
        if ans_norm is None:
            continue  # NaN / n.a.

        # --- build {norm_key: (original_key, props)} for this question ----
        yaml_answers = answers_meta.get(qid, {})
        if not yaml_answers:
            continue  # open question

        norm_lookup = {_normalize(a): (a, props) for a, props in yaml_answers.items()}

        best_norm, sim, _ = process.extractOne(
            ans_norm,
            norm_lookup.keys(),
            scorer=fuzz.token_sort_ratio,
        )
        if best_norm is None or sim < threshold:
            continue  # no confident hit

        _, props = norm_lookup[best_norm]

        # copy every missing property
        for col, val in props.items():
            if col not in df.columns:
                df[col] = np.nan
            if pd.isna(df.at[idx, col]):
                df.at[idx, col] = val

    return df
