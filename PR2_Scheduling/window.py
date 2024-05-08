import tkinter as tk
import tkinter.font as tkFont
from SOA import Process
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename

PROCESSES = []

class App:
    def __init__(self, root):
        #setting title
        root.title("SOA Proyecto II")
        #setting window size
        width=1440
        height=900
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        self.tasks_treeview = ttk.Treeview(root, columns=("Name", "Deadline Start", "Deadline End", "Time Period", "Arrival", "Status"), show="headings", height=15)
        self.tasks_treeview.heading("Name", text="Nombre de la tarea")
        self.tasks_treeview.heading("Deadline Start", text="Deadline de inicio")
        self.tasks_treeview.heading("Deadline End", text="Deadline de fin")
        self.tasks_treeview.heading("Time Period", text="Periodo")
        self.tasks_treeview.heading("Arrival", text="Llegada")
        self.tasks_treeview.heading("Status", text="Estado")
        self.tasks_treeview.column("Name", width=150)
        self.tasks_treeview.column("Deadline Start", width=120)
        self.tasks_treeview.column("Deadline End", width=120)
        self.tasks_treeview.column("Time Period", width=120)
        self.tasks_treeview.column("Arrival", width=120)
        self.tasks_treeview.column("Status", width=120)
        self.tasks_treeview.place(x=20, y=20)

        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tasks_treeview.yview)
        scrollbar.place(x=775, y=20, height=320)
        self.tasks_treeview.config(yscrollcommand=scrollbar.set)

        vlist = ["RMS", "EDF Períodico", "EDF Aperíodico", "EDF Aperíodico (Inactividad no forzada)"]
        

        self.current_algorithm = tk.StringVar(value="RMS")
        combo_algorithm = ttk.Combobox(root, values = vlist)
        combo_algorithm.set("RMS")
        combo_algorithm["textvariable"] = self.current_algorithm
        combo_algorithm.place(x=380,y=560,width=275,height=40)
        combo_algorithm.bind("<<ComboboxSelected>>", self.on_combobox_change)


        self.CREATE_FORM = {
            "name": {
                "text": "Nombre de la tarea",
                "value": tk.StringVar(root)
            },
            "deadline_start": {
                "text": "Deadline de inicio",
                "value": tk.StringVar(root),
                "active_on": [vlist[2], vlist[3]]
            },
            "deadline_end": {
                "text": "Deadline de fin",
                "value": tk.StringVar(root)
            },
            "time_period": {
                "text": "Periodo",
                "value": tk.StringVar(root),
                "active_on": [vlist[0], vlist[1]]
            },
            "arrival": {
                "text": "Llegada",
                "value": tk.StringVar(root),
                "active_on": [vlist[2], vlist[3]]
            }

        }

        self.max_simulation_time_entry = tk.StringVar(root)


        i = 0
        for key in self.CREATE_FORM:
            label=tk.Label(root)
            ft = tkFont.Font(family='Times',size=12)
            label["font"] = ft
            label["justify"] = "center"
            label["fg"] = "#333333"
            label["text"] = self.CREATE_FORM[key]["text"]
            label.place(x=20,y=380+(i*80))

            disabled_status = "normal" if ("active_on" not in self.CREATE_FORM[key] or self.current_algorithm.get() in self.CREATE_FORM[key]["active_on"]) else "disabled"
            self.CREATE_FORM[key]["entry"]=tk.Entry(root, state=disabled_status)
            self.CREATE_FORM[key]["entry"]["borderwidth"] = "1px"
            ft = tkFont.Font(family='Times',size=12)
            self.CREATE_FORM[key]["entry"]["font"] = ft
            self.CREATE_FORM[key]["entry"]["fg"] = "#333333"
            self.CREATE_FORM[key]["entry"]["justify"] = "center"
            self.CREATE_FORM[key]["entry"]["textvariable"] = self.CREATE_FORM[key]["value"]
            self.CREATE_FORM[key]["entry"].place(x=20,y=410+(i*80),width=276,height=40)
            i += 1

        create_task_button=tk.Button(root)
        create_task_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=12)
        create_task_button["font"] = ft
        create_task_button["fg"] = "#000000"
        create_task_button["bg"] = "#009688"
        create_task_button["justify"] = "center"
        create_task_button["text"] = "Crear tarea"
        create_task_button.place(x=380,y=410,width=275,height=40)
        create_task_button["command"] = self.create_task_button_command

        select_file_button=tk.Button(root)
        select_file_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=12)
        select_file_button["font"] = ft
        select_file_button["fg"] = "#000000"
        select_file_button["bg"] = "#009688"
        select_file_button["justify"] = "center"
        select_file_button["text"] = "Seleccionar archivo"
        select_file_button.place(x=380,y=470,width=275,height=40)
        select_file_button["command"] = self.select_file_button_command

        label=tk.Label(root)
        ft = tkFont.Font(family='Times',size=12)
        label["font"] = ft
        label["justify"] = "center"
        label["fg"] = "#333333"
        label["text"] = "Algoritmo a simular"
        label.place(x=380,y=530)

        label=tk.Label(root)
        ft = tkFont.Font(family='Times',size=12)
        label["font"] = ft
        label["justify"] = "center"
        label["fg"] = "#333333"
        label["text"] = "Tiempo a simular"
        label.place(x=380,y=610)

        entry=tk.Entry(root)
        entry["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=12)
        entry["font"] = ft
        entry["fg"] = "#333333"
        entry["justify"] = "center"
        entry["textvariable"] = self.max_simulation_time_entry
        entry.place(x=380,y=640,width=276,height=40)

        run_simulation_button=tk.Button(root)
        run_simulation_button["bg"] = "#f0f0f0"
        ft = tkFont.Font(family='Times',size=12)
        run_simulation_button["font"] = ft
        run_simulation_button["fg"] = "#fff"
        run_simulation_button["bg"] = "#cc0000"
        run_simulation_button["justify"] = "center"
        run_simulation_button["text"] = "Simular"
        run_simulation_button.place(x=380,y=730,width=275,height=40)
        run_simulation_button["command"] = self.run_simulation_button_command

    def on_combobox_change(self, event):
        for key in self.CREATE_FORM:
            if ("active_on" not in self.CREATE_FORM[key] or self.current_algorithm.get() in self.CREATE_FORM[key]["active_on"]):
                self.CREATE_FORM[key]["entry"].config(state="normal")
            else:
                self.CREATE_FORM[key]["entry"].config(state="disabled")

    def run_simulation_button_command(self):
        pass

    def select_file_button_command(self):
        filename = askopenfilename()
        print(filename)

    def create_task_button_command(self):
        name = self.CREATE_FORM["name"]["value"].get()
        deadline_start = self.CREATE_FORM["deadline_start"]["value"].get()
        deadline_end = self.CREATE_FORM["deadline_end"]["value"].get()
        time_period = self.CREATE_FORM["time_period"]["value"].get()
        arrival = self.CREATE_FORM["arrival"]["value"].get()

        # if not all([name, deadline_start, deadline_end, time_period, arrival]):
        #     messagebox.showerror("Error", "Por favor, complete todos los campos.")
        #     return

        PROCESSES.append(Process(name, deadline_end, time_period, deadline_start, arrival))
        process_info = (name, deadline_start, deadline_end, time_period, arrival, "Creado")
        self.tasks_treeview.insert("", tk.END, values=process_info)
        self.clear_form()

    def clear_form(self):
        for key in self.CREATE_FORM:
            self.CREATE_FORM[key]["value"].set("")

        

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
