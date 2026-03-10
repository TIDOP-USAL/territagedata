import csv

from models.Municipio import Municipio
from models.patrimonio.Patrimonio import Patrimonio
from models.patrimonio.TipoPatrimonio import TipoPatrimonio


class CsvDataSource:

    NOMBRE_PATRIMONIO = 1
    COD_MUNICIPIO = 3
    NOMBRE_MUNICIPIO = 2
    TIPO_PATRIMONIO = 4
    SUBTIPO_PATRIMONIO = 5

    def __init__(self, csv_file_path):
        self.csv_file = csv_file_path

    def get_municipio(self, cod_municipio) -> Municipio:

        municipio = Municipio()

        with open(self.csv_file, mode='r', newline='', encoding='utf-8') as archivo:
            lector_csv = csv.reader(archivo, delimiter=';')

            next(lector_csv)
            for fila in lector_csv:
                if cod_municipio == str(fila[self.COD_MUNICIPIO]):
                    municipio.nombre = fila[self.NOMBRE_MUNICIPIO]
                    patrimonio = Patrimonio(
                        tipo = self.__convert_tipo_patrimonio(fila[self.TIPO_PATRIMONIO]),
                        subtipo = str(fila[self.SUBTIPO_PATRIMONIO]),
                        nombre = fila[self.NOMBRE_PATRIMONIO],
                    )
                    municipio.add_patrimonio(patrimonio)


        return municipio

    def __convert_tipo_patrimonio(self, tipo_patrimonio):
        tipos={
            '0': TipoPatrimonio.DESCONOCIDO,
            '1': TipoPatrimonio.TRADICION,
            '2': TipoPatrimonio.ARQUEOLOGICO,
            '3': TipoPatrimonio.INDUSTRIAL,
            '4': TipoPatrimonio.ETNOLOGICO,
            '5': TipoPatrimonio.RUTA,
            '6': TipoPatrimonio.HISTORICO,
            '7': TipoPatrimonio.NATURAL,
            '8': TipoPatrimonio.SINGULAR
        }
        if tipo_patrimonio not in tipos:
            return TipoPatrimonio.DESCONOCIDO
        return tipos[tipo_patrimonio]
