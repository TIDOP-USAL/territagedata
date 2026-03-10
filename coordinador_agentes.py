import os

from pathlib import Path
from exceptions import EmptyFolderError, EmptyFileError
from ai.agentes.AgenteComparadorPatrimonio import AgenteComparadorPatrimonio
from ai.agentes.AgenteDepuradorPatrimonio import AgenteDepuradorPatrimonio
from ai.agentes.AgenteOrganizadorPatrimonio import AgenteOrganizadorPatrimonio
from ai.agentes.AgenteProcesadorFicheros import AgenteProcesadorFicheros
from ai.agentes.AgenteProcesadorTexto import AgenteProcesadorTexto
from ai.agentes.AgenteProcesadorWeb import AgenteProcesadorWeb
from ai.agentes.AgenteRecopilador import AgenteRecopilador
from ai.gemini.GeminiAI import GeminiAI
from config_loader import get_api_key
from models.Municipio import Municipio
from utils.export.txt.MunicipiosTxtExporter import MunicipiosTxtExporter


########################################################################################################################

def exportar_respuestas(respuestas, nombre_lugar, file_path):
    with open(file_path, "w", encoding='utf-8') as archivo:
        archivo.write(f"\nLugar: {nombre_lugar}\n\n")
        for text in respuestas:
            archivo.write(f'\n{text}')

def importar_texto(file_path):
    file_content = ""
    with open(file_path, 'r', encoding='utf-8') as archivo:
        file_content = archivo.read()
    return file_content

########################################################################################################################

