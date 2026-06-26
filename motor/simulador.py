import random
import math

# Función principal
def correr_simulacion_playa(tiempo_x, max_iteraciones, tiempo_llegada, tiempo_cobro, probs_tipo, probs_tiempo):
    reloj = 0.0
    posicion = 0
    contador_autos_global = 0  
    
    TARIFAS = {"Pequeño": 3000, "Grande": 4000, "Utilitario": 5000}

    primer_llegada = tiempo_llegada

    #Estado inicial
    estado_actual = {
        "posicion": 0, "evento": "Inicio", "reloj": 0.0,
        "rnd_tipo": "-", "tipo_vehiculo": "-", "rnd_tiempo_est": "-", "tiempo_est": "-",
        "proxima_llegada": primer_llegada , "estado_playa": "Libre", "capacidad_actual": 0,
        "tiempo_entre_llegadas": primer_llegada,
        "estado_lugar_1": "Libre", 
        "auto_en_cobro": None,        
        "fin_cobro_lugar_1": None, 
        "estado_lugar_2": "Libre", 
        "auto_esperando": None,
        
        # Estado incial de los sectores
        "sectores": {i: {"estado": "Libre", "inicio": None, "fin": None, "tipo_auto": "-", "horas_est": 0, "id_auto": "-", "inicio_bloqueo": None} for i in range(1, 11)},
        "cant_vehiculos_llegados": 0, "cant_vehiculos_rechazados": 0,
        "monto_cobrado": "-", 
        "recaudacion_total": 0.0,
        "acumulador_tiempo_ocupacion": 0.0,
        "acumulador_tiempo_bloqueo": 0.0,
        "cant_autos_bloqueados_total": 0,
        "cola_bloqueados": []
    }
    
    historial_vector = [estado_actual.copy()]
    
    # Límites acumulados de probabilidad para los Tipos de Vehículo
    limite_peq = probs_tipo[0]
    limite_gra = limite_peq + probs_tipo[1]

    # Límites acumulados de probabilidad para el Tiempo de Estacionamiento
    limite_1h = probs_tiempo[0]
    limite_2h = limite_1h + probs_tiempo[1]
    limite_3h = limite_2h + probs_tiempo[2]
    
    # Bucle de eventos
    while reloj <= tiempo_x and posicion < max_iteraciones:
        posicion += 1
        
        # Determinar el próximo evento
        tiempos_eventos = {"Llegada": estado_actual["proxima_llegada"]}
        if estado_actual["fin_cobro_lugar_1"] is not None:
            tiempos_eventos["Fin_Cobro"] = estado_actual["fin_cobro_lugar_1"]
            
        for sec_id, sec_data in estado_actual["sectores"].items():
            if sec_data["estado"] == "Estacionado" and sec_data["fin"] is not None:
                tiempos_eventos[f"Fin_Est_{sec_id}"] = sec_data["fin"]
                
        proximo_reloj = min(tiempos_eventos.values())
        evento_nombre = [k for k, v in tiempos_eventos.items() if v == proximo_reloj][0]
        
        # Tiempo transcurrido
        delta_t = proximo_reloj - reloj
        reloj = proximo_reloj
        
        # Crear una nueva fila de estado
        nueva_fila = {
            "posicion": posicion, "evento": evento_nombre, "reloj": round(reloj, 2),
            "rnd_tipo": "-", "tipo_vehiculo": "-", "rnd_tiempo_est": "-", "tiempo_est": "-",
            "proxima_llegada": estado_actual["proxima_llegada"],
            "tiempo_entre_llegadas": "-", # <-- Por defecto no se muestra el tiempo entre llegadas
            "estado_playa": estado_actual["estado_playa"],
            "capacidad_actual": estado_actual["capacidad_actual"],
            "estado_lugar_1": estado_actual["estado_lugar_1"],
            "auto_en_cobro": (estado_actual["auto_en_cobro"].copy() if estado_actual["auto_en_cobro"] else None),
            "fin_cobro_lugar_1": estado_actual["fin_cobro_lugar_1"],
            "estado_lugar_2": estado_actual["estado_lugar_2"],
            "auto_esperando": (estado_actual["auto_esperando"].copy() if estado_actual["auto_esperando"] else None),
            "cola_bloqueados": estado_actual["cola_bloqueados"].copy(),
            "sectores": {k: v.copy() for k, v in estado_actual["sectores"].items()},
            "cant_vehiculos_llegados": estado_actual["cant_vehiculos_llegados"],
            "cant_vehiculos_rechazados": estado_actual["cant_vehiculos_rechazados"],
            "monto_cobrado": "-",  
            "recaudacion_total": estado_actual["recaudacion_total"],
            "acumulador_tiempo_ocupacion": estado_actual["acumulador_tiempo_ocupacion"],
            "acumulador_tiempo_bloqueo": estado_actual["acumulador_tiempo_bloqueo"],
            "cant_autos_bloqueados_total": estado_actual["cant_autos_bloqueados_total"]
        }
        
        # Acumulador de tiempo de ocupación 
        for sec_id, sec_data in estado_actual["sectores"].items():
            if sec_data["estado"] == "Estacionado":
                nueva_fila["acumulador_tiempo_ocupacion"] += delta_t
        
        # Evento de llegada
        if evento_nombre == "Llegada":
            nueva_fila["cant_vehiculos_llegados"] += 1
            nueva_fila["tiempo_entre_llegadas"] = tiempo_llegada
            nueva_fila["proxima_llegada"] = round(reloj + tiempo_llegada, 2) 
            
            # Si hay lugar:
            if nueva_fila["capacidad_actual"] < 10:
                contador_autos_global += 1  
                sector_libre = min([k for k, v in nueva_fila["sectores"].items() if v["estado"] == "Libre"])
                
                # Gerear tipo de vehiculo
                rnd_t = random.random()
                nueva_fila["rnd_tipo"] = round(rnd_t, 4)
                
                if rnd_t < limite_peq: tipo = "Pequeño"
                elif rnd_t < limite_gra: tipo = "Grande"
                else: tipo = "Utilitario"
                
                nueva_fila["tipo_vehiculo"] = f"Auto {contador_autos_global} ({tipo[:3]})"
                
                # Generar tiempo de estacionamiento
                rnd_e = random.random()
                nueva_fila["rnd_tiempo_est"] = round(rnd_e, 4)
                
                if rnd_e < limite_1h: hs = 1
                elif rnd_e < limite_2h: hs = 2
                elif rnd_e < limite_3h: hs = 3
                else: hs = 4
                
                fin_estacionamiento = round(reloj + (hs * 60), 2)
                nueva_fila["tiempo_est"] = hs
                
                # Se ocupa el sector libre con el auto que llega
                nueva_fila["sectores"][sector_libre] = {
                    "estado": "Estacionado",
                    "inicio": round(reloj, 2),
                    "fin": fin_estacionamiento,
                    "tipo_auto": tipo,
                    "horas_est": hs,
                    "id_auto": f"Auto {contador_autos_global}",
                    "inicio_bloqueo": None
                }
                nueva_fila["capacidad_actual"] += 1
            
            # Si NO hay lugar:
            else:
                nueva_fila["tipo_vehiculo"] = "RECHAZADO"
                nueva_fila["cant_vehiculos_rechazados"] += 1
                
        # Evento de fin de estacionamiento
        elif "Fin_Est_" in evento_nombre:
            sector_id = int(evento_nombre.split("_")[-1])
            auto_tipo = nueva_fila["sectores"][sector_id]["tipo_auto"]
            horas = nueva_fila["sectores"][sector_id]["horas_est"]
            id_del_auto = nueva_fila["sectores"][sector_id]["id_auto"]

            auto = {"id": id_del_auto, "tipo": auto_tipo, "horas": horas}

            # Servidor de cobro libre
            if nueva_fila["estado_lugar_1"] == "Libre":
                nueva_fila["estado_lugar_1"] = "Ocupado"
                nueva_fila["auto_en_cobro"] = auto
                nueva_fila["fin_cobro_lugar_1"] = round(reloj + tiempo_cobro, 2)
                # Vacío el sector que estaba ocupado por el auto que se va a cobrar
                nueva_fila["sectores"][sector_id] = {"estado": "Libre", "inicio": None, "fin": None, "tipo_auto": "-", "horas_est": 0, "id_auto": "-", "inicio_bloqueo": None}
                nueva_fila["capacidad_actual"] -= 1

            # Servidor de cobro ocupado, zona de cobro libre
            elif nueva_fila["estado_lugar_2"] == "Libre":
                nueva_fila["estado_lugar_2"] = "Ocupado"
                nueva_fila["auto_esperando"] = auto
                # Vacío el sector que estaba ocupado por el auto que se va a cobrar
                nueva_fila["sectores"][sector_id] = {"estado": "Libre", "inicio": None, "fin": None, "tipo_auto": "-", "horas_est": 0, "id_auto": "-", "inicio_bloqueo": None}
                nueva_fila["capacidad_actual"] -= 1

            # Servidor y zona de cobro ocupados, se bloquea el sector
            else:
                nueva_fila["sectores"][sector_id]["estado"] = "Bloqueado"
                nueva_fila["sectores"][sector_id]["inicio_bloqueo"] = reloj
                nueva_fila["cola_bloqueados"].append(sector_id)

        # Evento de fin de cobro
        elif evento_nombre == "Fin_Cobro":
            auto_cobrado = nueva_fila["auto_en_cobro"]
            nueva_fila["tipo_vehiculo"] = auto_cobrado["id"]

            # Recaudacion
            tarifa_calculada = auto_cobrado["horas"] * TARIFAS[auto_cobrado["tipo"]]
            nueva_fila["monto_cobrado"] = tarifa_calculada
            nueva_fila["recaudacion_total"] += tarifa_calculada

            # Si había un auto esperando en la zona de cobro, se pasa a cobrar
            if nueva_fila["auto_esperando"] is not None:
                nueva_fila["auto_en_cobro"] = nueva_fila["auto_esperando"]
                nueva_fila["auto_esperando"] = None
                nueva_fila["estado_lugar_2"] = "Libre"
                nueva_fila["fin_cobro_lugar_1"] = round(reloj + tiempo_cobro, 2)

                # Si había autos bloqueados, se desbloquea el primero de la cola
                if nueva_fila["cola_bloqueados"]:
                    sec_desbloqueado = nueva_fila["cola_bloqueados"].pop(0)
                    hora_inicio_b = nueva_fila["sectores"][sec_desbloqueado]["inicio_bloqueo"]
                    if hora_inicio_b is not None:
                        tiempo_esperado = reloj - hora_inicio_b
                        nueva_fila["acumulador_tiempo_bloqueo"] += tiempo_esperado
                        
                        nueva_fila["cant_autos_bloqueados_total"] += 1

                    auto_desbloqueado = {"id": nueva_fila["sectores"][sec_desbloqueado]["id_auto"], "tipo": nueva_fila["sectores"][sec_desbloqueado]["tipo_auto"], "horas": nueva_fila["sectores"][sec_desbloqueado]["horas_est"]}
                    nueva_fila["auto_esperando"] = auto_desbloqueado
                    nueva_fila["estado_lugar_2"] = "Ocupado"
                    # Vacío el sector que estaba bloqueado
                    nueva_fila["sectores"][sec_desbloqueado] = {"estado": "Libre", "inicio": None, "fin": None, "tipo_auto": "-", "horas_est": 0, "id_auto": "-", "inicio_bloqueo": None}
                    nueva_fila["capacidad_actual"] -= 1
            else:
                nueva_fila["estado_lugar_1"] = "Libre"
                nueva_fila["auto_en_cobro"] = None
                nueva_fila["fin_cobro_lugar_1"] = None
                
        # Actualizar estado de la playa y zona de cobro
        nueva_fila["estado_playa"] = "Llena" if nueva_fila["capacidad_actual"] == 10 else "Libre"
        nueva_fila["estado_lugar_2"] = "Ocupado" if nueva_fila["auto_esperando"] is not None else "Libre"
            
        # Guardar el estado actual en el historial
        historial_vector.append(nueva_fila)
        estado_actual = nueva_fila

    return historial_vector