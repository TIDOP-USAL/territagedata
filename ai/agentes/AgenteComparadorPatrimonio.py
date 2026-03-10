import json

from models.Municipio import Municipio
from models.patrimonio.Patrimonio import Patrimonio
from models.patrimonio.TipoPatrimonio import TipoPatrimonio


class AgenteComparadorPatrimonio:
    def __init__(self, ai_assistant):
        self.ai_assistant = ai_assistant

    def compare(self, supervised_text, ai_generated_text):
        response = self.ai_assistant.get_response(request=f"""
                                                    Eres un comparador de información que analiza textos en busca de elementos complejos comunes.'
                                                    Te voy a proporcionar dos textos, deberás analizar ambos y comprobar qué
                                                    elementos hay en el segundo que coincidan con elementos del primero. Esto 
                                                    quiere decir que debes encontrar nombres compuestos o frases que sean idénticos o muy similares 
                                                    en ambos textos.
                                                    
                                                    Devuelve en forma de listado aquellos elementos que sean comunes en 
                                                    ambos textos.
                                                    
                                                    El primer texto es el siguiente:

                                                    {supervised_text}
                                                    
                                                    
                                                    Y el segundo texto a comparar es el siguiente:
                                                    
                                                    {ai_generated_text}
                                                    """)

        return response