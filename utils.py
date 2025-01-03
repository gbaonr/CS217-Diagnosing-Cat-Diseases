import json
import os
import unicodedata
from rapidfuzz import fuzz, process

PATH = "data"


# convert inferences.json to to_doc.json -> looks better on docs
def to_doc():
    with open(os.path.join(PATH, "inferences.json"), "r", encoding="utf-8") as file:
        data = json.load(file)
        new_data = {}
        for key in data:
            norm_key = unicodedata.normalize("NFC", key)
            if norm_key not in new_data:
                new_data[norm_key] = []
            line = list(data[key])
            line = [unicodedata.normalize("NFC", x) for x in line]
            new_line = ""
            for word in line:
                if word != "":
                    new_line += word + ", "

            new_data[norm_key] = new_line[:-2]

        with open(os.path.join(PATH, "to_doc.json"), "w", encoding="utf-8") as file:
            json.dump(new_data, file, ensure_ascii=False)


# Load dữ liệu triệu chứng từ file JSON
def load_symptoms(file_path="data/diseases_info.json"):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    symptoms = []
    for disease in data:
        symptoms.extend(disease["symptoms"])
    return symptoms


# Create normalization table and words
def create_norm_table(file_path="inferences.json"):
    file_path = os.path.join(PATH, file_path)
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    norm_table = {}
    words = list(data.keys())
    for word in words:
        synonyms = data[word]
        word_ = unicodedata.normalize("NFC", word)
        if word_ not in norm_table:
            norm_table[word_] = []
        for synonym in synonyms:
            synonym = unicodedata.normalize("NFC", synonym)
            if synonym in norm_table or synonym == "":
                continue
            norm_table[word_].append(synonym)

    words = [unicodedata.normalize("NFC", x) for x in words]
    return words, norm_table


# function to fuzzy match query with word and its synonyms (NOT USING)
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


# function to check if query is an absolute match of word or its synonyms
def absolute_match(query, word, norm_table):
    array = [word] + norm_table[word]
    # return the longest synonym
    res = (None, "", None)
    for synonym in array:
        if len(synonym) == 1:  # vd "u" -> "u nhọt"
            s = synonym.lower()
            q_split = query.lower().split(" ")
            if s in q_split and len(s) > len(res[1]):
                res = (True, word, synonym)
        else:
            if synonym.lower() in query.lower() and len(synonym) > len(res[1]):
                res = (True, word, synonym)
    if res[0]:
        return res
    return (False, None, None)


# convert chosen options to normalized form
def norm_chosen(chosens, words, norm_table, show_=False):
    norm_chosens = []

    for option in chosens:
        option = unicodedata.normalize("NFC", option.lower())
        norm_chosen = ""
        temp = ""
        # voi moi option, chuyen thanh 1 tu trong norm_table
        for word in words:
            res = absolute_match(option, word, norm_table)
            if res[0] and len(res[1]) > len(norm_chosen):
                norm_chosen = res[1]
                temp = res[2]

        if norm_chosen != "":
            norm_chosens.append(norm_chosen)

        if show_:
            print(f"{option} -> {norm_chosen} (exact word: {temp})")

    return norm_chosens


# Convert discriptions into normalized form
def norm_discription(discription, words, norm_table, show_=False):
    norm_discriptions = []
    discription = unicodedata.normalize("NFC", discription.lower())
    parts = discription.strip("?").split(", ")
    parts = [part.strip() for part in parts]

    norm_discriptions = norm_chosen(parts, words, norm_table, show_=show_)
    return norm_discriptions


# Diagnose the disease
def diagnose(chosens, discription):
    words, norm_table = create_norm_table()

    print("\nnorm chosen: ".upper())
    norm_chosens = norm_chosen(chosens, words, norm_table, show_=True)

    print("\nnorm discriptions: ".upper())
    norm_discriptions = norm_discription(discription, words, norm_table, show_=True)

    print("\n\nDONE NORMALIZING\n\n")
    input_symptoms = set(norm_chosens + norm_discriptions)

    path = os.path.join(PATH, "symptoms.json")
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    possible_diseases = []

    for key in data:
        id = int(key)
        disease_symptoms = data[key]

        # normalize disease_symptoms
        disease_symptoms = [unicodedata.normalize("NFC", x) for x in disease_symptoms]
        disease_symptoms = norm_chosen(disease_symptoms, words, norm_table)

        # count match
        match_count = 0
        for input_symptom in input_symptoms:  # da duoc norm
            if input_symptom in disease_symptoms:
                match_count += 1

        # calculate match ratio
        len_dis_symptoms = len(disease_symptoms)
        len_input_symptoms = len(input_symptoms)
        disease_match_ratio = (
            match_count / len_dis_symptoms if len_dis_symptoms != 0 else 0
        )
        input_match_ratio = (
            match_count / len_input_symptoms if len_input_symptoms != 0 else 0
        )
        match_ratio = (disease_match_ratio + input_match_ratio) / 2
        possible_diseases.append((id, match_ratio))

    # sort
    possible_diseases = sorted(possible_diseases, key=lambda x: x[1], reverse=True)
    return possible_diseases  # list of tuples (disease_id, match_ratio)


# Show info
def get_info(possible_diseases, n_show=3):
    results = []
    for p in possible_diseases[:n_show]:
        with open(os.path.join(PATH, "symptoms.json"), "r", encoding="utf-8") as file:
            disease_symptoms = dict(json.load(file))
        with open(os.path.join(PATH, "causes.json"), "r", encoding="utf-8") as file:
            causes = json.load(file)
        with open(os.path.join(PATH, "infectious.json"), "r", encoding="utf-8") as file:
            infectious = json.load(file)
        with open(os.path.join(PATH, "medicines.json"), "r", encoding="utf-8") as file:
            medicines = json.load(file)
        with open(os.path.join(PATH, "names.json"), "r", encoding="utf-8") as file:
            disease_names = json.load(file)
        with open(
            os.path.join(PATH, "preventions.json"), "r", encoding="utf-8"
        ) as file:
            preventions = json.load(file)
        with open(os.path.join(PATH, "treatments.json"), "r", encoding="utf-8") as file:
            treatments = json.load(file)

        id = p[0]
        score = p[1]
        if score == 0:
            continue

        disease_symptoms = disease_symptoms[str(id)]
        causes = causes[str(id)]
        medicines = medicines[str(id)]
        infectious = infectious[str(id)]
        treatments = treatments[str(id)]
        preventions = preventions[str(id)]
        disease_names = disease_names[str(id)]

        results.append(
            {
                "id": id,
                "name": disease_names,
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
    "u nhọt",
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


# possible_diseases = diagnose(chosen, discription[0])
# print(possible_diseases)
# print()
# res = get_info(possible_diseases, 2)

# for r in res:
#     print(r["name"])
to_doc()
