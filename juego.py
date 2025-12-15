# Finalizado el 14/12/2025 (23:51 hrs)
#!/usr/bin/env python3
# Juego En|Par| (Creado por T)

import random
import os
import sys
import time
import numpy as np

# --- Actualización -------------------------------------------------------------------------------------
import urllib.request
import webbrowser


version_actual = "1.0"
usuario = "vamotesdragons546-a11y" 
repositorio = "En-Par-" 

URL_VERSION = f"https://raw.githubusercontent.com/{usuario}/{repositorio}/main/version.txt"
URL_REPO = f"https://github.com/{usuario}/{repositorio}"

def verificar_actualizacion():
    """Consulta a GitHub si hay una versión nueva."""
    print(" Buscando actualizaciones...", end="\r")
    try:
        # Leer el archivo version.txt desde internet
        with urllib.request.urlopen(URL_VERSION) as response:
            version_online = response.read().decode('utf-8').strip()
            
        if version_online != version_actual:
            limpiar_pantalla()
            print("| Nueva versión disponible ¬¬ |")
            print(f"   Versión actual: {version_actual}")
            print(f"   Nueva versión: {version_online}")
            print("\n   Se abrirá la página de descarga en 3 segundos...")
            time.sleep(3)
            webbrowser.open(URL_REPO)
            return True # Hay actualización
            
    except Exception:
        pass # Si falla (sin internet), no te voy a molestar, puedes jugar tranquilo.
    return False

# ------------------------------------------------------------------------------   Eliminar terminal

def limpiar_pantalla():
    # Intentar limpieza por secuencia ANSI (más inmediata en muchos terminales)
    try:
        print("\033[H\033[J", end='', flush=True)
    except Exception:
        pass
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
# ------------------------------------------------------------------------------    Puntos del juego


def obtener_valor_puntos(filas):
    if filas == 4:
        return 10
    if filas == 6:
        return 20
    if filas == 8:
        return 30
    return 0
# ------------------------------------------------------------------------------   Las matrices de las cartas


