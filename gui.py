import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd
from Scheduling import main as run_scheduling

class MusicSchedulingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Scheduling App")
        self.root.geometry("400x300")

        # Title Label
        self.title_label = tk.Label(root, text="Music Scheduling App", font=("Arial", 16))
        self.title_label.pack(pady=10)

        # Run Scheduling Button
        self.run_button = tk.Button(root, text="Run Scheduling", command=self.run_scheduling)
        self.run_button.pack(pady=10)

        # View Schedule Button
        self.view_button = tk.Button(root, text="View Schedule", command=self.view_schedule)
        self.view_button.pack(pady=10)

        # Upload to Google Calendar Button
        self.upload_button = tk.Button(root, text="Upload to Google Calendar", command=self.upload_to_calendar)
        self.upload_button.pack(pady=10)

        # Exit Button
        self.exit_button = tk.Button(root, text="Exit", command=root.quit)
        self.exit_button.pack(pady=10)

    def run_scheduling(self):
        try:
            run_scheduling()
            messagebox.showinfo("Success", "Scheduling completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def view_schedule(self):
        try:
            file_path = filedialog.askopenfilename(title="Select Schedule File", filetypes=[("CSV Files", "*.csv")])
            if file_path:
                schedule_df = pd.read_csv(file_path)
                self.show_schedule_window(schedule_df)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def show_schedule_window(self, schedule_df):
        schedule_window = tk.Toplevel(self.root)
        schedule_window.title("Schedule")
        schedule_window.geometry("600x400")

        text = tk.Text(schedule_window, wrap=tk.WORD)
        text.pack(expand=True, fill=tk.BOTH)

        text.insert(tk.END, schedule_df.to_string(index=False))

    def upload_to_calendar(self):
        try:
            run_scheduling()  # This will also upload to Google Calendar as part of the process
            messagebox.showinfo("Success", "Schedule uploaded to Google Calendar successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicSchedulingApp(root)
    root.mainloop()
