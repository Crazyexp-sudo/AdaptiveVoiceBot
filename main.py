import os
import json
import threading
import subprocess
import queue
import speech_recognition as sr
import pyttsx3
import ollama
import customtkinter as ctk

# Import your custom scanner module from app_scanner.py
from app_scanner import scan_windows_apps

# Configure graphical interface presentation layers
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AdaptiveAIBot(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. Main Window Setup
        self.title("Adaptive Windows AI Assistant")
        self.geometry("500x480")
        self.resizable(False, False)
        
        # 2. System Controls & Application Cache Storage
        self.wake_word = "hey computer"
        self.is_running = False
        self.INSTALLED_APPS = {}
        
        # 3. Thread-Safe Audio Communication Queue
        self.speech_queue = queue.Queue()
        
        # 4. Dedicated Offline Audio Processing Engines
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)  # Sets text-to-speech reading pace
        self.recognizer = sr.Recognizer()
        
        # 5. Build Voice Name-to-ID Memory Map
        
        # 6. Generate Graphical UI Layout
        self.create_widgets()
        
        # 7. Start the background infinite loop checker for speech messages
        self.check_speech_queue()
        
        # 8. Execute On-Boot Scan Sequence (Calculates system map once)
        self.refresh_system_cache()

    def create_widgets(self):
        """Builds all graphical elements within the application canvas."""
        # Dynamic Operational Status Indicator
        self.status_label = ctk.CTkLabel(self, text="Status: Sleeping", font=("Arial", 16, "bold"), text_color="gray")
        self.status_label.pack(pady=15)
        
        # User Configuration Interface for Custom Wake Word
        self.wake_label = ctk.CTkLabel(self, text="Custom Wake Word:", font=("Arial", 12))
        self.wake_label.pack(pady=2)
        self.wake_entry = ctk.CTkEntry(self, width=250)
        self.wake_entry.insert(0, self.wake_word)
        self.wake_entry.pack(pady=5)
        
        
        # Visual Command Terminal / Debug Logger
        self.console_box = ctk.CTkTextbox(self, width=440, height=130, font=("Consolas", 11))
        self.console_box.pack(pady=15)
        
        # Operational Interactive Control Triggers
        self.start_btn = ctk.CTkButton(self, text="Start Listening", command=self.toggle_system, fg_color="green", hover_color="darkgreen")
        self.start_btn.pack(side="left", padx=40, pady=10)
        
        self.refresh_btn = ctk.CTkButton(self, text="Refresh System Apps", command=self.refresh_system_cache)
        self.refresh_btn.pack(side="right", padx=40, pady=10)

    def log_msg(self, text):
        """Safely outputs diagnostic updates directly onto the UI console box."""
        self.console_box.insert("end", f"{text}\n")
        self.console_box.see("end")

    def speak(self, text):
        """Visually prints text immediately, and drops audio into the queue."""
        self.log_msg(f"[Bot]: {text}")
        self.speech_queue.put(text)

    def check_speech_queue(self):
        """Runs on the main GUI thread. Checks the queue and speaks texts sequentially."""
        try:
            while not self.speech_queue.empty():
                text_to_say = self.speech_queue.get_nowait()
                self.engine.say(text_to_say)
                self.engine.runAndWait()
        except queue.Empty:
            pass
        finally:
            # Check back every 100 milliseconds without locking UI responsiveness
            self.after(100, self.check_speech_queue)

    def change_voice_accent(self, selected_voice_name):
        """Triggered automatically when a dropdown menu option is clicked."""
        try:
            target_voice_id = self.voice_map[selected_voice_name]
            self.engine.setProperty('voice', target_voice_id)
            self.speak(f"Voice updated to {selected_voice_name}")
        except Exception as e:
            self.log_msg(f"Failed to change voice accent: {e}")

    def refresh_system_cache(self):
        """Invokes the external scanner logic to remap Start Menu directory keys into active RAM."""
        self.log_msg("[System]: Initiating application directory scan...")
        self.INSTALLED_APPS = scan_windows_apps()
        self.log_msg(f"[System]: Memory sync complete. {len(self.INSTALLED_APPS)} paths indexed successfully.")

    def toggle_system(self):
        """Spins up or securely terminates the decoupled background listener thread."""
        if not self.is_running:
            self.wake_word = self.wake_entry.get().lower().strip()
            self.is_running = True
            self.start_btn.configure(text="Stop System", fg_color="red", hover_color="darkred")
            self.status_label.configure(text=f"Listening for: '{self.wake_word}'", text_color="green")
            
            # Spin off microphone tasks to keep GUI smooth and prevent app freezing
            threading.Thread(target=self.background_audio_loop, daemon=True).start()
        else:
            self.is_running = False
            self.start_btn.configure(text="Start Listening", fg_color="green", hover_color="darkgreen")
            self.status_label.configure(text="Status: Sleeping", text_color="gray")

    def background_audio_loop(self):
        """Monitors local environment audio streams entirely offline."""
        with sr.Microphone() as source:
            while self.is_running:
                try:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=4)
                    phrase = self.recognizer.recognize_google(audio).lower()
                    
                    if self.wake_word in phrase:
                        self.status_label.configure(text="Processing Command...", text_color="orange")
                        
                        # Isolate raw intent instruction payload by trimming the custom wake activation token
                        command = phrase.replace(self.wake_word, "").strip()
                        self.log_msg(f"[Detected]: {phrase}")
                        
                        if command:
                            self.process_with_qwen(command)
                        else:
                            self.speak("I am listening. What should I do?")
                        
                        self.status_label.configure(text=f"Listening for: '{self.wake_word}'", text_color="green")
                except:
                    continue

    def process_with_qwen(self, command):
        preinstalled_list = ["calculator", "camera", "settings", "weather", "photos", "paint", "notepad", "calendar", "mail", "store", "xbox", "clock", "maps"]
        scanned_list = list(self.INSTALLED_APPS.keys())[:80]
        combined_apps = ", ".join(preinstalled_list + scanned_list)
        
        

        system_prompt = (
            "You are a Windows automation router. Categorize the user's voice request.\n"
            f"AVAILABLE APPS SYSTEM CAN CONTROL: [{combined_apps}]\n\n"
            "Format Rules:\n"
            "1. If they want to LAUNCH/OPEN an app: {'intent': 'open_app', 'target_app': 'exact_name'}\n"
            "2. If they want to STOP/CLOSE/KILL an app: {'intent': 'close_app', 'target_app': 'exact_name'}\n"
            "3. If it's a general question or error: {'intent': 'chat', 'reply': 'conversational response or error message'}\n\n"
            "Reply ONLY with a raw JSON object string. Do not use markdown quotes or backticks."
        )
        
        try:
            response = ollama.generate(
                model='qwen2.5:1.5b',
                system=system_prompt,
                prompt=command,
                options={"temperature": 0.0, "num_gpu": 99}
            )
            self.execute_action(response['response'].strip())
        except Exception as e:
            self.log_msg(f"Ollama Interface Error: {e}")

            self.log_msg(f"Ollama Interface Error: {e}")

    def execute_action(self, json_str):
        """Interacts directly with native Windows OS sub-processes to toggle system states."""
        # URI Map for built-in/preinstalled Windows 10 & 11 Apps
        PREINSTALLED_URI_MAP = {
            "calculator": "ms-calculator:",
            "camera": "microsoft.windows.camera:",
            "settings": "ms-settings:",
            "weather": "bingweather:",
            "photos": "ms-photos:",
            "paint": "ms-paint:",
            "notepad": "notepad.exe",
            "calendar": "outlookcalendar:",
            "mail": "outlookmail:",
            "store": "ms-windows-store:",
            "microsoft store": "ms-windows-store:",
            "xbox": "xbox:",
            "clock": "ms-clock:",
            "maps": "bingmaps:"
        }



        # Background process execution signatures for closing preinstalled apps
        PREINSTALLED_PROCESS_MAP = {
            "calculator": "CalculatorApp.exe",
            "camera": "WindowsCamera.exe",
            "settings": "SystemSettings.exe",
            "weather": "Microsoft.Meteo.exe",
            "photos": "Microsoft.Photos.exe",
            "paint": "mspaint.exe",
            "notepad": "notepad.exe",
            "store": "WinStore.App.exe",
            "microsoft store": "WinStore.App.exe",
            "xbox": "XboxPcApp.exe",
            "clock": "Time.exe",
            "maps": "Maps.exe"
        }

        try:
            data = json.loads(json_str)
            intent = data.get("intent")
            target = data.get("target_app", "").lower().strip()
            
            if not target:
                self.speak(data.get("reply", "I am listening."))
                return

            # ==========================================
            # ROUTE 1: LAUNCHING / OPENING APPLICATIONS
            # ==========================================
            if intent == "open_app":
                # Check if it's a preinstalled Windows App URI
                if target in PREINSTALLED_URI_MAP:
                    self.speak(f"Opening {target}")
                    os.system(f"start {PREINSTALLED_URI_MAP[target]}")
                # Check if it's a scanned third-party desktop app
                elif target in self.INSTALLED_APPS:
                    self.speak(f"Launching {target}")
                    os.startfile(self.INSTALLED_APPS[target])
                else:
                    # Fallback: Attempt a direct shell start command
                    self.speak(f"Attempting to launch {target}")
                    os.system(f"start {target}")

            # ==========================================
            # ROUTE 2: CLOSING / TERMINATING APPLICATIONS
            # ==========================================
            elif intent == "close_app":
                # Special Handle Case: File Explorer
                if target in ["file explorer", "explorer"]:
                    self.speak("Closing the active File Explorer window.")
                    ps_script = (
                        "$shell = New-Object -ComObject Shell.Application; "
                        "foreach ($window in $shell.Windows()) { "
                        "  if ($window.Name -eq 'File Explorer' -or $window.Name -eq 'Windows Explorer') { "
                        "    $window.Quit(); break; "
                        "  } "
                        "}"
                    )
                    subprocess.Popen(["powershell", "-Command", ps_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Check if it's a preinstalled app process name mapping
                else:
                    process_name = PREINSTALLED_PROCESS_MAP.get(target, f"{target}.exe")
                    self.speak(f"Closing {target}.")
                    subprocess.Popen(
                        f"taskkill /f /im {process_name}", 
                        shell=True, 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL
                    )
                    
            # ==========================================
            # ROUTE 3: CONVERSATIONAL RESPONSE
            # ==========================================
            else:
                self.speak(data.get("reply", "Command not recognized."))
                
        except Exception as e:
            self.log_msg(f"System Action Error: {e}")

if __name__ == "__main__":
    app = AdaptiveAIBot()
    app.mainloop()
