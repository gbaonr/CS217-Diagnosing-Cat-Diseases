from fuzzywuzzy import fuzz  # Hoặc dùng rapidfuzz
import json
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def find_diseases(user_symptoms, data, threshold=80):
    possible_diseases = []
    # for disease in data.get("Bệnh", []):  # Truy cập danh sách bệnh từ JSON
    for disease in data["Bệnh"]:
        disease_name = disease.get("Tên bệnh", "Chưa xác định")
        symptoms = disease.get("Triệu chứng", [])
        match_count = 0
        for user_symptom in user_symptoms:
            for symptom in symptoms:
                similarity = fuzz.partial_ratio(user_symptom.lower(), symptom.lower())
                if similarity >= threshold:
                    match_count += 1
                    break  # Nếu đã khớp một triệu chứng thì bỏ qua các triệu chứng còn lại
        if match_count > 0:
            possible_diseases.append((disease_name, match_count))
    possible_diseases.sort(key=lambda x: x[1], reverse=True)
    return possible_diseases


# Đọc file JSON
with open("benh_meo.json", "r", encoding="utf-8") as file:
    data = json.load(file)


if __name__ == "__main__":
    # Nhập triệu chứng
    user_input = input("Nhập triệu chứng bạn gặp phải (cách nhau bằng dấu phẩy): ")
    user_symptoms = [symptom.strip() for symptom in user_input.split(",")]

    # Tìm bệnh
    results = find_diseases(user_symptoms, data)

    if results:
        print("Các bệnh có thể gặp phải:")
        for disease, count in results:
            # Tìm thông tin chi tiết của bệnh từ dữ liệu gốc
            # detailed_info = next((d for d in data["Bệnh"] if d["Tên bệnh"] == disease), None)
            detailed_info = [d for d in data["Bệnh"] if d["Tên bệnh"] == disease]
            if detailed_info:
                symptoms = detailed_info[0].get("Triệu chứng", [])
                print(f"- {disease} ({count} triệu chứng khớp):")
                print("  Triệu chứng của bệnh:")
                for symptom in symptoms:
                    print(f"    - {symptom}")
    else:
        print("Không tìm thấy bệnh nào phù hợp với các triệu chứng.")
