from models.patrimonio.Patrimonio import Patrimonio
from models.patrimonio.TipoPatrimonio import TipoPatrimonio


class Municipio:
    def __init__(
            self,
            nombre : str = '',
            codigo : str = '',
            descripcion: str = '',
    ):
        self.nombre = nombre
        self.codigo = codigo
        self.descripcion = descripcion
        self.patrimonio = {
            TipoPatrimonio.DESCONOCIDO : [],
            TipoPatrimonio.RUTA: [],
            TipoPatrimonio.NATURAL: [],
            TipoPatrimonio.SINGULAR: [],
            TipoPatrimonio.HISTORICO: [],
            TipoPatrimonio.ARQUEOLOGICO: [],
            TipoPatrimonio.ETNOLOGICO: [],
            TipoPatrimonio.INDUSTRIAL: [],
            TipoPatrimonio.TRADICION: [],
        }

    def add_patrimonio(self, patrimonio: Patrimonio):
        self.patrimonio[patrimonio.tipo].append(patrimonio)
