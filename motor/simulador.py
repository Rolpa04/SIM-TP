# motor/simulador.py
import random

def correr_simulacion_playa(tiempo_x, max_iteraciones):
    reloj = 0.0
    posicion = 0
    
    # Inicialización de la Fila 0 (Estado Inicial)
    estado_actual = {
        "posicion": 0,
        "evento": "Inicio",
        "reloj": 0.0,
        "rnd_tipo": "-", "tipo_vehiculo": "-",
        "rnd_tiempo_est": "-", "tiempo_est": "-",
        "proxima_llegada": 13.0, 
        "estado_playa": "Libre", 
        "capacidad_actual": 0,
        "estado_lugar_1": "Libre", 
        "fin_cobro_lugar_1": None,
        "estado_lugar_2": "Libre", 
        "cola_cobro": 0,
        "sectores": {i: {"estado": "Libre", "fin": None, "tipo_auto": "-"} for i in range(1, 11)},
        "cant_vehiculos_llegados": 0, 
        "cant_vehiculos_rechazados": 0
    }
    
    historial_vector = [estado_actual.copy()]
    
    while reloj <= tiempo_x and posicion < max_iteraciones:
        posicion += 1
        
        # 1. Determinar el próximo evento (Buscamos el menor tiempo futuro)
        tiempos_eventos = {"Llegada": estado_actual["proxima_llegada"]}
        if estado_actual["fin_cobro_lugar_1"] is not None:
            tiempos_eventos["Fin_Cobro"] = estado_actual["fin_cobro_lugar_1"]
            
        # Revisamos los tiempos de fin de estacionamiento de los 10 sectores
        for sec_id, sec_data in estado_actual["sectores"].items():
            if sec_data["estado"] == "Estacionado" and sec_data["fin"] is not None:
                tiempos_eventos[f"Fin_Est_{sec_id}"] = sec_data["fin"]
                
        # Avanzamos el reloj al evento más cercano
        proximo_reloj = min(tiempos_eventos.values())
        evento_nombre = [k for k, v in tiempos_eventos.items() if v == proximo_reloj][0]
        
        reloj = proximo_reloj
        
        # Clonamos el estado anterior para aplicar los cambios en esta nueva fila
        nueva_fila = {
            "posicion": posicion, "evento": evento_nombre, "reloj": round(reloj, 2),
            "rnd_tipo": "-", "tipo_vehiculo": "-",
            "rnd_tiempo_est": "-", "tiempo_est": "-",
            "proxima_llegada": estado_actual["proxima_llegada"],
            "estado_playa": estado_actual["estado_playa"],
            "capacidad_actual": estado_actual["capacidad_actual"],
            "estado_lugar_1": estado_actual["estado_lugar_1"],
            "fin_cobro_lugar_1": estado_actual["fin_cobro_lugar_1"],
            "estado_lugar_2": estado_actual["estado_lugar_2"],
            "cola_cobro": estado_actual["cola_cobro"],
            "sectores": {k: v.copy() for k, v in estado_actual["sectores"].items()},
            "cant_vehiculos_llegados": estado_actual["cant_vehiculos_llegados"],
            "cant_vehiculos_rechazados": estado_actual["cant_vehiculos_rechazados"]
        }
        
        # --- LÓGICA DE LOS EVENTOS ---
        if evento_nombre == "Llegada":
            nueva_fila["cant_vehiculos_llegados"] += 1
            nueva_fila["proxima_llegada"] = reloj + 13.0 # Llegada cada 13 min fijos
            
            if nueva_fila["capacidad_actual"] < 10:
                # Buscar el primer sector físico libre
                sector_libre = min([k for k, v in nueva_fila["sectores"].items() if v["estado"] == "Libre"])
                
                # RND Tipo de Vehículo
                rnd_t = random.random()
                nueva_fila["rnd_tipo"] = round(rnd_t, 4)
                if rnd_t < 0.45: tipo = "Pequeño"
                elif rnd_t < 0.70: tipo = "Grande"
                else: tipo = "Utilitario"
                nueva_fila["tipo_vehiculo"] = tipo
                
                # RND Tiempo Estacionamiento
                rnd_e = random.random()
                nueva_fila["rnd_tiempo_est"] = round(rnd_e, 4)
                if rnd_e < 0.50: hs = 1
                elif rnd_e < 0.80: hs = 2
                elif rnd_e < 0.95: hs = 3
                else: hs = 4
                nueva_fila["tiempo_est"] = hs
                
                # Ocupamos el sector
                nueva_fila["sectores"][sector_libre] = {
                    "estado": "Estacionado",
                    "fin": round(reloj + (hs * 60), 2),
                    "tipo_auto": tipo
                }
                nueva_fila["capacidad_actual"] += 1
            else:
                nueva_fila["tipo_vehiculo"] = "RECHAZADO (Playa Llena)"
                nueva_fila["cant_vehiculos_rechazados"] += 1
                
        elif "Fin_Est_" in evento_nombre:
            sector_id = int(evento_nombre.split("_")[-1])
            
            # El auto quiere pasar a la caja de cobro
            if nueva_fila["estado_lugar_1"] == "Libre":
                nueva_fila["estado_lugar_1"] = "Ocupado"
                nueva_fila["fin_cobro_lugar_1"] = round(reloj + 2.0, 2) # 2 min fijos de cobro
                # Libera el espacio físico del estacionamiento
                nueva_fila["sectores"][sector_id] = {"estado": "Libre", "fin": None, "tipo_auto": "-"}
                nueva_fila["capacidad_actual"] -= 1
            elif nueva_fila["estado_lugar_2"] == "Libre":
                nueva_fila["estado_lugar_2"] = "Ocupado"
                nueva_fila["cola_cobro"] += 1
                # También libera el espacio físico porque entra en la zona de espera de cobro
                nueva_fila["sectores"][sector_id] = {"estado": "Libre", "fin": None, "tipo_auto": "-"}
                nueva_fila["capacidad_actual"] -= 1
            else:
                # Zona de cobro llena. Se queda BLOQUEADO ocupando su sector físico
                nueva_fila["sectores"][sector_id]["estado"] = "Bloqueado"
                nueva_fila["sectores"][sector_id]["fin"] = None

        elif evento_nombre == "Fin_Cobro":
            if nueva_fila["cola_cobro"] > 0:
                # El auto del Lugar 2 pasa al Lugar 1 de atención
                nueva_fila["cola_cobro"] -= 1
                nueva_fila["fin_cobro_lugar_1"] = round(reloj + 2.0, 2)
                
                # Si había autos bloqueados en sectores, uno avanza al Lugar 2 de la caja
                autos_bloqueados = [k for k, v in nueva_fila["sectores"].items() if v["estado"] == "Bloqueado"]
                if autos_bloqueados:
                    sec_desbloqueado = autos_bloqueados[0]
                    nueva_fila["cola_cobro"] += 1
                    nueva_fila["sectores"][sec_desbloqueado] = {"estado": "Libre", "fin": None, "tipo_auto": "-"}
                    nueva_fila["capacidad_actual"] -= 1
            else:
                nueva_fila["estado_lugar_1"] = "Libre"
                nueva_fila["fin_cobro_lugar_1"] = None
                
        # Actualización de estados visuales dinámicos
        nueva_fila["estado_playa"] = "Llena" if nueva_fila["capacidad_actual"] == 10 else "Libre"
        nueva_fila["estado_lugar_2"] = "Ocupado" if nueva_fila["cola_cobro"] > 0 else "Libre"
            
        historial_vector.append(nueva_fila)
        estado_actual = nueva_fila

    # NOTA CLAVE: Esta línea debe estar alineada perfectamente con el inicio del 'while'
    return historial_vector