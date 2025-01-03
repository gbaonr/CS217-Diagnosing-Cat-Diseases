import json
import os
import unicodedata
from rapidfuzz import fuzz, process

PATH = "data"


# Create normalization table and words
def create_norm_table(file_path="inferences.json"):
    file_path = os.path.join(PATH, file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    words = []
    norm_table = {}
    for word in data:
        synonyms = data[word]
        synonyms = synonyms.split(", ")
        word = unicodedata.normalize("NFC", word)
        words.append(word)
        if word not in norm_table:
            norm_table[word] = []
        for synonym in synonyms:
            synonym = unicodedata.normalize("NFC", synonym)
            if synonym in norm_table or synonym == "":
                continue
            norm_table[word].append(synonym)
    # print(words)
    # print(norm_table)

    return words, norm_table


# function to fuzzy match query with word and its synonyms
def fuzzy_match(query, word, norm_table):
    array = [word] + norm_table[word]
    result = process.extractOne(query, array)
    # so sanh do dai de tranh cac short word match voi all query
    query_len = len(query)
    word_len = len(result[0])
    rate = word_len / query_len if query_len != 0 else 1
    if not (0.4 <= rate <= 1.2) and result[1] < 88:
        result = (result[0], 0)
    return [word, result[0], result[1]]  # word, matched_synonym, similarity score


# convert chosen options to normalized form
def norm_chosen(chosens, words, norm_table):
    norm_chosens = []
    temp_dict = {}
    for option in chosens:
        print(option)
        option = unicodedata.normalize("NFC", option.lower())
        parts = option.split(", ")
        for part in parts:
            if part not in temp_dict:
                temp_dict[part] = []
            print(f"\t- {part}:")
            for word in words:
                result = fuzzy_match(part, word, norm_table)
                if result[2] >= 85:
                    temp_dict[part].append(result)
            if len(temp_dict[part]) > 0:
                best_match = max(temp_dict[part], key=lambda x: x[2])
                print(f"\t\tword({best_match[0]}): {best_match[1]} -> {best_match[2]}")
                norm_chosens.append(best_match[1])

    print(f"Norm chosens: {norm_chosens}\n")

    return norm_chosens


# Convert discriptions into normalized form
def norm_discription(discription, words, norm_table):
    norm_discriptions = []
    temp_dict = {}

    print(discription)
    discription = unicodedata.normalize("NFC", discription.lower())
    parts = discription.strip("?").split(", ")
    parts = [part.strip() for part in parts]
    for part in parts:
        if part not in temp_dict:
            temp_dict[part] = []
        print(f"\t- {part}:")
        for word in words:
            result = fuzzy_match(part, word, norm_table)
            if result[2] >= 85:
                temp_dict[part].append(result)
        if len(temp_dict[part]) > 0:
            best_match = max(temp_dict[part], key=lambda x: x[2])
            print(f"\t\tword({best_match[0]}): {best_match[1]} -> {best_match[2]}")
            norm_discriptions.append(best_match[1])

    print(f"Norm discription: {norm_discriptions}\n")

    return norm_discriptions


# Diagnose the disease
def diagnose(chosens, discription):
    words, norm_table = create_norm_table()
    norm_chosens = norm_chosen(chosens, words, norm_table)
    norm_discriptions = norm_discription(discription, words, norm_table)

    input_symptoms = set(norm_chosens + norm_discriptions)

    path = os.path.join(PATH, "diseases_norm.json")
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    possible_diseases = []
    for disease in data:
        match_pairs = []
        id = disease.get("id", -1)
        disease_symptoms = disease.get("symptoms", [])
        disease_symptoms = [unicodedata.normalize("NFC", x) for x in disease_symptoms]
        match_count = 0
        total_symptoms = len(disease_symptoms)
        for symptom in disease_symptoms:
            if symptom in input_symptoms:
                match_count += 1
                match_pairs.append(symptom)
        match_ratio = match_count / total_symptoms
        possible_diseases.append((id, match_ratio))
    return possible_diseases  # list of tuples (disease_id, match_ratio)


# Show info
def get_info(possible_diseases, n_show=3):
    results = []
    sorted_diseases = sorted(possible_diseases, key=lambda x: x[1], reverse=True)[
        :n_show
    ]

    with open(os.path.join(PATH, "diseases_info.json"), "r", encoding="utf-8") as file:
        data = json.load(file)

    for disease in sorted_diseases:
        id = disease[0]
        score = disease[1]
        if score == 0:
            continue

        disease_name = data[id].get("name", "Chưa xác định")
        disease_symptoms = data[id].get("symptoms", [])
        causes = data[id].get("causes", [])
        medicines = data[id].get("medicines", [])
        infectious = data[id].get("infectious", "Không xác định")
        treatments = data[id].get("treatments", [])
        preventions = data[id].get("preventions", [])
        results.append(
            {
                "id": id,
                "name": disease_name,
                "score": score,
                "symptoms": disease_symptoms,
                "causes": causes,
                "medicines": medicines,
                "infectious": infectious,
                "treatments": treatments,
                "preventions": preventions,
            }
        )

    return results


chosen = [
    "Phân đôi khi lẫn máu",
    "Đau vùng bụng",
    "Bộ lông xơ xác, không được chải chuốt",
    "Tiêu chảy nhẹ đến trung bình",
    "Mắt đỏ, chảy nước mắt",
    "Sốt, mệt mỏi, kém ăn",
    "Dễ cáu kỉnh, hung tợn, thậm chí cắn cả chủ nuôi",
    "Cắn xé đồ đạc một cách điên loạn",
    "Sợ ánh sáng, bị co giật, suy hô hấp",
    "Di chuyển chậm chạp, buồn rầu",
]

discription = [
    "rất mệt mỏi, không muốn ăn, ngủ suốt ngày, nôn mửa nhiều lần trong ngày",
    "ho, thở khò khè, mũi chảy dịch, mắt đỏ, mắt sưng",
    "ngứa, gãi liên tục, vùng da trầy xước, rụng lông",
    "tiêu chảy, phân có màu khác thường, khát nước nhiều hơn, đi tiểu nhiều",
    "kêu meo meo không ngừng, lo lắng, có thể đau đớn hoặc căng thẳng",
    "kêu gào vào ban đêm, không muốn giao tiếp, trốn vào góc tối, không muốn ra ngoài",
    "Con mèo của tôi có vẻ rất mệt mỏi, không muốn ăn và ngủ suốt ngày, Nó còn bị nôn mửa nhiều lần trong ngày",
]


# words, norm_table = create_norm_table()
# p = diagnose(chosen[:2], discription[0])
# get_info(p, 2)
