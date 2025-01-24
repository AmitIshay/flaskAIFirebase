from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from flask_cors import CORS
import openai
import os, json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

firebase_key = os.getenv("FIREBASE_KEY")
if firebase_key:
    try:
        cred = credentials.Certificate(json.loads(firebase_key))
        firebase_admin.initialize_app(cred)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing Firebase key: {str(e)}")
else:
    raise ValueError("Firebase key is missing in environment variables.")



# חיבור למסד נתונים Firestore
db = firestore.client()

# אתחול OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# יצירת אפליקציה
app = Flask(__name__)
CORS(app)

# פונקציה ליצירת שאלה באמצעות OpenAI
def generate_question(level):
    prompt = f"Create a trivia question and its answer. Difficulty: {level}. Question:"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a trivia question generator."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=100,
            temperature=0.7,
        )
        generated_text = response['choices'][0]['message']['content'].strip()
        
        # הדפסת תגובת ה-AI
        print(f"AI Response: {generated_text}")

        # זיהוי הפורמט והתאמתו
        if "Question:" in generated_text and "Answer:" in generated_text:
            question_part = generated_text.split("Question:")[1].split("Answer:")[0].strip()
            answer_part = generated_text.split("Answer:")[1].strip()
            return {"question": question_part, "answer": answer_part}
        elif "Answer:" in generated_text:  # פורמט ללא "Question:"
            parts = generated_text.split("Answer:")
            question_part = parts[0].strip()
            answer_part = parts[1].strip()
            return {"question": question_part, "answer": answer_part}
        else:  # פורמט פשוט עם שאלה בשורה ראשונה ותשובה בשורה שנייה
            lines = generated_text.split("\n")
            if len(lines) >= 2:
                question_part = lines[0].strip()
                answer_part = lines[1].strip()
                return {"question": question_part, "answer": answer_part}
            else:
                print("Unexpected format in AI response")
                return None
    except Exception as e:
        print(f"Error during AI question generation: {str(e)}")
        return None

@app.route("/getQuestions", methods=["GET"])
def get_questions():
    # קבלת רמת הקושי מהפרמטר של ה-URL
    level = request.args.get("level", "medium").lower()

    # בדיקת רמת קושי חוקית
    valid_levels = {"easy", "medium", "hard"}
    if level not in valid_levels:
        return jsonify({"message": f"Invalid level: {level}. Valid levels are {valid_levels}"}), 400

    # בדיקת אם רוצים שאלה מ-AI
    use_ai = request.args.get("use_ai", "false").lower() == "true"

    if use_ai:
        question_data = generate_question(level)
        if question_data:
            return jsonify([question_data])  # החזר רשימה עם שאלה אחת
        else:
            return jsonify({"message": "Failed to generate question using AI. Please try again."}), 500

    # אם לא רוצים שאלה מ-AI, שליפת שאלות מ-Firebase
    try:
        questions_ref = db.collection("questions")
        query = questions_ref.where("level", "==", level).stream()  # שליפת שאלות לפי רמת קושי

        questions = [q.to_dict() for q in query]  # המרת השאלות לפורמט דיקט

        if questions:
            return jsonify(questions)  # החזרת השאלות
        else:
            return jsonify({"message": "No questions found for this level"}), 404
    except Exception as e:
        # הדפסת פרטי השגיאה
        print(f"Error occurred: {str(e)}")  # הדפס את השגיאה בקונסול
        return jsonify({"message": f"An error occurred: {str(e)}"}), 500  # החזרת השגיאה למשתמש

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



# from flask import Flask, request, jsonify
# import firebase_admin
# from firebase_admin import credentials, firestore
# from flask_cors import CORS
# from transformers import AutoTokenizer, GPT2LMHeadModel, pipeline


# # אתחול Firebase
# cred = credentials.Certificate("firebase-keyNew.json")  # קובץ המפתח של Firebase
# firebase_admin.initialize_app(cred)

# # חיבור למסד נתונים Firestore
# db = firestore.client()


# # יצירת אפליקציה
# app = Flask(__name__)
# CORS(app)
    
# # יצירת pipeline ל-Hugging Face עם טוקן
# tokenizer = AutoTokenizer.from_pretrained("gpt2")
# model = GPT2LMHeadModel.from_pretrained("gpt2", token="REDACTED")
# question_generator = pipeline("text-generation", model=model, tokenizer=tokenizer)

