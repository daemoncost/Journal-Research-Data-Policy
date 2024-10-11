from daemon_analysis_tools.data.question import Question


def group_questions_by_journal(data):
    grouped_data = data.groupby(["Publisher Name", "journal"])
    grouped_questions = {}

    for (publisher_name, journal_name), group in grouped_data:
        if publisher_name not in grouped_questions:
            grouped_questions[publisher_name] = {}

        if journal_name not in grouped_questions[publisher_name]:
            grouped_questions[publisher_name][journal_name] = {}

        for i, column in enumerate(data.columns):
            if column.split(".")[
                0
            ].isdigit():  # Check if the column label starts with an integer
                q_num = int(column.split(".")[0])

                # Check for the presence of an explanation column
                next_column = data.columns[i + 1] if i + 1 < len(data.columns) else None
                explanation_col = None
                if (
                    next_column
                    and (
                        "Please add the text from the RDP "
                        "that supports your answer below:"
                    )
                    in next_column
                ):
                    explanation_col = next_column

                if q_num not in grouped_questions[publisher_name][journal_name]:
                    grouped_questions[publisher_name][journal_name][q_num] = Question(
                        column
                    )

                for idx, answer in enumerate(group[column]):
                    explanation = (
                        group[explanation_col].iloc[idx]
                        if explanation_col in group.columns
                        else ""
                    )
                    grouped_questions[publisher_name][journal_name][q_num].add_answer(
                        answer, explanation
                    )

    return grouped_questions
