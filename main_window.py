
import sys
import os
from pathlib import Path
from urllib.parse import urlparse

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog

from coordinador_agentes import CoordinadorAgentes
from config_loader import get_api_key, get_model
from exceptions import (
    EmptyFolderError,
    EmptyFileError,
    InvalidUrlDir,
    MissingConfigurationError,
    ConnectionFailedError,
    RequiredFieldError,
    ApiConnectionError
)
from interfaz import Ui_Dialog

class DialogoPrincipal(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setFixedSize(self.size())
        
        # Cargar estilos QSS
        self.cargar_estilos()
        
        self.ui.pushButtonCompareFile.clicked.connect(self.seleccionar_fichero)
        self.ui.pushButtonFilesDirectory.clicked.connect(self.seleccionar_directorio_repositorio)
        self.ui.pushButtonResults.clicked.connect(self.seleccionar_directorio_resultados)
        self.ui.pushButtonAddUrl.clicked.connect(self.add_url)
        self.ui.pushButtonProcess.clicked.connect(self.process)
        self.ui.progressBar.setValue(0)

        self.num_tasks = 6
        self.completed_tasks = 0
        
        # Validar que config.json existe y es válido al iniciar
        self.validar_configuracion_inicial()
    
    def cargar_estilos(self):
        """Carga la hoja de estilos QSS"""
        try:
            # Determinar la ruta del archivo de estilos
            if getattr(sys, 'frozen', False):
                # Si es .exe, buscar en el directorio temporal de PyInstaller
                style_path = Path(sys._MEIPASS) / 'styles.qss'
            else:
                # Si es script, buscar en el directorio del proyecto
                style_path = Path(__file__).parent / 'styles.qss'
            
            if style_path.exists():
                with open(style_path, 'r', encoding='utf-8') as f:
                    self.setStyleSheet(f.read())
            else:
                print(f"Advertencia: No se encontró el archivo de estilos en {style_path}")
        except Exception as e:
            print(f"Error al cargar estilos: {e}")

    def validar_configuracion_inicial(self):
        """Valida que config.json existe y es válido al iniciar la aplicación"""
        try:
            # Intentar cargar la API key
            api_key = get_api_key()
            
            # Intentar cargar el modelo
            modelo = get_model()
            
            # Si todo está bien, mostrar mensaje de éxito en el log
            self.log_msg("Configuración cargada correctamente")
            
        except MissingConfigurationError as e:
            # Si falla, mostrar error pero permitir que la app continúe
            error_msg = str(e)
            self.log_msg(f"ADVERTENCIA DE CONFIGURACIÓN: {error_msg}")
            QtWidgets.QMessageBox.warning(
                self,
                "Configuración incompleta",
                f"Hay un problema con la configuración:\n\n{error_msg}\n\n"
                f"Por favor, verifica que el archivo 'config.json' exista en la carpeta raíz "
                f"del proyecto y tenga las siguientes claves:\n"
                f"- 'google_api_key': Tu clave de API de Google\n"
                f"- 'model': El modelo de IA a usar (ej: 'gemini-2.0-flash')"
            )

    def seleccionar_fichero(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo")
        if archivo:
            self.ui.lineEditCompareFile.setText(archivo)

    def seleccionar_directorio_repositorio(self):
        ruta = QtWidgets.QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if ruta:
            self.ui.lineEditFilesDirectory.setText(ruta)

    def seleccionar_directorio_resultados(self):
        ruta = QtWidgets.QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if ruta:
            self.ui.lineEditResults.setText(ruta)

    def add_url(self):
        try:
            url = self.ui.lineEditUrl.text().strip()
            self.validar_url(url)
            self.validar_url_duplicada(url)
            
            if url != "":
                self.ui.listWidgetUrls.addItem(url)
                self.ui.lineEditUrl.setText("")
                
        except InvalidUrlDir as e:
            error_msg = str(e)
            self.log_msg(f"URL inválida: {error_msg}")
            QtWidgets.QMessageBox.warning(
                self,
                "URL inválida",
                f"La URL ingresada no es válida:\n\n{error_msg}\n\nAsegúrate de que la URL tenga formato https://dominio.com y no esté duplicada en la lista."
            )
  
    def validar_url(self, url):
        """Valida que la URL tenga un formato correcto."""
        # Validar que URL no está vacía
        if not url or not url.strip():
            raise InvalidUrlDir("La URL no puede estar vacía")
        
        try:
            result = urlparse(url)
            
            # Verificar que tiene esquema (http o https) y netloc (dominio)
            if not result.scheme or not result.netloc:
                raise InvalidUrlDir(f"URL inválida: {url}\nDebe tener formato https://dominio.com")
            
            # Verificar que el esquema es http o https
            if result.scheme not in ("http", "https"):
                raise InvalidUrlDir(f"Esquema no válido: {result.scheme}\nUsa http:// o https://")
            
            return True
            
        except InvalidUrlDir:
            # Re-lanzar excepciones que ya son InvalidUrlDir
            raise
        except Exception as e:
            # Solo capturar excepciones inesperadas del parsing
            raise InvalidUrlDir(f"No se pudo procesar la URL: {url}")
            
    def validar_url_duplicada(self, url):
        """Verifica si la URL ya existe en la lista."""
        url_existentes = [self.ui.listWidgetUrls.item(i).text()
                          for i in range(self.ui.listWidgetUrls.count())]
    
        # Comparar ignorando espacios y mayúsculas
        if url.strip().lower() in [u.strip().lower() for u in url_existentes]:
            raise InvalidUrlDir(f"La URL ya existe en la lista: {url}")
        return True

    def log_msg(self, msg):
        self.ui.plainTextEdit.appendPlainText(msg)
        QtWidgets.QApplication.processEvents()

    def increment_task_completed(self):
        self.completed_tasks += 1
        self.update_progress()
        QtWidgets.QApplication.processEvents()

    def update_progress(self):
        self.ui.progressBar.setValue(int(self.completed_tasks/self.num_tasks*100))

    def validate_inputs(self):
        """
        Valida que todos los campos obligatorios estén completados.
        Lanza RequiredFieldError si falta algún campo.
        """
        # Validar nombre del municipio
        nombre_municipio = self.ui.lineNombreMunicipio.text().strip()
        if not nombre_municipio:
            raise RequiredFieldError("El nombre del municipio es obligatorio")
        
        # Validar carpeta de archivos
        carpeta_archivos = self.ui.lineEditFilesDirectory.text().strip()
        if not carpeta_archivos:
            raise RequiredFieldError("Debes seleccionar una carpeta de archivos")
        
        # Validar carpeta de resultados
        carpeta_resultados = self.ui.lineEditResults.text().strip()
        if not carpeta_resultados:
            raise RequiredFieldError("Debes seleccionar una carpeta de resultados")
        
        # Validar archivo de comparación
        archivo_comparacion = self.ui.lineEditCompareFile.text().strip()
        if archivo_comparacion:
            if not Path(archivo_comparacion).exists():
                raise EmptyFileError(f"El archivo de comparación no existe: {archivo_comparacion}")
            
            if os.path.getsize(archivo_comparacion) == 0:
                raise EmptyFileError(f"El archivo de comparación está vacío: {archivo_comparacion}")

    def process(self):
        try:
            # Validar que todos los campos obligatorios están completos
            self.validate_inputs()
            
            # Crear coordinador (esto lanzará EmptyFolderError si hay problema)
            coordinador = CoordinadorAgentes(
                nombre_municipio=self.ui.lineNombreMunicipio.text(),
                repositorio_path=self.ui.lineEditFilesDirectory.text(),
                lista_urls= [self.ui.listWidgetUrls.item(i).text() for i in range(self.ui.listWidgetUrls.count())],
                fichero_comparar=self.ui.lineEditCompareFile.text(),
                resultados_path=self.ui.lineEditResults.text(),
                log_function=self.log_msg,
                task_completed_function=self.increment_task_completed
            )

            self.num_tasks = coordinador.get_num_tasks()
            
            # Log del inicio
            self.log_msg("Validación completada. Iniciando procesamiento...")
            
            # Ejecutar el coordinador
            coordinador.run()
            
            # Si todo va bien
            self.log_msg("PROCESO COMPLETADO EXITOSAMENTE")
            QtWidgets.QMessageBox.information(
                self,
                "Éxito",
                "El procesamiento se completó exitosamente."
            )
        
        except RequiredFieldError as e:
            # Capturar errores de campos obligatorios
            self.ui.progressBar.setValue(0)
            error_msg = str(e)
            self.log_msg(f"CAMPO OBLIGATORIO: {error_msg}")
            QtWidgets.QMessageBox.warning(
                self,
                "Campo obligatorio",
                f"Por favor completa el siguiente campo:\n\n{error_msg}"
            )
        
        except EmptyFolderError as e:
            # Capturar errores de carpeta vacía
            self.ui.progressBar.setValue(0)
            error_msg = str(e)
            self.log_msg(f"ERROR: {error_msg}")
            QtWidgets.QMessageBox.warning(
                self,
                "Carpeta inválida",
                f"Problema con la carpeta de archivos:\n\n{error_msg}\n\nAsegúrate de que:\n• La carpeta existe\n• Contiene archivos PDF, DOCX o TXT"
            )
        
        except EmptyFileError as e:
            # Capturar errores de archivo vacío o inválido
            self.ui.progressBar.setValue(0)
            error_msg = str(e)
            self.log_msg(f"ERROR EN ARCHIVO: {error_msg}")
            QtWidgets.QMessageBox.warning(
                self,
                "Archivo inválido",
                f"Problema con el archivo:\n\n{error_msg}\n\nAsegúrate de que:\n• El archivo existe\n• El archivo no está vacío"
            )
        
        except ConnectionFailedError as e:
            # Capturar errores de conexión a URLs
            self.ui.progressBar.setValue(0)
            error_msg = str(e)
            self.log_msg(f"ERROR DE CONEXIÓN: {error_msg}")
            QtWidgets.QMessageBox.warning(
                self,
                "Error de conexión",
                f"No se pudo conectar a una o más URLs:\n\n{error_msg}\n\nVerifica que:\n• La URL sea correcta\n• Tengas conexión a internet\n• El sitio web esté disponible"
            )
        
        except ApiConnectionError as e:
            # Capturar errores de API de Google
            self.ui.progressBar.setValue(0)
            error_msg = str(e)
            self.log_msg(f"ERROR DE API: {error_msg}")
            QtWidgets.QMessageBox.critical(
                self,
                "Error de API",
                f"No se pudo conectar con la API de Google:\n\n{error_msg}\n\nVerifica que:\n• La API key sea válida\n• El modelo sea válido\n• No hayas excedido tu cuota\n• La API key no haya expirado"
            )
            
        except MissingConfigurationError as e:
            self.ui.progressBar.setValue(0)
            error_msg = str(e)
            self.log_msg(f"CONFIGURACIÓN FALTANTE: {error_msg}")
            QtWidgets.QMessageBox.critical(
                self,
                "Configuración faltante",
                f"No se pudo cargar la configuración:\n\n{error_msg}\n\nAsegúrate de que el archivo config.json esté presente y tenga la clave 'google_api_key' y 'model'."
            )
        
        except Exception as e:
            # Capturar cualquier otro error
            self.ui.progressBar.setValue(0)
            error_msg = str(e)
            self.log_msg(f"ERROR INESPERADO: {error_msg}")
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Ocurrió un error durante el procesamiento:\n\n{error_msg}"
            )


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ventana = DialogoPrincipal()
    ventana.setWindowTitle("Heritage Searcher")
    ventana.show()
    sys.exit(app.exec_())