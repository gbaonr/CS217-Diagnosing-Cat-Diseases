import streamlit as st
import os
import json
import sys
import io
import pandas as pd

from fuzzywuzzy import fuzz  # Hoặc dùng rapidfuzz
import unicodedata

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


# Load dữ liệu triệu chứng từ file JSON
def load_symptoms(file_path="cat_diseases.json"):
    with open(file_path, "r", encoding="utf-8") as file:
        symptoms = json.load(file)
    return symptoms


# Giao diện chính
def main():
    st.title("Triệu chứng chăm sóc mèo")
    st.write(
        "Ứng dụng giúp tìm kiếm và lựa chọn các triệu chứng để tìm ra bệnh phù hợp."
    )

    # Load triệu chứng từ file JSON (đảm bảo bạn có file `symptoms.json`)
    data = load_symptoms()
    symptoms = []
    for disease in data:
        symptoms.extend(disease["symptoms"])

    # Trạng thái lưu danh sách triệu chứng đã chọn
    if "selected_symptoms" not in st.session_state:
        st.session_state.selected_symptoms = []

    # Additional description
    search_query = st.text_input(
        "Mô tả thêm", placeholder="Nhập từ khóa để tìm triệu chứng..."
    )

    # Tìm kiếm triệu chứng và chọn từ danh sách
    selected_symptoms = st.multiselect(
        "Chọn triệu chứng:",
        options=symptoms,
        default=[],
        label_visibility="visible",
    )
    st.session_state.selected_symptoms = selected_symptoms

    # Hiển thị danh sách triệu chứng đã chọn
    st.write("### Danh sách triệu chứng đã chọn:")
    if selected_symptoms:
        df = pd.DataFrame(
            {
                "STT": range(1, len(selected_symptoms) + 1),
                "Triệu chứng": selected_symptoms,
            }
        )
        st.markdown(df.style.hide(axis="index").to_html(), unsafe_allow_html=True)

    else:
        st.write("Chưa có triệu chứng nào được chọn.")

    # Diagnose button
    st.write("### Chẩn đoán")
    if st.button("Chẩn đoán"):
        st.write("Chức năng chẩn đoán đang được phát triển.")
        symptoms = st.session_state.selected_symptoms
        st.write(symptoms)


if __name__ == "__main__":
    main()
