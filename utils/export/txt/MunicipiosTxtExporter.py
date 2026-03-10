from typing import List

from models.Municipio import Municipio
from models.patrimonio.Patrimonio import Patrimonio
from models.patrimonio.TipoPatrimonio import TipoPatrimonio


class MunicipiosTxtExporter:

    def __init__(self, municipios : List[Municipio], file_name : str):
        self.municipios = municipios
        self.file_name = file_name

    def export(self):
        for municipio in self.municipios:
            with open(f'{self.file_name}.txt', 'w') as archivo:
                archivo.write(f'Lugar: {municipio.nombre}\n\n')
                for tipo_patrimonio in municipio.patrimonio:
                    lista_patrimonio : List[Patrimonio] = municipio.patrimonio[tipo_patrimonio]
                    archivo.write(f'\n{tipo_patrimonio.name}\n')
                    archivo.write(f'========================================\n')

                    for item_patrimonio in lista_patrimonio:
                        archivo.write(f' - {item_patrimonio.nombre}\n')







