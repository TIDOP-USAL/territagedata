from exceptions import ConnectionFailedError, ApiConnectionError

consulta_especifica = "más destacado, zonas de interés, arqueología, patrimonio cultural o religioso, gastronomía, fiestas, rutas, etc"

class AgenteRecopilador:
    def __init__(
            self,
            agente_ficheros,
            agente_web,
            nombre_municipio,
            url_list = [],
            log_callback=lambda msg: None,
            task_completed_callback=lambda: None
    ):
        self.agente_ficheros = agente_ficheros
        self.agente_web = agente_web
        self.nombre_municipio = nombre_municipio
        self.target_urls = url_list
        self.log_callback = log_callback
        self.task_completed_callback = task_completed_callback

    def recopilar(self):

        ## Busqueda en ficheros
        self.log_callback("Procesando ficheros")

        try:
            request = f"únicamente del contenido del fichero, extrae todo el contenido relacionado con {self.nombre_municipio}. Si no hay, devuelve una respuesta vacía."
            file_responses_generic = self.agente_ficheros.get_response(request=request)
            #self.task_completed_callback()

            request = f"únicamente del contenido del fichero, extrae todo el contenido {consulta_especifica} relacionado con {self.nombre_municipio}. Si no hay, devuelve una respuesta vacía."
            file_responses_specific = self.agente_ficheros.get_response(request=request)
            #self.task_completed_callback()

            self.log_callback("Ficheros finalizado")
            
        except ApiConnectionError:
            # Re-lanzar errores de API para que lleguen a main_window
            raise

        ## Busqueda en webs especificas
        self.log_callback("Procesando urls web")
        web_responses = []
        for url in self.target_urls:
            try:
                request = f"busca todo lo relacionado con {self.nombre_municipio} en esta web: {url}"
                web_responses.append(self.agente_web.get_response(request=request))
                self.task_completed_callback()

                request = f"En relación a {self.nombre_municipio}, busca en esta web: {url}, todo lo {consulta_especifica}"
                web_responses.append(self.agente_web.get_response(request=request))
                self.task_completed_callback()

                self.log_callback(f"✅ Procesada Url: {url}")
                
            except ApiConnectionError:
                # Re-lanzar errores de API (credenciales inválidas, etc) para que lleguen a main_window
                raise
                
            except Exception as e:
                # Si falla la conexión a una URL específica, registrar y continuar con las demás
                error_msg = f"Error al procesar {url}: {str(e)}"
                self.log_callback(error_msg)
                # Marcar las tareas como completadas aunque fallen para actualizar progreso
                self.task_completed_callback()
                self.task_completed_callback()
                # Si es un error crítico de conexión, continuar pero avisar
                if "connection" in str(e).lower() or "timeout" in str(e).lower():
                    self.log_callback(f"No se pudo conectar a {url}. Continuando con el siguiente...")

        self.log_callback("Urls web finalizado")

        ## Busqueda en web global
        self.log_callback("Procesando búsqueda web")

        request = f"En relación a {self.nombre_municipio} quiero saber todo lo {consulta_especifica}"
        web_responses.append(self.agente_web.get_response(request=request))
        self.task_completed_callback()

        self.log_callback("Búsqueda web finalizado")

        return file_responses_generic + file_responses_specific + web_responses

    def get_num_tasks(self):
        num_files = len(self.agente_ficheros.file_path_list)*2
        num_urls = len(self.target_urls)*2
        num_global_search = 1

        return num_files + num_urls + num_global_search