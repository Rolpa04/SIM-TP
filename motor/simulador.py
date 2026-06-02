# motor/simulador.py
import random
import math

def correr_simulacion_playa(tiempo_x, max_iteraciones):
    reloj = 0.0
    posicion = 0
    contador_autos_global = 0  # Para asignarle un número único a cada auto que entra
    
    TARIFAS = {"Pequeño": 500, "Grande": 1500, "Utilitario": 3000}
    

    rnd_primer_llegada = round(random.random(), 4)
    primer_llegada = round(-13*math.log(1-rnd_primer_llegada),2)
    estado_actual = {
        "posicion": 0, "evento": "Inicio", "reloj": 0.0,
        "rnd_lleg": rnd_primer_llegada, "rnd_tipo": "-", "tipo_vehiculo": "-", "rnd_tiempo_est": "-", "tiempo_est": "-",
        "proxima_llegada": primer_llegada , "estado_playa": "Libre", "capacidad_actual": 0,
        "tiempo_entre_llegadas": primer_llegada,
        # --- ZONA DE COBRO ---
        "estado_lugar_1": "Libre", 
        "auto_en_cobro": None,        
        "fin_cobro_lugar_1": None, 
        "estado_lugar_2": "Libre", 
        "auto_esperando": None,
        
        "sectores": {i: {"estado": "Libre", "fin": None, "tipo_auto": "-", "horas_est": 0, "id_auto": "-"} for i in range(1, 11)},
        "cant_vehiculos_llegados": 0, "cant_vehiculos_rechazados": 0,
        "recaudacion_total": 0.0,
        "acumulador_tiempo_ocupacion": 0.0,
        "acumulador_tiempo_bloqueo": 0.0,
        "cant_autos_bloqueados_total": 0,
        "cola_bloqueados": []
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
            "rnd_lleg": "-", "rnd_tipo": "-", "tipo_vehiculo": "-", "rnd_tiempo_est": "-", "tiempo_est": "-",
            "proxima_llegada": estado_actual["proxima_llegada"],
            "tiempo_entre_llegadas": estado_actual["tiempo_entre_llegadas"],
            "estado_playa": estado_actual["estado_playa"],
            "capacidad_actual": estado_actual["capacidad_actual"],
            "estado_lugar_1": estado_actual["estado_lugar_1"],
            "auto_en_cobro": (
                estado_actual["auto_en_cobro"].copy()
                if estado_actual["auto_en_cobro"] else None
            ),
            "fin_cobro_lugar_1": estado_actual["fin_cobro_lugar_1"],
            "estado_lugar_2": estado_actual["estado_lugar_2"],
            "auto_esperando": (
                estado_actual["auto_esperando"].copy()
                if estado_actual["auto_esperando"] else None
            ),
            "cola_bloqueados": estado_actual["cola_bloqueados"].copy(),
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
            random_tiempo = random.random()
            nueva_fila["rnd_lleg"] = round(random_tiempo, 4)
            nueva_fila["tiempo_entre_llegadas"] = round((-13 * math.log(1-random_tiempo)), 2)
            nueva_fila["proxima_llegada"] = round(reloj + (-13 * math.log(1-random_tiempo)), 2)
            
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

            auto = {
                "id": id_del_auto,
                "tipo": auto_tipo,
                "horas": horas
            }

            # Caja libre → pasa a cobrar
            if nueva_fila["estado_lugar_1"] == "Libre":

                nueva_fila["estado_lugar_1"] = "Ocupado"
                nueva_fila["auto_en_cobro"] = auto
                nueva_fila["fin_cobro_lugar_1"] = round(reloj + 2.0, 2)

                nueva_fila["sectores"][sector_id] = {
                    "estado": "Libre",
                    "fin": None,
                    "tipo_auto": "-",
                    "horas_est": 0,
                    "id_auto": "-"
                }

                nueva_fila["capacidad_actual"] -= 1

            # Lugar de espera libre
            elif nueva_fila["estado_lugar_2"] == "Libre":

                nueva_fila["estado_lugar_2"] = "Ocupado"
                nueva_fila["auto_esperando"] = auto

                nueva_fila["sectores"][sector_id] = {
                    "estado": "Libre",
                    "fin": None,
                    "tipo_auto": "-",
                    "horas_est": 0,
                    "id_auto": "-"
                }

                nueva_fila["capacidad_actual"] -= 1

            # Zona de cobro completa
            else:
                nueva_fila["sectores"][sector_id]["estado"] = "Bloqueado"
                nueva_fila["cola_bloqueados"].append(sector_id)
                nueva_fila["cant_autos_bloqueados_total"] += 1

        elif evento_nombre == "Fin_Cobro":

            auto_cobrado = nueva_fila["auto_en_cobro"]

            # Mostrar qué auto terminó de pagar
            nueva_fila["tipo_vehiculo"] = auto_cobrado["id"]

            # Recaudación (ahora ocurre acá)
            nueva_fila["recaudacion_total"] += (
                auto_cobrado["horas"] *
                TARIFAS[auto_cobrado["tipo"]]
            )

            if nueva_fila["auto_esperando"] is not None:

                nueva_fila["auto_en_cobro"] = nueva_fila["auto_esperando"]

                nueva_fila["auto_esperando"] = None

                nueva_fila["estado_lugar_2"] = "Libre"

                nueva_fila["fin_cobro_lugar_1"] = round(reloj + 2.0, 2)

                if nueva_fila["cola_bloqueados"]:

                    sec_desbloqueado = nueva_fila["cola_bloqueados"].pop(0)

                    auto_desbloqueado = {
                        "id": nueva_fila["sectores"][sec_desbloqueado]["id_auto"],
                        "tipo": nueva_fila["sectores"][sec_desbloqueado]["tipo_auto"],
                        "horas": nueva_fila["sectores"][sec_desbloqueado]["horas_est"]
                    }

                    nueva_fila["auto_esperando"] = auto_desbloqueado

                    nueva_fila["estado_lugar_2"] = "Ocupado"

                    nueva_fila["sectores"][sec_desbloqueado] = {
                        "estado": "Libre",
                        "fin": None,
                        "tipo_auto": "-",
                        "horas_est": 0,
                        "id_auto": "-"
                    }

                    nueva_fila["capacidad_actual"] -= 1

            else:

                nueva_fila["estado_lugar_1"] = "Libre"
                nueva_fila["auto_en_cobro"] = None
                nueva_fila["fin_cobro_lugar_1"] = None
                
        nueva_fila["estado_playa"] = "Llena" if nueva_fila["capacidad_actual"] == 10 else "Libre"
        nueva_fila["estado_lugar_2"] = (
            "Ocupado"
            if nueva_fila["auto_esperando"] is not None
            else "Libre"
        )
            
        historial_vector.append(nueva_fila)
        estado_actual = nueva_fila

    return historial_vector