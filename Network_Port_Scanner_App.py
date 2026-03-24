import customtkinter as ctk
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk

# -------------------------
# GRADIENT FUNCTION
# -------------------------
def create_gradient(canvas, width, height, color1, color2):
    canvas.delete("all")
    r1, g1, b1 = canvas.winfo_rgb(color1)
    r2, g2, b2 = canvas.winfo_rgb(color2)

    for i in range(height):
        r = int(r1 + (r2 - r1) * i / height) // 256
        g = int(g1 + (g2 - g1) * i / height) // 256
        b = int(b1 + (b2 - b1) * i / height) // 256

        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, width, i, fill=color)

# -------------------------
# THEME
# -------------------------
ctk.set_appearance_mode("light")

PRIMARY = "#2563EB"
CARD = "#FFFFFF"
TEXT = "#1E293B"

# -------------------------
# PORTS
# -------------------------
COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
    53: 'DNS', 80: 'HTTP', 110: 'POP3',
    143: 'IMAP', 443: 'HTTPS', 3306: 'MySQL',
    3389: 'RDP', 8080: 'HTTP-Alt'
}

TARGET_PORTS = list(COMMON_PORTS.keys())

# -------------------------
# APP
# -------------------------
class PortScannerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Network Port Scanner")
        self.geometry("1000x600")

        self.running = False
        self.open_ports = []
        self.scanned = 0
        self.start_time = None

        self.build_ui()

    # -------------------------
    # UI
    # -------------------------
    def build_ui(self):
        from customtkinter import CTkFont
        btn_font = CTkFont(family="Segoe UI", size=14, weight="bold")

        # Gradient Background
        self.bg_canvas = tk.Canvas(self, highlightthickness=0)
        self.bg_canvas.place(relwidth=1, relheight=1)
        self.bind("<Configure>", self.draw_gradient)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color=CARD)
        self.sidebar.place(x=10, y=10, relheight=0.95)

        ctk.CTkLabel(self.sidebar, text="NePoScan",
                     font=("Segoe UI", 20, "bold"),
                     text_color=PRIMARY).pack(pady=20)

        self.start_btn = ctk.CTkButton(
            self.sidebar, text="Start Scan",
            font=btn_font, height=45,
            fg_color=PRIMARY,  text_color="white", command=self.start_scan
        )
        self.start_btn.pack(pady=10, padx=20, fill="x")

        self.stop_btn = ctk.CTkButton(
            self.sidebar, text="Stop Scan",
            font=btn_font, height=45,
            fg_color="#EF4444",  text_color="white", command=self.stop_scan
        )
        self.stop_btn.pack(pady=10, padx=20, fill="x")

        self.clear_btn = ctk.CTkButton(
            self.sidebar, text="Clear Output",
            font=btn_font, height=45,
            fg_color="#64748B",  text_color="white", command=self.clear_output
        )
        self.clear_btn.pack(pady=10, padx=20, fill="x")

        # Main
        self.main = ctk.CTkFrame(self, fg_color="transparent")
        self.main.place(x=240, y=10, relwidth=0.75, relheight=0.95)

        # Input
        self.input_card = ctk.CTkFrame(self.main, fg_color=CARD)
        self.input_card.pack(fill="x", pady=10)

        self.target_entry = ctk.CTkEntry(
            self.input_card,
            placeholder_text="Enter Target IP / Domain",
            height=40
        )
        self.target_entry.pack(padx=15, pady=15, fill="x")

        # Stats
        self.stats_card = ctk.CTkFrame(self.main, fg_color=CARD)
        self.stats_card.pack(fill="x", pady=10)

        self.status_label = ctk.CTkLabel(self.stats_card, text="Status: Idle", text_color=TEXT)
        self.status_label.pack(side="left", padx=15, pady=10)

        self.speed_label = ctk.CTkLabel(self.stats_card, text="Speed: 0 ports/sec", text_color=TEXT)
        self.speed_label.pack(side="right", padx=15, pady=10)

        # Progress
        self.progress = ctk.CTkProgressBar(self.main, height=18, progress_color="green")
        self.progress.pack(fill="x", padx=20, pady=15)
        self.progress.set(0)

        # Output
        self.output_card = ctk.CTkFrame(self.main, fg_color=CARD)
        self.output_card.pack(fill="both", expand=True, pady=10)

        self.output = ctk.CTkTextbox(self.output_card)
        self.output.pack(fill="both", expand=True, padx=10, pady=10)

        # Colors
        self.output.tag_config("open", foreground="green")
        self.output.tag_config("risk_high", foreground="red")
        self.output.tag_config("risk_medium", foreground="orange")
        self.output.tag_config("risk_low", foreground="green")

    def draw_gradient(self, event=None):
        width = self.winfo_width()
        height = self.winfo_height()
        create_gradient(self.bg_canvas, width, height, "#f99de0", "#b100ed")

    # -------------------------
    # SCAN
    # -------------------------
    def scan_port(self, target, port):
        if not self.running:
            return

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            result = s.connect_ex((target, port))

            if result == 0:
                service = COMMON_PORTS.get(port, "Unknown")

                # Risk Levels
                if port in [22, 3389]:
                    risk = "HIGH"
                    tag = "risk_high"
                elif port in [21, 23, 25]:
                    risk = "MEDIUM"
                    tag = "risk_medium"
                else:
                    risk = "LOW"
                    tag = "risk_low"

                self.open_ports.append(port)

                self.after(0, lambda:
                    self.output.insert("end",
                        f"[OPEN] {port} | {service} | Risk:{risk}\n", tag)
                )

                # HTTP Preview
                if port == 80:
                    try:
                        s.send(b"GET / HTTP/1.0\r\n\r\n")
                        response = s.recv(1024).decode(errors="ignore")
                        lines = response.split("\n")[:2]

                        for line in lines:
                            self.after(0, lambda l=line:
                                self.output.insert("end", l + "\n")
                            )
                    except:
                        pass

                self.after(0, lambda: self.output.insert("end", "\n"))

            s.close()

        except:
            pass

        self.scanned += 1
        self.after(0, self.update_progress)

    def start_scan(self):
        target = self.target_entry.get().strip()

        if not target:
            self.status_label.configure(text="Enter target!")
            return

        try:
            ip = socket.gethostbyname(target)
        except:
            self.status_label.configure(text="Invalid Host")
            return

        self.output.delete("1.0", "end")
        self.running = True
        self.open_ports = []
        self.scanned = 0
        self.start_time = time.time()

        self.output.insert("end", f"Scanning {target} ({ip})\n\n")

        self.status_label.configure(text="Scanning...")
        self.progress.set(0)

        threading.Thread(target=self.run_scan, args=(ip,), daemon=True).start()

    def run_scan(self, target):
        with ThreadPoolExecutor(max_workers=50) as executor:
            for port in TARGET_PORTS:
                executor.submit(self.scan_port, target, port)

        self.after(0, self.finish_scan)

    def update_progress(self):
        total = len(TARGET_PORTS)
        progress = self.scanned / total
        self.progress.set(progress)

        elapsed = time.time() - self.start_time
        speed = self.scanned / max(elapsed, 0.1)

        self.speed_label.configure(text=f"Speed: {speed:.1f} ports/sec")
        self.status_label.configure(text=f"Scanning {self.scanned}/{total}")

    def finish_scan(self):
        elapsed = time.time() - self.start_time

        self.output.insert("end", "\n--- Scan Complete ---\n")
        self.output.insert("end", f"Open Ports: {len(self.open_ports)}\n")
        self.output.insert("end", f"Time: {elapsed:.2f}s\n")

        self.status_label.configure(text="Completed")
        self.running = False

    def stop_scan(self):
        self.running = False
        self.status_label.configure(text="Stopped")

    def clear_output(self):
        self.output.delete("1.0", "end")

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app = PortScannerApp()
    app.mainloop()