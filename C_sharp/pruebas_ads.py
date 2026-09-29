import customtkinter as ctk
import pyads
import ctypes

# Establece la apariencia general y el tema de color para la interfaz grafica.
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Define la estructura de datos con alineacion en memoria empaquetada a 1 byte para coincidir con la disposicion del PLC.
class ST_SensorData(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        # Representa el estado de activacion del sensor mediante un booleano estandar de C (1 byte).
        ("bActive", ctypes.c_bool),
        # Almacena el identificador numerico del sensor en un entero con signo de 16 bits (INT).
        ("nId", ctypes.c_int16),
        # Almacena el valor de lectura en un numero de coma flotante de 32 bits (REAL).
        ("fValue", ctypes.c_float),
        # Reserva 81 bytes continuos para alojar una cadena de texto STRING(80) y su terminador nulo.
        ("sName", ctypes.c_char * 81),
        # Embebe un array de 5 elementos numericos enteros de 16 bits.
        ("aValues", ctypes.c_int16 * 5)
    ]

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configura las dimensiones y el titulo de la ventana principal del sistema.
        self.title("Monitor ADS - TwinCAT 3")
        self.geometry("600x550")

        # Inicializa la variable para almacenar la instancia de la conexion ADS.
        self.plc = None

        # --- SECCION: CONEXION ---
        self.frame_conexion = ctk.CTkFrame(self)
        self.frame_conexion.pack(pady=10, padx=20, fill="x")

        self.btn_conectar = ctk.CTkButton(self.frame_conexion, text="Conectar a PLC", command=self.conectar_plc)
        self.btn_conectar.pack(pady=10)

        # --- SECCION: CONTROL DE ARRAY ---
        self.frame_array = ctk.CTkFrame(self)
        self.frame_array.pack(pady=10, padx=20, fill="x")
        
        self.lbl_array = ctk.CTkLabel(self.frame_array, text="Gestión de MAIN.aBuffer", font=ctk.CTkFont(weight="bold"))
        self.lbl_array.pack(pady=5)

        self.btn_leer_array = ctk.CTkButton(self.frame_array, text="Leer Array Completo", command=self.leer_array)
        self.btn_leer_array.pack(side="left", padx=20, pady=10)

        self.btn_escribir_array = ctk.CTkButton(self.frame_array, text="Escribir 999 en aBuffer[0]", command=self.escribir_array)
        self.btn_escribir_array.pack(side="right", padx=20, pady=10)

        # --- SECCION: CONTROL DE ESTRUCTURA ---
        self.frame_struct = ctk.CTkFrame(self)
        self.frame_struct.pack(pady=10, padx=20, fill="x")

        self.lbl_struct = ctk.CTkLabel(self.frame_struct, text="Gestión de MAIN.stSensor", font=ctk.CTkFont(weight="bold"))
        self.lbl_struct.pack(pady=5)

        self.btn_leer_struct = ctk.CTkButton(self.frame_struct, text="Leer Estructura", command=self.leer_estructura)
        self.btn_leer_struct.pack(side="left", padx=20, pady=10)

        self.btn_escribir_struct = ctk.CTkButton(self.frame_struct, text="Conmutar y Modificar Estructura", command=self.escribir_estructura)
        self.btn_escribir_struct.pack(side="right", padx=20, pady=10)

        # --- SECCION: REGISTRO DE EVENTOS (LOG) ---
        self.textbox_log = ctk.CTkTextbox(self, width=560, height=150)
        self.textbox_log.pack(pady=10, padx=20)
        self.textbox_log.insert("0.0", "Sistema inicializado. Esperando conexión...\n")

        # Mapea el evento de cierre de ventana a una funcion para asegurar la liberacion de recursos.
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    def log(self, mensaje):
        # Inserta una nueva linea de texto al final del cuadro de registro y desplaza la vista hacia abajo.
        self.textbox_log.insert("end", f"{mensaje}\n")
        self.textbox_log.see("end")

    def conectar_plc(self):
        try:
            # Crea la instancia de conexion pasando el AMS Net ID de destino y el puerto especifico del Runtime.
            self.plc = pyads.Connection('10.55.128.28.1.1', 851)
            
            # Abre el socket TCP/IP asociado al router ADS.
            self.plc.open()
            
            # Valida que el canal de comunicacion se haya establecido correctamente.
            if self.plc.is_open:
                self.btn_conectar.configure(text="Conectado", fg_color="green", state="disabled")
                self.log("[OK] Conexión ADS establecida correctamente.")
        except Exception as e:
            self.log(f"[Error] Fallo al conectar: {e}")

    def leer_array(self):
        if not self.plc or not self.plc.is_open:
            self.log("[Error] El sistema no está conectado al PLC.")
            return

        try:
            # Ejecuta la lectura sincrona solicitando 10 elementos consecutivos de tipo DINT (entero de 32 bits).
            buffer = self.plc.read_by_name("MAIN.aBuffer", pyads.PLCTYPE_DINT * 10)
            self.log(f"[Lectura] aBuffer: {list(buffer)}")
        except Exception as e:
            self.log(f"[Error] Fallo en lectura de array: {e}")

    def escribir_array(self):
        if not self.plc or not self.plc.is_open:
            return

        try:
            # Extrae el array actual de la memoria del controlador logico.
            buffer = self.plc.read_by_name("MAIN.aBuffer", pyads.PLCTYPE_DINT * 10)
            
            # Modifica localmente el valor del primer elemento de la matriz.
            buffer[0] = 999
            
            # Sobrescribe el bloque de memoria completo en el entorno de ejecucion de TwinCAT.
            self.plc.write_by_name("MAIN.aBuffer", buffer, pyads.PLCTYPE_DINT * 10)
            self.log("[Escritura] Valor 999 asignado a MAIN.aBuffer[0].")
        except Exception as e:
            self.log(f"[Error] Fallo en escritura de array: {e}")

    def leer_estructura(self):
        if not self.plc or not self.plc.is_open:
            return

        try:
            # Lee el segmento de memoria asociado al simbolo y lo decodifica usando la clase de estructura definida con ctypes.
            sensor = self.plc.read_structure_by_name("MAIN.stSensor", ST_SensorData)
            
            # Decodifica la cadena de bytes de C a una cadena de texto UTF-8 estándar de Python.
            nombre = sensor.sName.decode('utf-8')
            valores = list(sensor.aValues)
            
            self.log(f"[Lectura] MAIN.stSensor -> bActive: {sensor.bActive}, nId: {sensor.nId}, sName: '{nombre}', aValues: {valores}")
        except Exception as e:
            self.log(f"[Error] Fallo en lectura de estructura: {e}")

    def escribir_estructura(self):
        if not self.plc or not self.plc.is_open:
            return

        try:
            # Extrae la estructura de datos actual para mantener intactos los campos que no se desean alterar.
            sensor = self.plc.read_structure_by_name("MAIN.stSensor", ST_SensorData)
            
            # Invierte el estado logico del atributo booleano.
            sensor.bActive = not sensor.bActive
            
            # Actualiza el identificador numerico asignando una constante estandarizada.
            sensor.nId = 1024
            
            # Modifica la cadena de texto codificandola previamente al estandar de bytes requerido por C.
            sensor.sName = b"Python_CTK_Sensor"
            
            # Escribe la modificacion sobre el primer elemento del array anidado en la estructura.
            sensor.aValues[0] = 77
            
            # Transmite la estructura serializada completa de vuelta al servidor ADS.
            self.plc.write_structure_by_name("MAIN.stSensor", sensor, ST_SensorData)
            self.log(f"[Escritura] Estructura modificada. Nuevo estado bActive: {sensor.bActive}")
        except Exception as e:
            self.log(f"[Error] Fallo en escritura de estructura: {e}")

    def cerrar_aplicacion(self):
        # Valida el estado del socket antes de forzar el cierre de la sesion.
        if self.plc and self.plc.is_open:
            # Libera el puerto local desconectando el canal ADS.
            self.plc.close()
            print("Conexion ADS cerrada.")
        
        # Destruye la instancia de la ventana principal y detiene el hilo de la interfaz grafica.
        self.destroy()

if __name__ == "__main__":
    # Instancia y arranca el ciclo principal de eventos del framework CustomTkinter.
    app = App()
    app.mainloop()