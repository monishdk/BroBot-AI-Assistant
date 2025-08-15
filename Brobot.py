# BroBot_GUI.py
# Fancy assistant window (Tkinter) that uses your BroBot logic.
# - Animated gradient background
# - Glowing buttons (Speak, Type, Exit)
# - Scrollable chat area showing user + BroBot lines
# - Non-blocking voice listening (thread)
# - Keeps your commands: music, jokes, to-dos, reminders, openers, Tamil mode
#
# Requirements: same as original (speechrecognition, pyttsx3, gTTS, playsound, pygame, etc.)

import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import queue
import time
import os
import random
import webbrowser
import datetime
import re

# Your original imports (kept)
import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import playsound
import pygame
import tempfile

# -------------------------
# Your original data (jokes, roasts)
# -------------------------
jokes = [
    "Why don’t scientists trust atoms? Because they make up everything.",
    "Why did the developer go broke? Because he used up all his cache.",
    "I'm reading a book about anti-gravity. It's impossible to put down.",
    "Why do Java developers wear glasses? Because they can’t C sharp."
]

roasts = [
    "Bro, your Wi-Fi speed is faster than your brain sometimes.",
    "Even ChatGPT needs a break after talking to you.",
    "You're running Python on pure luck and faith.",
    "If laziness was a subject, you'd have a PhD da.",
    "You dream of 100 crore but can’t even find your USB cable."
]

# -------------------------
# Globals & engine init
# -------------------------
engine = pyttsx3.init()
voices = engine.getProperty('voices')
if voices:
    voice_index = 1 if len(voices) > 1 else 0
    try:
        engine.setProperty('voice', voices[voice_index].id)
    except Exception:
        pass
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

recognizer = sr.Recognizer()

# Music variables (keep your folder)
music_dir = r"F:\pendrive\songs"  # change if needed
current_song_index = 0
songs = []

# Thread-safe queue for GUI messages
msg_queue = queue.Queue()

# Flag for stopping any long-running background threads if exit
stop_threads = False

# -------------------------
# Helper I/O for GUI chat
# -------------------------
def gui_log(text, sender="BroBot"):
    """Send a message to the GUI (puts into queue to be processed by mainloop)."""
    msg_queue.put((sender, text))

# -------------------------
# SPEAK (English) - reused engine
# -------------------------
def speak(text):
    # prints to console and queues to GUI
    print("BroBot: " + text)
    gui_log(text, "BroBot")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("[TTS error]", e)

# -------------------------
# SPEAK (Tamil) - gTTS
# -------------------------
def speak_tamil(text):
    try:
        # create a temp file and play it
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.close()
        tts = gTTS(text=text, lang='ta')
        tts.save(tmp.name)
        gui_log(text, "BroBot (TA)")
        playsound.playsound(tmp.name)
        os.remove(tmp.name)
    except Exception as e:
        print("[gTTS error]", e)
        speak("Tamil voice failed da.")

# -------------------------
# GREETING
# -------------------------
def wish_me():
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good morning da, Monish!")
    elif 12 <= hour < 18:
        speak("Good afternoon mapla!")
    else:
        speak("Good evening bro!")
    speak("I am BroBot, your local thambi. Tell me what to do da!")

# -------------------------
# LISTEN (non-blocking thread entry)
# -------------------------
def listen_blocking_and_respond():
    """Run in a thread: listen once and respond (puts user message into GUI)."""
    if stop_threads:
        return
    cmd = listen()  # uses the listen function defined below (kept)
    if cmd:
        gui_log(cmd, "You")
        respond(cmd)

def start_listen_thread():
    t = threading.Thread(target=listen_blocking_and_respond, daemon=True)
    t.start()

# Keep your listen but with safer behavior
def listen():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("🎙️ Listening da...")
            # quick noise reduction calibration
            try:
                r.adjust_for_ambient_noise(source, duration=0.5)
            except Exception:
                pass
            try:
                audio = r.listen(source, timeout=10, phrase_time_limit=15)
                query = r.recognize_google(audio)
                print(f"You said: {query}")
                return query.lower()
            except sr.WaitTimeoutError:
                speak("You didn’t say anything da.")
            except sr.UnknownValueError:
                speak("I couldn't understand, say it again.")
            except sr.RequestError:
                speak("There’s a problem with the speech service.")
    except OSError:
        speak("Microphone not available da.")
    return ""