# def generate_question_hf(level):
#     prompt = f"Create a trivia question and its answer. Difficulty: {level}. Question:"
#     result = question_generator(prompt, max_length=50, num_return_sequences=1)
#     if result:
#         text = result[0]['generated_text']
#         if "Question:" in text and "Answer:" in text:
#             question_part = text.split("Question:")[1].split("Answer:")[0].strip()
#             answer_part = text.split("Answer:")[1].strip()
#             return {"question": question_part, "answer": answer_part}
#     return None
    
# # @app.route("/getQuestions", methods=["GET"])
# # def get_questions():
# #     # קבלת רמת הקושי מהפרמטר של ה-URL
# #     level = request.args.get("level", "medium")

# #     # שליפת השאלות מרמת הקושי המבוקשת
# #     questions_ref = db.collection("questions")
# #     query = questions_ref.where("level", "==", level).stream()

# #     # יצירת רשימה של השאלות שמצאנו
# #     questions = []
# #     for question in query:
# #         questions.append(question.to_dict())  # המרת השאלה לפורמט דיקט

# #     if questions:
# #         return jsonify(questions)  # החזרת השאלות בפורמט JSON
# #     else:
# #         return jsonify({"message": "No questions found for this level"}), 404
# # -----------------------------------------------------------
# # @app.route("/getQuestions", methods=["GET"])
# # def get_questions():
# #     # קבלת רמת הקושי מהפרמטר של ה-URL
# #     level = request.args.get("level", "medium").lower()

# #     # בדיקת רמת קושי חוקית
# #     valid_levels = {"easy", "medium", "hard"}
# #     if level not in valid_levels:
# #         return jsonify({"message": f"Invalid level: {level}. Valid levels are {valid_levels}"}), 400

# #     # בדיקת אם רוצים שאלה מ-AI
# #     use_ai = request.args.get("use_ai", "false").lower() == "true"

# #     if use_ai:
# #         question_data = generate_question_hf(level)
# #         if question_data:
# #             return jsonify([question_data])  # החזר רשימה עם שאלה אחת
# #         else:
# #             return jsonify({"message": "Failed to generate question using AI"}), 500

#     # # אם לא רוצים שאלה מ-AI, שליפת שאלות מ-Firebase
#     # try:
#     #     questions_ref = db.collection("questions")
#     #     query = questions_ref.where(field_path="level", op_string="==", value=level)

#     #     questions = [q.to_dict() for q in query]

#     #     if questions:
#     #         return jsonify(questions)
#     #     else:
#     #         return jsonify({"message": "No questions found for this level"}), 404
#     # except Exception as e:
#     #     return jsonify({"message": f"An error occurred: {str(e)}"}), 500
# @app.route("/getQuestions", methods=["GET"])
# def get_questions():
#     # קבלת רמת הקושי מהפרמטר של ה-URL
#     level = request.args.get("level", "medium").lower()

#     # בדיקת רמת קושי חוקית
#     valid_levels = {"easy", "medium", "hard"}
#     if level not in valid_levels:
#         return jsonify({"message": f"Invalid level: {level}. Valid levels are {valid_levels}"}), 400

#     # בדיקת אם רוצים שאלה מ-AI
#     use_ai = request.args.get("use_ai", "false").lower() == "true"

#     if use_ai:
#         question_data = generate_question_hf(level)
#         if question_data:
#             return jsonify([question_data])  # החזר רשימה עם שאלה אחת
#         else:
#             return jsonify({"message": "Failed to generate question using AI"}), 500

#     # אם לא רוצים שאלה מ-AI, שליפת שאלות מ-Firebase
#     try:
#         questions_ref = db.collection("questions")
#         query = questions_ref.where("level", "==", level).stream()  # עדכון לשימוש ב-stream()

#         questions = [q.to_dict() for q in query]  # המרת השאלות לפורמט דיקט

#         if questions:
#             return jsonify(questions)  # החזרת השאלות
#         else:
#             return jsonify({"message": "No questions found for this level"}), 404
#     except Exception as e:
#         # הדפסת פרטי השגיאה
#         print(f"Error occurred: {str(e)}")  # הדפס את השגיאה בקונסול
#         return jsonify({"message": f"An error occurred: {str(e)}"}), 500  # החזרת השגיאה למשתמש


    
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)