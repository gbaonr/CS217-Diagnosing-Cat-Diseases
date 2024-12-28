import json
import os
import unicodedata
from rapidfuzz import fuzz, process


def create_norm_table(file_path="inferences.json"):
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


def fuzzy_match(query, word, norm_table):
    array = [word] + norm_table[word]
    result = process.extractOne(query, array)
    # so sanh do dai de tranh cac short word match voi all query
    query_len = len(query)
    word_len = len(result[0])
    rate = word_len / query_len
    if not (0.4 <= rate <= 1.2) and result[1] < 88:
        result = (result[0], 0)
    return [word, result[0], result[1]]  # word, matched_word, similarity score


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

    print(f"\n\n{norm_chosens}")


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

words, norm_table = create_norm_table()
norm_chosen(chosen, words, norm_table)
