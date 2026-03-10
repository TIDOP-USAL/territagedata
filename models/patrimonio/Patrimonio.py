from models.patrimonio.TipoPatrimonio import TipoPatrimonio


class Patrimonio:
    def __init__(self,
                 tipo : TipoPatrimonio = TipoPatrimonio.DESCONOCIDO,
                 subtipo = '0',
                 nombre : str = '',
                 descripcion: str = '',
                 ):
        self.tipo = tipo
        self.codigo = f'{self.tipo.value}{subtipo}'
        self.nombre = nombre
        self.descripcion = descripcion
