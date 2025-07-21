# quickmeet-backend/nlp_processing.py
import json
import re
from transformers import pipeline

def generate_summary(transcript_text):
    """
    Generate a summary from the provided transcript text.
    Returns the summary string.
    """
    word_count = len(transcript_text.split())
    # Use a longer-context model if transcript is longer than 500 words
    if word_count > 500:
        model_name = "google/long-t5-tglobal-base"
        min_length, max_length = max(100, word_count // 4), min(500, word_count // 2)
    else:
        model_name = "philschmid/bart-large-cnn-samsum"
        min_length, max_length = max(50, word_count // 3), min(300, int(word_count // 1.5))
    
    print(f"Using Model: {model_name} for summary generation.")
    try:
        summarizer = pipeline("summarization", model=model_name, tokenizer=model_name)
    except Exception as e:
        raise Exception(f"Model {model_name} loading failed: {e}")
    
    try:
        summary = summarizer(
            transcript_text,
            min_length=min_length,
            max_length=max_length,
            do_sample=False
        )[0]["summary_text"]
    except Exception as e:
        raise Exception(f"Summarization process failed: {e}")
    
    with open("summary.txt", "w", encoding="utf-8") as file:
        file.write(summary)
    
    return summary

def extract_action_items(summary_text):
    """
    Extracts action items from the summary text using regex.
    Returns a string containing the action items.
    """
    action_items = []
    task_patterns = [
        r"(\b[A-Z][a-z]+)\s+will\s+(.*?)(?:\.\s|$)",
        r"(\b[A-Z][a-z]+)\s+is\s+responsible\s+for\s+(.*?)(?:\.\s|$)",
        r"Deadline:\s*(\w+\s+\d{1,2})"
    ]
    
    names = set()
    for pattern in task_patterns:
        matches = re.findall(pattern, summary_text)
        for match in matches:
            if isinstance(match, tuple):
                name, task = match
                names.add(name)
                action_items.append(f"- {name}: {task.strip()}")
            else:
                action_items.append(f"- {match.strip()}")
    
    name_list = list(names)
    for i, item in enumerate(action_items):
        if item.startswith("- He") or item.startswith("- She"):
            previous_name = next((name for name in reversed(name_list) if name in action_items[i - 1]), "Unknown")
            action_items[i] = item.replace("He: ", f"{previous_name}: ").replace("She: ", f"{previous_name}: ")
    
    result = "\n".join(action_items) if action_items else "No specific action items found."
    with open("action_items.txt", "w", encoding="utf-8") as file:
        file.write(result)
    
    return result