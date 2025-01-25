### Trivia API


#### This is a Python-based backend application for handling trivia questions. The API supports fetching questions stored in MongoDB and generating new questions using OpenAI's GPT models.


#### Features
  - MongoDB Integration: Store and fetch trivia questions by difficulty level.
  - AI Question Generation: Dynamically create trivia questions using OpenAI's GPT model.
  - CORS Support: Allows cross-origin requests for seamless integration with front-end applications.


#### Installation


Prerequisites
  - Python 3.7+
  - MongoDB database
  - OpenAI API key
  - Environment variables configured in a .env file


Setup Steps
- Clone the repository.
- Install the required dependencies:
```python
pip install flask pymongo flask-cors openai python-dotenv
```
- Create a .env file in the project root directory and add the following:
```python
OPENAI_API_KEY=your_openai_api_key
MONGO_URI=your_mongodb_connection_string
```


#### Endpoints


Get Questions
  - URL: /getQuestions
  - Method: GET
  - level (required): Difficulty level (easy, medium, hard).
  - use_ai (optional): Set to true to generate a question using AI. Defaults to false.
  - Returns a list of questions from MongoDB if use_ai=false.
  - Returns a dynamically generated question if use_ai=true.


Example Response:
```python
[
    {
        "question": "What is the capital of France?",
        "answer": "Paris",
        "level": "easy"
    }
]
```


#### MongoDB Integration

  - Database: sample_mflix.
  - Collection: questions.
  - Structure:
    ```python
    {
    "question": "What is 2 + 2?",
    "answer": "4",
    "level": "easy"
    }
    ```


#### Example Usage


Starting the Server


Run the server locally with:
```python
flask run
```

Fetching Questions


From MongoDB:
```python
curl "http://127.0.0.1:5000/getQuestions?level=medium"
```


AI-Generated Question:
```python
curl "http://127.0.0.1:5000/getQuestions?level=hard&use_ai=true"
```









  
