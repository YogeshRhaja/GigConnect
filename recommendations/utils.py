from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_match(freelancer_skills, job_skills):
    if not freelancer_skills or not job_skills:
        return 0.0

    texts = [freelancer_skills, job_skills]

    try:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)

        score = cosine_similarity(
            tfidf_matrix[0:1],
            tfidf_matrix[1:2]
        )[0][0]
        match_percentage = score * 100
        return round(match_percentage, 2)

    except Exception as e:
        print("AI matching error:", e)
        return 0.0
