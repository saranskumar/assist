import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import os
import google.generativeai as genai

SYSTEM_PROMPT = """You are an AI assistant. Follow these rules:
1. For commands like 'play X', respond with: CMD_PLAY:{song_name}
2. For time queries,respond with: CMD_TIME:{current_time}
3. For weather: CMD_WEATHER:{location}
4. For general knowledge: Respond naturally
5. For system controls (volume, brightness): CMD_SYSTEM:{action}:{value}
6. Keep responses concise and action-oriented"""

os.environ["GEMINI_API_KEY"] = " "
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-pro", generation_config={
    "temperature": 0.9,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
})

class Assistant:
    def __init__(self):
        self.listener = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.chat = model.start_chat(history=[])
        self.chat.send_message(SYSTEM_PROMPT)

    def speak(self, text):
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = self.listener.listen(source)
                command = self.listener.recognize_google(audio).lower()
                print(f"User: {command}")
                return command
        except Exception as e:
            print(f"Error: {e}")
            return ""

    def execute_command(self, cmd):
        try:
            if cmd.startswith("CMD_PLAY:"):
                song = cmd.split(":")[1]
                self.speak(f"Playing {song} on YouTube.")
                pywhatkit.playonyt(song)
            
            elif  cmd.startswith("CMD_TIME:"):
                current_time = datetime.datetime.now().strftime('%I:%M %p')
                self.speak(f"The current time is {current_time}.")
            
            elif cmd.startswith("CMD_SYSTEM:"):
                action, value = cmd.split(":")[1:]
                import ctypes
                
                if action == "volume":
                    value = int(value)
                    if os.name == "nt":  # Windows
                        ctypes.windll.user32.SendMessageW(0xFFFF, 0x319, 0, (value * 0xFFFF // 100))
                    else:  # Linux or Mac
                        os.system(f"amixer -D pulse sset Master {value}%")
                
                elif action == "brightness":
                    import screen_brightness_control as sbc
                    value = int(value)
                    self.speak(f"Setting brightness to {value}%.")
                    sbc.set_brightness(value)
                
                else:
                    self.speak(f"Unknown system action: {action}.")
            else:
                self.speak("Command not recognized.")
        except Exception as e:
            self.speak(f"An error occurred while executing the command: {e}")

    def run(self):
        self.speak("Hello! How can I help?")
        while True:
            command = self.listen()
            if not command:
                continue
                
            if "goodbye" in command:
                self.speak("Goodbye!")
                break

            response = self.chat.send_message(command)
            response_text = response.text
            
            if response_text.startswith("CMD_"):
                self.execute_command(response_text)
            else:
                self.speak(response_text)

if __name__ == "__main__":
    assistant = Assistant()
    assistant.run()
