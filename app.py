from flask import Flask, request, send_file, jsonify, render_template
from flask_cors import CORS
import os
import io
from email_sender import send_meeting_email
from transcriber import transcribe_audio
from nlp_processing import generate_summary, extract_action_items
from ppt_generator import create_ppt
from pdf_generator import generate_pdf_from_files
from semantic_search import perform_semantic_search

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    return render_template("index.html")  # For initial upload

# ✅ New dashboard route
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")  # After transcription

@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio_endpoint():
    if 'file' not in request.files:
        return jsonify({"message": "No file provided"}), 400

    audio_file = request.files['file']
    if audio_file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    upload_folder = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, audio_file.filename)
    audio_file.save(file_path)

    transcript = transcribe_audio(file_path)

    if transcript:
        return jsonify({"transcript": transcript})
    else:
        return jsonify({"message": "Transcription failed"}), 500

@app.route('/generate_summary', methods=['POST'])
def generate_summary_endpoint():
    data = request.get_json()
    transcript = data.get("transcript")
    if not transcript:
        return jsonify({"message": "No transcript provided"}), 400
    try:
        summary_text = generate_summary(transcript)
        return jsonify({"summary": summary_text})
    except Exception as e:
        return jsonify({"message": f"Summary generation failed: {e}"}), 500

@app.route('/extract_action_items', methods=['POST'])
def extract_action_items_endpoint():
    data = request.get_json()
    summary_text = data.get("summary")
    if not summary_text:
        return jsonify({"message": "No summary provided"}), 400
    try:
        action_items = extract_action_items(summary_text)
        return jsonify({"action_items": action_items})
    except Exception as e:
        return jsonify({"message": f"Action items extraction failed: {e}"}), 500

@app.route('/generate_ppt', methods=['POST'])
def generate_ppt_endpoint():
    data = request.get_json()
    summary_text = data.get("summary", "")
    action_items_text = data.get("action_items", "")
    
    ppt_io = create_ppt(summary_text, action_items_text)

    return send_file(
        ppt_io,
        as_attachment=True,
        download_name="summary_action_items.pptx",
        mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

@app.route('/send_email', methods=['POST'])
def send_email_endpoint():
    data = request.get_json()
    to_addresses = data.get("to_addresses")
    subject = data.get("subject", "Meeting Summary & Action Items")
    summary_text = data.get("summary", "")
    action_items_text = data.get("action_items", "")

    if not to_addresses or not isinstance(to_addresses, list):
        return jsonify({"message": "Invalid or missing 'to_addresses' field"}), 400

    try:
        response = send_meeting_email(to_addresses, subject, summary_text, action_items_text)
        return jsonify({"message": "Email sent successfully", "response": response})
    except Exception as e:
        return jsonify({"message": f"Failed to send email: {e}"}), 500

@app.route('/generate_pdf', methods=['GET'])
def generate_pdf_endpoint():
    try:
        pdf_data = generate_pdf_from_files()
        return send_file(
            io.BytesIO(pdf_data),
            as_attachment=True,
            download_name="meeting_summary.pdf",
            mimetype="application/pdf"
        )
    except Exception as e:
        return jsonify({"message": f"PDF generation failed: {e}"}), 500

# ✅ Final semantic search route with static file saving for frontend
@app.route('/semantic_search', methods=['POST'])
def semantic_search_endpoint():
    data = request.get_json()
    query = data.get("query")
    if not query:
        return jsonify({"message": "No query provided"}), 400
    try:
        results = perform_semantic_search(query)

        # Save to static/search_results.txt for frontend
        static_dir = os.path.join(os.getcwd(), "static")
        os.makedirs(static_dir, exist_ok=True)
        result_path = os.path.join(static_dir, "search_results.txt")
        with open(result_path, "w") as f:
            f.write(results)

        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"message": f"Semantic search failed: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
