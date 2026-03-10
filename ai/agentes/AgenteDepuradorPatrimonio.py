import os
import json

from ai.gemini.GeminiAI import GeminiAI
from models.Municipio import Municipio
from models.patrimonio.Patrimonio import Patrimonio
from models.patrimonio.TipoPatrimonio import TipoPatrimonio
from utils.export.csv.MunicipiosCsvExporter import MunicipiosCsvExporter
from utils.export.txt.MunicipiosTxtExporter import MunicipiosTxtExporter


class AgenteDepuradorPatrimonio:
    def __init__(self, ai_assistant):
        self.ai_assistant = ai_assistant

    def process(self, text_to_process : str):
        response = self.ai_assistant.get_response(request=f"""
                                                    Eres un experto en sintetizar texto.
                                                    El siguiente texto tiene que ver con información sobre una ciudad, municipio, población... 
                                                    y me interesa resumirlo de modo que quede lo más relevante
                                                    y que tenga que ver con el patrimonio cultural, patrimonio histórico, 
                                                    cultura, costumbres, gastronomía, rutas, artesanía, fiestas, 
                                                    sitios destacados, zonas de interés, religión, naturaleza, etc.
                                                    
                                                    El resultado debe ser en forma de listado.
                                                    
                                                    A continuación el texto a procesar:
                                                    
                                                    {text_to_process}
                                                    """)

        return response