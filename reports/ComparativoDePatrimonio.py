from typing import List

from models.patrimonio.Patrimonio import Patrimonio
from utils.list_compare.ListComparator import ListComparator


class ComparativoDePatrimonio:
    def __init__(
            self,
            patrimonio_municipio_supervisado : List[Patrimonio],
            patrimonio_municipio_generado: List[Patrimonio],
            list_comparator : ListComparator,
    ):
        self.patrimonio_municipio_supervisado = patrimonio_municipio_supervisado
        self.patrimonio_municipio_generado = patrimonio_municipio_generado
        self.__list_comparator = list_comparator
        self.similar_elements = list_comparator.similars_unique(
            list(map(lambda patrimonio: patrimonio.nombre_municipio, self.patrimonio_municipio_supervisado)),
            list(map(lambda patrimonio: patrimonio.nombre_municipio, self.patrimonio_municipio_generado)),
        )
        self.num_items_supervisado = len(patrimonio_municipio_supervisado)
        self.num_items_generado = len(patrimonio_municipio_generado)
        self.num_coincidencias = len(self.similar_elements)
        self.tasa_coincidencias = self.__calcular_tasa_coincidencias()
        self.tasa_acierto = self.__calcular_tasa_acierto()
        self.tasa_error = self.__calcular_tasa_error()



    def __calcular_tasa_coincidencias(self):
        if self.num_coincidencias == 0 or self.num_items_generado == 0:
            return 0
        else:
            return self.num_coincidencias/self.num_items_supervisado*100

    def __calcular_tasa_acierto(self):
        if self.num_items_generado == 0 and self.num_items_supervisado == 0:
            return 100

        if self.num_items_generado == 0:
            return 0
        else:
            return self.num_coincidencias*100/self.num_items_generado

    def __calcular_tasa_error(self):
        return 100-self.tasa_acierto



