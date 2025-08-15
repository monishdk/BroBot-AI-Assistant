import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import random
import time
import tempfile
from gtts import gTTS
import playsound
import re
import pygame

# -------------------------
# Jokes & Roasts
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
# SPEAK (English)
# -------------------------
def speak(text):
    print("BroBot: " + text)
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if voices:
        voice_index = 1 if len(voices) > 1 else 0
        engine.setProperty('voice', voices[voice_index].id)
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()

# -------------------------
# SPEAK (Tamil)
# -------------------------
def speak_tamil(text):
    try:
        tts = gTTS(text=text, lang='ta')
        temp_audio = "temp_tamil.mp3"
        tts.save(temp_audio)
        playsound.playsound(temp_audio)
        os.remove(temp_audio)
    except Exception:
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
# LISTEN FUNCTION (fixed timeouts + quick noise calibration)
# -------------------------
def listen():
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            print("🎙️ Listening da...")
            # Quick ambient noise calibration to avoid long delays
            r.adjust_for_ambient_noise(source, duration=0.5)
            try:
                # Give more time to start and finish speaking
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
# MUSIC PLAYER SETUP
# -------------------------
music_dir = "F:\\pendrive\\songs"
current_song_index = 0
songs = []

def load_songs():
    global songs
    if os.path.exists(music_dir):
        songs = [os.path.join(music_dir, f) for f in os.listdir(music_dir) if f.lower().endswith(('.mp3', '.wav'))]
    if songs:
        speak(f"[Music] Loaded {len(songs)} songs.")
    else:
        speak("No songs found in your music folder bro.")


def play_song(index):
    global current_song_index
    if songs:
        index = index % len(songs)
        pygame.mixer.music.load(songs[index])
        pygame.mixer.music.play()
        speak(f"Playing: {os.path.basename(songs[index])}")
        current_song_index = index
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
# RESPOND FUNCTION
# -------------------------
def respond(query):
    global current_song_index

    if "time" in query:
        time_now = datetime.datetime.now().strftime("%H:%M")
        speak(f"Time is {time_now} bro")

    elif "youtube" in query:
        speak("Opening YouTube da")
        webbrowser.open("https://www.youtube.com")

    elif "google" in query:
        speak("Opening Google for you")
        webbrowser.open("https://www.google.com")

    elif "whatsapp" in query:
        speak("Opening WhatsApp web")
        webbrowser.open("https://web.whatsapp.com")

    elif "gmail" in query:
        speak("Opening Gmail")
        webbrowser.open("https://mail.google.com")

    elif "instagram" in query:
        speak("Opening Instagram")
        webbrowser.open("https://instagram.com")

    elif "play music" in query or "music" in query:
        if songs:
            play_song(current_song_index)
        else:
            speak("No songs loaded bro.")

    elif "next song" in query:
        next_song()

    elif "previous song" in query:
        previous_song()

    elif "pause music" in query:
        pygame.mixer.music.pause()
        speak("Music paused bro.")

    elif "resume music" in query:
        pygame.mixer.music.unpause()
        speak("Music resumed.")

    elif "volume up" in query:
        current_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(min(1.0, current_volume + 0.1))
        speak("Volume increased.")

    elif "volume down" in query:
        current_volume = pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(max(0.0, current_volume - 0.1))
        speak("Volume decreased.")

    elif "joke" in query:
        joke = random.choice(jokes)
        speak(joke)

    elif "roast" in query:
        roast = random.choice(roasts)
        speak(roast)

    elif "tamil" in query:
        speak("Tamil mode activated.")
        speak_tamil("வணக்கம் மோநிஷ். நான் புரோபாட். என்ன வேணும் சொல்லு.")

    elif "add to-do" in query or "add todo" in query:
        task = query.replace("add to-do", "").replace("add todo", "").strip()
        with open("todo.txt", "a", encoding="utf-8") as f:
            f.write(f"- {task}\n")
        speak("Task added to your to-do list.")

    elif "read my to-do" in query or "read tasks" in query:
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

    elif "clear my to-do" in query or "clear tasks" in query:
        open("todo.txt", "w", encoding="utf-8").close()
        speak("All your tasks are cleared da.")

    elif "remind me in" in query or "set a timer for" in query:
        minutes = 1
        match = re.search(r'\d+', query)
        if match:
            minutes = int(match.group())
        speak(f"Okay bro, reminding you in {minutes} minute{'s' if minutes > 1 else ''}.")
        time.sleep(minutes * 60)
        speak("Time's up! This is your reminder.")

    elif "stop" in query or "exit" in query or "bye" in query:
        speak("Okay bro, going offline. Call me if needed.")
        exit()

    else:
        speak("I don't know that command yet bro. Update me soon.")

# -------------------------
# MAIN
# -------------------------
def main():
    pygame.init()
    pygame.mixer.init()
    load_songs()
    wish_me()

    while True:
        command = listen()
        if command:
            respond(command)

if __name__ == "__main__":
    main()

