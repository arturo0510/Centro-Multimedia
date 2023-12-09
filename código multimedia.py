import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import time
import os
import threading
import vlc

class SmartTVApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart TV Interface")
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', self.exit_app)
        self.root.bind('<Control-q>', self.exit_app)

        # Obtener la resolución del monitor
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Inicializar variables para el fondo
        self.bg_paths = ["background1.jpg", "background2.jpg", "background3.jpg"]
        self.bg_images = [self.load_image(path, screen_width, screen_height) for path in self.bg_paths]
        self.current_bg_index = 0
        self.bg_label = tk.Label(root)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.root.bind("<Configure>", self.resize_background)
        self.update_background()

        # Crear botones de acceso
        buttons_info = [
            {"name": "Netflix", "icon": "netflix.png", "command": self.open_netflix_kiosk},
            {"name": "YouTube", "icon": "youtube.png", "command": self.open_youtube_kiosk},
            {"name": "Google", "icon": "google.png", "command": self.open_google_kiosk},
            {"name": "Reproducir", "icon": "usb.png", "command": self.play_usb_content},
            {"name": "Reproducir con VLC", "icon": "vlc.png", "command": self.play_vlc_content}
        ]

        self.buttons = []
        for i, button_info in enumerate(buttons_info):
            button = ttk.Button(root, text=button_info["name"], compound=tk.TOP, style="WhiteButton.TButton",
                                command=button_info["command"])
            button.image = self.load_image(button_info["icon"], 100, 100)
            button.config(image=button.image)
            button.grid(row=2, column=i, padx=10, pady=10)
            self.buttons.append(button)

        # Configurar la geometría de la ventana
        root.grid_rowconfigure(0, weight=1)
        root.grid_rowconfigure(4, weight=1)
        root.grid_columnconfigure(list(range(len(self.buttons))), weight=1)

        # Establecer estilos para los botones
        style = ttk.Style()
        style.configure("WhiteButton.TButton", background="white", foreground="black", bordercolor="white")

        # Añadir título en la parte superior izquierda
        title_label = tk.Label(root, text="Smart TV", font=("Helvetica", 30), fg="black", bg=root.cget("bg"))
        title_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Añadir la hora en la parte superior derecha
        self.time_label = tk.Label(root, text="", font=("Helvetica", 24), fg="black", bg=root.cget("bg"))
        self.time_label.grid(row=0, column=len(self.buttons)-1, padx=10, pady=10, sticky="e")
        self.update_time()

        # Estado para rastrear la posición actual del cursor
        self.current_button_index = 0

        # Inicializar la entrada del teclado universal
        self.keyboard = None  # inputs no se está utilizando actualmente

        # Lógica para manejar la entrada del teclado universal
        self.root.bind('<KeyPress>', self.handle_keypress)

        # Configurar estilos para los botones seleccionados
        style.configure("SelectedButton.TButton", background="yellow", foreground="black", bordercolor="white")

        # Inicializar el reproductor multimedia
        self.media_player = None
        self.media_thread = None

    def resize_background(self, event):
        img = self.bg_images[self.current_bg_index]
        img = img.resize((self.root.winfo_width(), self.root.winfo_height()), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else None)
        self.bg_images[self.current_bg_index] = ImageTk.PhotoImage(img)
        self.bg_label.configure(image=self.bg_images[self.current_bg_index])

    def update_background(self):
        self.current_bg_index = (self.current_bg_index + 1) % len(self.bg_images)
        self.bg_label.configure(image=self.bg_images[self.current_bg_index])
        self.root.after(5000, self.update_background)

    def update_time(self):
        current_time = time.strftime("%H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def open_netflix_kiosk(self):
        url_servicios_video = "https://www.netflix.com"
        os.system(f"chromium-browser --no-sandbox --kiosk {url_servicios_video}")

    def open_youtube_kiosk(self):
        url_servicios_video = "https://www.youtube.com"
        os.system(f"chromium-browser --no-sandbox --kiosk {url_servicios_video}")

    def open_google_kiosk(self):
        url_servicios_video = "https://www.google.com"
        os.system(f"chromium-browser --no-sandbox --kiosk {url_servicios_video}")

    def play_usb_content(self):
        usb_path = filedialog.askdirectory(title="Seleccionar USB")
        if usb_path:
            self.stop_media_player()  # Detener la reproducción actual si la hay
            self.show_usb_content_interface(usb_path)

    def play_vlc_content(self):
        self.stop_media_player()  # Detener la reproducción actual si la hay
        media_path = filedialog.askopenfilename(title="Seleccionar archivo multimedia",
                                                 filetypes=(("Archivos multimedia", "*.mp4;*.avi;*.mkv"), ("Todos los archivos", "*.*")))
        if media_path:
            self.play_video(media_path)

    def exit_app(self, event=None):
        self.stop_media_player()  # Detener la reproducción antes de salir
        self.root.destroy()

    def load_image(self, path, width, height):
        img = Image.open(path)
        img = img.resize((width, height), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else None)
        return ImageTk.PhotoImage(img)

    def handle_keypress(self, event):
        key = event.keysym.lower()

        if key == 'a':
            self.move_left()
        elif key == 'd':
            self.move_right()
        elif key == 'w':
            self.move_up()
        elif key == 's':
            self.move_down()
        elif key == 'return':
            self.select_application()
        elif key == 'm':
            self.show_media_player_interface()
        elif key == 'q':
            if self.media_player:
                self.stop_media_player()
                self.root.deiconify()  # Mostrar la ventana principal después de salir del reproductor multimedia

    def move_left(self):
        self.current_button_index = (self.current_button_index - 1) % len(self.buttons)
        self.highlight_current_button()

    def move_right(self):
        self.current_button_index = (self.current_button_index + 1) % len(self.buttons)
        self.highlight_current_button()

    def move_up(self):
        self.current_button_index = (self.current_button_index - len(self.buttons)) % len(self.buttons)
        self.highlight_current_button()

    def move_down(self):
        self.current_button_index = (self.current_button_index + len(self.buttons)) % len(self.buttons)
        self.highlight_current_button()

    def select_application(self):
        selected_button = self.buttons[self.current_button_index]
        selected_button.invoke()

    def exit_application(self):
        print("Saliendo de la aplicación")

    def highlight_current_button(self):
        for i, button in enumerate(self.buttons):
            if i == self.current_button_index:
                button.configure(style="SelectedButton.TButton")
            else:
                button.configure(style="WhiteButton.TButton")

    def show_usb_content_interface(self, usb_path):
        # Crear una nueva ventana para la interfaz de contenido USB
        usb_content_window = tk.Toplevel(self.root)
        usb_content_window.title("Contenido USB")
        usb_content_window.geometry("1600x900")

        # Obtener lista de archivos en la memoria USB
        usb_files = os.listdir(usb_path)

        # Filtrar archivos multimedia (imágenes, música, videos)
        image_files = [f for f in usb_files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        audio_files = [f for f in usb_files if f.lower().endswith(('.mp3', '.wav', '.flac'))]
        video_files = [f for f in usb_files if f.lower().endswith(('.mp4', '.avi', '.mkv'))]

        # Crear listas con nombres de archivos
        image_listbox = tk.Listbox(usb_content_window, selectmode=tk.SINGLE)
        for img in image_files:
            image_listbox.insert(tk.END, img)
        image_listbox.pack(pady=10)

        audio_listbox = tk.Listbox(usb_content_window, selectmode=tk.SINGLE)
        for audio in audio_files:
            audio_listbox.insert(tk.END, audio)
        audio_listbox.pack(pady=10)

        video_listbox = tk.Listbox(usb_content_window, selectmode=tk.SINGLE)
        for video in video_files:
            video_listbox.insert(tk.END, video)
        video_listbox.pack(pady=10)

        # Botones para reproducir el contenido seleccionado
        play_image_button = ttk.Button(usb_content_window, text="Reproducir Imágenes", command=lambda: self.play_media_files(image_listbox.get(tk.ACTIVE), usb_path, "image"))
        play_image_button.pack(pady=10)

        play_audio_button = ttk.Button(usb_content_window, text="Reproducir Música", command=lambda: self.play_media_files(audio_listbox.get(tk.ACTIVE), usb_path, "audio"))
        play_audio_button.pack(pady=10)

        play_video_button = ttk.Button(usb_content_window, text="Reproducir Video", command=lambda: self.play_media_files(video_listbox.get(tk.ACTIVE), usb_path, "video"))
        play_video_button.pack(pady=10)

        # Botón para salir de la interfaz de contenido USB
        back_button = ttk.Button(usb_content_window, text="Volver al Menú Principal", command=usb_content_window.destroy)
        back_button.pack(pady=10)

    def play_media_files(self, media_file, usb_path, media_type):
        if not media_file:
            return

        media_path = os.path.join(usb_path, media_file)
        self.stop_media_player()  # Detener la reproducción actual si la hay

        if media_type == "image":
            self.play_slideshow(usb_path, image_files)
        elif media_type == "audio":
            self.play_audio(media_path)
        elif media_type == "video":
            self.play_video(media_path)

    def play_slideshow(self, usb_path, image_files):
        # Reproducir imágenes en modo presentación
        for img_file in image_files:
            img_path = os.path.join(usb_path, img_file)
            img = Image.open(img_path)
            img = img.resize((self.root.winfo_width(), self.root.winfo_height()), Image.ANTIALIAS)
            img = ImageTk.PhotoImage(img)
            self.bg_label.configure(image=img)
            self.bg_label.image = img
            self.root.update()
            time.sleep(5)

    def play_audio(self, audio_path):
        # Reproducir música en bucle infinito
        self.media_player = vlc.MediaPlayer(audio_path)
        self.media_player.play()
        self.media_thread = threading.Thread(target=self.media_player_listener)
        self.media_thread.start()

    def play_video(self, video_path):
        self.media_player = vlc.MediaPlayer(video_path)
        self.media_player.play()
        self.media_thread = threading.Thread(target=self.media_player_listener)
        self.media_thread.start()

    def media_player_listener(self):
        while True:
            if self.media_player.get_state() == vlc.State.Ended:
                self.stop_media_player()
                break
            time.sleep(1)

    def stop_media_player(self):
        if self.media_player:
            self.media_player.stop()
            if self.media_thread:
                self.media_thread.join()
                self.media_thread = None

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartTVApp(root)
    root.mainloop()


