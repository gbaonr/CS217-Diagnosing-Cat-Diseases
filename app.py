import streamlit as st
import os
import json
import sys
import io
import pandas as pd

from fuzzywuzzy import fuzz  # Hoặc dùng rapidfuzz
import unicodedata

from utils import *

# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


# Giao diện chính
def main():
    st.set_page_config(
        page_title="Care for Cats",
        page_icon=":smiley_cat:",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    st.title(":blue[:thermometer: Cat Disease Diagnosis]")
    st.write(
        ":rainbow[Chẩn đoán bệnh cho mèo từ triệu chứng bên ngoài. Phần mềm này không thay thế cho việc chẩn đoán của bác sĩ.]"
    )

    symptoms = load_symptoms()

    # Trạng thái lưu danh sách triệu chứng đã chọn
    if "selected_symptoms" not in st.session_state:
        st.session_state.selected_symptoms = []

    # Additional description
    search_query = st.text_input(
        "Mô tả triệu chứng, ngắn gọn, phân cách bằng dấu phẩy",
        placeholder="Nhấn để nhập mô tả bằng tiếng Việt có dấu....",
    )

    # Tìm kiếm triệu chứng và chọn từ danh sách
    selected_symptoms = st.multiselect(
        "Hoặc chọn các triệu chứng có sẵn",
        placeholder="Nhấn để chọn...",
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
    if st.button("Chẩn đoán 😼"):
        print("\n\n\n\nDiagnostic results:")
        chosens = st.session_state.selected_symptoms
        if not search_query:
            search_query = ""

        possible_diseases = diagnose(chosens, search_query)
        diseases = get_info(possible_diseases, n_show=3)

        st.markdown("### Kết quả chẩn đoán")

        if len(diseases) == 0:
            st.write(
                ":red[Không tìm thấy bệnh phù hợp với triệu chứng đã chọn.]:confused:"
            )
            return

        # Hiển thị thông tin từng bệnh
        imgs = os.listdir("images")
        for disease in diseases:
            # path = f"images/{disease['id']}.jpg"
            path = f"images/ill_cat.jpg"
            with st.expander(
                f"**{disease['name'].upper()}** ({disease['score'] * 100:.2f}%)",
                expanded=False,
            ):
                i = disease["id"]
                if f"{i}.jpg" in imgs:
                    path = f"images/{i}.jpg"
                elif f"{i}.png" in imgs:
                    path = f"images/{i}.png"
                elif f"{i}.jpeg" in imgs:
                    path = f"images/{i}.jpeg"
                else:
                    path = "images/ill_cat.jpg"
                # st.image(path, caption=path, use_container_width=True)
                st.image(path, caption=f"{disease['name']}", use_container_width=True)

                st.write("#### Triệu chứng 🤒")
                st.markdown("- " + "\n- ".join(disease["symptoms"]))

                st.write("#### Nguyên nhân 🧐")
                st.markdown("- " + "\n- ".join(disease["causes"]))

                st.write("#### Lây nhiễm 🦠")
                infectious_text = (
                    "**:red[CÓ]**" if disease["infectious"] else "**:green[KHÔNG]**"
                )
                st.write(f"**Khả năng lây nhiễm:** {infectious_text}")

                st.write("#### Phương pháp điều trị 🩺")
                st.markdown("- " + "\n- ".join(disease["treatments"]))

                st.write("#### Các loại thuốc hữu ích 💊")
                st.markdown("- " + "\n- ".join(disease["medicines"]))

                st.write("#### Phòng ngừa 🛡️")
                st.markdown("- " + "\n- ".join(disease["preventions"]))


if __name__ == "__main__":
    main()
