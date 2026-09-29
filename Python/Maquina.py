import customtkinter as ctk
import tkinter as tk
import pyads
from datetime import datetime

# Configuración del esquema de color general de la interfaz gráfica.
ctk.set_appearance_mode("Light")

class HmiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Definición de las propiedades geométricas y título de la ventana principal.
        self.title("TwinCAT HMI")
        self.geometry("1100x820")
        self.configure(fg_color="#E2E5E9")
        self.plc = None

        # Inicialización del contenedor superior para la cabecera corporativa.
        self.frame_cabecera = ctk.CTkFrame(self, fg_color="#B30000", corner_radius=0, height=70)
        self.frame_cabecera.pack(fill="x", side="top")
        
        self.lbl_logo = ctk.CTkLabel(
            self.frame_cabecera, text="BECKHOFF", 
            font=ctk.CTkFont(family="Arial Black", size=26, weight="bold"), text_color="#FFFFFF"
        )
        self.lbl_logo.pack(pady=15, padx=20, anchor="w")

        # Implementación del sistema de navegación por pestañas simplificado (Principal y Alarmas).
        self.tabview = ctk.CTkTabview(self, fg_color="transparent", segmented_button_selected_color="#B30000")
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tab_principal = self.tabview.add("PRINCIPAL")
        self.tab_alarmas = self.tabview.add("ALARMAS")

        # Invocación de los métodos de construcción de las pantallas de la aplicación.
        self._construir_pestana_principal()
        self._construir_pestana_alarmas()

        # Vinculación del evento de cierre de ventana y arranque de la conexión de red.
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)
        self.iniciar_conexion()

    def _construir_pestana_principal(self):
        # Configuración de la estructura de filas y columnas de la pestaña principal.
        self.tab_principal.grid_columnconfigure(0, weight=5)
        self.tab_principal.grid_columnconfigure(1, weight=4)
        self.tab_principal.grid_rowconfigure(0, weight=3)
        self.tab_principal.grid_rowconfigure(1, weight=2)

        # -------------------------------------------------------------
        # SECCIÓN IZQUIERDA: SINÓPTICO GRÁFICO DEL EJE
        # -------------------------------------------------------------
        self.frame_grafico = ctk.CTkFrame(self.tab_principal, fg_color="#FFFFFF", border_width=1, border_color="#CCCCCC")
        self.frame_grafico.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        self.lbl_titulo_sinoptico = ctk.CTkLabel(self.frame_grafico, text="Sinóptico de Eje Lineal", text_color="#333333", font=ctk.CTkFont(weight="bold", size=16))
        self.lbl_titulo_sinoptico.pack(pady=10, padx=15, anchor="w")

        self.canvas = tk.Canvas(self.frame_grafico, width=500, height=220, bg="#F5F6F7", highlightthickness=1, highlightbackground="#CCCCCC")
        self.canvas.pack(pady=5, padx=15)

        self.canvas.create_line(50, 110, 450, 110, width=6, fill="#A0A0A0")
        pos_x = [50, 183, 316, 450]
        nombres = ["S_HOME", "S_MID1", "S_MID2", "S_END"]
        self.leds = []

        for i in range(4):
            x = pos_x[i]
            self.canvas.create_rectangle(x-10, 90, x+10, 130, fill="#555555", outline="#333333")
            led = self.canvas.create_oval(x-10, 150, x+10, 170, fill="#333333", outline="#222222")
            self.canvas.create_text(x, 185, text=nombres[i], font=("Arial", 9, "bold"), fill="#555555")
            self.leds.append(led)

        self.carro_movil = self.canvas.create_rectangle(20, 80, 80, 105, fill="#005A9E", outline="#003366", width=2)
        self.txt_posicion_carro = self.canvas.create_text(50, 65, text="0.0 mm", font=("Arial", 10, "bold"), fill="#005A9E")

        # -------------------------------------------------------------
        # SECCIÓN DERECHA: PANEL DE CONTROL Y ACCIONAMIENTOS
        # -------------------------------------------------------------
        self.frame_control = ctk.CTkFrame(self.tab_principal, fg_color="#FFFFFF", border_width=1, border_color="#CCCCCC")
        self.frame_control.grid(row=0, column=1, sticky="nsew", pady=(0, 10))

        self.frame_modo = ctk.CTkFrame(self.frame_control, fg_color="#F0F0F0")
        self.frame_modo.pack(fill="x", padx=15, pady=10)
        
        self.switch_modo = ctk.CTkSwitch(
            self.frame_modo, text="MODO MANUAL", command=self.cambiar_modo,
            progress_color="#005A9E", button_color="#333333", font=ctk.CTkFont(weight="bold")
        )
        self.switch_modo.pack(pady=6, padx=10, anchor="w")

        self.switch_continuo = ctk.CTkSwitch(
            self.frame_modo, text="MODO CONTINUO", command=self.cambiar_continuo,
            progress_color="#FF8C00", button_color="#333333", font=ctk.CTkFont(weight="bold")
        )
        self.switch_continuo.pack(pady=6, padx=10, anchor="w")

        self.btn_start = ctk.CTkButton(
            self.frame_control, text="MARCHA (START)", fg_color="#00802B", hover_color="#006622",
            font=ctk.CTkFont(weight="bold", size=13), height=35,
            command=lambda: self.escribir_variable("GVL_HMI.bCmdStart", True, pyads.PLCTYPE_BOOL)
        )
        self.btn_start.pack(fill="x", padx=15, pady=3)

        self.btn_stop = ctk.CTkButton(
            self.frame_control, text="PARO (STOP)", fg_color="#E3000F", hover_color="#B30000",
            font=ctk.CTkFont(weight="bold", size=13), height=35,
            command=lambda: self.escribir_variable("GVL_HMI.bCmdStop", True, pyads.PLCTYPE_BOOL)
        )
        self.btn_stop.pack(fill="x", padx=15, pady=3)

        self.btn_reset_seq = ctk.CTkButton(
            self.frame_control, text="RESET SEC. (A ORIGEN)", fg_color="#FF8C00", hover_color="#CC7000",
            font=ctk.CTkFont(weight="bold", size=13), height=35, text_color="#FFFFFF",
            command=lambda: self.escribir_variable("GVL_HMI.bCmdResetSeq", True, pyads.PLCTYPE_BOOL)
        )
        self.btn_reset_seq.pack(fill="x", padx=15, pady=3)

        self.frame_jog = ctk.CTkFrame(self.frame_control, fg_color="transparent")
        self.frame_jog.pack(fill="x", padx=15, pady=3)

        self.btn_jog_bwd = ctk.CTkButton(self.frame_jog, text="◄ JOG [-]", fg_color="#777777", font=ctk.CTkFont(weight="bold", size=12), height=32, state="disabled")
        self.btn_jog_bwd.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        self.btn_jog_fwd = ctk.CTkButton(self.frame_jog, text="JOG [+] ►", fg_color="#777777", font=ctk.CTkFont(weight="bold", size=12), height=32, state="disabled")
        self.btn_jog_fwd.pack(side="right", fill="x", expand=True, padx=(2, 0))

        self.btn_jog_bwd.bind("<ButtonPress-1>", lambda e: self.escribir_jog("GVL_HMI.bCmdJogBwd", True))
        self.btn_jog_bwd.bind("<ButtonRelease-1>", lambda e: self.escribir_jog("GVL_HMI.bCmdJogBwd", False))
        self.btn_jog_fwd.bind("<ButtonPress-1>", lambda e: self.escribir_jog("GVL_HMI.bCmdJogFwd", True))
        self.btn_jog_fwd.bind("<ButtonRelease-1>", lambda e: self.escribir_jog("GVL_HMI.bCmdJogFwd", False))

        self.slider_speed = ctk.CTkSlider(self.frame_control, from_=0, to=100, command=self.actualizar_velocidad, button_color="#555555", progress_color="#B30000")
        self.slider_speed.set(50)
        self.slider_speed.pack(pady=8, padx=15, fill="x")

        # -------------------------------------------------------------
        # SECCIÓN INFERIOR: HISTÓRICO DE EVENTOS INTEGRADO EN PRINCIPAL
        # -------------------------------------------------------------
        self.frame_log_main = ctk.CTkFrame(self.tab_principal, fg_color="#FFFFFF", border_width=1, border_color="#CCCCCC")
        self.frame_log_main.grid(row=1, column=0, columnspan=2, sticky="nsew")

        ctk.CTkLabel(self.frame_log_main, text="Histórico de Eventos y Comandos", font=ctk.CTkFont(weight="bold", size=12), text_color="#333333").pack(pady=5, padx=15, anchor="w")

        self.txt_log = ctk.CTkTextbox(self.frame_log_main, height=110, font=("Consolas", 11), fg_color="#1E1E1E", text_color="#00FF00")
        self.txt_log.pack(pady=5, padx=15, fill="both", expand=True)
        self.txt_log.insert("0.0", "HMI Inicializada con eventos en pantalla principal.\n")
        self.txt_log.configure(state="disabled")

    def _construir_pestana_alarmas(self):
        # Configuración de la pantalla dedicada a la gestión de alarmas y estados críticos.
        frame_alarma_cont = ctk.CTkFrame(self.tab_alarmas, fg_color="#FFFFFF", border_width=1, border_color="#CCCCCC")
        frame_alarma_cont.pack(fill="both", expand=True, padx=20, pady=20)

        self.lbl_banner_estado = ctk.CTkLabel(
            frame_alarma_cont, text="ESTADO: DESCONECTADO", 
            font=ctk.CTkFont(size=20, weight="bold"), text_color="#999999"
        )
        self.lbl_banner_estado.pack(pady=40)

        self.btn_reset = ctk.CTkButton(
            frame_alarma_cont, text="REARMAR ALARMAS (ACK)", fg_color="#005A9E", hover_color="#004578",
            font=ctk.CTkFont(weight="bold", size=16), height=45, width=250,
            command=lambda: self.escribir_variable("GVL_HMI.bCmdReset", True, pyads.PLCTYPE_BOOL)
        )
        self.btn_reset.pack(pady=20)

    def registrar_log(self, mensaje):
        # Inserción de nuevas líneas de auditoría cronológica en el cuadro de texto.
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {mensaje}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def iniciar_conexion(self):
        # Establecimiento del enlace de red ADS con el Runtime del autómata programable.
        try:
            self.plc = pyads.Connection('10.55.128.28.1.1', 851)
            self.plc.open()
            if self.plc.is_open:
                self.registrar_log("Conexión ADS operativa.")
                modo_manual = self.plc.read_by_name("GVL_HMI.bModeManual", pyads.PLCTYPE_BOOL)
                modo_continuo = self.plc.read_by_name("GVL_HMI.bModeContinuous", pyads.PLCTYPE_BOOL)
                
                if modo_manual: self.switch_modo.select()
                if modo_continuo: self.switch_continuo.select()
                
                self.gestionar_interfaz_modo(modo_manual)
                self.slider_speed.set(self.plc.read_by_name("GVL_HMI.nSimSpeed", pyads.PLCTYPE_INT))
                self.actualizar_hmi()
        except Exception as e:
            self.registrar_log(f"Error de red: {e}")
            self.lbl_banner_estado.configure(text="ERROR DE COMUNICACIÓN", text_color="#E3000F")

    def cambiar_modo(self):
        # Envío de consigna de conmutación entre modo automático y manual.
        es_manual = self.switch_modo.get() == 1
        self.escribir_variable("GVL_HMI.bModeManual", es_manual, pyads.PLCTYPE_BOOL)
        self.gestionar_interfaz_modo(es_manual)
        self.registrar_log(f"Modo Operación: {'MANUAL' if es_manual else 'AUTOMÁTICO'}")

    def cambiar_continuo(self):
        # Envío de consigna para conmutar entre ciclo paso a paso y ciclo continuo.
        es_continuo = self.switch_continuo.get() == 1
        self.escribir_variable("GVL_HMI.bModeContinuous", es_continuo, pyads.PLCTYPE_BOOL)
        self.registrar_log(f"Ciclo Automático: {'CONTINUO' if es_continuo else 'PASO A PASO'}")

    def gestionar_interfaz_modo(self, es_manual):
        # Modificación dinámica de la habilitación de componentes gráficos según el modo.
        if es_manual:
            self.btn_start.configure(state="disabled", fg_color="#EEEEEE")
            self.btn_stop.configure(state="disabled", fg_color="#EEEEEE")
            self.btn_reset_seq.configure(state="disabled", fg_color="#EEEEEE")
            self.btn_jog_fwd.configure(state="normal", fg_color="#005A9E")
            self.btn_jog_bwd.configure(state="normal", fg_color="#005A9E")
        else:
            self.btn_start.configure(state="normal", fg_color="#00802B")
            self.btn_stop.configure(state="normal", fg_color="#E3000F")
            self.btn_reset_seq.configure(state="normal", fg_color="#FF8C00")
            self.btn_jog_fwd.configure(state="disabled", fg_color="#777777")
            self.btn_jog_bwd.configure(state="disabled", fg_color="#777777")

    def escribir_variable(self, nombre, valor, tipo):
        # Escritura síncrona de datos orientada a variables del PLC por nombre de símbolo.
        if self.plc and self.plc.is_open:
            try:
                self.plc.write_by_name(nombre, valor, tipo)
                if "Jog" not in nombre: self.registrar_log(f"Comando: {nombre} -> {valor}")
            except Exception as e:
                self.registrar_log(f"Error ADS ({nombre}): {e}")

    def escribir_jog(self, nombre_var, estado):
        # Envío de pulsaciones de tipo hombre muerto para la traslación manual.
        if self.switch_modo.get() == 1: self.escribir_variable(nombre_var, estado, pyads.PLCTYPE_BOOL)

    def actualizar_velocidad(self, valor):
        # Actualización de la consigna analógica de velocidad de simulación.
        self.escribir_variable("GVL_HMI.nSimSpeed", int(valor), pyads.PLCTYPE_INT)

    def actualizar_hmi(self):
        # Bucle periódico de lectura de variables y refresco gráfico de elementos del sinóptico.
        if self.plc and self.plc.is_open:
            try:
                estado = self.plc.read_by_name("GVL_HMI.nState", pyads.PLCTYPE_INT)
                posicion = self.plc.read_by_name("GVL_HMI.fPosition", pyads.PLCTYPE_REAL)
                alarma = self.plc.read_by_name("GVL_HMI.bAlarmActive", pyads.PLCTYPE_BOOL)
                msg = self.plc.read_by_name("GVL_HMI.sAlarmMsg", pyads.PLCTYPE_STRING)
                
                sensores = [
                    self.plc.read_by_name("GVL_HMI.bSensorHome", pyads.PLCTYPE_BOOL),
                    self.plc.read_by_name("GVL_HMI.bSensorMid1", pyads.PLCTYPE_BOOL),
                    self.plc.read_by_name("GVL_HMI.bSensorMid2", pyads.PLCTYPE_BOOL),
                    self.plc.read_by_name("GVL_HMI.bSensorEnd", pyads.PLCTYPE_BOOL)
                ]

                if alarma:
                    self.lbl_banner_estado.configure(text=f"ALARMA: {msg}", text_color="#FFFFFF", fg_color="#E3000F")
                else:
                    self.lbl_banner_estado.configure(fg_color="transparent")
                    if estado == 30: self.lbl_banner_estado.configure(text="ESTADO: MODO JOG ACTIVO", text_color="#005A9E")
                    elif estado == 0: self.lbl_banner_estado.configure(text="ESTADO: REPOSO (Esperando Start)", text_color="#333333")
                    elif 10 <= estado <= 14: self.lbl_banner_estado.configure(text=f"ESTADO: AVANCE ACTIVO (Paso {estado})", text_color="#00802B")
                    elif estado == 20: self.lbl_banner_estado.configure(text="ESTADO: FINAL ALCANZADO", text_color="#005A9E")
                    elif estado == 21: self.lbl_banner_estado.configure(text="ESTADO: RETORNANDO A ORIGEN...", text_color="#FF8C00")

                x_px = 50 + (min(max(posicion, 0.0), 1000.0) / 1000.0) * 400.0
                self.canvas.coords(self.carro_movil, x_px - 30, 80, x_px + 30, 105)
                self.canvas.coords(self.txt_posicion_carro, x_px, 65)
                self.canvas.itemconfig(self.txt_posicion_carro, text=f"{posicion:.1f} mm")

                for i, estado_sensor in enumerate(sensores):
                    self.canvas.itemconfig(self.leds[i], fill="#00E600" if estado_sensor else "#333333")

            except Exception: pass
        self.after(50, self.actualizar_hmi)

    def cerrar_aplicacion(self):
        # Liberación de recursos y desconexión segura del socket TCP antes de destruir la ventana.
        if self.plc and self.plc.is_open: self.plc.close()
        self.destroy()

if __name__ == "__main__":
    app = HmiApp()
    app.mainloop()