def crear_juego(filas, columnas):
    cartas = list(range(1, (filas * columnas) // 2 + 1)) * 2
    random.shuffle(cartas)
    return np.array(cartas).reshape(filas, columnas)


# ------------------------------------------------------------------------------   Lo que se muestra en el tablero de cartas


def mostrar_tablero(cartas_visibles, cartas, header=None):
    """Muestra el encabezado opcional y el tablero de cartas."""
    if header:
        print(header)
    print("\n   ", end="")
    for j in range(cartas.shape[1]):
        print(f"{j}  ", end="")
    print()
    for i in range(cartas.shape[0]):
        print(f"{i}: ", end="")
        for j in range(cartas.shape[1]):
            if cartas_visibles[i, j]:
                print(f"{cartas[i, j]:2} ", end="")
            else:
                print("🎴 ", end="")  # se puede cambiar la interfáz de las cartas
                
        print()

# ------------------------------------------------------------------------------    Ubicación de la carta


def pedir_coordenada_validada(prompt, max_dim, funcion_redibujar):
    """
    Pide una coordenada y valida que sea número y esté en rango.
    Si hay error, ejecuta 'funcion_redibujar' para restaurar la pantalla.
    Retorna -1 si el usuario escribe '000'.
    """
    while True:
        entrada = input(prompt)

        # Chequeo de salida inmediata
        if entrada == "000":
            return -1

        # Validación de número y rango
        try:
            valor = int(entrada)
            if 0 <= valor < max_dim:
                return valor  # ¡Todo correcto!
            else:
                print(f"Error: La posición debe ser entre 0 y {max_dim - 1}.")
        except ValueError:
            print("Error: Ingresa solo números enteros.")
                

        # Manejo de errores
        time.sleep(1.5)       
        limpiar_pantalla()    
        
        
        if funcion_redibujar:
            funcion_redibujar()

# ------------------------------------------------------------------------------    Evita errores que no pueden otras validaciones (Adaptado para maCos, Unix y Windows)



def flush_input():
    """Descarta cualquier entrada pendiente en stdin.
    En Unix usa termios.tcflush; en Windows usa msvcrt.getch()."""
    # Primero intentar tcflush (Unix, incl. macOS)
    try:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        # return
    except Exception:
        pass

    # Luego intentar método Windows
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
         # return
    except Exception:
        pass

    # Fallback portable: leer lo que esté disponible usando select
    try:
        import select
        while True:
            r, _, _ = select.select([sys.stdin], [], [], 0)
            if not r:
                break
            try:
                # leer sin bloquear lo disponible
                sys.stdin.read(1024)
            except Exception:
                break
    except Exception:
        # No podemos descartar la entrada; seguir sin fallo
        pass

# ------------------------------------------------------------------------------   Comprueba las cartas



def revelar_y_comprobar(cartas, visibles, f1, c1, f2, c2, puntos_por_pareja):
    """Revela dos cartas, devuelve (matched: bool, puntos: int)."""
    visibles[f1, c1] = True
    visibles[f2, c2] = True
    if cartas[f1, c1] == cartas[f2, c2]:
        return True, puntos_por_pareja
    # si no coinciden, ocultar después de llamar
    return False, 0


# ------------------------------------------------------------------------------   Creación del juevo competitivo VS



def jugar_versus(nombres):
    """Partida versus independiente: el que acierta sigue; al fallar pasa el turno."""
    # elegir dificultad
    limpiar_pantalla()
    while True:
        print("[1] FACIL (4x4)\n[2] NORMAL (6x6)\n[3] DIFICIL (8x8)\n")
        dif = input("Dificultad (0 para cancelar): ")
        if dif == '0':
            return
        if dif in ('1', '2', '3'):
            dif = int(dif)
            break
        print('Opción inválida.')
        time.sleep(1)   
        limpiar_pantalla()

    A = B = 4 if dif == 1 else (6 if dif == 2 else 8)
    puntos_por_pareja = obtener_valor_puntos(A)
    cartas = crear_juego(A, B)
    visibles = np.zeros_like(cartas, dtype=bool)
    total_parejas = (A * B) // 2
    encontradas = 0

    players = [{'name': n, 'score': 0} for n in nombres]
    current = 0

    limpiar_pantalla()
    print(f"Iniciando Versus: {', '.join(nombres)}")
    for j in range(3, 0, -1):
        print(f"Comenzando en {j}...", end="\r", flush=True)
        
        time.sleep(1)
        flush_input()
        
        continue

    while encontradas < total_parejas:
        p = players[current]

        def turno_base():        # def para mostrar puntaje
            limpiar_pantalla()
            # Mostramos puntajes de todos para fomentar la competencia muajajaj
            scores = " | ".join([f"{pl['name']}: {pl['score']}" for pl in players])
            header = f"--- Turno de: {p['name']} ---\n{scores}\nParejas restantes: {total_parejas - encontradas}\n"
            mostrar_tablero(visibles, cartas, header=header)

        def ver_carta1():       # def para indicar que estas en la carta 1
            turno_base()
            print("--> Carta 1")
        

        # seleccionar primera carta

        ver_carta1()
        while True:
            f1 = pedir_coordenada_validada(f"Fila (0-{A-1}): ", A, ver_carta1)
            if f1 == -1: 
                print('Saliendo partida...')
                time.sleep(1); return
            
            def ver_columna1():      # def para que también en la columna te diga que estás en la carta 1 mostrandote también la fila que seleccionaste
                ver_carta1()
                print(f"--> Fila: {f1}")

            
            c1 = pedir_coordenada_validada(f"Columna (0-{B-1}): ", B, ver_columna1)
            if c1 == -1:
                print('Saliendo partida...')
                time.sleep(0.7)
                return
            if visibles[f1, c1]:
                print('Esa carta ya está descubierta. Elige otra.')
                time.sleep(0.8)
                ver_carta1()
                continue
            break

        visibles[f1, c1] = True

        def ver_carta2():            # otro def para mostrarte la carta
            turno_base()
            print(f"--> Carta 1: {cartas[f1, c1]}")
            print("--> Carta 2")


        ver_carta2()

        # seleccionar segunda carta
        while True:
            f2 = pedir_coordenada_validada(f"Fila (0-{A-1}) - {p['name']}: ", A, ver_carta2)
            if f2 == -1:
                print('Saliendo partida...')
                time.sleep(0.7)
                return

            def ver_columna2():        # otro def para mostrar carta en la columna
                ver_carta2()
                print(f"--> Fila 2: {f2}")

            c2 = pedir_coordenada_validada(f"Columna (0-{B-1}) - {p['name']}: ", B, ver_columna2)
            if c2 == -1:
                print('Saliendo partida...')
                time.sleep(0.7)
                return
            
            if f1 == f2 and c1 == c2:
                print('No puedes elegir la misma carta dos veces.')
                time.sleep(0.8)
                ver_carta2()
                continue
            if visibles[f2, c2]:
                print('Esa carta ya está descubierta. Elige otra.')
                time.sleep(0.8)
                ver_carta2()
            break

        # revelar y comprobar
        matched, pts = revelar_y_comprobar(cartas, visibles, f1, c1, f2, c2, puntos_por_pareja)
        turno_base()
        print(f"--> Carta 1: {cartas[f1, c1]}")
        print(f"--> Carta 2: {cartas[f2, c2]}")

        if matched:
            print(f"¡{p['name']} encontró una pareja! +{pts} puntos.")
            p['score'] += pts
            encontradas += 1
            time.sleep(2)
            # el mismo jugador continúa (no cambiar current)
            if encontradas < total_parejas:
                print(f"{p['name']} sigue jugando...")
                time.sleep(0.8)
        else:
            for i in range(3, 0, -1):
                print(f'No coinciden. Ocultando en {i}...', end='\r', flush=True)
                time.sleep(1)
            
            
            visibles[f1, c1] = False
            visibles[f2, c2] = False
            # pasar turno
            current = (current + 1) % len(players)

    # fin de la partida
    limpiar_pantalla()
    max_score = max(p['score'] for p in players)
    winners = [p for p in players if p['score'] == max_score]
   
    print("\n| ° RESULTADOS FINALES ° |\n")
    for p in players:
        print(f"- {p['name']}: {p['score']} puntos")
    
    print("\n" + "¬"*30)
    if len(winners) == 1:
        print(f"  ¡GANADOR: {winners[0]['name']}!")
    else:
        names = ', '.join(w['name'] for w in winners)
        print(f"  ¡EMPATE entre {names}!")
    print("¬"*30 + "\n")
    input("Presiona Enter para salir...")
    flush_input()

# ------------------------------------------------------------------------------    Creación reglas del juego



def Reglas_del_Juego():
    limpiar_pantalla()
    print("\n**************** [ Reglas del juego ] **************** \n")
    print("1) El Juego consta de 1 a 3 jugadores.")
    print("2) Los jugadores deberán ponerse de acuerdo para ver quien comienza.")
    print("3) El ganador se definirá por quien tenga más puntos al finalizar el juego.")
    print("4) En Versus, si aciertas una pareja, continúas jugando; si fallas, pasa el turno.\n")


# ------------------------------------------------------------------------------     Creación del juego individual



def jugar_solitario():
    limpiar_pantalla()
    Reglas_del_Juego()
    modos_disponibles()
    print("Modo Solitario seleccionado.\n")
    time.sleep(1)
    # elegir dificultad
    limpiar_pantalla()
    while True:
        print("¬" * 40, "\n")
        print("[1] FACIL (4x4)\n[2] NORMAL (6x6)\n[3] DIFICIL (8x8)\n")
        dif = input("Dificultad (0 para cancelar): ")
        if dif == '0':
            return
        if dif in ('1', '2', '3'):
            dif = int(dif)
            break
        print('Opción inválida.')
        time.sleep(1)
        limpiar_pantalla()
        

    A = B = 4 if dif == 1 else (6 if dif == 2 else 8)
    puntos_por_pareja = obtener_valor_puntos(A)
    cartas = crear_juego(A, B)
    visibles = np.zeros_like(cartas, dtype=bool)
    total_parejas = (A * B) // 2
    encontradas = 0
    puntaje_total = 0

    limpiar_pantalla()
    def dibujar_pantalla():         # def para mostrar puntaje y otras cosas
        header = f"Puntaje actual: {puntaje_total}"
        mostrar_tablero(visibles, cartas, header=header)

    print("Modo Solitario: Encuentra todas las parejas. Escribe 000 para salir al menú.")
    time.sleep(3)
    flush_input()

    
    
    while encontradas < total_parejas:

        def redibujar_c1():         # def  para que no desaparezca la posicion ni las cartas al haber un error
            dibujar_pantalla()
            print("--> Carta 1")


        limpiar_pantalla()
        redibujar_c1()
        
        # Primera carta
        while True:
            
            f1 = pedir_coordenada_validada(f"Fila (0-{A-1}): ", A, redibujar_c1)
            if f1 == -1:
                
                return
                
            def redibujar_fila1():       # def para redibujar la fila 1
                redibujar_c1()
                print(f"--> Fila 1: {f1}")
            c1 = pedir_coordenada_validada(f"Columna (0-{B-1}): ", B, redibujar_fila1)
            if c1 == -1:
                return
            if visibles[f1, c1]:
                print('Esa carta ya está visible. Elige otra.')
                time.sleep(1)
                limpiar_pantalla()
                redibujar_c1()
                continue
            break

        visibles[f1, c1] = True
        limpiar_pantalla()
        redibujar_c1()
        
        # Segunda carta

        def redibujar_c2():            # def igual que para la carta 1 peoro ahora para la casrta 2
            limpiar_pantalla()
            dibujar_pantalla()
            print(f"--> Carta 1: {cartas[f1, c1]}")
            print("--> Carta 2")

        redibujar_c2()


        while True:
            
            f2 = pedir_coordenada_validada(f"Fila (0-{A-1}): ", A, redibujar_c2)
            if f2 == -1:
                return
            def redibujar_fila2():      # def para mostrar la fila de la carta 2
                redibujar_c2()
                print(f"--> Fila 2: {f2}")
            c2 = pedir_coordenada_validada(f"Columna (0-{B-1}): ", B, redibujar_fila2)
            if c2 == -1:
                return
            if f1 == f2 and c1 == c2:
                print('No puedes elegir la misma carta dos veces.')
                time.sleep(1)
                limpiar_pantalla()
                redibujar_c2()
                continue
            if visibles[f2, c2]:
                print('Esa carta ya está visible. Elige otra.')
                time.sleep(1)
                limpiar_pantalla()
                redibujar_c2()
                continue
            break

        matched, pts = revelar_y_comprobar(cartas, visibles, f1, c1, f2, c2, puntos_por_pareja)
        limpiar_pantalla()
        dibujar_pantalla()
        if matched:
            print('¡Encontraste una pareja!')
            encontradas += 1
            puntaje_total += pts
            time.sleep(1.2)
        else:

            print('No coinciden. Se ocultarán en 3 segundos...')
            time.sleep(3)
            visibles[f1, c1] = False
            visibles[f2, c2] = False

    limpiar_pantalla()
    print('¡Ganaste! ¡Encontraste todas las parejas!')
    print(f'Puntaje Final: {puntaje_total}')
    input('\nPresiona Enter para volver al menú...')
    flush_input()


# ------------------------------------------------------------------------------   Muestra los modos de juego


def modos_disponibles():      
    print('\nModos disponibles:')
    print('[1] Solitario')
    print('[2] Versus (2-3 jugadores)\n')


# ------------------------------------------------------------------------------  Main para evitar errores no deseados en el archivo



if __name__ == '__main__':
    verificar_actualizacion()
    # Menú principal: elegir modo
    while True:
        limpiar_pantalla()
        Reglas_del_Juego()
        modos_disponibles()
        
        opcion = input('Modo (0 para salir): ')
        if opcion == '0':
            print('Saliendo...')
            break
        if opcion == '1':
            jugar_solitario()
            continue
        if opcion == '2':
            # pedir cantidad y nombres
            while True:
                limpiar_pantalla()
                Reglas_del_Juego()
                modos_disponibles()
                print('Modo Versus seleccionado.\n')
                print("¬" * 40)
                cantidad = input('Cantidad de jugadores (2-3, 0 para cancelar): ')
                if cantidad == '0':
                    break
                try:
                    num = int(cantidad)
                except ValueError:
                    print('Ingrese un número válido.')
                    time.sleep(1)
                    limpiar_pantalla()
                    continue
                if 2 <= num <= 3:
                    limpiar_pantalla()
                    nombres = []

        # ---------------------------------- NUEVO BLOQUE DE CÓDIGO -----------------------------------------------   Este bloque esta dedicado a los nombres de los jugadores, poder editarlos, y confirmarlos.
                    def mostrar_progreso():
                        limpiar_pantalla()
                        registrados = len(nombres)
                        faltan = num - registrados
                        
                        if faltan == 0:
                            print(f'--- ¡LISTO! Todos los jugadores configurados ---\n')
                        else:
                            txt = 'jugador' if faltan == 1 else 'jugadores'
                            print(f'--- Configurando Versus (Faltan {faltan} {txt}) ---\n')

                        if nombres:
                            print("Jugadores listos:")
                            for n in nombres:
                                print(f" ¬ {n}")
                            print("¬" * 20)

                        if faltan == 0:
                            time.sleep(2)
                            return 

                    # --- FASE 1: PEDIR NOMBRES  ---
                    for i in range(num):
                        while True:
                            mostrar_progreso()
                            nombre = input(f"\nNombre Jugador {i+1} (Máx 12 letras): ").strip()
                            
                            if not nombre:
                                print("El nombre no puede estar vacío.")
                                time.sleep(1); continue
                            if len(nombre) > 12:
                                print("Muy largo (máximo 12 letras).")
                                time.sleep(1); continue
                            if nombre in nombres:
                                print("Ese nombre ya está en uso.")
                                time.sleep(1); continue
                                
                            nombres.append(nombre)
                            break
                    
                    # Mostramos el efecto final de "LISTO" una sola vez
                    mostrar_progreso()
                    limpiar_pantalla() # Limpiamos para entrar al menú de edición

                    # --- FASE 2: CONFIRMACIÓN Y EDICIÓN  ---
                    while True:
                        limpiar_pantalla()
                        print(f'--- Confirmación de {num} Jugadores ---\n')
                        
                        # Mostramos la lista con NÚMEROS para que sea fácil elegir
                        for idx, n in enumerate(nombres, start=1):
                            print(f" {idx}. {n}")
                        print("\n" + "¬"*30)

                        print("¿Están correctos los nombres?")
                        opc = input("Presiona 'S' para Jugar o 'N' para cambiar alguno: ").strip().upper()

                        if opc == 'S':
                            print("\n¡Excelente! Iniciando partida...")
                            time.sleep(1.5)
                            jugar_versus(nombres)
                            input('\nPresiona Enter para volver al menú...')
                            break 

                        elif opc == 'N':
                            # --- MODO EDICIÓN ---
                            while True:
                                try:
                                    # Preguntamos qué número cambiar
                                    elegido = int(input(f"\n¿Qué número de jugador quieres corregir? (1-{num}): "))
                                    
                                    if 1 <= elegido <= num:
                                        # Pedimos el NUEVO nombre
                                        while True:
                                            nuevo_nombre = input(f"Nuevo nombre para Jugador {elegido}: ").strip()
                                            
                                            # Validaciones simples
                                            if not nuevo_nombre:
                                                print("Está Vacío."); time.sleep(0.5); continue
                                            if len(nuevo_nombre) > 12:
                                                print("Muy largo."); time.sleep(0.5); continue
                                            # Validamos que no sea igual a otro (pero sí puede ser igual al que ya tenía)
                                            if nuevo_nombre in nombres and nuevo_nombre != nombres[elegido-1]:
                                                print("Nombre repetido."); time.sleep(1); continue
                                            
                                            # Actualizamos
                                            nombres[elegido-1] = nuevo_nombre
                                            print("¡Nombre actualizado!")
                                            time.sleep(1)
                                            break 
                                        break 
                                    else:
                                        print(f"Ingresa un número entre 1 y {num}.")
                                except ValueError:
                                    print("Entrada inválida.")
                                                   
                            continue
        
  # -------------------------------------------------------------------------------------------------------------      

                    
                    jugar_versus(nombres)
                    input('\nPresiona Enter para volver al menú...')
                    break
                else:
                    print('Número inválido. Intente nuevamente.')
                    time.sleep(1)
                    limpiar_pantalla()
            continue
        print('Opción inválida. Intente nuevamente.')

