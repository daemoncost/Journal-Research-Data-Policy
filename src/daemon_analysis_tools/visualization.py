import matplotlib.pyplot as plt
import seaborn as sns

def plot_publisher_scores(average_scores):
    average_publisher_scores = average_scores.groupby('Publisher Name')['normalized_score'].mean().reset_index()
    average_publisher_scores = average_publisher_scores.sort_values(by='normalized_score', ascending=False)
    
    plt.figure(figsize=(7, 4))
    sns.barplot(data=average_publisher_scores, x='Publisher Name', y='normalized_score', hue='Publisher Name', palette='viridis', legend = False)
    plt.xlabel('Publishers')
    plt.ylabel('Normalized Average Score')
    plt.title('Normalized Average Research Data Policy Scores per Publisher')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

