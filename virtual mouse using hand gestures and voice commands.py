import cv2
from cvzone.HandTrackingModule import HandDetector
import pyautogui
import time
import pyttsx3
import speech_recognition as sr
import pywhatkit
import datetime
import webbrowser
import threading
import psutil
import wikipedia
import pyjokes
import numpy as np
import mouse
from screeninfo import get_monitors


frameR = 100
cam_w, cam_h = 640, 480
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

cap.set(3, cam_w)
cap.set(4, cam_h)
detector = HandDetector(detectionCon=0.9, maxHands=1)


monitor = get_monitors()[0]  # Assuming we have one monitor
screen_width, screen_height = monitor.width, monitor.height
print(f"Screen resolution: {screen_width}x{screen_height}")


listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.8)

def talk(text):
    """Make the assistant speak."""
    engine.say(text)
    engine.runAndWait()

def take_command():
    """Listen for voice commands."""
    command = ""
    try:
        with sr.Microphone() as source:
            print('Listening...')
            listener.adjust_for_ambient_noise(source, duration=1)
            voice = listener.listen(source, timeout=10)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'nova' in command:
                command = command.replace('nova', '')
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
    except sr.RequestError:
        print("Sorry, there was an issue with the speech recognition service.")
    except sr.WaitTimeoutError:
        print("Listening timed out. Please try again.")
    return command

def close_browser_tabs():
    """Function to close Google or YouTube tabs."""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'chrome' in proc.info['name'].lower() or 'firefox' in proc.info['name'].lower():
                if 'google' in proc.info['name'].lower() or 'youtube' in proc.info['name'].lower():
                    print(f"Terminating process {proc.info['name']} with PID {proc.info['pid']}")
                    proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def run_nova():
    """Main function to process and continuously listen for commands."""
    while True:
        command = take_command()
        print(command)

        if 'Bye' in command or 'stop' in command:
            talk("Goodbye! Have a great day.")
            break

        if 'what is your name' in command or 'who are you' in command:
            talk("My name is Nova.")
        elif 'how are you' in command:
            talk("I'm doing well, thank you for asking! How are you?")
        elif 'play' in command:
            song = command.replace('play', '').strip()
            talk('Playing ' + song)
            pywhatkit.playonyt(song)
        elif 'time' in command:
            current_time = datetime.datetime.now().strftime('%I:%M %p')
            talk('Current time is ' + current_time)
        elif 'date' in command:
            current_date = datetime.datetime.now().strftime('%Y-%m-%d')
            talk(f"Today's date is {current_date}")
        elif 'search on youtube' in command:
            query = command.replace('search on youtube', '').strip()
            talk(f"Searching YouTube for {query}...")
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        elif 'open youtube' in command:
            talk('Opening YouTube...')
            webbrowser.open('https://www.youtube.com')
        elif 'open google' in command:
            talk('Opening Google...')
            webbrowser.open('https://www.google.com')
        elif 'search on google' in command:
            query = command.replace('search on google', '').strip()
            talk(f"Searching Google for {query}...")
            webbrowser.open(f"https://www.google.com/search?q={query}")
        elif 'close google' in command:
            talk('Closing Google...')
            close_browser_tabs()
        elif 'close youtube' in command:
            talk('Closing YouTube...')
            close_browser_tabs()
        elif 'who' in command or 'what' in command or 'where' in command or 'why' in command or 'how' in command:
            query = command
            talk(f"Searching Wikipedia for {query}...")
            try:
                wikipedia.set_lang("en")
                info = wikipedia.summary(query, sentences=1)
                print(info)
                talk(info)
                webbrowser.open(f"https://en.wikipedia.org/wiki/{query.replace(' ', '_')}")
            except wikipedia.exceptions.DisambiguationError as e:
                talk("There are multiple results. Could you be more specific?")
            except wikipedia.exceptions.HTTPTimeoutError:
                talk("Sorry, I couldn't fetch the information. Please try again later.")
            except wikipedia.exceptions.PageError:
                talk("Sorry, I couldn't find any information on that topic.")
        elif 'joke' in command:
            talk(pyjokes.get_joke())
        elif 'date and time' in command or 'date & time' in command:
            current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p')
            talk(f"The current date and time is {current_datetime}")
        else:
            talk("I'm not sure how to respond to that.")


talk("Hello ma'am, I am your voice assistant, Nova. How can I help you today?")


def hand_tracking():
    """Perform hand gesture operations."""
    last_left_click = 0
    last_right_click = 0
    last_double_click = 0
    delay_time = 1
    double_delay_time = 2
    is_clicking = False
    last_vol_dist = None
    volume_threshold = 50

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to grab frame")
            break
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)
        cv2.rectangle(img, (frameR, frameR), (cam_w - frameR, cam_h - frameR), (255, 0, 255), 2)

        if hands:
            lmlist = hands[0]['lmList']
            if len(lmlist) > 12:
                ind_x, ind_y = lmlist[8][0], lmlist[8][1]
                mid_x, mid_y = lmlist[12][0], lmlist[12][1]
                thumb_x, thumb_y = lmlist[4][0], lmlist[4][1]
                pinky_x, pinky_y = lmlist[20][0], lmlist[20][1]

                dist = np.linalg.norm(np.array([ind_x, ind_y]) - np.array([mid_x, mid_y]))
                fingers = detector.fingersUp(hands[0])

                if fingers == [0, 1, 1, 1, 0]:
                    pyautogui.press("volumeup")
                    print("Volume Up")
                    last_vol_dist = time.time()

                thumb_index_dist = np.linalg.norm(np.array([thumb_x, thumb_y]) - np.array([ind_x, ind_y]))

                if fingers == [0, 0, 1, 1, 1] and thumb_index_dist < 30:
                    pyautogui.press("volumedown")
                    print("Volume Down")
                    last_vol_dist = time.time()

                if not is_clicking:
                    if fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 1:

                        conv_x = int(np.interp(ind_x, (frameR, cam_w - frameR), (0, screen_width)))
                        conv_y = int(np.interp(ind_y, (frameR, cam_h - frameR), (0, screen_height)))
                        mouse.move(conv_x, conv_y)

                    if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 1:
                        if abs(ind_x - mid_x) < 25 and fingers[4] == 0 and time.time() - last_left_click > delay_time:
                            mouse.click(button="left")
                            last_left_click = time.time()
                            is_clicking = True
                            time.sleep(0.5)
                            is_clicking = False

                    if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 1:
                        if abs(ind_x - mid_x) < 25 and fingers[4] == 1 and time.time() - last_right_click > delay_time:
                            mouse.click(button="right")
                            last_right_click = time.time()
                            is_clicking = True
                            time.sleep(0.5)
                            is_clicking = False


                if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[4] == 0:
                    if abs(ind_x - mid_x) < 25:
                        mouse.wheel(delta=-1)
                        print("Scrolling Down")


                if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[4] == 1:
                    if abs(ind_x - mid_x) < 25:
                        mouse.wheel(delta=1)
                        print("Scrolling Up")

        cv2.imshow("Hand Gesture Control", img)
        cv2.waitKey(1)

if __name__ == "__main__":
    threading.Thread(target=run_nova, daemon=True).start()
    hand_tracking()
