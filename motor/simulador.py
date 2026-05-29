# motor/simulador.py
import random

def correr_simulacion_playa(tiempo_x, max_iteraciones):
    reloj = 0.0
    posicion = 0
    contador_autos_global = 0  # Para asignarle un número único a cada auto que entra
    
    TARIFAS = {"Pequeño": 3000, "Grande": 4000, "Utilitario": 5000}
    
    estado_actual = {
        "posicion": 0, "evento": "Inicio", "reloj": 0.0,
        "rnd_tipo": "-", "tipo_vehiculo": "-", "rnd_tiempo_est": "-", "tiempo_est": "-",
        "proxima_llegada": 13.0, "estado_playa": "Libre", "capacidad_actual": 0,
        
        # --- ZONA DE COBRO ---
        "estado_lugar_1": "Libre", 
        "auto_en_cobro": "-",        
        "fin_cobro_lugar_1": None, 
        "estado_lugar_2": "Libre", 
        "cola_cobro": 0,
        
        "sectores": {i: {"estado": "Libre", "fin": None, "tipo_auto": "-", "horas_est": 0, "id_auto": "-"} for i in range(1, 11)},
        "cant_vehiculos_llegados": 0, "cant_vehiculos_rechazados": 0,
        "recaudacion_total": 0.0,
        "acumulador_tiempo_ocupacion": 0.0,
        "acumulador_tiempo_bloqueo": 0.0,
        "cant_autos_bloqueados_total": 0
    }
    
    historial_vector = [estado_actual.copy()]
    
    while reloj <= tiempo_x and posicion < max_iteraciones:
        posicion += 1
        
        tiempos_eventos = {"Llegada": estado_actual["proxima_llegada"]}
        if estado_actual["fin_cobro_lugar_1"] is not None:
            tiempos_eventos["Fin_Cobro"] = estado_actual["fin_cobro_lugar_1"]
            
        for sec_id, sec_data in estado_actual["sectores"].items():
            if sec_data["estado"] == "Estacionado" and sec_data["fin"] is not None:
                tiempos_eventos[f"Fin_Est_{sec_id}"] = sec_data["fin"]
                
        proximo_reloj = min(tiempos_eventos.values())
        evento_nombre = [k for k, v in tiempos_eventos.items() if v == proximo_reloj][0]
        
        delta_t = proximo_reloj - reloj
        reloj = proximo_reloj
        
        nueva_fila = {
            "posicion": posicion, "evento": evento_nombre, "reloj": round(reloj, 2),
            "rnd_tipo": "-", "tipo_vehiculo": "-", "rnd_tiempo_est": "-", "tiempo_est": "-",
            "proxima_llegada": estado_actual["proxima_llegada"],
            "estado_playa": estado_actual["estado_playa"],
            "capacidad_actual": estado_actual["capacidad_actual"],
            
            "estado_lugar_1": estado_actual["estado_lugar_1"],
            "auto_en_cobro": estado_actual["auto_en_cobro"],  
            "fin_cobro_lugar_1": estado_actual["fin_cobro_lugar_1"],
            
            "estado_lugar_2": estado_actual["estado_lugar_2"],
            "cola_cobro": estado_actual["cola_cobro"],
            "sectores": {k: v.copy() for k, v in estado_actual["sectores"].items()},
            "cant_vehiculos_llegados": estado_actual["cant_vehiculos_llegados"],
            "cant_vehiculos_rechazados": estado_actual["cant_vehiculos_rechazados"],
            "recaudacion_total": estado_actual["recaudacion_total"],
            "acumulador_tiempo_ocupacion": estado_actual["acumulador_tiempo_ocupacion"],
            "acumulador_tiempo_bloqueo": estado_actual["acumulador_tiempo_bloqueo"],
            "cant_autos_bloqueados_total": estado_actual["cant_autos_bloqueados_total"]
        }
        
        for sec_id, sec_data in estado_actual["sectores"].items():
            if sec_data["estado"] == "Estacionado":
                nueva_fila["acumulador_tiempo_ocupacion"] += delta_t
            elif sec_data["estado"] == "Bloqueado":
                nueva_fila["acumulador_tiempo_bloqueo"] += delta_t
        
        if evento_nombre == "Llegada":
            nueva_fila["cant_vehiculos_llegados"] += 1
            nueva_fila["proxima_llegada"] = round(reloj + 13.0, 2)
            
            if nueva_fila["capacidad_actual"] < 10:
                contador_autos_global += 1  
                sector_libre = min([k for k, v in nueva_fila["sectores"].items() if v["estado"] == "Libre"])
                
                rnd_t = random.random()
                nueva_fila["rnd_tipo"] = round(rnd_t, 4)
                if rnd_t < 0.45: tipo = "Pequeño"
                elif rnd_t < 0.70: tipo = "Grande"
                else: tipo = "Utilitario"
                nueva_fila["tipo_vehiculo"] = f"Auto {contador_autos_global} ({tipo[:3]})"
                
                rnd_e = random.random()
                nueva_fila["rnd_tiempo_est"] = round(rnd_e, 4)
                if rnd_e < 0.50: hs = 1
                elif rnd_e < 0.80: hs = 2
                elif rnd_e < 0.95: hs = 3
                else: hs = 4
                fin_estacionamiento = round(reloj + (hs * 60), 2)
                nueva_fila["tiempo_est"] = hs
                nueva_fila["sectores"][sector_libre] = {
                    "estado": "Estacionado",
                    "fin": fin_estacionamiento,
                    "tipo_auto": tipo,
                    "horas_est": hs,
                    "id_auto": f"Auto {contador_autos_global}" 
                }
                nueva_fila["capacidad_actual"] += 1
            else:
                nueva_fila["tipo_vehiculo"] = "RECHAZADO"
                nueva_fila["cant_vehiculos_rechazados"] += 1
                
        elif "Fin_Est_" in evento_nombre:
            sector_id = int(evento_nombre.split("_")[-1])
            auto_tipo = nueva_fila["sectores"][sector_id]["tipo_auto"]
            horas = nueva_fila["sectores"][sector_id]["horas_est"]
            id_del_auto = nueva_fila["sectores"][sector_id]["id_auto"]
            
            nueva_fila["recaudacion_total"] += horas * TARIFAS[auto_tipo]
            
            if nueva_fila["estado_lugar_1"] == "Libre":
                nueva_fila["estado_lugar_1"] = "Ocupado"
                nueva_fila["auto_en_cobro"] = id_del_auto  
                nueva_fila["fin_cobro_lugar_1"] = round(reloj + 2.0, 2)
                nueva_fila["sectores"][sector_id] = {"estado": "Libre", "fin": None, "tipo_auto": "-", "horas_est": 0, "id_auto": "-"}
                nueva_fila["capacidad_actual"] -= 1
            elif nueva_fila["cola_cobro"] == 0:
                nueva_fila["cola_cobro"] = 1
                nueva_fila["sectores"][sector_id] = {"estado": "Libre", "fin": None, "tipo_auto": "-", "horas_est": 0, "id_auto": "-"}
                nueva_fila["capacidad_actual"] -= 1
            else:
                nueva_fila["sectores"][sector_id]["estado"] = "Bloqueado"
                nueva_fila["cant_autos_bloqueados_total"] += 1

        elif evento_nombre == "Fin_Cobro":
            if nueva_fila["cola_cobro"] > 0:
                nueva_fila["cola_cobro"] -= 1
                nueva_fila["fin_cobro_lugar_1"] = round(reloj + 2.0, 2)
                
                autos_bloqueados = [k for k, v in nueva_fila["sectores"].items() if v["estado"] == "Bloqueado"]
                if autos_bloqueados:
                    sec_desbloqueado = autos_bloqueados[0]
                    id_bloqueado = nueva_fila["sectores"][sec_desbloqueado]["id_auto"]
                    
                    nueva_fila["auto_en_cobro"] = id_bloqueado 
                    nueva_fila["cola_cobro"] += 1
                    nueva_fila["sectores"][sec_desbloqueado] = {"estado": "Libre", "fin": None, "tipo_auto": "-", "horas_est": 0, "id_auto": "-"}
                    nueva_fila["capacidad_actual"] -= 1
                else:
                    nueva_fila["auto_en_cobro"] = "Auto de Cola"
            else:
                nueva_fila["estado_lugar_1"] = "Libre"
                nueva_fila["auto_en_cobro"] = "-" 
                nueva_fila["fin_cobro_lugar_1"] = None
                
        nueva_fila["estado_playa"] = "Llena" if nueva_fila["capacidad_actual"] == 10 else "Libre"
        nueva_fila["estado_lugar_2"] = "Ocupado" if nueva_fila["cola_cobro"] > 0 else "Libre"
            
        historial_vector.append(nueva_fila)
        estado_actual = nueva_fila

    return historial_vector