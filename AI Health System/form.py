import tkinter as tk
import psycopg2
import pyttsx3
from home import open_health_dashboard
from tts_manager import speak


def open_form():
    splash = tk.Toplevel()
    splash.title("Health Care Assistant")

    # ✅ Maximize window
    splash.state('zoomed')
    splash.config(bg="#34495E")

    frame = tk.Frame(splash, bg="#34495E")
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text="Patient Information Form", font=("Arial", 16, "bold"), fg="white", bg="#34495E").pack(pady=15)


    # ✅ Centered frame for content
    
    # ---------------- Name ----------------
    name_label = tk.Label(frame, text="Name:", font=("Arial", 16), bg="#34495E", fg="white")
    name_label.pack()
    name_label.bind("<Button-1>", lambda e: speak("Please enter your name"))  # click label to speak

    name_entry = tk.Entry(frame, font=("Arial", 14), width=40)
    name_entry.pack(pady=5)
    name_entry.bind("<FocusIn>", lambda e: speak("Please enter your name"))

    # ---------------- Age ----------------
    age_label = tk.Label(frame, text="Age:", font=("Arial", 16), bg="#34495E", fg="white")
    age_label.pack()
    age_label.bind("<Button-1>", lambda e: speak("Please enter your age"))

    age_entry = tk.Entry(frame, font=("Arial", 14), width=40)
    age_entry.pack(pady=5)
    age_entry.bind("<FocusIn>", lambda e: speak("Please enter your age"))

    # ---------------- Allergies ----------------
    allergy_label = tk.Label(frame, text="Allergies (if any):", font=("Arial", 16), bg="#34495E", fg="white")
    allergy_label.pack()
    allergy_label.bind("<Button-1>", lambda e: speak("Please enter any allergy"))

    allergy_entry = tk.Entry(frame, font=("Arial", 14), width=40)
    allergy_entry.pack(pady=5)
    allergy_entry.bind("<FocusIn>", lambda e: speak("Please enter any allergy"))

    status_label = tk.Label(frame, text="", font=("Arial", 12), bg="#34495E")
    status_label.pack(pady=10)

    # ✅ Connect DB
    def connect_db():
        return psycopg2.connect(
            host="localhost",
            database="healthcare",
            user="postgres",
            password="ali"  # your PostgreSQL password
        )

    def submit_form():
        name = name_entry.get()
        age = age_entry.get()
        allergy = allergy_entry.get()

        speak("Submitting your information. Please wait.")


        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO patients (name, age, allergy) VALUES (%s, %s, %s) RETURNING id",
                (name, age, allergy)
            )
            patient_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()

            status_label.config(text="✅ Data Saved! Opening Home Page...", fg="lightgreen")
            speak("Your information has been saved successfully. Opening home page.")

            frame.after(3000, lambda: [frame.destroy(), open_health_dashboard(patient_id, name, age)])
        except Exception as e:
            status_label.config(text=f"❌ Error: {e}", fg="red")
            speak("Error while saving data. Please try again.")
    # ✅ Submit Button
    tk.Button(frame, text="Submit", command=submit_form,
              font=("Arial", 14, "bold"), bg="#1ABC9C", fg="white", width=20).pack(pady=15)

    splash.mainloop()
