import tkinter as tk
import tkinter.font as tkFont
#from SOA import Process
from SOA import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
import sys
import os
import subprocess
import time
import threading

PROCESSES = []

class App:
    def __init__(self, root):

        # variables
        self.file_name = ""

        # output txt
        self.text_widget = tk.Text(root, wrap="word", width=50, height=50)
        self.text_widget.pack(pady=10)
        self.text_widget.place(x=1000, y= 20)

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

        self.tasks_treeview = ttk.Treeview(root, columns=("Name", "Deadline Start", "Deadline End", "Proc Time", "Period", "Arrival", "Status"), show="headings", height=15)
        self.tasks_treeview.heading("Name", text="Nombre de la tarea")
        self.tasks_treeview.heading("Deadline Start", text="Deadline de inicio")
        self.tasks_treeview.heading("Deadline End", text="Deadline de fin")
        self.tasks_treeview.heading("Proc Time", text="Duración")
        self.tasks_treeview.heading("Period", text="Periodo")
        self.tasks_treeview.heading("Arrival", text="Llegada")
        self.tasks_treeview.heading("Status", text="Estado")
        self.tasks_treeview.column("Name", width=150)
        self.tasks_treeview.column("Deadline Start", width=120)
        self.tasks_treeview.column("Deadline End", width=120)
        self.tasks_treeview.column("Proc Time", width=120)
        self.tasks_treeview.column("Period", width=120)
        self.tasks_treeview.column("Arrival", width=120)
        self.tasks_treeview.column("Status", width=120)
        self.tasks_treeview.place(x=20, y=20)

        scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=self.tasks_treeview.yview)
        scrollbar.place(x=895, y=20, height=320)
        self.tasks_treeview.config(yscrollcommand=scrollbar.set)

        vlist = ["RMS", "EDF-p", "EDF-a"]
        

        self.current_algorithm = tk.StringVar(value="RMS")
        self.combo_algorithm = ttk.Combobox(root, values = vlist)
        self.combo_algorithm.set("RMS")
        self.combo_algorithm["textvariable"] = self.current_algorithm
        self.combo_algorithm.place(x=380,y=560,width=275,height=40)
        self.combo_algorithm.bind("<<ComboboxSelected>>", self.on_combobox_change)


        self.CREATE_FORM = {
            "name": {
                "text": "Nombre de la tarea",
                "value": tk.StringVar(root)
            },
            "deadline_start": {
                "text": "Deadline de inicio",
                "value": tk.StringVar(root),
                "active_on": [vlist[2]]
            },
            "deadline_end": {
                "text": "Deadline de fin",
                "value": tk.StringVar(root)
            },
            "time_period": {
                "text": "Duración",
                "value": tk.StringVar(root),
                "active_on": [vlist[0], vlist[1], vlist[2]]
            },
            "period": {
                "text": "Periodo",
                "value": tk.StringVar(root),
                "active_on": [vlist[1]]
            },
            "arrival": {
                "text": "Llegada",
                "value": tk.StringVar(root),
                "active_on": [vlist[2]]
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
        label["text"] = "Subclase de algoritmo"
        label.place(x=700,y=530)

        self.subtype_algorithm = tk.StringVar(value="start-unforced_idle_times")
        subtype_algorithm_list = [
            "start-unforced_idle_times",
            "end-unforced_idle_times",
            "both-unforced_idle_times",
            "start-not_unforced_idle_times",
            "end-not_unforced_idle_times",
            "both-not_unforced_idle_times"
        ]
        self.combo_sub_algorithm = ttk.Combobox(root, values = subtype_algorithm_list, state="disabled")
        self.combo_sub_algorithm.set("start-unforced_idle_times")
        self.combo_sub_algorithm["textvariable"] = self.subtype_algorithm
        self.combo_sub_algorithm.place(x=700,y=560,width=190,height=40)

        label=tk.Label(root)
        ft = tkFont.Font(family='Times',size=12)
        label["font"] = ft
        label["justify"] = "center"
        label["fg"] = "#333333"
        label["text"] = "Habilitar Timelines"
        label.place(x=700,y=610)

        self.show_timelines = tk.StringVar(value="Sí")
        show_timelines_list = [
            "Sí",
            "No",
        ]
        self.combo_show_timelines = ttk.Combobox(root, values = show_timelines_list, state="normal")
        self.combo_show_timelines.set("Sí")
        self.combo_show_timelines["textvariable"] = self.show_timelines
        self.combo_show_timelines.place(x=700,y=640,width=190,height=40)
        #self.combo_show_timelines.bind("<<ComboboxSelected>>", self.on_combobox_change)

        label=tk.Label(root)
        ft = tkFont.Font(family='Times',size=12)
        label["font"] = ft
        label["justify"] = "center"
        label["fg"] = "#333333"
        label["text"] = "Tiempo a simular"
        label.place(x=380,y=610)

        self.max_time_entry=tk.Entry(root)
        self.max_time_entry["borderwidth"] = "1px"
        ft = tkFont.Font(family='Times',size=12)
        self.max_time_entry["font"] = ft
        self.max_time_entry["fg"] = "#333333"
        self.max_time_entry["justify"] = "center"
        self.max_time_entry["textvariable"] = self.max_simulation_time_entry
        self.max_time_entry.place(x=380,y=640,width=276,height=40)

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

    def on_combobox_change(self, reset_flag=0):
        #Clear the treeview list items
        if reset_flag:
            for item in self.tasks_treeview.get_children():
                self.tasks_treeview.delete(item)
            PROCESSES.clear()

        if self.current_algorithm.get() == "EDF-a":
            self.combo_sub_algorithm.config(state="normal")
            self.max_time_entry.config(state="disabled")
        else:
            self.combo_sub_algorithm.config(state="disabled")
            self.max_time_entry.config(state="normal")
        for key in self.CREATE_FORM:
            if ("active_on" not in self.CREATE_FORM[key] or self.current_algorithm.get() in self.CREATE_FORM[key]["active_on"]):
                self.CREATE_FORM[key]["entry"].config(state="normal")
            else:
                self.CREATE_FORM[key]["entry"].config(state="disabled")

    def run_simulation_button_command(self):
        # run python3 SOA.py -t 20 -a EDF-p -i edf2.txt -o o.txt -tl 1
        #ttk.Button(win, text= "Open", command= open_prompt).pack()
        #os.system('SOA.py -t 20 -a EDF-p -i edf2.txt -o o.txt -tl 1')
        #TODO: crear archivo de input a partir de PROCESSES
        f = open("procs.txt", "w")
        is_edf_a = False
        for proc in PROCESSES:
            # RMS
            if proc.period == 0 and proc.deadline_start == -1:
                f.write(f"{proc.pid},{proc.deadline},{proc.time_period}\n")
            # EDF-p
            elif proc.deadline_start == -1:
                f.write(f"{proc.pid},{proc.period},{proc.deadline},{proc.time_period}\n")
            # EDF-a
            else:
                is_edf_a = True
                f.write(f"{proc.pid},{proc.deadline},{proc.time_period},{proc.deadline_start},{proc.arrival_time}\n")
        f.close()
        #params = ["python", "SOA.py", "-t", "20", "-a", f"{self.combo_algorithm.get()}", "-i", "procs.txt", "-o", "output.txt", "-tl", "0"]
        #tl = 
        #print(self.combo_show_timelines.get(), type(self.combo_show_timelines.get()))
        params = ["Scheduling", "-t", "20", "-a", f"{self.combo_algorithm.get()}", "-i", "procs.txt", "-o", "output.txt", "-tl", f"{1 if 'Sí' in self.combo_show_timelines.get() else 0}"]
        
        if is_edf_a:
            subtype = self.subtype_algorithm.get().split("-")
            deadline = subtype[0]
            unforced_idle_times = "0" if "not" in subtype[1] else "1"
            params = params + ["-s", deadline, "-u", unforced_idle_times] 
            print(params)

        main(params)
        self.read_output_file()
    
    def select_file_button_command(self):
        #Clear the treeview list items
        for item in self.tasks_treeview.get_children():
            self.tasks_treeview.delete(item)
        self.file_name = askopenfilename()
        PROCESSES.clear()
        f = open(self.file_name, "r")
        while True:
            line = f.readline().strip().split(',')
            #print(line)
            if len(line) < 2:
                break
            line = [int(i) for i in line] # str to int
            #"RMS":
            if len(line) == 3:
                PROCESSES.append(Process(line[0],0,line[1],line[2]))
                process_info = (line[0], "None", line[1], line[2], "None","Periodic", "Creado")
                self.tasks_treeview.insert("", tk.END, values=process_info)
                self.clear_form()
                self.combo_algorithm.set("RMS")
                self.combo_sub_algorithm.config(state="disabled")
            # EDF-p            
            elif len(line) == 4:
                PROCESSES.append(Process(line[0],line[1],line[2],line[3]))
                process_info = (line[0], "None", line[2], line[3], line[1], "Periodic", "Creado")
                self.tasks_treeview.insert("", tk.END, values=process_info)
                self.clear_form()
                self.combo_algorithm.set("EDF-p")
                self.combo_sub_algorithm.config(state="disabled")
             # EDF-a
            else:
                PROCESSES.append(Process(line[0],0,line[1],line[2],line[3],line[4]))
                process_info = (line[0], line[3], line[1], line[2], "None", line[4], "Creado")
                self.tasks_treeview.insert("", tk.END, values=process_info)
                self.clear_form()
                self.combo_algorithm.set("EDF-a")
                self.combo_sub_algorithm.config(state="normal")
            

    def create_task_button_command(self):
        name = self.CREATE_FORM["name"]["value"].get()
        deadline_start = self.CREATE_FORM["deadline_start"]["value"].get()
        deadline_end = self.CREATE_FORM["deadline_end"]["value"].get()
        time_period = self.CREATE_FORM["time_period"]["value"].get()
        period = self.CREATE_FORM["period"]["value"].get()
        arrival = self.CREATE_FORM["arrival"]["value"].get()

        #print(type(self.CREATE_FORM["name"]["value"].get()), type(self.CREATE_FORM["deadline_end"]["value"].get()), self.CREATE_FORM["time_period"]["value"].get())
        if ( not (self.CREATE_FORM["name"]["value"].get() == "") and 
            (self.combo_algorithm.get() == "RMS" and not (self.CREATE_FORM["deadline_end"]["value"].get() == "") and not (self.CREATE_FORM["time_period"]["value"].get()) == "") or
            (self.combo_algorithm.get() == "EDF-p" and not (self.CREATE_FORM["deadline_end"]["value"].get() == "") and not (self.CREATE_FORM["time_period"]["value"].get()) == "" and not (self.CREATE_FORM["period"]["value"].get()) == "") or
            (self.combo_algorithm.get() == "EDF-a" and not (self.CREATE_FORM["deadline_end"]["value"].get() == "") and not (self.CREATE_FORM["time_period"]["value"].get()) == "" and not (self.CREATE_FORM["deadline_start"]["value"].get()) == "" and not (self.CREATE_FORM["arrival"]["value"].get()) == "")
        ):
            # if not all([name, deadline_start, deadline_end, time_period, arrival]):
            #     messagebox.showerror("Error", "Por favor, complete todos los campos.")
            #     return

            PROCESSES.append(Process(name, period, deadline_end, time_period, deadline_start, arrival))
            process_info = (name, deadline_start, deadline_end, time_period, period, arrival, "Creado")
            self.tasks_treeview.insert("", tk.END, values=process_info)
            self.clear_form()

    def clear_form(self):
        for key in self.CREATE_FORM:
            self.CREATE_FORM[key]["value"].set("")

    def read_output_file(self):
        if ('output.txt'):
            with open('output.txt', 'r') as file:
                content = file.read()
                self.text_widget.delete(1.0, tk.END)  # Clear previous content
                self.text_widget.insert(tk.END, content)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
