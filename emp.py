import pandas as pd
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import os

# --- Configuration ---
DB_FILE = "dbh.xlsx"  
OUTPUT_FILE = "Training_Responses.xlsx"  

class TrainingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Participant Log System")
        self.root.geometry("550x850")
        self.root.configure(bg="#f4f7f6")

        self.name_var = tk.StringVar()
        self.branch_var = tk.StringVar()
        self.training_date_var = tk.StringVar()
        self.stay_option = tk.StringVar(value="None")
        self.status_msg = tk.StringVar(value="Ready")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="🏨 PARTICIPANT LOG SYSTEM", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white", pady=15).pack(fill=tk.X)

        # EMPLID Section
        input_frame = tk.Frame(self.root, bg="#f4f7f6")
        input_frame.pack(pady=10)
        tk.Label(input_frame, text="Enter EMPLID:", font=("Arial", 10, "bold"), bg="#f4f7f6").grid(row=0, column=0, padx=5)
        self.EMPLID_entry = tk.Entry(input_frame, font=("Arial", 11))
        self.EMPLID_entry.grid(row=0, column=1, padx=5)
        tk.Button(input_frame, text="Fetch Info", command=self.fetch_details, bg="#3498db", fg="white", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5)

        tk.Label(self.root, textvariable=self.status_msg, font=("Arial", 10, "italic"), fg="blue", bg="#f4f7f6").pack()

        # Info Section
        info_frame = tk.LabelFrame(self.root, text=" Participant Details ", bg="#f4f7f6", padx=10, pady=10)
        info_frame.pack(pady=5, padx=20, fill="x")
        self.create_info_row(info_frame, "Name:", self.name_var)
        self.create_info_row(info_frame, "Branch:", self.branch_var)
        self.create_info_row(info_frame, "Tr. Date:", self.training_date_var)

        # Log Section
        log_frame = tk.LabelFrame(self.root, text=" Timings ", bg="#f4f7f6", padx=10, pady=10, fg="blue")
        log_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(log_frame, text="Check-in Date:", bg="#f4f7f6").grid(row=0, column=0, sticky="w", pady=5)
        self.checkin_date = tk.Entry(log_frame, width=15); self.checkin_date.grid(row=0, column=1, pady=5)
        tk.Label(log_frame, text="Time:", bg="#f4f7f6").grid(row=0, column=2, padx=5)
        self.checkin_time = tk.Entry(log_frame, width=10); self.checkin_time.grid(row=0, column=3)

        tk.Label(log_frame, text="Check-out Date:", bg="#f4f7f6").grid(row=1, column=0, sticky="w", pady=5)
        self.checkout_date = tk.Entry(log_frame, width=15); self.checkout_date.grid(row=1, column=1, pady=5)
        tk.Label(log_frame, text="Time:", bg="#f4f7f6").grid(row=1, column=2, padx=5)
        self.checkout_time = tk.Entry(log_frame, width=10); self.checkout_time.grid(row=1, column=3)
        
        tk.Button(log_frame, text="Set Current Time", command=self.set_checkout_time, bg="#e67e22", fg="white", font=("Arial", 8, "bold")).grid(row=2, column=1, columnspan=3, pady=5, sticky="e")

        # Accommodation
        acc_frame = tk.LabelFrame(self.root, text=" Accommodation ", bg="#f4f7f6", padx=10, pady=10)
        acc_frame.pack(pady=10, padx=20, fill="x")
        tk.Radiobutton(acc_frame, text="Hostel", variable=self.stay_option, value="Hostel", bg="#f4f7f6").grid(row=0, column=0, sticky="w")
        self.hostel_room = tk.Entry(acc_frame, width=20); self.hostel_room.grid(row=0, column=2, padx=5)

        tk.Radiobutton(acc_frame, text="Other", variable=self.stay_option, value="Other", bg="#f4f7f6").grid(row=1, column=0, sticky="w")
        self.other_details = tk.Entry(acc_frame, width=20); self.other_details.grid(row=1, column=2, padx=5)

        self.submit_btn = tk.Button(self.root, text="SAVE LOG", command=self.submit_form, bg="#27ae60", fg="white", font=("Arial", 12, "bold"), pady=10)
        self.submit_btn.pack(pady=20, fill="x", padx=40)

    def create_info_row(self, frame, label, var):
        row = tk.Frame(frame, bg="#f4f7f6")
        row.pack(fill="x", pady=2)
        tk.Label(row, text=label, width=12, anchor="w", bg="#f4f7f6", font=("Arial", 10, "bold")).pack(side="left")
        tk.Entry(row, textvariable=var, state="readonly", bd=1).pack(side="left", fill="x", expand=True)

    def fetch_details(self):
        emplid = self.EMPLID_entry.get().strip()
        if not os.path.exists(DB_FILE):
            messagebox.showerror("Error", f"{DB_FILE} not found!")
            return
        try:
            df_master = pd.read_excel(DB_FILE)
            df_master.columns = [str(c).strip() for c in df_master.columns]
            res = df_master[df_master['EMPLID'].astype(str) == emplid]
            
            if res.empty:
                messagebox.showerror("Error", "EMPLID not found in Master DB!")
                return

            self.name_var.set(res.iloc[0]['NAME'])
            self.branch_var.set(res.iloc[0]['Place of Posting'])
            self.training_date_var.set(res.iloc[0].get('Tr. Date', 'N/A'))
            
            now = datetime.now()
            
            # Check if participant already has a pending check-out in the response file
            if os.path.exists(OUTPUT_FILE):
                df_resp = pd.read_excel(OUTPUT_FILE)
                df_resp['EMPLID'] = df_resp['EMPLID'].astype(str)
                mask = (df_resp['EMPLID'] == emplid) & (df_resp['Check-out Time'] == "00:00")
                pending = df_resp[mask]

                if not pending.empty:
                    self.status_msg.set("Status: Updating Existing Entry")
                    self.submit_btn.config(text="UPDATE LOG", bg="#8e44ad")
                    self.checkin_date.delete(0, tk.END); self.checkin_date.insert(0, pending.iloc[0]['Check-in Date'])
                    self.checkin_time.delete(0, tk.END); self.checkin_time.insert(0, pending.iloc[0]['Check-in Time'])
                    self.checkout_date.delete(0, tk.END); self.checkout_date.insert(0, now.strftime("%d-%m-%Y"))
                    self.checkout_time.delete(0, tk.END); self.checkout_time.insert(0, "00:00")
                    return

            # Default: New Entry
            self.status_msg.set("Status: New Check-in")
            self.submit_btn.config(text="SAVE LOG", bg="#27ae60")
            self.checkin_date.delete(0, tk.END); self.checkin_date.insert(0, now.strftime("%d-%m-%Y"))
            self.checkin_time.delete(0, tk.END); self.checkin_time.insert(0, now.strftime("%H:%M"))
            self.checkout_date.delete(0, tk.END); self.checkout_date.insert(0, now.strftime("%d-%m-%Y"))
            self.checkout_time.delete(0, tk.END); self.checkout_time.insert(0, "00:00")

        except Exception as e:
            messagebox.showerror("Error", f"Fetch Error: {e}")

    def set_checkout_time(self):
        now = datetime.now()
        if now.hour < 17 or (now.hour == 17 and now.minute < 15):
            messagebox.showwarning("Restricted", "Check-out is only allowed after 05:15 PM (17:15).")
        else:
            self.checkout_time.delete(0, tk.END)
            self.checkout_time.insert(0, now.strftime("%H:%M"))

    def submit_form(self):
        if not self.name_var.get():
            messagebox.showwarning("Warning", "Fetch data first!")
            return
        
        emplid = self.EMPLID_entry.get().strip()
        c_time = self.checkout_time.get().strip()
        
        # Validate time format if it's not the default 00:00
        if c_time != "00:00":
            try:
                h, m = map(int, c_time.split(":"))
                if h < 17 or (h == 17 and m < 15):
                    messagebox.showerror("Error", "Check-out must be after 17:15")
                    return
            except:
                messagebox.showerror("Error", "Use HH:MM format.")
                return

        stay_info = f"Hostel({self.hostel_room.get()})" if self.stay_option.get() == "Hostel" else f"Other({self.other_details.get()})"

        new_data = {
            "EMPLID": emplid,
            "Name": self.name_var.get(),
            "Branch": self.branch_var.get(),
            "Check-in Date": self.checkin_date.get(),
            "Check-in Time": self.checkin_time.get(),
            "Check-out Date": self.checkout_date.get(),
            "Check-out Time": c_time,
            "Stay Details": stay_info,
            "Last Update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            if os.path.exists(OUTPUT_FILE):
                df = pd.read_excel(OUTPUT_FILE)
                df['EMPLID'] = df['EMPLID'].astype(str)
                
                # Check for existing pending row
                mask = (df['EMPLID'] == emplid) & (df['Check-out Time'] == "00:00")
                if not df[mask].empty:
                    idx = df[mask].index[0]
                    for key, val in new_data.items():
                        df.at[idx, key] = val
                    df_final = df
                else:
                    df_final = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            else:
                df_final = pd.DataFrame([new_data])

            df_final.to_excel(OUTPUT_FILE, index=False)
            messagebox.showinfo("Success", "Record Saved/Updated!")
            self.clear_all()
        except Exception as e:
            messagebox.showerror("Error", f"Save Error: {e}")

    def clear_all(self):
        self.EMPLID_entry.delete(0, tk.END)
        for var in [self.name_var, self.branch_var, self.training_date_var]: var.set("")
        self.checkin_date.delete(0, tk.END); self.checkin_time.delete(0, tk.END)
        self.checkout_date.delete(0, tk.END); self.checkout_time.delete(0, tk.END)
        self.hostel_room.delete(0, tk.END); self.other_details.delete(0, tk.END)
        self.stay_option.set("None")
        self.status_msg.set("Ready")
        self.submit_btn.config(text="SAVE LOG", bg="#27ae60")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingApp(root)
    root.mainloop()
