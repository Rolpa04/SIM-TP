# gui/interfaz.py
import customtkinter as ctk
from tkinter import ttk, messagebox
from motor.simulador import correr_simulacion_playa

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AppSimulacion(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Simulación - Playa de Estacionamiento Privada")
        self.geometry("1300x700") # Un poco más ancha para que entren los sectores
        
        self.vector_completo = []

        # --- PANEL IZQUIERDO: PARÁMETROS ---
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="Configuración TP", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        # Inputs Parametrizables
        self.entry_x = self.crear_input("Tiempo Máximo a Simular (X minutos):", "500")
        self.entry_n = self.crear_input("Máximo de Iteraciones (N):", "100000")
        self.entry_j = self.crear_input("Mostrar desde hora/minuto (j):", "100")
        self.entry_i = self.crear_input("Cantidad de filas a mostrar (i):", "50")

        # Botón para simular
        self.btn_simular = ctk.CTkButton(self.sidebar, text="Correr Simulación", command=self.ejecutar)
        self.btn_simular.pack(fill="x", padx=20, pady=20)
        
        # Panel de Resultados Estadísticos
        self.lbl_res = ctk.CTkLabel(self.sidebar, text="Resultados Finales:", font=ctk.CTkFont(weight="bold"), justify="left")
        self.lbl_res.pack(anchor="w", padx=20, pady=(20, 0))
        self.txt_resultados = ctk.CTkLabel(self.sidebar, text="-\n-", justify="left")
        self.txt_resultados.pack(anchor="w", padx=20)

        # --- PANEL DERECHO: TABLA DEL VECTOR DE ESTADO ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.main_frame, text="Vector de Estado con Estado de Sectores 1-10", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)

        # Configuración de las Columnas de la Tabla (Columnas base + 10 Sectores)
        columnas_base = ("pos", "evento", "reloj", "rnd_t", "tipo", "rnd_e", "t_est", "prox_lleg", "est_playa", "cap", "caja1", "caja2", "cola")
        columnas_sectores = tuple(f"sec_{i}" for i in range(1, 11))
        self.columnas = columnas_base + columnas_sectores
        
        # Añadimos barras de desplazamiento (Scrollbars) porque ahora la tabla es ancha
        scroll_x = ttk.Scrollbar(self.main_frame, orient="horizontal")
        scroll_y = ttk.Scrollbar(self.main_frame, orient="vertical")
        
        self.tabla = ttk.Treeview(self.main_frame, columns=self.columnas, show="headings", 
                                  xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        
        scroll_x.config(command=self.tabla.xview)
        scroll_y.config(command=self.tabla.yview)
        
        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")

        # Diccionario de Encabezados Base
        encabezados = {
            "pos": "N° Fila", "evento": "Evento", "reloj": "Reloj (min)", 
            "rnd_t": "RND Tipo", "tipo": "Tipo Auto", "rnd_e": "RND Est.", 
            "t_est": "Tiempo Est.", "prox_lleg": "Prox. Llegada", "est_playa": "Playa",
            "cap": "Cap. Ocupada", "caja1": "Lugar 1 Caja", "caja2": "Lugar 2 Caja", "cola": "Cola Cobro"
        }
        
        # Configurar encabezados base
        for col, texto in encabezados.items():
            self.tabla.heading(col, text=texto)
            self.tabla.column(col, width=90, anchor="center")
            
        # Configurar encabezados de los 10 sectores
        for i in range(1, 11):
            col_name = f"sec_{i}"
            self.tabla.heading(col_name, text=f"Sector {i}")
            self.tabla.column(col_name, width=80, anchor="center")

        self.tabla.pack(fill="both", expand=True, padx=5, pady=5)
        self.tabla.bind("<ButtonRelease-1>", self.on_fila_clic)

    def crear_input(self, texto, defecto):
        ctk.CTkLabel(self.sidebar, text=texto, anchor="w").pack(fill="x", padx=20, pady=(5, 0))
        entry = ctk.CTkEntry(self.sidebar)
        entry.insert(0, defecto)
        entry.pack(fill="x", padx=20, pady=(0, 5))
        return entry

    def ejecutar(self):
        try:
            x = float(self.entry_x.get())
            n = int(self.entry_n.get())
            j = float(self.entry_j.get())
            i_filas = int(self.entry_i.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa números válidos en los campos.")
            return

        # 1. Correr simulación
        self.vector_completo = correr_simulacion_playa(x, n)
        
        # 2. Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        # 3. Filtrar filas j e i
        filas_filtradas = []
        contador = 0
        for fila in self.vector_completo:
            if fila["reloj"] >= j and contador < i_filas:
                filas_filtradas.append(fila)
                contador += 1

        ultima_fila = self.vector_completo[-1]
        if ultima_fila not in filas_filtradas:
            filas_filtradas.append(ultima_fila)

        # 4. Insertar filas en la tabla
        for f in filas_filtradas:
            # Construimos los valores básicos de la fila
            valores_fila = [
                f["posicion"], f["evento"], f["reloj"], f["rnd_tipo"], f["tipo_vehiculo"],
                f["rnd_tiempo_est"], f["tiempo_est"], f["proxima_llegada"], f["estado_playa"],
                f["capacidad_actual"], f["estado_lugar_1"], f["estado_lugar_2"], f["cola_cobro"]
            ]
            
            # Agregamos dinámicamente el estado de cada uno de los 10 sectores para esta fila
            for i in range(1, 11):
                estado_sector = f["sectores"][i]["estado"]  # Puede ser "Libre", "Estacionado" o "Bloqueado"
                valores_fila.append(estado_sector)
                
            self.tabla.insert("", "end", iid=f["posicion"], values=valores_fila)
            
        # 5. Estadísticas finales
        llegados = ultima_fila["cant_vehiculos_llegados"]
        rechazados = ultima_fila["cant_vehiculos_rechazados"]
        porc_rechazo = (rechazados / llegados * 100) if llegados > 0 else 0
        
        self.txt_resultados.configure(text=f"Autos Llegados: {llegados}\nAutos Rechazados: {rechazados}\n% de Rechazo: {porc_rechazo:.2f}%")

    def on_fila_clic(self, event):
        item_id = self.tabla.focus()
        if not item_id: return
        
        fila_selec = next((f for f in self.vector_completo if str(f["posicion"]) == item_id), None)
        
        if fila_selec:
            ventana_obj = ctk.CTkToplevel(self)
            ventana_obj.title(f"Detalle Completo - Fila {fila_selec['posicion']}")
            ventana_obj.geometry("480結構x380")
            ventana_obj.geometry("500x380")
            ventana_obj.attributes("-topmost", True)
            
            ctk.CTkLabel(ventana_obj, text="Atributos de Autos en Sectores", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=10)
            
            algun_ocupado = False
            for sec_id, datos in fila_selec["sectores"].items():
                if datos["estado"] != "Libre":
                    algun_ocupado = True
                    txt = f"Sector {sec_id} -> Estado: {datos['estado']} | Tipo: {datos['tipo_auto']} | Fin Est.: {datos['fin']} min"
                    ctk.CTkLabel(ventana_obj, text=txt, anchor="w", text_color="#1f538d").pack(fill="x", padx=20, pady=2)
            
            if not algun_ocupado:
                ctk.CTkLabel(ventana_obj, text="Todos los sectores están libres en este instante.", text_color="gray").pack(pady=20)