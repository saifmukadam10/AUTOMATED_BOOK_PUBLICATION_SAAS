import requests
import time

# Function to get response from local Ollama LLM
def get_ollama_response(prompt, model="llama3"):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["response"].strip()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def spin_text():
    input_file = "scraper/output/chapter1_content.txt"
    output_file = "chapter1_output.txt"

    with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
        paragraphs = infile.read().split('\n\n')
        for idx, paragraph in enumerate(paragraphs, 1):
            prompt = f"Rephrase this paragraph while retaining meaning:\n\n{paragraph}\n\nRewritten paragraph:"
            try:
                print(f"Processing paragraph {idx}...")

                rewritten_paragraph = get_ollama_response(prompt)

                if rewritten_paragraph:
                    outfile.write(rewritten_paragraph + "\n\n")
                    print(f"✅ Rewrote paragraph {idx}")
                else:
                    print(f"❌ Failed to rewrite paragraph {idx}, skipping.")

                time.sleep(1.5)  # Pause to avoid overloading your system

            except Exception as e:
                print(f"❌ Error rewriting paragraph {idx}: {e}")
                time.sleep(1)

if __name__ == "__main__":
    spin_text()

