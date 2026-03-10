# -*- coding: utf-8 -*-
class EmptyFolderError(Exception):
    """Se lanza cuando una carpeta está vacía o no contiene archivos válidos"""
    pass


class EmptyFileError(Exception):
    """Se lanza cuando un archivo está vacío o sin contenido válido"""
    pass


class InvalidUrlDir(Exception):
    """Se lanza cuando una URL tiene formato inválido"""
    pass


class MissingConfigurationError(Exception):
    """Se lanza cuando falta configuración en config.json"""
    pass


class ConnectionFailedError(Exception):
    """Se lanza cuando falla la conexión a un sitio web"""
    pass


class RequiredFieldError(Exception):
    """Se lanza cuando falta un campo obligatorio en la interfaz"""
    pass

class ApiConnectionError(Exception):
    """Se lanza cuando hay un error de conexión con la API"""
    pass
