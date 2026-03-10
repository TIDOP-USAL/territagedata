import json
import sys
from pathlib import Path

from exceptions import MissingConfigurationError


def get_api_key():
    """Obtiene la API key desde config.json"""
    # Si es .exe, buscar en el directorio del ejecutable
    if getattr(sys, "frozen", False):
        config_path = Path(sys.executable).parent / "config.json"
    else:
        # Si es script, buscar en el directorio raíz del proyecto
        config_path = Path(__file__).parent / "config.json"

    if not config_path.exists():
        raise MissingConfigurationError(
            f"No se encontró el archivo de configuración: {config_path}"
        )

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise MissingConfigurationError(
            f"config.json tiene un error de formato: {str(e)}"
        )

    if "google_api_key" not in config:
        raise MissingConfigurationError(
            "Falta la clave 'google_api_key' en config.json"
        )

    api_key = config["google_api_key"].strip()

    if not api_key:
        raise MissingConfigurationError(
            "La clave 'google_api_key' en config.json está vacía."
        )
        
    return api_key


def get_model():
    """Obtiene el modelo desde config.json"""
    # Si es .exe, buscar en el directorio del ejecutable
    if getattr(sys, "frozen", False):
        config_path = Path(sys.executable).parent / "config.json"
    else:
        # Si es script, buscar en el directorio raíz del proyecto
        config_path = Path(__file__).parent / "config.json"

    if not config_path.exists():
        raise MissingConfigurationError(
            f"No se encontró el archivo de configuración: {config_path}"
        )

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise MissingConfigurationError(
            f"config.json tiene un error de formato: {str(e)}"
        )
        
    # Validar que modelo existe
    if 'model' not in config:
        raise MissingConfigurationError(
            "Falta la clave 'model' en config.json"
        )
    
    model = config['model'].strip()
    
    # Validar que no está vacío
    if not model:
        raise MissingConfigurationError(
            "El campo 'model' está vacío en config.json"
        )
        
    return model
