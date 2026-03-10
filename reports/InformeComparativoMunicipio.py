
from models.Municipio import Municipio
from models.patrimonio.TipoPatrimonio import TipoPatrimonio
from reports.ComparativoDePatrimonio import ComparativoDePatrimonio
from utils.list_compare.ListComparator import ListComparator


class InformeComparativoMunicipio:
    def __init__(
            self,
            municipio_supervisado : Municipio,
            municipio_generado : Municipio,
            list_comparator : ListComparator
    ):
        self.__municipio_supervisado = municipio_supervisado
        self.__municipio_generado = municipio_generado
        self.__list_comparator = list_comparator
        self.municipio = self.__municipio_supervisado
        self.comparativa_desconocido = self.__generar_comparativa(TipoPatrimonio.DESCONOCIDO)
        self.comparativa_tradicion = self.__generar_comparativa(TipoPatrimonio.TRADICION)
        self.comparativa_arqueologico = self.__generar_comparativa(TipoPatrimonio.ARQUEOLOGICO)
        self.comparativa_industrial = self.__generar_comparativa(TipoPatrimonio.INDUSTRIAL)
        self.comparativa_etnologico = self.__generar_comparativa(TipoPatrimonio.ETNOLOGICO)
        self.comparativa_ruta = self.__generar_comparativa(TipoPatrimonio.RUTA)
        self.comparativa_historico = self.__generar_comparativa(TipoPatrimonio.HISTORICO)
        self.comparativa_natural = self.__generar_comparativa(TipoPatrimonio.NATURAL)
        self.comparativa_singular = self.__generar_comparativa(TipoPatrimonio.SINGULAR)
        self.informes = []


    def __generar_comparativa(self, tipo_patrimonio : TipoPatrimonio):
        return ComparativoDePatrimonio(
            self.__municipio_supervisado.patrimonio[tipo_patrimonio],
            self.__municipio_generado.patrimonio[tipo_patrimonio],
            self.__list_comparator
        )