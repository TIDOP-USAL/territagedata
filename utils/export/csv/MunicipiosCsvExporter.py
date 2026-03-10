from typing import List

from models.Municipio import Municipio
from models.patrimonio.Patrimonio import Patrimonio
from models.patrimonio.TipoPatrimonio import TipoPatrimonio


class MunicipiosCsvExporter:

    def __init__(self, municipios : List[Municipio], file_name : str):
        self.municipios = municipios
        self.file_name = file_name

    def export(self):
        for municipio in self.municipios:
            patrimonios = [
                municipio.patrimonio[TipoPatrimonio.DESCONOCIDO],
                municipio.patrimonio[TipoPatrimonio.TRADICION],
                municipio.patrimonio[TipoPatrimonio.ARQUEOLOGICO],
                municipio.patrimonio[TipoPatrimonio.INDUSTRIAL],
                municipio.patrimonio[TipoPatrimonio.ETNOLOGICO],
                municipio.patrimonio[TipoPatrimonio.RUTA],
                municipio.patrimonio[TipoPatrimonio.HISTORICO],
                municipio.patrimonio[TipoPatrimonio.NATURAL],
                municipio.patrimonio[TipoPatrimonio.SINGULAR]
            ]

            with open(f'{self.file_name}.csv', 'w') as archivo:
                archivo.write('id;nombre;municipio;cod_municipio;tipo;subtipo;nombre_tipo;\n')
                for lista in patrimonios:
                    for patrimonio in lista:
                        archivo.write(self.__componer_cadena_csv(municipio, patrimonio))



    def __componer_cadena_csv(self, municipio : Municipio, patrimonio: Patrimonio):
        return f';{patrimonio.nombre};{municipio.nombre};{municipio.codigo};{patrimonio.tipo.value};;{patrimonio.tipo.name};\n'
