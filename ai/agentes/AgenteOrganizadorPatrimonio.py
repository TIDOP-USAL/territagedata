import json

from models.Municipio import Municipio
from models.patrimonio.Patrimonio import Patrimonio
from models.patrimonio.TipoPatrimonio import TipoPatrimonio


def get_tipo_patrimonio(num):
    result = TipoPatrimonio.DESCONOCIDO
    for tipo in TipoPatrimonio:
        if tipo.value == num:
            result = tipo
    return result


class AgenteOrganizadorPatrimonio:
    def __init__(self, ai_assistant, text_to_organize : str, municipio : Municipio):
        self.ai_assistant = ai_assistant
        self.text_to_organize = text_to_organize
        self.response = ""
        self.municipio = municipio
        self.new_municipio = Municipio()

    def get_organized(self):
        self.response = self.ai_assistant.get_response(request=f"""
                                                    Eres un organizador de información que da la salida en formato json.'
                                                    Te voy a proporcionar la estructura json, las categorias y posteriormente el texto para clasificar por categoría'
                                                    los elementos que contiene, sin que se repitan, es decir, no debe agregarse un elemento si ya existe otro elemento con el mismo nombre. Te indico las categorías y'
                                                    qué tipo de elementos corresponden, posteriormente te proporciono el texto.'


                                                    Usa el siguiente esquema conceptual JSON:

                                                    Item = {{ 'nombre':'str' }}
                                                    Category = 'int':'list[Item]'
                                                    return = list[Category]

                                                    Las categorías son las siguientes, en primer lugar el número correspondiente al nombre y segundo el tipo de elementos:
                                                    {TipoPatrimonio.TRADICION.value}: que incluye tradiciones, fiestas religiosas, fiestas o festivales, gastronomía, tradiciones orales, peñas sacra,
                                                    {TipoPatrimonio.ARQUEOLOGICO.value}: que incluye Yacimientos y centros de interpretación,
                                                    {TipoPatrimonio.INDUSTRIAL.value}: que incluye Molinos de harina o agua, canteras y talleres artesanales,
                                                    {TipoPatrimonio.ETNOLOGICO.value}: que incluye Potros de herrar, chozos de pastores y patrimonio artístico',
                                                    {TipoPatrimonio.RUTA.value}: que incluye caminos históricos, calzadas, rutas y cañadas reales,
                                                    {TipoPatrimonio.HISTORICO.value}: que incluye Castillos, ermitas, iglesias, rollos, montasterios,conventos, museos, imaginarios religiosos, fuentes, lavaderos y puentes históricos,
                                                    {TipoPatrimonio.NATURAL.value}: que incluye Activos geológicos, cauces de ríos, entorno natural, picos montañosos y stelariums,
                                                    {TipoPatrimonio.SINGULAR.value}: que incluye miradores, manantiales, árboles singulares, zonas de escalada,

                                                    El texto a analizar es el siguiente:
                                                    {self.text_to_organize}
                                                    """)

        new_municipio = Municipio(
            nombre=self.municipio.nombre,
            codigo=self.municipio.codigo,
            descripcion=self.municipio.descripcion
        )

        json_data = json.loads(self.response.replace('\n', '').replace('```json', '').replace('```', ''))
        for item_categoria in json_data:
            for key, value in item_categoria.items():
                for item in value:
                    patrimonio = Patrimonio(
                        tipo=get_tipo_patrimonio(key),
                        nombre=item['nombre'],
                    )
                    new_municipio.add_patrimonio(patrimonio)

        self.new_municipio = new_municipio

        return new_municipio