# gui/interfaz.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from motor.simulador import correr_simulacion_playa

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ─── Paleta ────────────────────────────────────────────────────────────────────
BG_DARK    = "#0f1117"
BG_MID     = "#161b27"
BG_CARD    = "#1c2233"
BG_INPUT   = "#222840"
ACCENT     = "#f5c842"
ACCENT2    = "#3b82f6"
GREEN      = "#22c55e"
RED        = "#ef4444"
SKY        = "#38bdf8"
ORANGE     = "#f97316"
MUTED      = "#4b5563"
TEXT       = "#e2e8f0"
TEXT2      = "#94a3b8"
BORDER     = "#2a3347"

# ─── Colores por tipo de evento (tags de Treeview) ─────────────────────────────
TAG_LLEGADA   = "#22c55e"
TAG_FIN_EST   = "#38bdf8"
TAG_FIN_COBRO = "#f97316"
TAG_INICIO    = "#6b7280"
TAG_RECHAZADO = "#ef4444"
TAG_BLOQUEADO = "#f59e0b"


class AppSimulacion(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simulación — Playa de Estacionamiento Privada")
        self.geometry("1560x800")
        self.minsize(1200, 650)
        self.configure(fg_color=BG_DARK)

        self.vector_completo = []

        self._build_treeview_style()
        self._build_layout()

    # ── Estilo Treeview ────────────────────────────────────────────────────────
    def _build_treeview_style(self):
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Sim.Treeview",
            background=BG_CARD,
            foreground=TEXT2,
            fieldbackground=BG_CARD,
            rowheight=24,
            borderwidth=0,
            relief="flat",
            font=("JetBrains Mono", 9) if self._font_exists("JetBrains Mono") else ("Courier New", 9),
        )
        style.configure("Sim.Treeview.Heading",
            background=BG_MID,
            foreground=TEXT2,
            relief="flat",
            borderwidth=0,
            font=("Segoe UI", 8, "bold"),
        )
        style.map("Sim.Treeview",
            background=[("selected", "#1e3a5f")],
            foreground=[("selected", TEXT)],
        )
        style.configure("Sim.Vertical.TScrollbar",
            background=BG_MID, troughcolor=BG_DARK,
            borderwidth=0, arrowsize=12)
        style.configure("Sim.Horizontal.TScrollbar",
            background=BG_MID, troughcolor=BG_DARK,
            borderwidth=0, arrowsize=12)

    def _font_exists(self, name):
        try:
            import tkinter.font as tkfont
            return name in tkfont.families()
        except Exception:
            return False

    # ── Layout principal ───────────────────────────────────────────────────────
    def _build_layout(self):
        # ── Sidebar ──────────────────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, width=270, corner_radius=0,
                                    fg_color=BG_MID, border_width=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Título sidebar
        title_frame = ctk.CTkFrame(self.sidebar, fg_color=BG_DARK, corner_radius=0)
        title_frame.pack(fill="x")
        ctk.CTkLabel(title_frame, text="🅿", font=ctk.CTkFont(size=28),
                     text_color=ACCENT).pack(pady=(20, 0))
        ctk.CTkLabel(title_frame, text="Playa de\nEstacionamiento",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=TEXT).pack()
        ctk.CTkLabel(title_frame, text="SIMULACIÓN DE EVENTOS DISCRETOS",
                     font=ctk.CTkFont(size=8),
                     text_color=MUTED).pack(pady=(2, 16))

        # Separador
        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER, corner_radius=0).pack(fill="x")

        # Configuración
        cfg_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        cfg_frame.pack(fill="x", padx=16, pady=8)

        ctk.CTkLabel(cfg_frame, text="PARÁMETROS",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=MUTED).pack(anchor="w", pady=(0, 4))

        self.entry_x = self._input(cfg_frame, "Tiempo máximo X (min)", "500")
        self.entry_n = self._input(cfg_frame, "Iteraciones máximas (N)", "100000")
        self.entry_j = self._input(cfg_frame, "Mostrar desde minuto (j)", "0")
        self.entry_i = self._input(cfg_frame, "Cantidad de filas (i)", "50")
        self.entry_tlleg = self._input(cfg_frame, "Tiempo entre llegadas (min)", "13")
        #corregidos
        self.entradas_prob_tipo = self._input_row(cfg_frame, "Prob. Auto (%) [Peq/Gra/Uti]", ["45", "25", "30"])
        self.entradas_prob_tiempo = self._input_row(cfg_frame, "Prob. Hs (%) [1h/2h/3h/4h]", ["50", "30", "15", "5"])

        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER, corner_radius=0).pack(fill="x")

        # Botón
        btn_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        btn_frame.pack(fill="x", padx=16, pady=10)
        self.btn_simular = ctk.CTkButton(
            btn_frame,
            text="▶   Correr Simulación",
            command=self.ejecutar,
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=ACCENT,
            hover_color="#d4a832",
            text_color=BG_DARK,
        )
        self.btn_simular.pack(fill="x")

        ctk.CTkFrame(self.sidebar, height=1, fg_color=BORDER, corner_radius=0).pack(fill="x")

        # Resultados
        res_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        res_frame.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(res_frame, text="RESULTADOS FINALES",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=MUTED).pack(anchor="w", pady=(0, 4))

        self.txt_resultados = ctk.CTkLabel(
            res_frame,
            text="—\n—",
            justify="left",
            font=ctk.CTkFont(size=11),
            text_color=TEXT2,
            anchor="w",
            wraplength=230,
        )
        self.txt_resultados.pack(anchor="w")

        # ── Panel derecho ─────────────────────────────────────────────────────
        right = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        right.pack(side="right", fill="both", expand=True)

        # Header del panel
        header = ctk.CTkFrame(right, fg_color=BG_MID, corner_radius=0, height=52)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(
            header,
            text="Vector de Estado  —  Servidor con Identificación de Vehículos",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=TEXT,
        ).pack(side="left", padx=20, pady=14)

        self.lbl_rowcount = ctk.CTkLabel(header, text="", font=ctk.CTkFont(size=11),
                                          text_color=ACCENT)
        self.lbl_rowcount.pack(side="right", padx=20)

        # Leyenda de colores
        legend = ctk.CTkFrame(right, fg_color=BG_MID, corner_radius=0, height=28)
        legend.pack(fill="x")
        legend.pack_propagate(False)
        for txt, color in [("● Llegada", TAG_LLEGADA), ("● Fin Estacionamiento", TAG_FIN_EST),
                           ("● Fin Cobro", TAG_FIN_COBRO), ("● Bloqueado", TAG_BLOQUEADO),
                           ("● Rechazado", TAG_RECHAZADO), ("● Inicio", TAG_INICIO)]:
            ctk.CTkLabel(legend, text=txt, font=ctk.CTkFont(size=9),
                         text_color=color).pack(side="left", padx=10)

        # Separador
        ctk.CTkFrame(right, height=1, fg_color=BORDER, corner_radius=0).pack(fill="x")

        # Tabla
        self._build_table(right)

        # Statusbar
        statusbar = ctk.CTkFrame(right, fg_color=BG_MID, corner_radius=0, height=28)
        statusbar.pack(fill="x", side="bottom")
        statusbar.pack_propagate(False)
        self.lbl_status = ctk.CTkLabel(statusbar, text="● Listo",
                                        font=ctk.CTkFont(size=9), text_color=MUTED)
        self.lbl_status.pack(side="left", padx=16)
        self.lbl_status_extra = ctk.CTkLabel(statusbar, text="",
                                              font=ctk.CTkFont(size=9), text_color=MUTED)
        self.lbl_status_extra.pack(side="left")

    # ── Helper input ──────────────────────────────────────────────────────────
    def _input(self, parent, label, default):
        ctk.CTkLabel(parent, text=label,
                     font=ctk.CTkFont(size=10), text_color=TEXT2).pack(anchor="w", pady=(4, 0))
        entry = ctk.CTkEntry(
            parent,
            height=30,
            corner_radius=6,
            border_width=1,
            border_color=BORDER,
            fg_color=BG_INPUT,
            text_color=TEXT,
            font=ctk.CTkFont(size=11, family="Courier New"),
        )
        entry.insert(0, default)
        entry.pack(fill="x", pady=(0, 2))
        return entry
    
    def _input_row(self, parent, label, defaults):
        ctk.CTkLabel(parent, text=label,
                     font=ctk.CTkFont(size=10), text_color=TEXT2).pack(anchor="w", pady=(4, 0))
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 2))

        entries = []
        for default in defaults:
            entry = ctk.CTkEntry(
                row_frame,
                height=30,
                width=40,         # <--- CORRECCIÓN: Ancho base pequeño para evitar el desborde
                justify="center", # <--- CORRECCIÓN: Centramos el texto para que se vea mejor
                corner_radius=6,
                border_width=1,
                border_color=BORDER,
                fg_color=BG_INPUT,
                text_color=TEXT,
                font=ctk.CTkFont(size=11, family="Courier New"),
            )
            entry.insert(0, default)
            entry.pack(side="left", expand=True, fill="x", padx=2) # padx=2 separa un poquito las cajas
            entries.append(entry)
        return entries

        ctk.CTkLabel(parent, text=label,
                     font=ctk.CTkFont(size=10), text_color=TEXT2).pack(anchor="w", pady=(4, 0))
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", pady=(0, 2))

        entries = []
        for default in defaults:
            entry = ctk.CTkEntry(
                row_frame,
                height=30,
                corner_radius=6,
                border_width=1,
                border_color=BORDER,
                fg_color=BG_INPUT,
                text_color=TEXT,
                font=ctk.CTkFont(size=11, family="Courier New"),
            )
            entry.insert(0, default)
            entry.pack(side="left", expand=True, fill="x", padx=1)
            entries.append(entry)
        return entries

    # ── Tabla ─────────────────────────────────────────────────────────────────
    def _build_table(self, parent):
        # Se agrega "cant_bloq" a la tupla base
        columnas_base = (
            "pos", "evento", "reloj", "rnd_t", "tipo",
            "rnd_e", "t_est", "tmp_lleg", "prox_lleg",
            "est_playa", "cap", "caja1", "auto_cobro",
            "fin_cobro", "caja2", "cola", "monto_cobrado", "recaudacion", 
            "acum_bloqueo", "cant_bloq"
        )
        columnas_sectores = tuple(f"sec_{i}" for i in range(1, 11))
        self.columnas = columnas_base + columnas_sectores

        table_frame = ctk.CTkFrame(parent, fg_color=BG_DARK, corner_radius=0)
        table_frame.pack(fill="both", expand=True, padx=0, pady=0)

        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", style="Sim.Horizontal.TScrollbar")
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical",   style="Sim.Vertical.TScrollbar")

        self.tabla = ttk.Treeview(
            table_frame,
            columns=self.columnas,
            show="headings",
            style="Sim.Treeview",
            xscrollcommand=scroll_x.set,
            yscrollcommand=scroll_y.set,
        )

        scroll_x.config(command=self.tabla.xview)
        scroll_y.config(command=self.tabla.yview)
        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right",  fill="y")
        self.tabla.pack(fill="both", expand=True)

        encabezados = {
            "pos":           ("N° Fila",              60),
            "evento":        ("Evento",               120),
            "reloj":         ("Reloj (min)",           90),
            "rnd_t":         ("RND Tipo",              80),
            "tipo":          ("Tipo / Id Auto",        120),
            "rnd_e":         ("RND Est.",              80),
            "t_est":         ("Tiempo Est.",           85),
            "tmp_lleg":      ("T. Entre Llegadas",     110),
            "prox_lleg":     ("Próx. Llegada",         100),
            "est_playa":     ("Playa",                 80),
            "cap":           ("Cant. Autos",           85),
            "caja1":         ("Servidor",              85),
            "auto_cobro":    ("AUTO EN COBRO",         160),
            "fin_cobro":     ("Fin Cobro",             90),
            "caja2":         ("Espacio Cola",          95),
            "cola":          ("AUTO EN COLA",          160),
            "monto_cobrado": ("Tarifa Vehículo",       110),
            "recaudacion":   ("Recaudación Acum.",     130),
            "acum_bloqueo":  ("Tiempo Bloq. Acum.",    130),
            "cant_bloq":     ("Cant. Bloqueados",      120),
        }

        for col, (texto, w) in encabezados.items():
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=w, minwidth=w, anchor="center")

        for i in range(1, 11):
            col_name = f"sec_{i}"
            self.tabla.heading(col_name, text=f"Sector {i}")
            self.tabla.column(col_name, width=155, minwidth=120, anchor="center")

        # Tags de color por evento
        self.tabla.tag_configure("tag_llegada",   foreground=TAG_LLEGADA)
        self.tabla.tag_configure("tag_fin_est",   foreground=TAG_FIN_EST)
        self.tabla.tag_configure("tag_fin_cobro", foreground=TAG_FIN_COBRO)
        self.tabla.tag_configure("tag_inicio",    foreground=TAG_INICIO)
        self.tabla.tag_configure("tag_rechazado", foreground=TAG_RECHAZADO)
        self.tabla.tag_configure("tag_bloqueado", foreground=TAG_BLOQUEADO)
        self.tabla.tag_configure("row_odd",       background="#191f2e")
        self.tabla.tag_configure("row_even",      background=BG_CARD)

        self.tabla.bind("<ButtonRelease-1>", self.on_fila_clic)

    # ── Validar un campo numérico ─────────────────────────────────────────────
    def _validar_campo(self, entry, nombre, permite_cero=False):
        errores = []
        texto = entry.get().strip()

        if texto == "":
            errores.append(f"• {nombre}: no puede estar vacío.")
            return None, errores

        try:
            valor = float(texto)
        except ValueError:
            errores.append(
                f"• {nombre}: solo se permiten números (sin letras ni caracteres especiales)."
            )
            return None, errores

        if valor < 0:
            errores.append(f"• {nombre}: no puede ser negativo.")
        elif valor == 0 and not permite_cero:
            errores.append(f"• {nombre}: no puede ser 0.")

        return valor, errores

    # ── Ejecutar simulación ───────────────────────────────────────────────────
    def ejecutar(self):
        errores_totales = []

        x, errs = self._validar_campo(self.entry_x, "Tiempo máximo X")
        errores_totales.extend(errs)

        n_val, errs = self._validar_campo(self.entry_n, "Iteraciones máximas N")
        errores_totales.extend(errs)

        j, errs = self._validar_campo(self.entry_j, "Mostrar desde minuto j", permite_cero=True)
        errores_totales.extend(errs)

        i_val, errs = self._validar_campo(self.entry_i, "Cantidad de filas i")
        errores_totales.extend(errs)

        t_lleg, errs = self._validar_campo(self.entry_tlleg, "Tiempo entre llegadas")
        errores_totales.extend(errs)

        # --- VALIDAR PROB. TIPOS DE AUTO ---
        probs_tipo_num = []
        nombres_tipo = ["Prob Peq", "Prob Gra", "Prob Uti"]
        for entry, nombre in zip(self.entradas_prob_tipo, nombres_tipo):
            val, errs = self._validar_campo(entry, nombre, permite_cero=True)
            errores_totales.extend(errs)
            if val is not None: probs_tipo_num.append(val)

        if len(probs_tipo_num) == 3 and round(sum(probs_tipo_num), 2) != 100:
            errores_totales.append("• Las probabilidades de Tipo deben sumar exactamente 100%.")

        # --- VALIDAR PROB. TIEMPOS DE ESTACIONAMIENTO ---
        probs_tiempo_num = []
        nombres_tiempo = ["Prob 1h", "Prob 2h", "Prob 3h", "Prob 4h"]
        for entry, nombre in zip(self.entradas_prob_tiempo, nombres_tiempo):
            val, errs = self._validar_campo(entry, nombre, permite_cero=True)
            errores_totales.extend(errs)
            if val is not None: probs_tiempo_num.append(val)

        if len(probs_tiempo_num) == 4 and round(sum(probs_tiempo_num), 2) != 100:
            errores_totales.append("• Las probabilidades de Tiempo deben sumar exactamente 100%.")

        # Cortar ejecución si hay errores
        if errores_totales:
            messagebox.showerror(
                "Error de validación",
                "Corregí los siguientes campos:\n\n" + "\n".join(errores_totales),
            )
            return

        x = float(x)
        n = int(n_val)
        j = float(j)
        i_filas = int(i_val)
        t_lleg = float(t_lleg)
        
        # Convertir a decimales para el motor
        probs_tipo_dec = [p / 100.0 for p in probs_tipo_num]
        probs_tiempo_dec = [p / 100.0 for p in probs_tiempo_num]

        self.btn_simular.configure(state="disabled", text="Simulando...")
        self.lbl_status.configure(text="● Simulando...", text_color=ACCENT)
        self.update()

        # --- LLAMADA AL MOTOR ACTUALIZADA ---
        self.vector_completo = correr_simulacion_playa(x, n, t_lleg, probs_tipo_dec, probs_tiempo_dec)
        
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        # ... (Sigue igual a partir de la lógica de filtrado de filas) ...

        # Filtrar filas
        filas_filtradas = []
        contador = 0
        for fila in self.vector_completo:
            if fila["reloj"] >= j and contador < i_filas:
                filas_filtradas.append(fila)
                contador += 1

        ultima_fila = self.vector_completo[-1]
        if ultima_fila not in filas_filtradas:
            filas_filtradas.append(ultima_fila)

        for idx, f in enumerate(filas_filtradas):
            fc = f["fin_cobro_lugar_1"] if f["fin_cobro_lugar_1"] is not None else "-"

            if f["auto_en_cobro"] is not None:
                ac = f["auto_en_cobro"]
                auto_cobro = f"{ac['id']} [{ac['tipo'][:3]}] {ac['horas']}h"
            else:
                auto_cobro = "-"

            if f["auto_esperando"] is not None:
                ae = f["auto_esperando"]
                auto_espera = f"{ae['id']} [{ae['tipo'][:3]}] {ae['horas']}h"
            else:
                auto_espera = "-"

            monto_f = f"${f['monto_cobrado']:.2f}" if isinstance(f.get("monto_cobrado"), (int, float)) else "-"
            recaud_f = f"${f['recaudacion_total']:.2f}"
            
            # Se agrega la variable "cant_autos_bloqueados_total" al final del array
            valores_fila = [
                f["posicion"], f["evento"], f["reloj"],
                f["rnd_tipo"], f["tipo_vehiculo"],
                f["rnd_tiempo_est"], f["tiempo_est"],
                f["tiempo_entre_llegadas"], f["proxima_llegada"],
                f["estado_playa"], f["capacidad_actual"],
                f["estado_lugar_1"], auto_cobro,
                fc, f["estado_lugar_2"], auto_espera,
                monto_f, recaud_f,
                f"{f['acumulador_tiempo_bloqueo']:.2f}",
                f["cant_autos_bloqueados_total"] # <--- NUEVO CONTADOR VISIBLE
            ]

            for i in range(1, 11):
                sec = f["sectores"][i]
                if sec["estado"] == "Estacionado":
                    texto_celda = f"{sec['id_auto']} [{sec['tipo_auto'][:3]}] F:{sec['fin']}"
                elif sec["estado"] == "Bloqueado":
                    texto_celda = f"{sec['id_auto']} BLOQUEADO"
                else:
                    texto_celda = "Libre"
                valores_fila.append(texto_celda)

            # Determinar tags
            ev = f["evento"].lower()
            tags = []
            if ev == "llegada":
                tags.append("tag_llegada")
            elif ev.startswith("fin_est"):
                tags.append("tag_fin_est")
            elif ev == "fin_cobro":
                tags.append("tag_fin_cobro")
            elif ev == "inicio":
                tags.append("tag_inicio")

            if f["tipo_vehiculo"] == "RECHAZADO":
                tags.append("tag_rechazado")

            bloqueado = any(
                s["estado"] == "Bloqueado" for s in f["sectores"].values()
            )
            if bloqueado:
                tags.append("tag_bloqueado")

            tags.append("row_odd" if idx % 2 else "row_even")

            self.tabla.insert("", "end", iid=f["posicion"],
                              values=valores_fila, tags=tags)

        # Resultados en sidebar
        tiempo_total_simulado  = ultima_fila["reloj"]
        recaudacion            = ultima_fila["recaudacion_total"]
        tiempo_ocupacion       = ultima_fila["acumulador_tiempo_ocupacion"]
        capacidad_maxima_tiempo = tiempo_total_simulado * 10
        porc_utilizacion = (tiempo_ocupacion / capacidad_maxima_tiempo * 100) if capacidad_maxima_tiempo > 0 else 0
        tiempo_bloqueo     = ultima_fila["acumulador_tiempo_bloqueo"]
        autos_bloqueados   = ultima_fila["cant_autos_bloqueados_total"]
        promedio_espera_bloqueo = (tiempo_bloqueo / autos_bloqueados) if autos_bloqueados > 0 else 0

        texto_sidebar = (
            f"Tiempo Simulado:\n  {tiempo_total_simulado} min\n"
            f"a) Recaudación Total:\n  ${recaudacion:,.2f}\n"
            f"b) Utilización Playa:\n  {porc_utilizacion:.2f}%\n"
            f"c) Prom. Espera Cobro:\n  {promedio_espera_bloqueo:.2f} min ({autos_bloqueados} bloqueados)"
        )
        self.txt_resultados.configure(text=texto_sidebar)

        total_filas = len(self.vector_completo)
        self.lbl_rowcount.configure(text=f"{total_filas} eventos totales  ·  {len(filas_filtradas)} mostradas")
        self.lbl_status.configure(text="● Simulación completada", text_color=GREEN)
        self.lbl_status_extra.configure(
            text=f"   Bloqueados: {autos_bloqueados}  ·  "
                 f"Ocup. acum.: {tiempo_ocupacion:.1f} min  ·  "
                 f"Vehículos llegados: {ultima_fila['cant_vehiculos_llegados']}  ·  "
                 f"Rechazados: {ultima_fila['cant_vehiculos_rechazados']}"
        )
        self.btn_simular.configure(state="normal", text="▶   Correr Simulación")

    # ── Detalle al hacer clic en una fila ─────────────────────────────────────
    def on_fila_clic(self, event):
        item_id = self.tabla.focus()
        if not item_id:
            return
        fila_selec = next(
            (f for f in self.vector_completo if str(f["posicion"]) == item_id), None
        )
        if not fila_selec:
            return

        ventana = ctk.CTkToplevel(self)
        ventana.title(f"Detalle — Fila {fila_selec['posicion']}")
        ventana.geometry("540x420")
        ventana.attributes("-topmost", True)
        ventana.configure(fg_color=BG_DARK)
        ventana.resizable(False, False)

        # Header
        header = ctk.CTkFrame(ventana, fg_color=BG_MID, corner_radius=0, height=52)
        header.pack(fill="x")
        header.pack_propagate(False)
        ctk.CTkLabel(header,
                     text=f"Fila {fila_selec['posicion']}  ·  {fila_selec['evento']}  ·  Reloj: {fila_selec['reloj']} min",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=ACCENT).pack(side="left", padx=16, pady=14)

        ctk.CTkFrame(ventana, height=1, fg_color=BORDER, corner_radius=0).pack(fill="x")

        # Contenido
        scroll_frame = ctk.CTkScrollableFrame(ventana, fg_color=BG_DARK, corner_radius=0)
        scroll_frame.pack(fill="both", expand=True, padx=0, pady=0)

        ctk.CTkLabel(scroll_frame,
                     text="ESTADO DE SECTORES",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=MUTED).pack(anchor="w", padx=20, pady=(14, 6))

        algun_ocupado = False
        for sec_id, datos in fila_selec["sectores"].items():
            if datos["estado"] != "Libre":
                algun_ocupado = True
                if datos["estado"] == "Bloqueado":
                    color = TAG_BLOQUEADO
                    icono = "⚠"
                else:
                    color = TAG_FIN_EST
                    icono = "🚗"

                row = ctk.CTkFrame(scroll_frame, fg_color=BG_CARD, corner_radius=6)
                row.pack(fill="x", padx=16, pady=3)

                ctk.CTkLabel(row,
                             text=f"  {icono}  Sector {sec_id}",
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=color, width=110, anchor="w").pack(side="left", padx=(10, 0), pady=8)
                ctk.CTkLabel(row,
                             text=f"{datos['estado']}",
                             font=ctk.CTkFont(size=10),
                             text_color=color, width=90, anchor="w").pack(side="left")
                ctk.CTkLabel(row,
                             text=f"{datos['id_auto']}  ({datos['tipo_auto']})",
                             font=ctk.CTkFont(size=10),
                             text_color=TEXT2, width=160, anchor="w").pack(side="left")
                ctk.CTkLabel(row,
                             text=f"Fin: {datos['fin']} min",
                             font=ctk.CTkFont(size=10, family="Courier New"),
                             text_color=TEXT2).pack(side="left", padx=(0, 12))

        if not algun_ocupado:
            ctk.CTkLabel(scroll_frame,
                         text="Todos los sectores están libres en este instante.",
                         font=ctk.CTkFont(size=11),
                         text_color=MUTED).pack(pady=30)

        # Info de cobro
        ctk.CTkFrame(scroll_frame, height=1, fg_color=BORDER, corner_radius=0).pack(fill="x", padx=16, pady=(12, 6))
        ctk.CTkLabel(scroll_frame,
                     text="ZONA DE COBRO",
                     font=ctk.CTkFont(size=9, weight="bold"),
                     text_color=MUTED).pack(anchor="w", padx=20, pady=(0, 6))

        cobro_row = ctk.CTkFrame(scroll_frame, fg_color=BG_CARD, corner_radius=6)
        cobro_row.pack(fill="x", padx=16, pady=(0, 16))
        cobro_row.columnconfigure((0, 1, 2), weight=1)

        for col, (lbl, val) in enumerate([
            ("Caja (Lugar 1)", fila_selec["estado_lugar_1"]),
            (
                "Auto en Cobro",
                f"{fila_selec['auto_en_cobro']['id']} ({fila_selec['auto_en_cobro']['tipo'][:3]}) {fila_selec['auto_en_cobro']['horas']}h"
                if fila_selec["auto_en_cobro"] is not None
                else "-"
            ),
            (
                "Auto en Cola",
                f"{fila_selec['auto_esperando']['id']} ({fila_selec['auto_esperando']['tipo'][:3]}) {fila_selec['auto_esperando']['horas']}h"
                if fila_selec["auto_esperando"] is not None
                else "-"
            ),
        ]):
            cell = ctk.CTkFrame(cobro_row, fg_color="transparent")
            cell.grid(row=0, column=col, padx=14, pady=10, sticky="w")
            ctk.CTkLabel(cell, text=lbl,
                         font=ctk.CTkFont(size=9), text_color=MUTED).pack(anchor="w")
            ctk.CTkLabel(cell, text=val,
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=SKY).pack(anchor="w")