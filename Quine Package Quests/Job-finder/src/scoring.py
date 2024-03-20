from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

df = pd.read_csv('your_file.csv')
queries_df = pd.read_json('your_queries.json')
job_descriptions = df['description'].tolist()
queries = queries_df['query'].tolist()

for query in queries:
    query_vector = [query] * len(job_descriptions)
    scores = cosine_similarity(job_descriptions, query_vector)
    df['score_' + query] = scores

df.to_csv('your_scored_file.csv', index=False)