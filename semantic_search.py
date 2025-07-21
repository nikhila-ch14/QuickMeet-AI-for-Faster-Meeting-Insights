from sentence_transformers import SentenceTransformer, util
import re
import os

def split_into_sentences(text):
    # Split text on a period, exclamation, or question mark followed by whitespace and a capital letter.
    return [s.strip() for s in re.split(r'(?<=[.?!])\s+(?=[A-Z])', text) if s.strip()]

def load_sentences():
    combined_text = ""
    for filename in ['summary.txt', 'action_items.txt']:
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                combined_text += file.read() + "\n"
        except FileNotFoundError:
            print(f"⚠️ {filename} not found. Skipping.")
    return split_into_sentences(combined_text)

def perform_semantic_search(query):
    """
    Perform a semantic search on the content of summary.txt and action_items.txt.
    Writes the best matching sentence to static/search_results.txt and returns it.
    """
    sentences = load_sentences()

    if not sentences:
        result = "No content to search."
        _write_result_to_file(result)
        return result

    # Initialize SentenceTransformer and encode all sentences as well as the query.
    model = SentenceTransformer('all-MiniLM-L6-v2')
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
    query_embedding = model.encode(query, convert_to_tensor=True)
    
    # Compute cosine similarities between the query and each sentence.
    similarities = util.cos_sim(query_embedding, sentence_embeddings)[0]
    best_idx = int(similarities.argmax())
    result = sentences[best_idx]

    # Write the search result to the file in the static folder.
    _write_result_to_file(result)
    
    return result

def _write_result_to_file(result_text):
    """
    Writes the result text to static/search_results.txt.
    """
    # Determine the static folder path relative to this file.
    static_folder = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_folder, exist_ok=True)
    file_path = os.path.join(static_folder, "search_results.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(result_text)

def main():
    query = input("Enter your query for similarity search: ")
    result = perform_semantic_search(query)
    print("\nMost relevant result:")
    print(result)
    print(f"\nResult has been saved to 'static/search_results.txt'.")

if __name__ == "__main__":
    main()
