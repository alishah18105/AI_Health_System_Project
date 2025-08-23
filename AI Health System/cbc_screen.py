import tkinter as tk
from tkinter import filedialog, ttk
from cbc_analyzer import analyze_cbc_report


def go_back(window):
    """Close this window and open home.py"""
    window.destroy()
    from home import open_health_dashboard
    open_health_dashboard()


def open_cbc_screen():
    cbc_window = tk.Tk()
    cbc_window.title("CBC Report Analyzer")
    cbc_window.state("zoomed")  # Maximized
    cbc_window.configure(bg="#ecf0f1")

    # --- TOP BAR ---
    top_bar = tk.Frame(cbc_window, bg="#ecf0f1")
    top_bar.pack(fill="x", pady=5)

    # Back button (left)
    back_btn = tk.Button(
        top_bar,
        text="← Back",
        font=("Arial", 12, "bold"),
        bg="#e74c3c",
        fg="white",
        command=lambda: go_back(cbc_window)
    )
    back_btn.pack(side="left", padx=10, pady=5)

    # Upload button (right)
    def upload_and_analyze():
        file_path = filedialog.askopenfilename(
            title="Select CBC Report",
            filetypes=[
                ("PDF or Image Files", "*.pdf *.jpg *.jpeg *.png"),
                ("PDF Files", "*.pdf"),
                ("Image Files", "*.jpg *.jpeg *.png")
            ]
    )
        if file_path:
            results, remarks = analyze_cbc_report(file_path)

            # Clear old data
            tree.delete(*tree.get_children())

            # Insert new results
            for r in results:
                status_tag = r["Status"].lower()
                tree.insert(
                    "",
                    "end",
                    values=(r["Test"], r["Value"], r["Unit"], r["Status"]),
                    tags=(status_tag,)
                )

            # Tag colors
            tree.tag_configure("low", background="#ff4d4d", foreground="black")
            tree.tag_configure("high", background="#ffb84d", foreground="black")
            tree.tag_configure("normal", background="#99e699", foreground="black")

            # Show remarks
            remarks_box.config(state="normal")
            remarks_box.delete("1.0", tk.END)
            for rem in remarks:
                remarks_box.insert(tk.END, f"• {rem}\n")
            remarks_box.config(state="disabled")

    upload_btn = tk.Button(
        top_bar,
        text="📂 Upload CBC Report",
        command=upload_and_analyze,
        font=("Arial", 12, "bold"),
        bg="#3498db",
        fg="white",
        activebackground="#2980b9",
        activeforeground="white",
        relief="flat",
        padx=15,
        pady=5
    )
    upload_btn.pack(side="right", padx=10, pady=5)

    # --- TITLE ---
    tk.Label(
        cbc_window,
        text="🩸 CBC Report Analyzer",
        font=("Helvetica", 20, "bold"),
        bg="#ecf0f1",
        fg="#2c3e50"
    ).pack(pady=10)

    # --- MAIN CONTENT ---
    main_frame = tk.Frame(cbc_window, bg="#ecf0f1")
    main_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Table
    columns = ("Test", "Value", "Unit", "Status")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=18)
    for col in columns:
        tree.heading(col, text=col, anchor="center")

    tree.column("Test", width=400, anchor="w")
    tree.column("Value", width=120, anchor="center")
    tree.column("Unit", width=120, anchor="center")
    tree.column("Status", width=150, anchor="center")

    tree.pack(fill="both", expand=True, pady=5)

    # Remarks
    remarks_frame = tk.Frame(main_frame, bg="#ecf0f1")
    remarks_frame.pack(fill="x", pady=10)

    tk.Label(
        remarks_frame,
        text="📝 Remarks:",
        font=("Arial", 14, "bold"),
        bg="#ecf0f1",
        fg="#2c3e50"
    ).pack(anchor="w")

    remarks_box = tk.Text(
        remarks_frame,
        height=6,
        wrap="word",
        font=("Arial", 12),
        bg="white",
        fg="black",
        state="disabled"
    )
    remarks_box.pack(fill="x", pady=5)

    cbc_window.mainloop()