# -------------------------
# MUSIC functions (kept + made safe)
# -------------------------
def load_songs():
    global songs
    songs = []
    try:
        if os.path.exists(music_dir):
            songs = [os.path.join(music_dir, f) for f in os.listdir(music_dir) if f.lower().endswith(('.mp3', '.wav'))]
    except Exception as e:
        print("[load_songs]", e)
    if songs:
        speak(f"[Music] Loaded {len(songs)} songs.")
    else:
        speak("No songs found in your music folder bro.")

def play_song(index):
    global current_song_index
    if songs:
        index = index % len(songs)
        try:
            pygame.mixer.music.load(songs[index])
            pygame.mixer.music.play()
            speak(f"Playing: {os.path.basename(songs[index])}")
            current_song_index = index
        except Exception as e:
            print("[play_song]", e)
            speak("Couldn't play the song da.")
    else:
        speak("No songs to play bro.")

def next_song():
    global current_song_index
    if songs:
        current_song_index = (current_song_index + 1) % len(songs)
        play_song(current_song_index)
    else:
        speak("No songs loaded bro.")

def previous_song():
    global current_song_index
    if songs:
        current_song_index = (current_song_index - 1) % len(songs)
        play_song(current_song_index)
    else:
        speak("No songs loaded bro.")

# -------------------------
# RESPOND FUNCTION (your logic)
# -------------------------
def respond(query):
    global current_song_index
    q = query.lower()

    if "time" in q:
        time_now = datetime.datetime.now().strftime("%H:%M")
        speak(f"Time is {time_now} bro")

    elif "youtube" in q:
        speak("Opening YouTube da")
        webbrowser.open("https://www.youtube.com")

    elif "google" in q:
        speak("Opening Google for you")
        webbrowser.open("https://www.google.com")

    elif "whatsapp" in q:
        speak("Opening WhatsApp web")
        webbrowser.open("https://web.whatsapp.com")

    elif "gmail" in q:
        speak("Opening Gmail")
        webbrowser.open("https://mail.google.com")

    elif "instagram" in q:
        speak("Opening Instagram")
        webbrowser.open("https://instagram.com")

    elif "play music" in q or ("music" in q and "play" in q):
        if songs:
            # start playing in a thread so GUI doesn't hang
            threading.Thread(target=play_song, args=(current_song_index,), daemon=True).start()
        else:
            speak("No songs loaded bro.")

    elif "next song" in q:
        next_song()

    elif "previous song" in q:
        previous_song()

    elif "pause music" in q:
        try:
            pygame.mixer.music.pause()
            speak("Music paused bro.")
        except Exception:
            speak("Couldn't pause music da.")

    elif "resume music" in q:
        try:
            pygame.mixer.music.unpause()
            speak("Music resumed.")
        except Exception:
            speak("Couldn't resume da.")

    elif "volume up" in q:
        try:
            current_volume = pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(min(1.0, current_volume + 0.1))
            speak("Volume increased.")
        except Exception:
            speak("Volume control failed da.")

    elif "volume down" in q:
        try:
            current_volume = pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(max(0.0, current_volume - 0.1))
            speak("Volume decreased.")
        except Exception:
            speak("Volume control failed da.")

    elif "joke" in q:
        joke = random.choice(jokes)
        speak(joke)

    elif "roast" in q:
        roast = random.choice(roasts)
        speak(roast)

    elif "tamil" in q:
        speak("Tamil mode activated.")
        speak_tamil("வணக்கம் மோநிஷ். நான் புரோபாட். என்ன வேணும் சொல்லு.")

    elif "add to-do" in q or "add todo" in q:
        task = q.replace("add to-do", "").replace("add todo", "").strip()
        with open("todo.txt", "a", encoding="utf-8") as f:
            f.write(f"- {task}\n")
        speak("Task added to your to-do list.")

    elif "read my to-do" in q or "read tasks" in q:
        try:
            with open("todo.txt", "r", encoding="utf-8") as f:
                tasks = f.read()
            if tasks.strip():
                speak("Here are your tasks:")
                speak(tasks)
            else:
                speak("Your to-do list is empty bro.")
        except FileNotFoundError:
            speak("You don't have a to-do list yet.")

    elif "clear my to-do" in q or "clear tasks" in q:
        open("todo.txt", "w", encoding="utf-8").close()
        speak("All your tasks are cleared da.")

    elif "remind me in" in q or "set a timer for" in q:
        minutes = 1
        match = re.search(r'\d+', q)
        if match:
            minutes = int(match.group())
        speak(f"Okay bro, reminding you in {minutes} minute{'s' if minutes > 1 else ''}.")
        # run timer in background
        def timer_thread(mins, text="Reminder"):
            if stop_threads:
                return
            time.sleep(mins * 60)
            speak("Time's up! This is your reminder.")
        threading.Thread(target=timer_thread, args=(minutes,), daemon=True).start()

    elif "stop" in q or "exit" in q or "bye" in q:
        speak("Okay bro, going offline. Call me if needed.")
        # ask GUI to stop
        gui_log("exit_now", "SYSTEM")
    else:
        speak("I don't know that command yet bro. Update me soon.")