class CoordinadorAgentes:
    def __init__(self,
                 nombre_municipio,
                 repositorio_path="",
                 lista_urls=[],
                 fichero_comparar="",
                 resultados_path="",
                 task_completed_function=lambda:None,
                 log_function=lambda msg:None
                 ):
        self.nombre_municipio = nombre_municipio
        self.repositorio_path = repositorio_path
        self.lista_urls = lista_urls
        self.fichero_comparar = fichero_comparar
        self.resultados_path = resultados_path
        self.log_function = log_function
        self.task_completed_function = task_completed_function

        self.municipio = Municipio(
            nombre=nombre_municipio,
            codigo="",
        )

        self.api_key = get_api_key()
        self.ai_assistant_processor = GeminiAI(api_key=self.api_key)
        self.ai_assistant_web_processor = GeminiAI(api_key=self.api_key, use_search=True)

        self.agente_ficheros = AgenteProcesadorFicheros(
            ai_assistant=self.ai_assistant_processor,
            file_path_list=self.get_file_list(),
            task_completed_callback=task_completed_function,
            log_callback=log_function
        )
        self.agente_web = AgenteProcesadorWeb(ai_assistant=self.ai_assistant_web_processor)
        self.agente_procesador_texto = AgenteProcesadorTexto(ai_assistant=self.ai_assistant_processor)

        self.agente_recopilador = AgenteRecopilador(
            agente_ficheros=self.agente_ficheros,
            agente_web=self.agente_web,
            nombre_municipio=self.nombre_municipio,
            url_list=self.lista_urls,
            log_callback=self.log_function,
            task_completed_callback=self.task_completed_function
        )

        self.agente_depurador = AgenteDepuradorPatrimonio(ai_assistant=self.agente_procesador_texto)

        self.num_tasks = self.get_num_tasks()


    def run(self):
        ####### Recopilando informacion
        info_recopilada_file_name = "info_recopilada.txt"
        resultado = self.recopilar_informacion()
        info_recopilada = resultado['info_recopilada']
        info_unida = resultado['info_unida']

        ####### Depurando
        file_name_depurado = "info_depurada.txt"
        texto_depurado = self.depurar_informacion(info_unida)

        ####### Organizando el patrimonio
        self.organizar_informacion(info_recopilada_file_name)

        ####### Comparando los resultados (OPCIONAL - solo si se seleccionó archivo)
        if self.fichero_comparar:  # Si hay archivo seleccionado
            self.comparar_informacion(file_name_depurado)
        else:
            self.log_function("Comparación omitida: no se seleccionó archivo de comparación")
            # Marcar como completada aunque esté omitida para que la barra llegue al 100%
            self.task_completed_function()



    def recopilar_informacion(self):
        self.log_function("**** RECOPILANDO INFORMACIÓN ****")

        file_list = self.get_file_list()
        self.log_function(f"{len(file_list)} ficheros para analizar")

        info_recopilada: list = self.agente_recopilador.recopilar()
        info_unida: str = ''.join(info_recopilada)

        info_recopilada_file_name = "info_recopilada.txt"
        with open(f"{self.resultados_path}/{info_recopilada_file_name}", "w", encoding='utf-8') as archivo:
            archivo.write(info_unida)

        self.log_function("Información recopilada exportada")

        return {"info_recopilada":info_recopilada, "info_unida":info_unida}


    def depurar_informacion(self, text_to_process):
        self.log_function("Depurando resultados")
        texto_depurado = self.agente_depurador.process(text_to_process=text_to_process)

        file_name_depurado = "info_depurada.txt"
        with open(f"{self.resultados_path}/{file_name_depurado}", "w", encoding='utf-8') as archivo:
            archivo.write(texto_depurado)

        self.log_function("Información recopilada depurada exportada")
        self.task_completed_function()

        return texto_depurado


    def organizar_informacion(self, info_recopilada_file_name):
        self.log_function("Organizando la información")
        file_name = info_recopilada_file_name
        file_content = ""
        with open(f'{self.resultados_path}/{file_name}', 'r', encoding='utf-8') as archivo:
            file_content = archivo.read()

        organizador = AgenteOrganizadorPatrimonio(
            ai_assistant=self.ai_assistant_processor,
            text_to_organize=file_content,
            municipio=self.municipio
        )
        municipio_organizado = organizador.get_organized()
        txt_exporter = MunicipiosTxtExporter(
            municipios=[municipio_organizado],
            file_name=f'{self.resultados_path}/info_clasificada'
        )
        txt_exporter.export()
        self.log_function("Fichero organizado exportado")
        self.task_completed_function()


    def comparar_informacion(self, file_name_depurado):
        self.log_function("Comparando resultados")
        
        # Validar que el archivo de comparación existe y no está vacío
        if not self.fichero_comparar:
            raise EmptyFileError("No se seleccionó archivo de comparación")
        
        if not Path(self.fichero_comparar).exists():
            raise EmptyFileError(f"El archivo de comparación no existe: {self.fichero_comparar}")
        
        if os.path.getsize(self.fichero_comparar) == 0:
            raise EmptyFileError(f"El archivo de comparación está vacío: {self.fichero_comparar}")
        
        # Si todo OK, proceder con la comparación
        supervised_text = importar_texto(f"{self.fichero_comparar}")
        ai_generated_text = importar_texto(f"{self.resultados_path}/{file_name_depurado}")

        agente_comparador_patrimonio = AgenteComparadorPatrimonio(ai_assistant=self.agente_procesador_texto)
        resultado_comparacion = agente_comparador_patrimonio.compare(
            supervised_text=supervised_text,
            ai_generated_text=ai_generated_text
        )

        comparacion_export_path = f"{self.resultados_path}/resultado_comparativa.txt"
        with open(comparacion_export_path, "w", encoding='utf-8') as archivo:
            archivo.write(resultado_comparacion)

        self.task_completed_function()
        self.log_function("Resultados de comparación exportados")


    def get_num_tasks(self):
        tasks = self.agente_recopilador.get_num_tasks()
        tasks += 3
        #num_files = len(self.get_file_list())*2
        #num_urls = len(self.lista_urls) * 2
        #num_global_search = 1

        return tasks

    def get_file_list(self):
        directorio = Path(self.repositorio_path)
        
        # Validar que la carpeta existe
        if not directorio.exists():
            raise EmptyFolderError(f"La carpeta no existe: {self.repositorio_path}")
        
        extensiones = ('.pdf', '.docx', '.txt')
        archivos = [f"{self.repositorio_path}/{f.name}" for f in directorio.iterdir() if
                    f.is_file() and f.suffix.lower() in extensiones]
        
        # Validar que la carpeta no está vacía
        if not archivos:
            raise EmptyFolderError(
                f"La carpeta no contiene archivos PDF, DOCX o TXT: {self.repositorio_path}"
            )
        
        return archivos
