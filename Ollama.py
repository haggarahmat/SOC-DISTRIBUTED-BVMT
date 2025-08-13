{% python %}
 
import requests
 
# Ollama API URL via NGINX (accessible from local network)
URL = "http://192.168.5.99:11434/api/generate"
 
# Detailed instructions for Ollama (in English)
instructions = (
    "You are a SOC analyst. Analyze the following alert from Suricata or Zeek detection system via Graylog. "
    "Provide a concise and clear text output with the following sections, each on a new line:\n\n"
    "Type of threat: [brief name or classification]\n"
    "Probable cause: [detailed explanation of root cause based on the alert]\n"
    "Observed behavior: [what has been detected or observed]\n"
    "Potential risks: [possible impacts or dangers]\n"
    "Immediate recommendations: [urgent steps to mitigate]\n"
    "Preventive security measures for the long term: [strategic measures to avoid future threats]\n"
    "Severity (low, medium, high): [criticality based on alert]\n\n"
    "Do not include markdown formatting, tables, or lists. Do not repeat information between sections. "
    "Answer only based on the alert data provided."
)
 
# Context given to Ollama
context = "Here is an alert from your Suricata/Zeek detection system via Graylog."
 
# Dynamic alert sample (replace with actual or injected alert data)
alert = "$loop.#._source.filebeat_alert_signature\nFull log: $loop.#._source.message"
 
# Build the full prompt
prompt_text = f"{instructions}\n{context}\n{alert}"
 
# Payload for the request to Ollama
payload = {
    "model": "llama3:8b",
    "prompt": prompt_text,
    "temperature": 0.1,
    "max_tokens": 300,
    "stream": False
}
 
# Simple message cleanup function
def format_message(message_content):
    # Remove double asterisks, clean spaces, keep line structure
    formatted_message = message_content.replace('**', '')
    formatted_message = ' '.join(formatted_message.split())
    lines = formatted_message.split('\\n')  # in case of escaped newlines
    return '\n'.join([line.strip() for line in lines])
 
# Function to return the final response (can be customized)
def summarize_for_soc(raw_response):
    return raw_response
 
# Send the request to Ollama
with requests.Session() as session:
    try:
        response = session.post(URL, json=payload)
        if response.status_code == 200:
            response_json = response.json()
            message_content = response_json.get("response", "No content received")
            formatted_message = format_message(message_content)
            print(summarize_for_soc(formatted_message))
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except requests.exceptions.Timeout:
        print("⏱️ Timeout: The request took too long.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
 
 
{% endpython %}
