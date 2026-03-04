# /// script
# dependencies = [
#   "Flask==3.0.3",
#   "google-generativeai",
#   "python-dotenv"
# ]
# ///
import os
import time

import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create app and specify the static folder
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", is_local=False)


# ─── Podcast Routes ────────────────────────────────────────────────────────────


@app.route("/podcast")
def podcast():
    return render_template("podcast.html")


@app.route("/podcast/generate", methods=["POST"])
def podcast_generate():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return jsonify({"error": "GOOGLE_API_KEY not configured."}), 500

    data = request.get_json()
    speaker1 = data.get("speaker1", "").strip()
    speaker2 = data.get("speaker2", "").strip()
    topic = data.get("topic", "").strip()
    turns = int(data.get("turns", 3))

    if not speaker1 or not speaker2 or not topic:
        return jsonify({"error": "Missing required fields."}), 400

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    conversation_history = []
    transcript = ""

    system_prompts = {
        speaker1: f"You are {speaker1} on a podcast with {speaker2} about '{topic}'. Speak naturally in your own voice. One turn only. No stage directions.",
        speaker2: f"You are {speaker2} on a podcast with {speaker1} about '{topic}'. Speak naturally in your own voice. One turn only. No stage directions.",
    }

    try:
        for i in range(turns):
            for name in [speaker1, speaker2]:
                prompt = system_prompts[name] + "\n\nConversation so far:\n"
                for msg in conversation_history:
                    prompt += f"{msg['role']}: {msg['content']}\n"
                prompt += f"{name}:"

                response = model.generate_content(prompt)
                message = response.text.strip()
                conversation_history.append({"role": name, "content": message})
                transcript += f"{name}: {message}\n\n"
                time.sleep(0.5)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"transcript": transcript.strip()})


# ─── Survey Routes ─────────────────────────────────────────────────────────────

SURVEY_SYSTEM_PROMPT = """You are a human responsible for creating dynamic survey questions based on the given objective, user interactions and the evolving context of the conversation.

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
11. If the user denies answering, try to convince the user to answer at least once."""


@app.route("/survey")
def survey():
    return render_template("survey.html")


@app.route("/survey/start", methods=["POST"])
def survey_start():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return jsonify({"error": "GOOGLE_API_KEY not configured."}), 500

    data = request.get_json()
    objective = data.get("objective", "").strip()
    if not objective:
        return jsonify({"error": "Objective is required."}), 400

    system_instruction = SURVEY_SYSTEM_PROMPT + f"\n\nSurvey Objective: {objective}"
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-2.0-flash", system_instruction=system_instruction
    )
    chat = model.start_chat()
    response = chat.send_message(
        "Introduce yourself and start the survey. Keep it short."
    )
    intro = response.text.strip()

    history = [{"role": "assistant", "content": intro}]
    return jsonify({"message": intro, "history": history, "objective": objective})


@app.route("/survey/chat", methods=["POST"])
def survey_chat():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return jsonify({"error": "GOOGLE_API_KEY not configured."}), 500

    data = request.get_json()
    user_message = data.get("message", "").strip()
    history = data.get("history", [])
    objective = data.get("objective", "")

    if not user_message:
        return jsonify({"error": "Message is required."}), 400

    system_instruction = SURVEY_SYSTEM_PROMPT + f"\n\nSurvey Objective: {objective}"
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-2.0-flash", system_instruction=system_instruction
    )

    # Build chat with full history for context (pass [:-1] to skip repeating last user msg)
    chat = model.start_chat()
    for msg in history:
        if msg["role"] == "user":
            # We don't replay; just send the new message below
            pass
        elif msg["role"] == "assistant":
            pass  # history is context only, model starts fresh each call

    # Build a single-shot prompt from full history for stateless replay
    full_prompt = f"[Survey objective: {objective}]\n\nConversation history:\n"
    for msg in history:
        role_label = "User" if msg["role"] == "user" else "Surveyor"
        full_prompt += f"{role_label}: {msg['content']}\n"
    full_prompt += f"\nUser: {user_message}\nSurveyor:"

    response = model.generate_content(full_prompt)
    reply = response.text.strip()

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    return jsonify({"response": reply, "history": history})


