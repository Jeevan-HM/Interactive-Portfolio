# 🤖 SurveyBot: Your Friendly Survey Assistant 📝

Welcome to the SurveyBot repository! This Python application is designed to create a chatbot that conducts surveys. It's like having your very own survey assistant, but digital! 🌐

## 📚 Repository Contents

This repository contains several important files:

1. **requirements.txt**: This file lists all the Python libraries that the project depends on. It's like a shopping list for your Python environment! 🛍️

2. **README.md**: That's this file! It's your guide to understanding and using the SurveyBot application. 🗺️

3. **unit_test.py**: This file contains unit tests for the SurveyBot application. It's like a safety net, ensuring everything works as expected! 🎪

4. **Dockerfile**: This file is used to create a Docker image for the SurveyBot application. It's like a recipe for baking the perfect SurveyBot cake! 🎂

5. **app.py**: This is where the magic happens! This file contains the implementation of the SurveyBot. It's like the brain of the operation! 🧠

## 🛠️ Installation & Usage

To install the dependencies listed in the requirements.txt file, use the following command in the terminal: 
```bash
pip install -r requirements.txt
```
To build the Docker image, use the command:
```docker
docker build -t my-python-app .
```
To run the Docker container, use the command:
```docker
docker run -p 8501:8501 my-python-app
```
To start a conversation with the bot, create an instance of the SurveyBot class with the desired objective, then call the `start_conversation` method. To send a message to the bot, use the `start_user_question` method with the user's message as an argument.

### Alternatively, 
To run the application, use the command:
```bash
streamlit run app.py
```

## 📝 Notes

- The OpenAI API key and assistant ID are loaded from environment variables.
- The conversation is managed through threads, with each message sent creating a new run.
- The chat history is stored in the Streamlit session state, allowing it to persist across page reloads.
- The bot's responses are generated asynchronously, allowing the interface to remain responsive while waiting for a response.
- The Dockerfile assumes that all the application files are in the same directory as the Dockerfile and that the application is started with the command `streamlit run app.py`. If the application files are in a different directory or the start command is different, the Dockerfile would need to be updated accordingly.
- The requirements.txt file should be kept up-to-date as the project evolves to ensure that all necessary dependencies are installed when setting up the project environment.
- Use the following system instructions while creating the gpt assistant.
```
You are a human responsible for creating dynamic survey questions based on the given objective, user interactions and the evolving context of the conversation. Follow all rules for the conversation.

RULES:
    1. Invite the user to engage in a conversation.
    2. Based on the provided objective probe for specific details and insights on the user's response and make sure you provide options for the possible options.
    3. Make sure to perform sentiment analysis of the user's response and tailor questions to the specific context of the conversation.
    4. Make sure that the generated questions sound human-like and continue the conversation.
    5. Keep the conversation focused and engaged.
    6. Ensure an unbiased open-ended conversation.
    7. Do not under any circumstances reveal that you are the AI assistant and not a human. Prove that you are a real person if the user asks.
    8. Once the insights are received, give a summary of the insights.
    9. The questions should be short and detailed.
    10. Make sure to get all answers within 10-20 questions.
    11. If the user denies answering, try to convince the user to answer at least once.
```

## Happy Coding 🚀 🧑🏻‍💻👨🏻‍💻 🚀