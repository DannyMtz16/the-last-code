# the_last_code.py
import tkinter as tk
from tkinter import messagebox
import json
import os
import random
import threading
import time

# Sonidos opcionales con pygame (si no está instalado funciona sin sonidos)
try:
    import pygame
    pygame.mixer.init()
    SOUND_AVAILABLE = True
except Exception:
    SOUND_AVAILABLE = False

SAVEFILE = "savegame.json"

# ---------------------------
# UTILIDADES: guardar / cargar
# ---------------------------
def load_save():
    if os.path.exists(SAVEFILE):
        try:
            with open(SAVEFILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_game(data: dict):
    with open(SAVEFILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ---------------------------
# Sonidos (si están disponibles)
# ---------------------------
def play_sound(path, loops=0):
    if not SOUND_AVAILABLE:
        return
    try:
        s = pygame.mixer.Sound(path)
        s.play(loops=loops)
    except Exception:
        pass

def stop_music():
    if not SOUND_AVAILABLE:
        return
    try:
        pygame.mixer.stop()
    except Exception:
        pass

# ---------------------------
# APP
# ---------------------------
class TheLastCodeApp:
    def __init__(self, root):
        self.root = root
        root.title("The Last Code")
        root.geometry("900x640")
        root.resizable(False, False)

        # estado del juego en memoria
        self.state = load_save()
        self.player_name = self.state.get("player_name", None)
        self.current_scene = self.state.get("current_scene", None)  # e.g. "scenario1", etc.
        self.scene_data = self.state.get("scene_data", {})

        # contenedores
        self.main_frame = tk.Frame(root, bg="#111111")
        self.main_frame.pack(fill="both", expand=True)

        # Fuente simple
        self.title_font = ("Segoe UI", 36, "bold")
        self.h1 = ("Segoe UI", 18, "bold")
        self.h2 = ("Segoe UI", 14, "normal")

        self.show_welcome_screen()

    # ---------------------------
    # UTIL: limpiar pantalla
    # ---------------------------
    def clear(self):
        for w in self.main_frame.winfo_children():
            w.destroy()
        stop_music()

    # ---------------------------
    # Animación de texto (tipo máquina)
    # ---------------------------
    def type_text(self, label, text, delay=30, after_callback=None):
        # label: tk.Label, text: str, delay in ms per char
        label.config(text="")
        def run(i=0):
            if i <= len(text):
                label.config(text=text[:i])
                self.root.after(delay, run, i+1)
            else:
                if after_callback:
                    after_callback()
        run(1)

    # ---------------------------
    # PANTALLA: Bienvenida
    # ---------------------------
    def show_welcome_screen(self):
        self.clear()
        f = self.main_frame

        # Left title box
        left = tk.Frame(f, bg="#0f1720", width=420, height=640)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        title_label = tk.Label(left, text="The Last Code", font=self.title_font, bg="#0f1720", fg="#f7fafc")
        title_label.place(relx=0.5, rely=0.15, anchor="center")

        # Small description
        desc = tk.Label(left, text="Aventura interactiva\n", bg="#0f1720", fg="#cbd5e1", font=self.h2)
        desc.place(relx=0.5, rely=0.25, anchor="center")

        # Right area for buttons
        right = tk.Frame(f, bg="#081018")
        right.pack(side="left", fill="both", expand=True)
        right.pack_propagate(False)

        # Spacer to place buttons ~3cm below title (approx)
        spacer = tk.Frame(right, height=120, bg="#081018")
        spacer.pack()

        new_btn = tk.Button(right, text="New Game", font=self.h1, width=18, command=self.new_game)
        new_btn.pack(pady=(0, 10))

        # Continue only if save exists
        if os.path.exists(SAVEFILE):
            cont_btn = tk.Button(right, text="Continue", font=self.h1, width=18, command=self.continue_game)
            cont_btn.pack()
        else:
            # invisible placeholder for spacing niceness
            tk.Label(right, text="", bg="#081018").pack()

        # Small footer
        footer = tk.Label(right, text="© The Last Code - Demo", bg="#081018", fg="#94a3b8", font=("Segoe UI", 10))
        footer.pack(side="bottom", pady=12)

    def new_game(self):
        # reset saved current_scene and scene_data (but keep player_name if any? we will ask name anyway)
        self.state = {}
        if os.path.exists(SAVEFILE):
            try:
                os.remove(SAVEFILE)
            except Exception:
                pass
        self.player_name = None
        self.current_scene = None
        self.scene_data = {}
        self.show_name_screen()

    def continue_game(self):
        self.state = load_save()
        self.player_name = self.state.get("player_name", None)
        self.current_scene = self.state.get("current_scene", None)
        self.scene_data = self.state.get("scene_data", {})
        if self.player_name is None:
            self.show_name_screen()
            return
        # if in the middle of a scenario, resume
        if self.current_scene in ("scenario1", "scenario2", "scenario3"):
            self.start_scenario(self.current_scene, resume=True)
        else:
            self.show_scenario_selection()

    # ---------------------------
    # PANTALLA: Registro / Nombre
    # ---------------------------
    def show_name_screen(self):
        self.clear()
        f = self.main_frame

        label_frame = tk.Frame(f, bg="#07101a")
        label_frame.pack(fill="both", expand=True)

        text_label = tk.Label(label_frame, text="", font=self.h1, bg="#07101a", fg="#e2e8f0")
        text_label.place(relx=0.5, rely=0.35, anchor="center")

        entry_var = tk.StringVar()
        name_entry = tk.Entry(label_frame, textvariable=entry_var, font=self.h2, width=30)
        name_entry.place(relx=0.5, rely=0.47, anchor="center")

        def after_typing():
            name_entry.focus_set()

        # start typing animation
        anim_text = "Bienvenido... Introduce tu nombre o apodo"
        self.type_text(text_label, anim_text, delay=40, after_callback=after_typing)

        def submit_name(event=None):
            name = entry_var.get().strip()
            if not name:
                messagebox.showwarning("Nombre requerido", "Introduce un nombre o apodo para continuar.")
                return
            self.player_name = name
            # save minimal data
            self.state = {"player_name": self.player_name}
            save_game(self.state)
            self.show_scenario_selection()

        submit_btn = tk.Button(label_frame, text="Continuar", font=self.h2, command=submit_name)
        submit_btn.place(relx=0.5, rely=0.58, anchor="center")
        name_entry.bind("<Return>", submit_name)

    # ---------------------------
    # PANTALLA: Selección de escenarios
    # ---------------------------
    def show_scenario_selection(self):
        self.clear()
        f = self.main_frame

        header_frame = tk.Frame(f, bg="#0b1220", height=90)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        header_label = tk.Label(header_frame, text="", font=self.h1, bg="#0b1220", fg="#e6eef6")
        header_label.place(relx=0.5, rely=0.5, anchor="center")

        welcome_text = f"Selecciona un nivel ({self.player_name})"
        self.type_text(header_label, welcome_text, delay=35)

        cards_frame = tk.Frame(f, bg="#07101a")
        cards_frame.pack(fill="both", expand=True, pady=12, padx=20)

        # Create 3 cards horizontally
        card_width = 250
        padx = 20

        # Helper to create a card
        def create_card(parent, title, difficulty, description, command):
            card = tk.Frame(parent, bg="#0f1720", width=card_width, height=300, relief="raised", bd=2)
            card.pack(side="left", padx=padx, pady=20)
            card.pack_propagate(False)
            # "icon" as canvas drawing
            cv = tk.Canvas(card, width=80, height=80, bg="#0f1720", highlightthickness=0)
            cv.create_oval(10,10,70,70, outline="#94a3b8", width=3)
            cv.pack(pady=12)
            title_lbl = tk.Label(card, text=title, bg="#0f1720", fg="#e6eef6", font=self.h2)
            title_lbl.pack()
            diff_lbl = tk.Label(card, text=f"Dificultad: {difficulty}", bg="#0f1720", fg="#94a3b8")
            diff_lbl.pack()
            desc_lbl = tk.Label(card, text=description, bg="#0f1720", fg="#9fb4c9", wraplength=220, justify="center")
            desc_lbl.pack(pady=8)
            btn = tk.Button(card, text="Jugar", command=command)
            btn.pack(side="bottom", pady=12)
            return card

        create_card(cards_frame,
                    "Escenario 1: Habitación",
                    "Fácil",
                    "Escapa de una habitación con lluvia y truenos. Escribe tus acciones.",
                    lambda: self.start_scenario("scenario1"))

        create_card(cards_frame,
                    "Escenario 2: Hospital",
                    "Medio",
                    "Estás en el 3er piso de un hospital de 12. Evita ser descubierto.",
                    lambda: self.start_scenario("scenario2"))

        create_card(cards_frame,
                    "Escenario 3: Bosque",
                    "Difícil",
                    "Sobrevive al bosque con fauna salvaje y encuentra una cabaña.",
                    lambda: self.start_scenario("scenario3"))

    # ---------------------------
    # INICIO ESCENARIO
    # ---------------------------
    def start_scenario(self, scenario_id, resume=False):
        self.current_scene = scenario_id
        # save state
        self.state["player_name"] = self.player_name
        self.state["current_scene"] = self.current_scene
        self.state.setdefault("scene_data", {})
        save_game(self.state)

        # Routing
        if scenario_id == "scenario1":
            self.scene1(resume=resume)
        elif scenario_id == "scenario2":
            self.scene2(resume=resume)
        elif scenario_id == "scenario3":
            self.scene3(resume=resume)

    # ---------------------------
    # ESCENARIO 1: Habitación (Fácil)
    # ---------------------------
    def scene1(self, resume=False):
        self.clear()
        f = self.main_frame

        # Ambient sound: rain+thunder (if present, you must provide your own sound files in same folder)
        # try to play "rain.wav" looped and "thunder.wav" on events
        if SOUND_AVAILABLE:
            # Attempt to play rain.wav looped; if file missing, ignore
            try:
                rain = pygame.mixer.Sound("rain.wav")
                rain.play(loops=-1)
            except Exception:
                pass

        # initial description
        desc_frame = tk.Frame(f, bg="#071018")
        desc_frame.pack(fill="both", expand=True)

        title = tk.Label(desc_frame, text="Escenario 1 - Habitación", font=self.h1, bg="#071018", fg="#e6eef6")
        title.pack(pady=8)

        text_area = tk.Text(desc_frame, height=14, wrap="word", font=("Segoe UI", 12), bg="#0b1b22", fg="#e6eef6")
        text_area.pack(padx=20, pady=8, fill="both", expand=False)

        input_frame = tk.Frame(desc_frame, bg="#071018")
        input_frame.pack(pady=6)

        cmd_var = tk.StringVar()
        entry = tk.Entry(input_frame, textvariable=cmd_var, font=self.h2, width=60)
        entry.pack(side="left", padx=8)
        entry.focus_set()

        submit_btn = tk.Button(input_frame, text="OK", command=lambda: process_command(cmd_var.get().strip().lower()))
        submit_btn.pack(side="left")

        # Game state
        data = self.state.get("scene_data", {}).get("scenario1", {})
        if not data:
            data = {"found_key": False, "bed_checked": False, "curtains_open": False, "window_checked": False, "escaped": False}
            self.state.setdefault("scene_data", {})["scenario1"] = data
            save_game(self.state)

        # helper to print and save
        def write(text):
            text_area.insert("end", text + "\n\n")
            text_area.see("end")

        # initial description (typed quickly)
        intro = ("Despiertas en una habitación con ventanas empañadas. Afuera llueve y se escuchan truenos. "
                 "Hay una cama, una mesa pequeña con un cajón, unas cortinas y una ventana con pestillo. "
                 "¿Qué deseas hacer? (Escribe acciones como: checar debajo de la cama, mover cortinas, mirar por la ventana, abrir cajón)")
        write(intro)

        def process_command(cmd):
            if not cmd:
                return
            write(f"> {cmd}")
            # core logic
            if "bajo" in cmd or "debajo" in cmd or "cama" in cmd:
                if not data["bed_checked"]:
                    write("Revisas debajo de la cama y encuentras una llave pequeña. (La llave podría servir).")
                    data["found_key"] = True
                    data["bed_checked"] = True
                else:
                    write("Ya revisaste debajo de la cama, solo hay polvo.")
            elif "cortina" in cmd or "mover" in cmd:
                if not data["curtains_open"]:
                    write("Abres las cortinas. Afuera sólo ves una calle vacía y la lluvia; la ventana tiene un pestillo.")
                    data["curtains_open"] = True
                else:
                    write("Las cortinas ya están abiertas.")
            elif "ventana" in cmd or "mirar" in cmd:
                write("Al mirar la ventana notas que el pestillo está oxidado pero se puede abrir desde dentro con una herramienta.")
                data["window_checked"] = True
            elif "cajón" in cmd or "abrir cajón" in cmd:
                if data["found_key"]:
                    write("Abres el cajón usando la llave. Dentro hay un destornillador. Puede servir para forzar el pestillo.")
                    data["has_screwdriver"] = True
                else:
                    write("Intentas abrir el cajón pero está cerrado con un pequeño candado.")
            elif "usar" in cmd or "forzar" in cmd or "destornillador" in cmd:
                if data.get("has_screwdriver") or data.get("found_key"):
                    write("Usas la herramienta para forzar el pestillo. La ventana cede y puedes salir por ella. ¡Has escapado!")
                    data["escaped"] = True
                    self.state["scene_data"]["scenario1"] = data
                    save_game(self.state)
                    self.win_screen()
                    return
                else:
                    write("No tienes herramientas para forzar el pestillo.")
            else:
                write("No entiendo esa acción exactamente. Intenta acciones como: checar debajo de la cama, abrir cajón, mover cortinas, mirar por la ventana, usar destornillador.")
            # save after every action
            self.state["scene_data"]["scenario1"] = data
            save_game(self.state)

        # optional: allow Enter to submit
        entry.bind("<Return>", lambda e: submit_btn.invoke())

    # ---------------------------
    # ESCENARIO 2: Hospital (Medio)
    # ---------------------------
    def scene2(self, resume=False):
        self.clear()
        f = self.main_frame

        # Basic setup: player starts at floor 3
        data = self.state.get("scene_data", {}).get("scenario2", {})
        if not data:
            # floors: 1..12; player starts at floor 3
            # each floor has rooms, some occupied (if enter occupied -> defeat)
            floors = {}
            for i in range(1, 13):
                # each floor has 4 rooms, some are occupied randomly
                rooms = {}
                for r in range(1, 5):
                    occupied = random.random() < (0.18 + 0.02 * i)  # higher floors maybe more chance
                    rooms[f"R{r}"] = {"occupied": occupied, "has_tool": random.random() < 0.25}
                floors[str(i)] = rooms
            data = {"floor": 3, "floors": floors, "has_key": False, "escaped": False}
            self.state.setdefault("scene_data", {})["scenario2"] = data
            save_game(self.state)

        title = tk.Label(f, text="Escenario 2 - Hospital", font=self.h1, bg="#071018", fg="#e6eef6")
        title.pack(pady=6)

        text_area = tk.Text(f, height=14, wrap="word", font=("Segoe UI", 12), bg="#08121a", fg="#e6eef6")
        text_area.pack(padx=20, pady=8, fill="both", expand=False)

        input_frame = tk.Frame(f, bg="#071018")
        input_frame.pack(pady=6)

        cmd_var = tk.StringVar()
        entry = tk.Entry(input_frame, textvariable=cmd_var, font=self.h2, width=60)
        entry.pack(side="left", padx=8)
        entry.focus_set()
        submit_btn = tk.Button(input_frame, text="OK", command=lambda: process_command(cmd_var.get().strip().lower()))
        submit_btn.pack(side="left")

        def write(text):
            text_area.insert("end", text + "\n\n")
            text_area.see("end")

        # initial description
        intro = (f"Estás en el pasillo del piso {data['floor']} de un hospital de 12 pisos. Hay puertas a las habitaciones etiquetadas R1..R4, "
                 "un elevador y escaleras. Ten cuidado: si entras a una habitación que está ocupada, serás descubierto y perderás.")
        write(intro)

        def process_command(cmd):
            if not cmd:
                return
            write(f"> {cmd}")
            floor = data["floor"]
            floors = data["floors"]

            if "ir a" in cmd or "subir" in cmd or "bajar" in cmd:
                # change floor
                if "subir" in cmd or "ir arriba" in cmd or "subir a" in cmd:
                    if floor >= 12:
                        write("Ya estás en el piso más alto.")
                    else:
                        floor += 1
                        data["floor"] = floor
                        write(f"Subes al piso {floor}.")
                elif "bajar" in cmd or "ir abajo" in cmd or "bajar a" in cmd:
                    if floor <= 1:
                        write("Ya estás en el piso 1.")
                    else:
                        floor -= 1
                        data["floor"] = floor
                        write(f"Bajas al piso {floor}.")
                else:
                    write("Especifica subir o bajar.")
            elif "elevador" in cmd:
                # random chance elevator active
                if random.random() < 0.6:
                    dest = random.randint(1, 12)
                    data["floor"] = dest
                    write(f"El elevador funciona. Sales en el piso {dest}.")
                else:
                    write("El elevador está fuera de servicio en este momento.")
            elif "entrar r" in cmd or "entrar a r" in cmd or "abrir r" in cmd:
                # detect room code
                found = None
                for token in cmd.split():
                    if token.upper().startswith("R") and token[1:].isdigit():
                        found = token.upper()
                        break
                if not found:
                    write("Indica la habitación (ej: entrar R2).")
                else:
                    room = floors[str(floor)].get(found)
                    if not room:
                        write("No existe esa habitación en este piso.")
                    else:
                        if room["occupied"]:
                            # defeat
                            write(f"Entras a {found} y hay alguien dentro. Te han descubierto.")
                            self.state["scene_data"]["scenario2"] = data
                            save_game(self.state)
                            self.lose_screen(reason="descubierto")
                            return
                        else:
                            write(f"Entras a {found}. La habitación está vacía.")
                            if room.get("has_tool"):
                                # collect tool
                                write("Encuentras una herramienta (destornillador/manija). Podría servir para abrir puertas cerradas.")
                                data["has_key"] = True
                                room["has_tool"] = False
            elif "buscar" in cmd or "revisar" in cmd or "inspeccionar" in cmd:
                write("Revisas el pasillo: hay puertas, una salida de emergencia en el piso 1 y un acceso a urgencias en la planta baja.")
            elif "salir" in cmd or "urgencias" in cmd or "salida" in cmd:
                # if on floor 1 or 0, can escape to urgencias
                if data["floor"] <= 1:
                    write("Encuentras la salida de urgencias. ¡Has salido del hospital!")
                    data["escaped"] = True
                    self.state["scene_data"]["scenario2"] = data
                    save_game(self.state)
                    self.win_screen()
                    return
                else:
                    write("La entrada de urgencias está en la planta baja. Debes descender primero.")
            else:
                write("Acciones posibles: subir, bajar, elevador, entrar R1..R4, buscar, salir/urgencias.")
            # save
            self.state["scene_data"]["scenario2"] = data
            save_game(self.state)

        entry.bind("<Return>", lambda e: submit_btn.invoke())

    # ---------------------------
    # ESCENARIO 3: Bosque (Difícil)
    # ---------------------------
    def scene3(self, resume=False):
        self.clear()
        f = self.main_frame

        data = self.state.get("scene_data", {}).get("scenario3", {})
        if not data:
            data = {"pos": 0, "has_light": False, "water_bottles": 0, "escaped": False}
            self.state.setdefault("scene_data", {})["scenario3"] = data
            save_game(self.state)

        title = tk.Label(f, text="Escenario 3 - Bosque", font=self.h1, bg="#071018", fg="#e6eef6")
        title.pack(pady=6)

        text_area = tk.Text(f, height=14, wrap="word", font=("Segoe UI", 12), bg="#07101a", fg="#e6eef6")
        text_area.pack(padx=20, pady=8, fill="both", expand=False)

        input_frame = tk.Frame(f, bg="#071018")
        input_frame.pack(pady=6)

        cmd_var = tk.StringVar()
        entry = tk.Entry(input_frame, textvariable=cmd_var, font=self.h2, width=60)
        entry.pack(side="left", padx=8)
        entry.focus_set()
        submit_btn = tk.Button(input_frame, text="OK", command=lambda: process_command(cmd_var.get().strip().lower()))
        submit_btn.pack(side="left")

        def write(text):
            text_area.insert("end", text + "\n\n")
            text_area.see("end")

        intro = ("Te adentras en un bosque al anochecer. Hay senderos, señales viejas, una linterna tirada cerca, y sonidos de animales. "
                 "Debes encontrar una cabaña para refugiarte. Ten cuidado: algunos animales son agresivos.")
        write(intro)

        def random_encounter():
            # 15% chance of encountering wild animal on move
            if random.random() < 0.15:
                animal = random.choice(["lobo", "serpiente", "oso"])
                write(f"¡Encuentras un {animal}! Es peligroso.")
                # player can try to huir or usar objeto
                return animal
            return None

        def process_command(cmd):
            if not cmd:
                return
            write(f"> {cmd}")
            if "tomar linterna" in cmd or "linterna" in cmd:
                if not data.get("has_light"):
                    write("Recoges la linterna. Puede ayudarte por la noche.")
                    data["has_light"] = True
                else:
                    write("Ya tienes la linterna.")
            elif "avanzar" in cmd or "seguir" in cmd or "ir" in cmd:
                # move forward
                # chance of water bottle, rope, or encounter
                data["pos"] += 1
                write("Caminas por el sendero...")
                # random find
                rr = random.random()
                if rr < 0.12:
                    write("Encuentras una botella de agua.")
                    data["water_bottles"] = data.get("water_bottles", 0) + 1
                elif rr < 0.18:
                    write("Encuentras una cuerda que podría servir.")
                    data["rope"] = True
                # encounter
                animal = random_encounter()
                if animal:
                    # simple resolution: if bear or wolf, need to huir or use rope/linterna
                    if animal == "serpiente":
                        # chance to avoid: if you have stick/rope, safe
                        if data.get("rope") or data.get("has_light"):
                            write("Logras espantar a la serpiente y sigues.")
                        else:
                            write("La serpiente te muerde. Pierdes consciencia.")
                            self.state["scene_data"]["scenario3"] = data
                            save_game(self.state)
                            self.lose_screen(reason="atacado")
                            return
                    else:
                        # wolf or oso
                        if data.get("has_light") and random.random() < 0.7:
                            write("Usas la linterna para asustar al animal y escapas.")
                        elif data.get("rope") and random.random() < 0.5:
                            write("Usas la cuerda para distraer y escapas.")
                        else:
                            write(f"El {animal} te ataca.")
                            self.state["scene_data"]["scenario3"] = data
                            save_game(self.state)
                            self.lose_screen(reason="atacado")
                            return
                # maybe find cabin
                if data["pos"] >= 5 and random.random() < 0.35:
                    write("Ves una cabaña entre los árboles. Has encontrado refugio. ¡Has sobrevivido!")
                    data["escaped"] = True
                    self.state["scene_data"]["scenario3"] = data
                    save_game(self.state)
                    self.win_screen()
                    return
            elif "buscar" in cmd or "inspeccionar" in cmd:
                write("Exploras alrededor: hay senderos, señales viejas y zonas con animales. Mantén la calma.")
            elif "usar cuerda" in cmd or "usar cuerda" in cmd:
                if data.get("rope"):
                    write("Usas la cuerda para cruzar un precipicio o distraer animales si es necesario.")
                else:
                    write("No tienes cuerda.")
            elif "beber" in cmd or "agua" in cmd:
                if data.get("water_bottles", 0) > 0:
                    data["water_bottles"] -= 1
                    write("Bebes agua y recuperas energías.")
                else:
                    write("No tienes agua.")
            else:
                write("Intenta acciones como: tomar linterna, avanzar, buscar, usar cuerda, beber.")
            # save
            self.state["scene_data"]["scenario3"] = data
            save_game(self.state)

        entry.bind("<Return>", lambda e: submit_btn.invoke())

    # ---------------------------
    # PANTALLA: Éxito
    # ---------------------------
    def win_screen(self):
        self.clear()
        f = self.main_frame

        # play success bells
        if SOUND_AVAILABLE:
            try:
                bell = pygame.mixer.Sound("bells.wav")
                bell.play()
            except Exception:
                pass

        frame = tk.Frame(f, bg="#072016")
        frame.pack(fill="both", expand=True)

        msg = tk.Label(frame, text=f"Felicidades {self.player_name} por completar el nivel", font=self.h1, bg="#072016", fg="#dff6e3")
        msg.pack(expand=True)

        # After 5 seconds, go to welcome screen
        def go_back():
            # reset current scene
            self.state["current_scene"] = None
            self.state["scene_data"] = {}
            save_game(self.state)
            self.show_welcome_screen()

        # run after 5s (5000 ms)
        self.root.after(5000, go_back)

    # ---------------------------
    # PANTALLA: Derrota
    # ---------------------------
    def lose_screen(self, reason="descubierto"):
        self.clear()
        f = self.main_frame

        # stop ambient music if any
        stop_music()

        frame = tk.Frame(f, bg="#19080a")
        frame.pack(fill="both", expand=True)

        # Glitch animation: flash text a few times
        label1 = tk.Label(frame, text="El juego está fallando...", font=self.h2, bg="#19080a", fg="#fca5a5")
        label1.pack(pady=30)
        final_label = tk.Label(frame, text="", font=self.h1, bg="#19080a", fg="#ffeeee")
        final_label.pack(pady=20)

        def glitch_cycle(i=0):
            if i < 6:
                final_label.config(text="¡¡ ERROR !!", fg=random.choice(["#ff4d4d", "#ffeeee", "#ffbcbc"]))
                self.root.after(200, glitch_cycle, i+1)
            else:
                # final game over message
                if reason == "descubierto":
                    final_label.config(text="Has sido descubierto", fg="#ffffff")
                else:
                    final_label.config(text="Has sido atacado", fg="#ffffff")
                sub = tk.Label(frame, text="Game Over", font=self.h1, bg="#19080a", fg="#f87171")
                sub.pack(pady=8)
                # option to return to start
                btn = tk.Button(frame, text="Volver al inicio", command=self.reset_to_start)
                btn.pack(pady=12)

        glitch_cycle()

    def reset_to_start(self):
        # clear saved current scene and data
        self.state["current_scene"] = None
        self.state["scene_data"] = {}
        save_game(self.state)
        self.show_welcome_screen()

# ---------------------------
# Ejecutar app
# ---------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = TheLastCodeApp(root)
    root.mainloop()