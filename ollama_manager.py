import ollama

class OllamaManager:
    def __init__(self, host='http://ollama:11434')):
        self.client = ollama.Client(host=host)

    def get_ollama_response(self, model, prompt):
        try:
            response = self.client.chat(
                model=model,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content']
        except Exception as e:
            return f"Error al conectar con Ollama: {e}"
