from ai.gemini.GeminiAI import GeminiAI


class AgenteProcesadorTexto:
    def __init__(self, ai_assistant):
        self.ai_assistant = ai_assistant

    def get_response(self, request):
        return self.ai_assistant.get_response(request=request)
