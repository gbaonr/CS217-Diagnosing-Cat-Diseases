from fuzzywuzzy import fuzz  # Hoặc dùng rapidfuzz
import json
import sys
import io
import os
import unicodedata

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

data = None
with open("cat_diseases.json", "r", encoding="utf-8") as file:
    data = json.load(file)


def find_diseases(user_symptoms, data, threshold=80):
    possible_diseases = []
    for disease in data:
        disease_name = disease.get("name", "Chưa xác định")
        symptoms = disease.get("symptoms", [])
        match_count = 0
        for user_symptom in user_symptoms:
            for symptom in symptoms:
                similarity = fuzz.partial_ratio(user_symptom.lower(), symptom.lower())
                if similarity >= threshold:
                    match_count += 1
                    break
        if match_count > 0:
            drugs = disease.get("drugs", [])
            possible_diseases.append((disease_name, match_count, drugs))

    possible_diseases.sort(key=lambda x: x[1], reverse=True)
    return possible_diseases


def search_symptoms(all_symptoms, query):
    query = query.lower()
    query = unicodedata.normalize("NFC", query)

    all_symptoms = [
        unicodedata.normalize("NFC", symptom.lower()) for symptom in all_symptoms
    ]
    results = []
    for symptom in all_symptoms:
        if query in symptom:
            results.append(symptom)
            continue
        if fuzz.partial_ratio(query, symptom) >= 80:
            results.append(symptom)
            continue

    return results
