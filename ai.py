import os
import datetime
import pywhatkit
import google.generativeai as genai
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import wmi
import subprocess

# Set the API key directly in the script (only for testing)
os.environ["GEMINI_API_KEY"] = "YOUR API!!!"

# Ensure the API key is stored securely in an environment variable
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API key not found in environment variables")

genai.configure(api_key=api_key)

# Define generation configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create and configure the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",  # Correct model name
    generation_config=generation_config
)

# Start a new chat session
chat_session = model.start_chat()

# Send the SYS message to configure the chat
SYS = """You are an AI assistant.YOu can do the following things and Follow these rules:
1. For commands like 'play X', respond with: CMD_PLAY:{song_name}
2. For time queries: CMD_TIME
3. For DATE or day  queries: CMD_DATE
4. For general knowledge: Respond naturally 
5. Also resond what action is now doing along with the command as the first word
(like CMD_PLAY, CMD_TIME as 1st word)
6. For system controls (volume, brightness): CMD_SYSTEM:{action}:{value}
7. Keep responses concise and action-oriented
8. For weather: CMD_WEATHER:{location} 
9. For opening applications: CMD_OPEN:{app_name}"""
chat_session.send_message(SYS)

class CommandExecutor:
   
    def execute_command(self, cmd):
        print("DATA::",cmd,":END")
        if cmd.startswith("CMD_PLAY:"):
            song = cmd.split(":")[1]
            pywhatkit.playonyt(song)
            
        elif cmd.startswith("CMD_DATE"):
            date = datetime.date.today()
            day = date.strftime("%A")
            print(f"Date is {date} and ToDay is {day}")
        elif cmd.startswith("CMD_TIME"):
            time = datetime.datetime.now().strftime("%H:%M")
            print(f"Current time is {time}")

        elif cmd.startswith("CMD_SYSTEM:"):
             action, value = cmd.split(":")[1:]
             if action == "volume":
                value = int(value)
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(value / 100, None)
                print(f"Volume set to {value}")
             elif action == "brightness":
                 wmi.WMI(namespace='wmi').WmiMonitorBrightnessMethods()[0].WmiSetBrightness(value, int(value))
                 print(f"Brightness set to {value}%")
             else:
               print(f"Unknown system control action: {action}")
        elif cmd.startswith("CMD_WEATHER:"):
            location = cmd.split(":")[1]
            pywhatkit.search(f"weather in {location}")
executor = CommandExecutor()

# Loop to continue the conversation
while True:
    # Get user input
    ask = input("You: ")

    # Send a message to the chat model
    response = chat_session.send_message(ask)

    # Print the generated response
    print(response.text)

    # Check if the response contains a command
    if response.text.startswith("CMD_"):
        executor.execute_command(response.text)

    # Check if the user wants to end the conversation
    if ask.lower() in ['exit', 'quit', 'bye']:
        print("Ending the conversation.")
        break
