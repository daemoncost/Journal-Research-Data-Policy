from .file_handling import normalize_series

# Function to check if all elements in a series are the same and return differences if any
def all_equal(series):
    series = normalize_series(series)
    unique_values = series.dropna().unique()
    if len(unique_values) == 1:
        return True, None, None
    else:
        differing_indices = series.index[~series.duplicated(keep=False)]
        differing_values = series[~series.duplicated(keep=False)].tolist()
        return False, differing_indices, differing_values

# Function to compute Jaccard similarity between two strings
def jaccard_similarity(str1, str2):
    set1, set2 = set(str1.split()), set(str2.split())
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union

# Function to check if all open text answers are similar above a threshold
def all_similar(series, threshold=0.8):
    series = normalize_series(series)
    texts = series.dropna().unique()
    differing_indices = []
    differing_values = []
    for i, text1 in enumerate(texts):
        for text2 in texts[i+1:]:
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
        data_duplicated[question_text + '_score'] = data_duplicated[question_text].apply(
            lambda x: assign_score(question_num, x, multiple_choice_scores)
        )
    data_duplicated['total_score'] = data_duplicated[
        [question_text + '_score' for question_text in question_num_to_text.values()]
    ].sum(axis=1)
    return data_duplicated

def normalize_scores(average_scores):
    min_score = average_scores['total_score'].min()
    max_score = average_scores['total_score'].max()
    average_scores['normalized_score'] = (average_scores['total_score'] - min_score) / (max_score - min_score)
    return average_scores

