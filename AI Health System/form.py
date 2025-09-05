import tkinter as tk
import psycopg2
from home import open_health_dashboard
from tts_manager import speak


def open_form():
    splash = tk.Toplevel()
    splash.title("Health Care Assistant")
    splash.state('zoomed')
    splash.config(bg="#34495E")

    frame = tk.Frame(splash, bg="#34495E")
    frame.place(relx=0.5, rely=0.1, anchor="n")  # top-centered

    # ---------------- Title ----------------
    tk.Label(frame, text="Patient Information", font=("Arial", 26, "bold"), fg="white", bg="#34495E").pack(pady=10)

    status_label = tk.Label(frame, text="", font=("Arial", 12), bg="#34495E")
    status_label.pack(pady=5)

    # ✅ Connect DB
    def connect_db():
        return psycopg2.connect(
            host="localhost",
            database="healthcare",
            user="postgres",
            password="ali"
        )

    # ---------------- Returning Patient Section ----------------
        # ---------------- Returning Patient Section ----------------
    tk.Label(frame, text="If you have visited before:", font=("Arial", 16, "italic"), 
             fg="white", bg="#34495E").pack(pady=20)

    returning_frame = tk.Frame(frame, bg="#34495E")  # container for returning patient widgets
    returning_frame.pack(pady=5)

    row_frame = tk.Frame(returning_frame, bg="#34495E")
    row_frame.pack(pady=5)

    tk.Label(row_frame, text="Phone No:", font=("Arial", 16), bg="#34495E", fg="white").pack(side="left", padx=5)

    phone_entry = tk.Entry(row_frame, font=("Arial", 14), width=25)
    phone_entry.pack(side="left", padx=5)

    search_btn = tk.Button(row_frame, text="Search", font=("Arial", 11, "bold"),
                           bg="#3498DB", fg="white", width=8)
    search_btn.pack(side="left", padx=15)

    # ---------------- Returning Patient Dropdown ----------------
    dropdown_var = tk.StringVar()
    dropdown_menu = None  # will hold the dropdown

    def show_dropdown(names, rows):
        nonlocal dropdown_menu
        if dropdown_menu:
            dropdown_menu.destroy()

        # Create a row for dropdown + button
        dropdown_row = tk.Frame(returning_frame, bg="#34495E")
        dropdown_row.pack(pady=20)

        dropdown_var.set(names[0])
        dropdown_menu = tk.OptionMenu(dropdown_row, dropdown_var, *names)
        dropdown_menu.config(font=("Arial", 14), width=15, bg="#1ABC9C", fg="white")
        dropdown_menu.pack(side="left", padx=5)

        def select_patient():
            selected = dropdown_var.get()
            idx = names.index(selected)
            pid, pname, page, pallergy = rows[idx]
            status_label.config(text=f"✅ Welcome back {pname}", fg="lightgreen")
            frame.after(2000, lambda: [frame.destroy(), open_health_dashboard(pid, pname, page)])

        tk.Button(dropdown_row, text="Continue", command=select_patient,
                  font=("Arial", 12, "bold"), bg="#1ABC9C", fg="white", width=8).pack(side="left", padx=10)

    # Horizontal Line Separator
    separator = tk.Frame(frame, height=2, bd=1, relief="sunken", bg="white")
    separator.pack(fill="x", padx=30, pady=20)


    # ---------------- New Patient Section ----------------
    tk.Label(frame, text="New Patient", font=("Arial", 18, "bold"), fg="white", bg="#34495E").pack(pady=20)

    # Row 1: Name + Phone
    row1 = tk.Frame(frame, bg="#34495E")
    row1.pack(pady=5)
    tk.Label(row1, text="Name:", font=("Arial", 16), bg="#34495E", fg="white").pack(side="left", padx=5)
    name_entry = tk.Entry(row1, font=("Arial", 14), width=20)
    name_entry.pack(side="left", padx=5)

    tk.Label(row1, text="Phone No:", font=("Arial", 16), bg="#34495E", fg="white").pack(side="left", padx=5)
    ph_entry = tk.Entry(row1, font=("Arial", 14), width=20)
    ph_entry.pack(side="left", padx=5)

    # Row 2: Age + Allergy
    row2 = tk.Frame(frame, bg="#34495E")
    row2.pack(pady=5)
    tk.Label(row2, text="Age:", font=("Arial", 16), bg="#34495E", fg="white").pack(side="left", padx=5)
    age_entry = tk.Entry(row2, font=("Arial", 14), width=10)
    age_entry.pack(side="left", padx=5)

    tk.Label(row2, text="Allergy:", font=("Arial", 16), bg="#34495E", fg="white").pack(side="left", padx=5)
    allergy_entry = tk.Entry(row2, font=("Arial", 14), width=20)
    allergy_entry.pack(side="left", padx=5)

    # Register Button
    tk.Button(frame, text="Register", font=("Arial", 14, "bold"),
              bg="#E67E22", fg="white", width=15).pack(pady=20)

    
    # ✅ Attach fetch logic to Search button
    def fetch_patient():
        phone = phone_entry.get()
        if not phone:
            status_label.config(text="❌ Please enter phone number", fg="red")
            return

        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT id, name, age, allergy FROM patients WHERE ph_num = %s", (phone,))
            rows = cur.fetchall()
            cur.close()
            conn.close()

            if not rows:
                status_label.config(text="❌ No records found for this phone", fg="red")
                return

            if len(rows) == 1:
                pid, pname, page, pallergy = rows[0]
                status_label.config(text=f"✅ Welcome back {pname}", fg="lightgreen")
                frame.after(2000, lambda: [frame.destroy(), open_health_dashboard(pid, pname, page)])
            else:
                names = [f"{row[1]} (Age {row[2]})" for row in rows]
                show_dropdown(names, rows)

        except Exception as e:
            status_label.config(text=f"❌ Error: {e}", fg="red")

    search_btn.config(command=fetch_patient)

    splash.mainloop()
