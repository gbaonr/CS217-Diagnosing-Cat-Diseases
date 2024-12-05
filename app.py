from flask import Flask, request, jsonify, render_template
from backend import *
import json
import os

app = Flask(__name__)

# Load the disease data from the JSON file
with open("cat_diseases.json", "r", encoding="utf-8") as file:
    data = json.load(file)


@app.route("/")
def index():
    return render_template("home.html")


# get all symptoms
@app.route("/get_symptoms", methods=["GET"])
def get_symptoms():
    all_symptoms = []
    for disease in data:
        all_symptoms.extend(disease["symptoms"])
    return jsonify(all_symptoms)


# find diseases by selected symptoms
@app.route("/find_diseases", methods=["POST"])
def find_diseases_route():
    user_symptoms = request.json.get("symptoms", [])
    threshold = request.json.get("threshold", 80)
    possible_diseases = find_diseases(user_symptoms, data, threshold)
    return jsonify(possible_diseases)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
