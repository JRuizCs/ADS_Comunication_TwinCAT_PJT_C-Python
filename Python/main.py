import customtkinter as ctk
import pyads

# Establece el esquema de colores claro para emular el entorno de trabajo industrial de Windows.
ctk.set_appearance_mode("Light")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Define el titulo de la aplicacion y las dimensiones de la ventana principal.
        self.title("Terminal ADS - Soporte Técnico")
        self.geometry("700x720")
        
        # Asigna el color de fondo principal utilizando el gris metalizado caracteristico de la interfaz.
        self.configure(fg_color="#E2E5E9")

        # Inicializa la variable destinada a retener el objeto de conexion del protocolo ADS.
        self.plc = None

        # Define una coleccion estatica con las rutas de las variables de memoria disponibles.
        self.variables_disponibles = [
            "MAIN.aBuffer",
            "MAIN.stSensor",
            "MAIN.stSensor.bActive",
            "MAIN.stSensor.nId",
            "MAIN.stSensor.fValue",
            "MAIN.stSensor.sName"
        ]

        # --- CABECERA CORPORATIVA BECKHOFF ---
        # Instancia un contenedor superior sin bordes redondeados para actuar como banner corporativo.
        self.frame_cabecera = ctk.CTkFrame(self, fg_color="#B30000", corner_radius=0, height=70)
        self.frame_cabecera.pack(fill="x", side="top")

        # Inserta el texto del logotipo con tipografia gruesa y color blanco sobre el fondo rojo.
        self.lbl_logo = ctk.CTkLabel(
            self.frame_cabecera, text="BECKHOFF", 
            font=ctk.CTkFont(family="Arial Black", size=28, weight="bold"), 
            text_color="#FFFFFF"
        )
        self.lbl_logo.pack(pady=15, padx=20, anchor="w")

        # --- PANEL SUPERIOR: CONEXION ---
        # Crea un panel blanco con borde sutil para agrupar los controles de estado de red.
        self.frame_conexion = ctk.CTkFrame(self, fg_color="#FFFFFF", border_width=1, border_color="#CCCCCC", corner_radius=5)
        self.frame_conexion.pack(pady=(20, 10), padx=20, fill="x")

        # Inicializa el boton para establecer el enlace de red, aplicando el rojo corporativo.
        self.btn_conectar = ctk.CTkButton(
            self.frame_conexion, text="Conectar a PLC", 
            fg_color="#B30000", hover_color="#8A0000", text_color="#FFFFFF",
            font=ctk.CTkFont(weight="bold"),
            command=self.conectar_plc
        )
        self.btn_conectar.pack(side="left", padx=15, pady=15)

        # Inicializa el boton para finalizar la sesion TCP/IP en estado inactivo con color gris neutro.
        self.btn_desconectar = ctk.CTkButton(
            self.frame_conexion, text="Desconectar", 
            fg_color="#999999", hover_color="#777777", text_color="#FFFFFF",
            state="disabled", font=ctk.CTkFont(weight="bold"),
            command=self.desconectar_plc
        )
        self.btn_desconectar.pack(side="left", padx=5, pady=15)

        # --- PANEL CENTRAL: SELECCION Y LECTURA ---
        # Instancia un contenedor intermedio blanco para la interaccion de lectura de datos.
        self.frame_lectura = ctk.CTkFrame(self, fg_color="#FFFFFF", border_width=1, border_color="#CCCCCC", corner_radius=5)
        self.frame_lectura.pack(pady=10, padx=20, fill="x")

        self.lbl_seleccion = ctk.CTkLabel(self.frame_lectura, text="1. Seleccionar Variable y Puntero (Opcional):", text_color="#333333", font=ctk.CTkFont(weight="bold"))
        self.lbl_seleccion.pack(pady=(15, 5), padx=15, anchor="w")

        self.frame_input_seleccion = ctk.CTkFrame(self.frame_lectura, fg_color="transparent")
        self.frame_input_seleccion.pack(pady=5, padx=15, fill="x")

        # Crea un menu desplegable para seleccionar la variable raiz, adaptado al modo claro.
        self.menu_variables = ctk.CTkOptionMenu(
            self.frame_input_seleccion, 
            values=self.variables_disponibles,
            width=280,
            fg_color="#F0F0F0", button_color="#E0E0E0", button_hover_color="#D0D0D0", text_color="#000000"
        )
        self.menu_variables.pack(side="left")

        # Configura una caja de texto para capturar el indice especifico si la variable objetivo es un array.
        self.entry_indice = ctk.CTkEntry(
            self.frame_input_seleccion, 
            placeholder_text="Índice (Ej: 0)", 
            width=120,
            fg_color="#FFFFFF", text_color="#000000", border_color="#CCCCCC"
        )
        self.entry_indice.pack(side="left", padx=10)

        # Vincula el boton de accion para ejecutar la extraccion de datos, utilizando un azul estandar de ingenieria.
        self.btn_leer = ctk.CTkButton(
            self.frame_lectura, text="Leer Selección", 
            fg_color="#0066CC", hover_color="#004C99", text_color="#FFFFFF", font=ctk.CTkFont(weight="bold"),
            command=self.ejecutar_lectura
        )
        self.btn_leer.pack(pady=(10, 15), padx=15, anchor="w")

        # --- PANEL INFERIOR: ESCRITURA ---
        # Instancia el contenedor inferior responsable de procesar e inyectar valores en memoria.
        self.frame_escritura = ctk.CTkFrame(self, fg_color="#FFFFFF", border_width=1, border_color="#CCCCCC", corner_radius=5)
        self.frame_escritura.pack(pady=10, padx=20, fill="x")

        self.lbl_escritura = ctk.CTkLabel(self.frame_escritura, text="2. Escribir Nuevo Valor:", text_color="#333333", font=ctk.CTkFont(weight="bold"))
        self.lbl_escritura.pack(pady=(15, 5), padx=15, anchor="w")

        self.frame_input_escritura = ctk.CTkFrame(self.frame_escritura, fg_color="transparent")
        self.frame_input_escritura.pack(pady=5, padx=15, fill="x")

        # Configura la caja de entrada para la recepcion del dato a inyectar en memoria.
        self.entry_valor = ctk.CTkEntry(
            self.frame_input_escritura, 
            placeholder_text="Introduzca el nuevo valor...", 
            fg_color="#FFFFFF", text_color="#000000", border_color="#CCCCCC"
        )
        self.entry_valor.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Vincula el boton de confirmacion con el metodo de parseo, utilizando un verde estandar de confirmacion.
        self.btn_escribir = ctk.CTkButton(
            self.frame_input_escritura, text="Escribir Selección", 
            fg_color="#00802B", hover_color="#006622", text_color="#FFFFFF", width=140, font=ctk.CTkFont(weight="bold"),
            command=self.ejecutar_escritura
        )
        self.btn_escribir.pack(side="right")

        # --- PANEL DE DIAGNOSTICO (LOG) ---
        # Configura el visor de texto empleando fondo oscuro y texto claro para contrastar como una terminal de sistema.
        self.txt_log = ctk.CTkTextbox(
            self, height=180, 
            font=ctk.CTkFont(family="Consolas", size=13),
            fg_color="#1E1E1E", text_color="#E0E0E0", border_width=2, border_color="#333333"
        )
        self.txt_log.pack(pady=(10, 20), padx=20, fill="both", expand=True)
        self.txt_log.insert("0.0", "Interfaz industrial inicializada. Esperando conexión ADS...\n")
        self.txt_log.configure(state="disabled")

        # Intercepta el evento de cierre de ventana para invocar la limpieza del socket.
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    def log(self, mensaje):
        # Deshabilita temporalmente la proteccion del visor para añadir nuevos registros.
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f"> {mensaje}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def conectar_plc(self):
        try:
            # Construye el objeto de comunicacion definiendo la ruta y el puerto del Runtime objetivo.
            self.plc = pyads.Connection('10.55.128.28.1.1', 851)
            self.plc.open()

            # Permuta la accesibilidad de la botonera tras validar el estado del socket logico.
            if self.plc.is_open:
                self.log("[OK] Enlace establecido con el controlador.")
                self.btn_conectar.configure(state="disabled", fg_color="#E0E0E0")
                self.btn_desconectar.configure(state="normal", fg_color="#B30000", hover_color="#8A0000")
        except Exception as e:
            self.log(f"[ERROR] Fallo de conexion de red: {e}")

    def desconectar_plc(self):
        # Valida el estado activo del socket antes de ejecutar el cierre por protocolo TCP.
        if self.plc and self.plc.is_open:
            self.plc.close()
            self.log("[INFO] Comunicacion terminada por instruccion manual.")

            # Restituye el aspecto inicial de la botonera corporativa.
            self.btn_conectar.configure(state="normal", fg_color="#B30000", hover_color="#8A0000")
            self.btn_desconectar.configure(state="disabled", fg_color="#999999")

    def obtener_variable_objetivo(self):
        # Extrae la seleccion principal y evalua la presencia de un indice en la caja de texto contigua.
        variable_base = self.menu_variables.get()
        indice_str = self.entry_indice.get().strip()

        # Concatena la notacion de corchetes si se define un puntero, delegando la resolucion al router ADS.
        if indice_str:
            return f"{variable_base}[{indice_str}]"
        
        return variable_base

    def ejecutar_lectura(self):
        if not self.plc or not self.plc.is_open:
            self.log("[ERROR] Requiere conexion activa al PLC.")
            return

        variable_objetivo = self.obtener_variable_objetivo()

        try:
            # Extrae la estructura descriptiva completa del simbolo alojado en el sistema remoto.
            simbolo = self.plc.get_symbol(variable_objetivo)
            
            # Efectua una transaccion de lectura bloqueante sobre el bloque de memoria recien mapeado.
            valor_leido = simbolo.read()

            self.log(f"[LECTURA] {variable_objetivo} = {valor_leido}")
        except pyads.ADSError as e:
            self.log(f"[ERROR ADS] Falla al resolver el simbolo {variable_objetivo}: {e}")
        except Exception as e:
            self.log(f"[ERROR SISTEMA] {e}")

    def ejecutar_escritura(self):
        if not self.plc or not self.plc.is_open:
            self.log("[ERROR] Requiere conexion activa al PLC.")
            return

        valor_str = self.entry_valor.get().strip()
        if not valor_str:
            self.log("[ADVERTENCIA] El campo de valor no puede estar vacio.")
            return

        variable_objetivo = self.obtener_variable_objetivo()

        try:
            # Construye la representacion logica del simbolo para determinar su tipo estructural o nativo.
            simbolo = self.plc.get_symbol(variable_objetivo)

            # Verifica si el objetivo resultante es una matriz y ajusta el empaquetado iterativo del dato.
            if isinstance(simbolo.value, (list, tuple)):
                longitud_array = len(simbolo.value)
                valor_evaluado = eval(valor_str)
                
                if isinstance(valor_evaluado, (list, tuple)):
                    # Garantiza la consistencia dimensional descartando listas de longitud despareja.
                    if len(valor_evaluado) != longitud_array:
                        self.log(f"[ERROR] El array requiere exactamente {longitud_array} elementos.")
                        return
                    valor_final = list(valor_evaluado)
                else:
                    # Rellena el bloque secuencial iterando el valor escalar provisto de manera uniforme.
                    valor_final = [valor_evaluado] * longitud_array
            else:
                # Transforma el formato del dato crudo al tipo de dato nativo requerido por IEC 61131-3.
                if simbolo.symbol_type == 'BOOL':
                    valor_final = valor_str.lower() in ['true', '1', 't', 'yes']
                elif simbolo.symbol_type in ['INT', 'DINT', 'SINT', 'USINT', 'UINT', 'UDINT', 'WORD', 'DWORD']:
                    valor_final = int(valor_str)
                elif simbolo.symbol_type in ['REAL', 'LREAL']:
                    valor_final = float(valor_str)
                elif 'STRING' in simbolo.symbol_type:
                    valor_final = str(valor_str)
                else:
                    # Aplica parseo de expresion dinamica para la inyeccion de enumeradores u otros objetos de sistema.
                    valor_final = eval(valor_str)

            # Ejecuta la sobrescritura del objeto validado directamente en el segmento de memoria remota.
            simbolo.write(valor_final)
            self.log(f"[ESCRITURA EXITO] {variable_objetivo} actualizado a: {valor_final}")
            
            # Limpia los campos de entrada visuales una vez completada y verificada la instruccion.
            self.entry_valor.delete(0, 'end')

        except pyads.ADSError as e:
            self.log(f"[ERROR ADS] Operacion rechazada por la capa fisica o logica del Runtime: {e}")
        except ValueError:
            self.log(f"[ERROR CASTING] Imposible instanciar '{valor_str}' en el formato requerido de {simbolo.symbol_type}.")
        except Exception as e:
            self.log(f"[ERROR SISTEMA] Excepcion critica durante la evaluacion en tiempo de ejecucion: {e}")

    def cerrar_aplicacion(self):
        # Destruye ordenadamente el hilo del socket TCP activo antes del cierre definitivo de la aplicacion grafica.
        if self.plc and self.plc.is_open:
            self.plc.close()
        self.destroy()

if __name__ == "__main__":
    # Inicializa el motor de la interfaz grafica y desplaza el control al bucle manejador de eventos asincrono.
    app = App()
    app.mainloop()