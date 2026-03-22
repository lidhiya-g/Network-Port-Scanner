# Network-Port-Scanner
# Description
A GUI-based Network Port Scanner developed using Python and CustomTkinter. This application scans common ports on a target IP address or domain and displays open ports along with their associated services in a structured interface.

# Features
1.Graphical user interface built with CustomTkinter
2.Multi-threaded port scanning for improved performance
3.Scans commonly used network ports
4.Displays open ports with corresponding service names
5.Real-time progress tracking and scan speed display
6.Start, Stop, and Clear scan controls

# Technologies Used
Python
Socket Programming
Threading (ThreadPoolExecutor)
CustomTkinter

# Installation and Usage
```git clone https://github.com/lidhiya-g/Network-Port-Scanner.git
```
```cd Network-Port-Scanner
```
```pip install customtkinter
```
```python scanner.py
```

# Project Structure
```Network-Port-Scanner/
```
```├── Network_Port_Scanner_App.py
```
```├── README.md
```

# Ports Covered
The application scans the following commonly used ports:

21 (FTP)
22 (SSH)
23 (Telnet)
25 (SMTP)
53 (DNS)
80 (HTTP)
110 (POP3)
143 (IMAP)
443 (HTTPS)
3306 (MySQL)
3389 (RDP)
8080 (HTTP-Alt)

# How It Works
The scanner uses Python socket connections to attempt communication with each port on the target system. If a connection is successfully established, the port is marked as open. Multi-threading is used to perform scans concurrently, improving speed and efficiency. The interface updates in real time with scan progress and results.

# Disclaimer
This tool is intended for educational and learning purposes only. Unauthorized scanning of networks or systems may be illegal. Use this application only on systems for which you have permission.

