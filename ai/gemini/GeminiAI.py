import os
from google import genai
from google.genai import types

from config_loader import get_model
from exceptions import ApiConnectionError, MissingConfigurationError

# ai_model = "gemini-2.0-flash"
default_ai_model = "gemini-2.5-flash"  # Modelo por defecto temporal para que ejecute la aplicacion aunque no se configure el modelo en config.json
# api_key = os.getenv("GOOGLE_API_KEY")


class GeminiAI:
    def __init__(
        self,
        api_key,
        ai_model=None,
        use_search=False,
    ):
        # Validar que la clave de API no esté vacía
        if not api_key or not api_key.strip():
            raise MissingConfigurationError("La clave de API no puede estar vacía.")

        # Si no se proporciona modelo, intentar cargarlo desde config.json
        if ai_model is None:
            try:
                ai_model = get_model()
            except MissingConfigurationError as e:
                # Si falla cargar config, usar modelo por defecto
                print(f"Advertencia: {str(e)}. Usando modelo por defecto: {default_ai_model}")
                ai_model = default_ai_model

        # Validar que el modelo de IA no esté vacío
        if not ai_model or not ai_model.strip():
            raise MissingConfigurationError("El modelo de IA no puede estar vacío.")

        self.ai_model = ai_model
        self.use_search = use_search

        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            raise MissingConfigurationError(
                f"Error al conectar con la API de Google: {str(e)}"
            )

    def _raise_descriptive_api_error(self, error):
        """Convierte errores brutos de Gemini en mensajes amigables."""
        error_msg = str(error).lower()

        # API Key inválida / autenticación
        if (
            "api key not valid" in error_msg
            or "api_key_invalid" in error_msg
            or "invalid api key" in error_msg
            or "unauthenticated" in error_msg
            or "authentication" in error_msg
            or "permission_denied" in error_msg
        ):
            raise ApiConnectionError(
                "Tu API key no es válida o ha expirado. Revisa la clave en config.json."
            )

        # Cuota o rate limit
        if (
            "resource_exhausted" in error_msg
            or "quota" in error_msg
            or "quota exceeded" in error_msg
            or "rate_limit" in error_msg
            or "too many requests" in error_msg
            or "429" in error_msg
        ):
            raise ApiConnectionError(
                "Has superado la cuota/límite de peticiones de Gemini. Espera unos minutos o revisa tu plan de facturación."
            )

        # Modelo inválido/no disponible
        if "model" in error_msg and (
            "not found" in error_msg
            or "invalid" in error_msg
            or "not available" in error_msg
            or "unsupported" in error_msg
        ):
            raise ApiConnectionError(
                f"El modelo '{self.ai_model}' no es válido o no está disponible para tu cuenta."
            )

        # Red / timeout
        if (
            "timeout" in error_msg
            or "connection" in error_msg
            or "temporarily unavailable" in error_msg
            or "unavailable" in error_msg
        ):
            raise ApiConnectionError(
                "No se pudo conectar con Gemini en este momento. Comprueba tu conexión e inténtalo de nuevo."
            )

        # Fallback
        raise ApiConnectionError(
            "Error inesperado al comunicarse con Gemini. Revisa los logs técnicos para más detalle."
        )

    def get_response(self, request=""):
        try:
            response = self.client.models.generate_content(
                model=self.ai_model,
                contents=request,
                # config=types.GenerateContentConfig(
                #     temperature=0.1, # 0 low creativity 2 high creativity
                #     top_p=0.99,
                #     top_k=0
                # )
                # config = types.GenerateContentConfig(
                #     tools=[types.Tool(
                #         google_search=types.GoogleSearchRetrieval
                #     )]
                # )
                config=types.GenerateContentConfig(
                    # temperature=0.1, # 0 low creativity 2 high creativity
                    # top_p=0.99,
                    # top_k=0,
                    tools=(
                        [
                            types.Tool(
                                google_search=types.GoogleSearchRetrieval(
                                    dynamic_retrieval_config=types.DynamicRetrievalConfig(
                                        dynamic_threshold=0
                                    )
                                )
                            )
                        ]
                        if self.use_search
                        else None
                    ),
                ),
            )
            return response.text

        except Exception as e:
            self._raise_descriptive_api_error(e)

    def get_file_response(self, file_path, request):
        try:
            print("subiendo fichero:")
            print(file_path)
            print("")
            myfile = self.client.files.upload(file=file_path)
            result = self.client.models.generate_content(
                model=self.ai_model,
                contents=[
                    myfile,
                    "\n\n",
                    f"{request}",
                ],
            )
            return result.text
        except Exception as e:
            self._raise_descriptive_api_error(e)