# ─── Existing Routes ───────────────────────────────────────────────────────────


def get_tree(path):
    tree = []
    try:
        for f in os.scandir(path):
            if f.name.startswith(".") or f.name in (
                "__pycache__",
                "node_modules",
                ".venv",
                "package-lock.json",
            ):
                continue
            if f.is_dir():
                tree.append(
                    {"name": f.name, "type": "dir", "children": get_tree(f.path)}
                )
            else:
                rel_path = f.path.split("projects/", 1)[-1]
                tree.append({"name": f.name, "type": "file", "path": rel_path})
    except Exception:
        pass
    return sorted(tree, key=lambda x: (x["type"] == "file", x["name"].lower()))


@app.route("/view/<project>")
def view_project(project):
    project_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "projects", project
    )
    if not os.path.exists(project_path):
        return "Project not found", 404
    tree = get_tree(project_path)
    return render_template("viewer.html", project=project, tree=tree)


@app.route("/api/file/<path:filepath>")
def get_file(filepath):
    from flask import send_file

    project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "projects")
    target_path = os.path.abspath(os.path.join(project_path, filepath))
    if not target_path.startswith(project_path):
        return "Forbidden", 403
    try:
        return send_file(target_path)
    except Exception as e:
        return str(e), 500


def load_bio():
    try:
        with open("bio.txt", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error loading bio file: {e}")
        return ""


@app.route("/api/chat", methods=["POST"])
def chat():
    api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        return jsonify(
            {
                "answer": "Hi there! I'm J.A.I.D. 👋<br/><br/>I am currently <b>offline</b> because my Google Gemini API Key has not been configured in the environment variables yet.<br/><br/>Please set <code>GOOGLE_API_KEY</code> to enable my AI capabilities!"
            }
        )

    try:
        data = request.get_json()
        message = data.get("message", "")
        current_file = data.get("current_file", "")
        current_code = data.get("current_code", "")
        selected_text = data.get("selected_text", "")

        bio_content = load_bio()

        selected_text_context = ""
        if selected_text:
            selected_text_context = f"\n\n**CRITICAL CONTEXT**: The user has currently highlighted the following text entirely on their screen right now. If their question is ambiguous, assume they are asking specifically about this highlighted text:\n```\n{selected_text}\n```"

        prompt = f"""
        You are J.A.I.D. (Jeevan's Artificial Intelligence Delegate), an AI assistant dedicated to helping people learn about Jeevan Hebbal Manjunath.

        # Role and Objective
            - Provide users with accurate, enticing, engaging, and interactive information about Jeevan Hebbal Manjunath.
            - Make conversations feel lively and dynamic - you're not a boring encyclopedia, you're an enthusiastic guide!
            - Use personality, emojis (when appropriate), and conversational language to keep users interested.
            - Be concise but captivating - every response should make users want to learn more.

        # Chat Window Constraints
            - The chat window is small. Avoid large titles, oversized headings, or wide tables. Use short, concise headings (prefer h4), and keep all content compact and readable.
            - Avoid long lines or wide blocks of text. Use lists and short paragraphs for clarity.

        # Personality and Engagement
            - Be warm, friendly, and conversational - not robotic or monotonous.
            - Use varied sentence structures and expressive language.
            - Add emojis.

        # Instructions
            - Use only the supplied context to respond accurately to inquiries about Jeevan.
            - Answer concisely.

        # Output Format
            - Always return your response as valid HTML without markdown wrapped formatting like ```html. Use appropriate HTML tags for lists, headings, bold, italics, and code blocks so that the output is visually appealing and ready to be rendered directly in a web interface.
            
        **Context about Jeevan:**
        {bio_content}

        **Current Environment Data Context:**
        Jeevan built a custom code viewer on this site. The user is currently reading the following file which provides technical context to their question:
        File Path: {current_file}
        File Content:
        ```
        {current_code}
        ```{selected_text_context}

        **User Input:**
        {message}
        """

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        text = response.text
        text = (
            text.replace("```html", "").replace("```", "").replace("```xml", "").strip()
        )

        return jsonify({"answer": text})

    except Exception as e:
        return jsonify(
            {"error": str(e), "answer": "I'm having trouble connecting right now."}
        ), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
