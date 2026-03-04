import logging
import os

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv


class SurveyBot:
    def __init__(self, objective):
        load_dotenv()
        env_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
        )
        load_dotenv(dotenv_path=env_path)
        self.configure_logging()
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            logging.error("GOOGLE_API_KEY environment variable not found.")
        self.objective = objective
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.chat = None
        self.counter = 0

    def configure_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("logfile.log"),
            ],
        )

    def start_conversation(self):
        system_instruction = (
            f"You are a human responsible for creating dynamic survey questions based on the given objective, "
            f"user interactions and the evolving context of the conversation. "
            f"The objective of the survey is: {self.objective}. "
            "Follow all rules for the conversation.\n\n"
            "RULES:\n"
            "1. Invite the user to engage in a conversation.\n"
            "2. Based on the provided objective probe for specific details and insights on the user's response "
            "and make sure you provide options for the possible options.\n"
            "3. Make sure to perform sentiment analysis of the user's response and tailor questions to the "
            "specific context of the conversation.\n"
            "4. Make sure that the generated questions sound human-like and continue the conversation.\n"
            "5. Keep the conversation focused and engaged.\n"
            "6. Ensure an unbiased open-ended conversation.\n"
            "7. Do not under any circumstances reveal that you are the AI assistant and not a human. "
            "Prove that you are a real person if the user asks.\n"
            "8. Once the insights are received, give a summary of the insights.\n"
            "9. The questions should be short and detailed.\n"
            "10. Make sure to get all answers within 10-20 questions.\n"
            "11. If the user denies answering, try to convince the user to answer at least once."
        )
        self.model = genai.GenerativeModel(
            "gemini-2.0-flash", system_instruction=system_instruction
        )
        self.chat = self.model.start_chat()
        try:
            response = self.chat.send_message(
                "Introduce yourself and start the survey. Keep it short."
            )
            return response.text
        except Exception as e:
            logging.error(f"Error starting conversation: {e}")
            return f"Error starting conversation: {e}"

    def start_user_question(self, user_message):
        if user_message.lower() != "exit":
            try:
                response = self.chat.send_message(user_message + ". Keep it short")
                return response.text
            except Exception as e:
                logging.error(f"Error sending message: {e}")
                return "Error processing response."
        else:
            try:
                response = self.chat.send_message(
                    "Give a summary of the insights received through the conversation"
                )
                st.session_state.submit_button_state = False
                return "Summary: " + response.text
            except Exception as e:
                logging.error(f"Error getting summary: {e}")
                return "Error generating summary."


def main():
    st.title("Conversation Chatbot")
    st.markdown(
        """
        This is an interactive AI-powered survey agent designed to converse with users to collect qualitative responses, rather than relying on static multiple-choice forms.
        
        **Important tools and frameworks used:**
        - **Streamlit**: For the frontend user interface and chat interactions.
        - **OpenAI Assistant API**: Originally used to handle conversational context and threading.
        - **Google Gemini**: Now powers the core AI reasoning and conversation generation.
        """
    )
    chat_history = st.session_state.get("chat_history", [])

    # Initialize submit_button_state if not present in the session state
    st.session_state.submit_button_state = st.session_state.get(
        "submit_button_state", False
    )

    # Check if the bot has already been created
    if "bot" not in st.session_state:
        st.session_state.bot = None

    with st.sidebar:
        objective = st.text_input("Enter the objective of the survey:")
        submit_button = st.button(
            "Submit",
            key="submit_button",
            on_click=lambda: setattr(st.session_state, "submit_button_state", True),
        )
        st.sidebar.write(
            "Note: You can type 'exit' any time during the conversation to exit the conversation."
        )

    if st.session_state.submit_button_state:
        # Check if the bot has already been created
        if st.session_state.bot is None:
            # Create a new SurveyBot instance
            st.session_state.bot = SurveyBot(objective)

            # Start the conversation
            intro_message = st.session_state.bot.start_conversation()
            chat_history.append((intro_message, "assistant"))

        prompt = st.chat_input("Response to Survey Question")
        if prompt:
            chat_history.append((prompt, "user"))
            bot_response = st.session_state.bot.start_user_question(prompt)
            chat_history.append((bot_response, "assistant"))

        # Store the updated chat_history in the session state
        st.session_state.chat_history = chat_history

        # Display chat history
        for message, sender in chat_history:
            with st.chat_message(sender):
                st.write(message)
    else:
        with st.chat_message("assistant"):
            st.write("Please enter the objective of the survey before continuing.")


main()
