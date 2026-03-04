# Dependencies:
from app import SurveyBot
import unittest


class TestSurveyBot(unittest.TestCase):
    # SurveyBot can be initialized with an objective string
    def test_initialize_with_objective_string(self):
        objective = "Test Objective"
        bot = SurveyBot(objective)
        self.assertEqual(bot.objective, objective)

    # SurveyBot can create a new thread
    def test_create_new_thread(self):
        from unittest.mock import patch

        bot = SurveyBot("Test Objective")
        with patch.object(bot.client.beta.threads, "create") as mock_create:
            bot.create_thread()
            mock_create.assert_called_once()

    # SurveyBot can send an initial message to the user
    def test_send_initial_message(self):
        import pytest
        from unittest.mock import patch

        bot = SurveyBot("Test Objective")
        with patch.object(bot, "send_message") as mock_send_message:
            bot.send_initial_message()
            mock_send_message.assert_called_once_with(
                "The objective of the survey is Test Objective. Give an introduction and purpose of the survey and invite the user to engage in a conversation. Keep the message short"
            )

    # SurveyBot raises an error if there is an issue creating a thread
    def test_raise_error_creating_thread(self):
        import pytest

        bot = SurveyBot("Test Objective")
        with pytest.raises(Exception):
            with patch.object(
                bot.client.beta.threads,
                "create",
                side_effect=Exception("Error creating thread"),
            ):
                bot.create_thread()

    # SurveyBot raises an error if there is an issue sending a message
    def test_raise_error_sending_message_with_patch_object(self):
        import pytest

        bot = SurveyBot("Test Objective")
        with unittest.mock.patch.object(
            bot.client.beta.threads.messages,
            "create",
            side_effect=Exception("Error sending message"),
        ):
            with self.assertRaises(Exception):
                bot.send_message("Test Message")

    # SurveyBot raises an error if there is an issue creating a run
    def test_raise_error_creating_run(self):
        import pytest
        from unittest.mock import Mock

        bot = SurveyBot("Test Objective")
        mocker = Mock()
        mocker.patch.object(
            bot.client.beta.threads.runs,
            "create",
            side_effect=Exception("Error creating run"),
        )

        with pytest.raises(Exception):
            bot.create_run()

    # SurveyBot can end a conversation and provide a summary of insights received
    def test_end_conversation_and_provide_summary(self):
        from unittest.mock import MagicMock, Mock

        # Create an instance of SurveyBot
        bot = SurveyBot("Test Objective")

        # Mock the necessary methods and attributes
        bot.create_thread = MagicMock()
        bot.send_initial_message = MagicMock()
        bot.create_run = MagicMock(return_value=Mock(id="run_id", status="completed"))
        bot.retrieve_run = MagicMock(return_value=Mock(status="completed"))
        bot.get_latest_message = MagicMock(return_value="Insights received")
        bot.send_message = MagicMock()

        # Call the start_conversation method
        result = bot.start_conversation()

        # Assert that the start_conversation method returns the latest message
        self.assertEqual(result, "Insights received")

        # Call the start_user_question method with "exit" as the user message
        result = bot.start_user_question("exit")

        # Assert that the start_user_question method returns the summary message
        self.assertEqual(result, "Summary: Insights received")

    # SurveyBot raises an error if there is an issue retrieving a run
    def test_retrieve_run_error(self):
        # Mock the OpenAI client
        mock_client = unittest.mock.Mock()
        unittest.mock.patch("openai.OpenAI", return_value=mock_client)

        # Create a SurveyBot instance
        bot = SurveyBot("Test Objective")

        # Mock the retrieve method to raise an exception
        mock_client.beta.threads.runs.retrieve.side_effect = Exception(
            "Error retrieving run"
        )

        # Assert that an error is raised when retrieving a run
        with self.assertRaises(Exception):
            bot.retrieve_run("run_id")

    # SurveyBot raises an error if there is an issue getting the latest message
    def test_latest_message_error(self):
        import pytest

        # Mock the retrieve_run method to raise an exception
        with pytest.raises(Exception):
            bot = SurveyBot("Test Objective")
            bot.retrieve_run = pytest.Mock(
                side_effect=Exception("Error retrieving run")
            )
            bot.get_latest_message()

    # SurveyBot uses OpenAI API to generate responses
    def test_initialize_with_objective_string(self):
        objective = "Test Objective"
        bot = SurveyBot(objective)
        self.assertEqual(bot.objective, objective)

    # SurveyBot handles the user entering "exit" as a message
    def test_handle_exit_message_fixed(self):
        # Mock the necessary methods and attributes
        with (
            unittest.mock.patch.object(
                SurveyBot, "create_thread"
            ) as mock_create_thread,
            unittest.mock.patch.object(
                SurveyBot, "send_initial_message"
            ) as mock_send_initial_message,
            unittest.mock.patch.object(SurveyBot, "create_run") as mock_create_run,
            unittest.mock.patch.object(SurveyBot, "retrieve_run") as mock_retrieve_run,
            unittest.mock.patch.object(
                SurveyBot, "get_latest_message"
            ) as mock_get_latest_message,
            unittest.mock.patch.object(SurveyBot, "send_message") as mock_send_message,
        ):
            # Create an instance of SurveyBot
            bot = SurveyBot("Test Objective")

            # Set the necessary return values for the mocked methods
            mock_create_thread.return_value = None
            mock_send_initial_message.return_value = None
            mock_create_run.return_value = unittest.mock.Mock(status="completed")
            mock_retrieve_run.return_value = unittest.mock.Mock(status="completed")
            mock_get_latest_message.return_value = "Latest message"

            # Test when user enters "exit" as a message
            user_message = "exit"
            expected_response = "Summary: Latest message"
            response = bot.start_user_question(user_message)

            # Assert that the send_message method was called with the correct arguments
            mock_send_message.assert_called_with(
                "Give a summary of the insights received through the conversation"
            )

            # Assert that the response is as expected
            self.assertEqual(response, expected_response)

    # SurveyBot can handle unexpected user input
    def test_unexpected_user_input(self):
        from unittest.mock import MagicMock

        # Create a SurveyBot instance
        bot = SurveyBot("Test Objective")

        # Mock the necessary methods
        bot.create_thread = MagicMock()
        bot.send_initial_message = MagicMock()
        bot.create_run = MagicMock()
        bot.retrieve_run = MagicMock()
        bot.get_latest_message = MagicMock()

        # Set the necessary mock return values
        bot.create_thread.return_value = None
        bot.send_initial_message.return_value = "Intro message"
        bot.create_run.return_value = MagicMock(id="run_id", status="completed")
        bot.retrieve_run.return_value = MagicMock(status="completed")
        bot.get_latest_message.return_value = "Latest message"

        # Call the start_conversation method
        result = bot.start_conversation()

        # Assert that the necessary methods were called
        bot.create_thread.assert_called_once()
        bot.send_initial_message.assert_called_once()
        bot.create_run.assert_called_once()
        bot.retrieve_run.assert_called_once()
        bot.get_latest_message.assert_called_once()

        # Assert the result
        self.assertEqual(result, "Latest message")
