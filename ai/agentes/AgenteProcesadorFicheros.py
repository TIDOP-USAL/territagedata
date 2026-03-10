from ai.gemini.GeminiAI import GeminiAI


class AgenteProcesadorFicheros:
    def __init__(
            self,
            ai_assistant,
            file_path_list,
            task_completed_callback=lambda:None,
            log_callback=lambda msg:None
    ):
        self.ai_assistant = ai_assistant
        self.file_path_list = file_path_list
        self.task_completed_callback = task_completed_callback
        self.log_callback = log_callback

    def get_response(self, request):
        responses = []
        for path in self.file_path_list:
            #responses.append(self.ai_assistant.get_file_response(file_path=path, request=request))
            response = self.ai_assistant.get_file_response(
                file_path=path,
                request=request
            ) or ""
            self.task_completed_callback()
            self.log_callback(f" ✅ {path}")
        return responses