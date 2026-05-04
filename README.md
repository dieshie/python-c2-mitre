# Custom C2 with 11 MITRE ATT&CK Techniques
>Disclaimer: This project was created for educational and defensive purposes only. It demonstrates how C2 frameworks operate to help Blue Teams and SOC analysts build better detections. This code is not intended for unlawful use against any system without explicit authorization. The techniques are outdated and no longer effective on modern, fully updated systems.

## What is this

A custom remote administration tool written on top of plain TCP sockets. Both client and server are in Python. Data is chunked into 1024-byte pieces for reliable transfer of files, screenshots, audio, and video.

## Architecture

- **Server** – console menu, accepts a connection and sends selected commands.
- **Client** – executes commands via `subprocess`, `pyperclip`, `PIL`, `OpenCV` and returns the result.
- **Data transfer** – implemented through `send_chunks()` / `receive_chunks()`. Each chunk is 1024 bytes, with a size header prepended for larger payloads.

## Implemented MITRE Techniques

11 options available in the server menu:

| # | Technique | MITRE ID | What it does |
|---|-----------|----------|-------------|
| 1 | System Information Discovery | T1082 | Runs `systeminfo` |
| 2 | Command-Line Interface | T1059 | Remote cmd shell |
| 3 | File and Directory Discovery | T1083 | Searches files by name |
| 4 | Remote File Copy | T1105 | Downloads files to server |
| 5 | File Deletion | T1107 | Deletes files from client |
| 6 | Process Discovery | T1057 | Remote `tasklist` |
| 7 | Input Capture | T1056 | Keylogger via `keyboard.Listener` |
| 8 | Clipboard Data | T1115 | Reads clipboard |
| 9 | Screen Capture | T1113 | Screenshot with `PIL.ImageGrab` |
| 10 | Audio Capture | T1123 | Microphone recording |
| 11 | Video Capture | T1125 | Webcam capture with `OpenCV` |

## How it works

Server binds and listens:

    s.bind(('0.0.0.0', 4444))
    s.listen(1)

Client connects and waits. Server displays menu, operator picks a technique by number. The result is sent back.

Example of T1082 – system info:

<img width="483" height="646" alt="1" src="https://github.com/user-attachments/assets/13875fd6-19c8-4382-8e7f-f535ae1290a4" />

T1059 – remote command line:

<img width="507" height="343" alt="1" src="https://github.com/user-attachments/assets/219efd81-bd08-49f7-883c-9f0a2340c6a9" />

T1056 – live keylogger output:

<img width="1009" height="183" alt="image" src="https://github.com/user-attachments/assets/b669a88a-4e53-4599-a0da-0569e749bf47" />

T1113 – screenshot from victim:

<img width="1009" height="547" alt="image" src="https://github.com/user-attachments/assets/3f929229-320d-42ef-8679-5360a7ec9052" />

T1125 – video capture (camera was covered):

<img width="1009" height="447" alt="image" src="https://github.com/user-attachments/assets/f9b6863a-eff0-43b1-b0c4-1d6e1167c942" />

## Anti-VM

From the previous lab (dynamic analysis), added a hypervisor check via `cpuid` – bit 31 in ECX. If a VM is detected, the client exits silently. Basic sandbox evasion.

## Possible improvements

- Replace TCP with HTTPS (WebSockets + Flask) to blend in
- Add traffic encryption (XOR or RC4 minimum)
- Implement persistence module
- Build a web UI instead of console menu
- Support multiple simultaneous clients

## Files

- `client/client.py` – client-side payload
- `server/server.py` – server menu and handlers