# -------------------------
# GUI: Fancy assistant window
# -------------------------
class BroBotGUI:
    def __init__(self, root):
        self.root = root
        root.title("BroBot Assistant")
        root.geometry("520x600")
        root.resizable(False, False)
        # top-level style
        self.setup_styles()
        # animated canvas background
        self.canvas = tk.Canvas(root, width=520, height=600, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        # frame on top of canvas
        self.frame = tk.Frame(self.canvas, bg="#0b1020")
        self.frame.place(relwidth=0.95, relheight=0.95, relx=0.025, rely=0.025)
        # chat area
        self.chat = scrolledtext.ScrolledText(self.frame, wrap=tk.WORD, state='disabled', bg="#071022", fg="#E6F0FF", font=("Helvetica", 11), padx=10, pady=10)
        self.chat.place(relx=0.03, rely=0.03, relwidth=0.94, relheight=0.66)
        # input box for typing
        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(self.frame, textvariable=self.entry_var, font=("Helvetica", 11))
        self.entry.place(relx=0.03, rely=0.71, relwidth=0.66, relheight=0.06)
        # send button (type)
        self.btn_type = tk.Button(self.frame, text="⌨ Type", command=self.on_type, font=("Helvetica", 11, "bold"), bd=0)
        self.btn_type.place(relx=0.71, rely=0.71, relwidth=0.12, relheight=0.06)
        # speak button
        self.btn_speak = tk.Button(self.frame, text="🎤 Speak", command=self.on_speak, font=("Helvetica", 11, "bold"), bd=0)
        self.btn_speak.place(relx=0.84, rely=0.71, relwidth=0.13, relheight=0.06)
        # status label
        self.status = tk.Label(self.frame, text="Ready", bg="#071022", fg="#9FB5FF", font=("Helvetica", 10))
        self.status.place(relx=0.03, rely=0.79, relwidth=0.94, relheight=0.05)
        # small control buttons at bottom
        self.btn_exit = tk.Button(self.frame, text="❌ Exit", command=self.on_exit, bd=0, font=("Helvetica", 10, "bold"))
        self.btn_exit.place(relx=0.03, rely=0.86, relwidth=0.94, relheight=0.08)
        # animation params
        self.color_phase = 0
        self.animate_background()
        # glow effect
        self.glow_on = True
        self.glow_cycle()
        # start queue processor
        self.root.after(200, self.process_queue)
        # start up: init pygame + load songs + greet
        try:
            pygame.init()
            pygame.mixer.init()
        except Exception as e:
            print("[pygame init]", e)
        load_songs()
        # greet in thread so GUI remains responsive
        threading.Thread(target=wish_me, daemon=True).start()

    def setup_styles(self):
        # set ttk theme for entry
        style = ttk.Style()
        style.theme_use('clam')

    def animate_background(self):
        # smooth gradient-ish animation by changing hex colors
        phase = (time.time() % 10) / 10.0  # 0..1 every 10s
        # compute two colors blending
        def mix(a, b, t):
            return int(a + (b - a) * t)
        # base colours (two palettes)
        c1 = (7, 16, 34)
        c2 = (2, 62, 138)
        c3 = (10, 20, 60)
        t = (0.5 + 0.5 * (math_sin := lambda x: __import__('math').sin(x))(time.time() * 0.6))  # 0..1
        r = mix(c1[0], c2[0], t)
        g = mix(c1[1], c2[1], t)
        b = mix(c1[2], c2[2], t)
        color = f'#{r:02x}{g:02x}{b:02x}'
        self.canvas.configure(bg=color)
        self.frame.configure(bg=color)
        # schedule next frame
        self.root.after(80, self.animate_background)

    def glow_cycle(self):
        # simple glowing effect for buttons (change bg)
        if self.glow_on:
            self.btn_speak.configure(bg="#1B6EFF", fg="white")
            self.btn_type.configure(bg="#1BFF9E", fg="black")
            self.btn_exit.configure(bg="#FF4D6D", fg="white")
        else:
            self.btn_speak.configure(bg="#0f2a57", fg="#9FB5FF")
            self.btn_type.configure(bg="#0f2a57", fg="#9FB5FF")
            self.btn_exit.configure(bg="#0f2a57", fg="#FFB6C1")
        self.glow_on = not self.glow_on
        self.root.after(700, self.glow_cycle)

    def append_chat(self, sender, message):
        self.chat.configure(state='normal')
        if sender == "You":
            self.chat.insert(tk.END, f"You: {message}\n", "you")
        elif sender == "BroBot":
            self.chat.insert(tk.END, f"BroBot: {message}\n", "bot")
        elif sender == "BroBot (TA)":
            self.chat.insert(tk.END, f"BroBot (TA): {message}\n", "bot_ta")
        elif sender == "SYSTEM":
            self.chat.insert(tk.END, f"{message}\n", "sys")
        else:
            self.chat.insert(tk.END, f"{sender}: {message}\n")
        self.chat.see(tk.END)
        self.chat.configure(state='disabled')

    def process_queue(self):
        # read from msg_queue and append to chat
        try:
            while True:
                sender, text = msg_queue.get_nowait()
                # special case: exit
                if sender == "SYSTEM" and text == "exit_now":
                    self.on_exit()
                    return
                self.append_chat(sender, text)
        except queue.Empty:
            pass
        # schedule again
        self.root.after(150, self.process_queue)

    def on_speak(self):
        self.status.configure(text="Listening... 🎙️")
        start_listen_thread()
        # reset status after a delay (will update more accurately by responses)
        self.root.after(12000, lambda: self.status.configure(text="Ready"))

    def on_type(self):
        user_text = self.entry_var.get().strip()
        if not user_text:
            self.status.configure(text="Type something in the box then press Type")
            return
        # clear entry
        self.entry_var.set("")
        gui_log(user_text, "You")
        # respond in a background thread
        threading.Thread(target=respond, args=(user_text,), daemon=True).start()

    def on_exit(self):
        global stop_threads
        stop_threads = True
        speak("Shutting down BroBot GUI. Bye da!")
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.root.destroy()

# -------------------------
# Utility: process msg_queue into GUI (used inside class)
# -------------------------
# (class handles it)

# -------------------------
# Run App
# -------------------------
if __name__ == "__main__":
    # Prepare pygame silently
    try:
        pygame.init()
    except Exception:
        pass

    # Create main window
    root = tk.Tk()
    app = BroBotGUI(root)
    # key binding: Enter to type
    root.bind('<Return>', lambda e: app.on_type())
    root.mainloop()
