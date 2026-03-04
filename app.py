# /// script
# dependencies = [
#   "Flask==3.0.3",
#   "google-generativeai",
#   "python-dotenv"
# ]
# ///
import os

import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

# Create app and specify the static folder
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


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
    project_path = os.path.join(os.getcwd(), "projects", project)
    if not os.path.exists(project_path):
        return "Project not found", 404
    tree = get_tree(project_path)
    return render_template("viewer.html", project=project, tree=tree)


@app.route("/api/file/<path:filepath>")
def get_file(filepath):
    project_path = os.path.join(os.getcwd(), "projects")
    target_path = os.path.abspath(os.path.join(project_path, filepath))
    if not target_path.startswith(project_path):
        return "Forbidden", 403
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        return "Cannot display binary or non-text file", 400
    except Exception as e:
        return str(e), 500


def load_bio():
    try:
        with open("bio.txt", "r", encoding="utf-8") as file:
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

        bio_content = load_bio()

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
        ```

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
    # Start the Flask app
    app.run(host="0.0.0.0", port=8080, debug=True)
