from functools import cmp_to_key
import copy
import sys
import os.path

class Process:
    def __init__(self, pid, period, deadline, time_period, deadline_start=-1, arrival_time=-1):
        self.pid = pid
        self.period = period
        self.time_period = time_period
        self.deadline = deadline
        self.remaining_time = time_period
        self.deadline_start = deadline_start
        self.arrival_time = arrival_time
        # [[deadline miss (end), periodos en ejecución, periodos sin ejecución, linea del tiempo?, deadline miss (start)]]
        self.stats = [0, 0, 0, []] # TODO: Linea del tiempo?

def print_procs(procs):
    for proc in procs:
        print(f"(PID: {proc.pid}, deadline: {proc.deadline}, time period: {proc.time_period}), remaining time: {proc.remaining_time}")  
    
#procs = [Process(1,4,1),Process(2,5,2),Process(3,7,2)]
#print_procs(procs)

# procs: list of processes, each a tuple (or dict) of (ID, time_period, deadline, time_remaining)
def rate_monotonic_scheduling(procs, steps = 15):
    # simulate
    for i in range(steps):
        print("------- Iter: ", i, "-------")
        for proc in procs:
            # Stats update (assuming no proc is used in this iter)
            proc.stats[2] += 1
            proc.stats[3].append(f"Iter {i}:\n")
            # Get deadline Misses
            if i > 0 and i % proc.deadline == 0:
                if proc.remaining_time > 0: 
                    # stats update
                    proc.stats[0] += 1
                    print(f"Deadline mniss. Pid: {proc.pid}, rem: {proc.remaining_time}")
                    proc.stats[3][i] += f"        Deadline miss with {proc.remaining_time} time remaining\n"
                # reset procs
                proc.remaining_time = proc.time_period
                print(f"Initializing process. Pid: {proc.pid}, rem: {proc.remaining_time}")
                proc.stats[3][i] += f"        Initializing process\n"
                #print_procs([proc])
            elif 1 > 0 and proc.remaining_time == 0:
                proc.stats[3][i] += f"        Waiting to reinitialize\n"
            
        # schedule proc
        unfinished_procs = [proc for proc in procs if proc.remaining_time > 0]
        print_procs(unfinished_procs)
        if unfinished_procs:
            # (shortest time_period first)    
            current_proc = min(unfinished_procs, key=lambda x: x.time_period)
            current_proc.remaining_time -= 1
            print(f"Giving CPU to pid: {current_proc.pid}, rem: {current_proc.remaining_time}")
            current_proc.stats[3][i] += f"        Running on CPU\n"
            # stats update
            if current_proc.remaining_time == 0:
                current_proc.stats[3][i] += f"        Finished execution\n"
            current_proc.stats[1] += 1
            current_proc.stats[2] -= 1 # to account for the sum done in line 32
            for proc in unfinished_procs:
                if not (proc.pid == current_proc.pid):
                    proc.stats[3][i] += f"        Waiting for CPU\n"
            
def build_summary_maps(procs):
    arrival_map = {}
    deadline_start_map = {}
    deadline_end_map  = {}
    procs_map = {}
    for proc in procs:
        arrival_map.setdefault(proc.arrival_time, []).append(proc.pid)
        deadline_start_map.setdefault(proc.deadline_start, []).append(proc.pid)
        deadline_end_map.setdefault(proc.deadline, []).append(proc.pid)
        procs_map[proc.pid] = proc
    return {"arrival_map": arrival_map, "deadline_start_map": deadline_start_map, "deadline_end_map": deadline_end_map, "procs_map": procs_map }

def get_earliest_deadline(procs_map, ready_tasks, deadline="start"):
    earliest_deadline = [99999999, None]
    for pid in ready_tasks:
        proc = procs_map[pid]
        deadline_check = proc.deadline_start if deadline != "end" else proc.deadline
        if deadline_check < earliest_deadline[0]:
            earliest_deadline[0] = deadline_check
            earliest_deadline[1] = proc.pid
    return earliest_deadline

def get_earliest_deadline_plan(procs):
    return sorted(procs, key=cmp_to_key(lambda x, y: x.deadline_start - y.deadline_start)), \
    sorted(procs, key=cmp_to_key(lambda x, y: x.deadline - y.deadline))

def edf_define_running_task(running_task, ready_tasks, unforced_idle_times, execution_plan_start_d, step, procs_map, execution_plan_indx):
    if running_task is None and len(ready_tasks) > 0:
        if unforced_idle_times:
            if execution_plan_start_d[execution_plan_indx].pid in ready_tasks:
                running_task = execution_plan_start_d[execution_plan_indx].pid
                execution_plan_indx += 1
                procs_map[running_task].stats[3].append(f"\t[Step: {step}] Task {procs_map[running_task].pid} assigned to CPU.")
        else:
            earliest_deadline = get_earliest_deadline(procs_map, ready_tasks)
            running_task = earliest_deadline[1]
            ready_tasks.discard(running_task)
            procs_map[running_task].stats[3].append(f"\t[Step: {step}] Task {procs_map[running_task].pid} assigned to CPU.")
    return running_task, execution_plan_indx

def edf_aperiodic(procs, deadline="start", unforced_idle_times=False):
    tasks_to_process = len(procs)
    summary_maps = build_summary_maps(procs)
    arrival_map = summary_maps["arrival_map"]
    deadline_start_map = summary_maps["deadline_start_map"]
    deadline_end_map = summary_maps["deadline_end_map"]
    procs_map = summary_maps["procs_map"]
    step = 0
    running_task  = None
    ready_tasks = set()
    execution_plan_start_d = []
    execution_plan_indx = 0
    if unforced_idle_times:
        execution_plan_start_d, _ = get_earliest_deadline_plan(procs)

    while tasks_to_process > 0:
        step += 1

        # Task running
        if running_task:
            procs_map[running_task].remaining_time -= 1
            if procs_map[running_task].remaining_time == 0:
                tasks_to_process -= 1
                procs_map[running_task].stats[3].append(f"\t[Step: {step}] Task {procs_map[running_task].pid} finished.")
                running_task = None
                if tasks_to_process == 0:
                    continue
                    
        arrived_tasks = arrival_map.get(step)
        if arrived_tasks:
            for arrived_task in  arrived_tasks:
                procs_map[arrived_task].stats[3].append(f"\t[Step: {step}] Arrived task: {arrived_task}")
                deadline_check = step <= procs_map[arrived_task].deadline_start if deadline != "end" else step < procs_map[arrived_task].deadline
                if deadline_check:
                    procs_map[arrived_task].stats[3].append(f"\t[Step: {step}] Task {arrived_task} ready.")
                    ready_tasks.add(arrived_task)
                else:
                    procs_map[arrived_task].stats[3].append(f"\t[Step: {step}] Task {arrived_task} will not run.")

        running_task, execution_plan_indx =  edf_define_running_task( \
            running_task, ready_tasks, unforced_idle_times, execution_plan_start_d, step, procs_map, execution_plan_indx)

        # Check deadlines
        deadlined_start_tasks = deadline_start_map.get(step)
        deadlined_end_tasks = deadline_end_map.get(step)
        if deadline != "end" and deadlined_start_tasks:
            for deadlined_task in deadlined_start_tasks:
                if procs_map[deadlined_task].remaining_time == procs_map[deadlined_task].time_period and running_task != deadlined_task:
                    procs_map[deadlined_task].stats[3].append(f"\t[Step: {step}] Missed start deadline for {deadlined_task}.")
                    procs_map[deadlined_task].stats[0] += 1
                    tasks_to_process -= 1
                    ready_tasks.discard(deadlined_task)

        if deadline != "start" and deadlined_end_tasks:
            for deadlined_task in deadlined_end_tasks:
                if procs_map[deadlined_task].remaining_time != 0:
                    procs_map[deadlined_task].stats[3].append(f"\t[Step: {step}] Missed end deadline for {deadlined_task}.")
                    procs_map[deadlined_task].stats[0] += 1
                    tasks_to_process -= 1
                    if running_task == deadlined_task:
                        procs_map[running_task].stats[3].append(f"\t[Step: {step}] Task {procs_map[running_task].pid} killed.")
                        running_task = None
                        running_task, execution_plan_indx =  \
                            edf_define_running_task(running_task, ready_tasks, unforced_idle_times, execution_plan_start_d, step, procs_map, execution_plan_indx)
                    ready_tasks.discard(deadlined_task)
    
# procs_2 = [
#     Process("A", 130, 20, 110, 10),
#     Process("B", 40, 20, 20, 20),
#     Process("C", 60, 20, 50, 40),
#     Process("D", 100, 20, 90, 50),
#     Process("E", 80, 20, 70, 60)
# ]

def EDF_Periodic(tasks, procs, max_period=None):
    
    start = copy.deepcopy(tasks)

    #Esta seccion se utiliza para el caso en que no se asigna cpu se pueda aumentar los stats
    procs_copia = copy.deepcopy(procs)
    nueva_lista = []
    for p in procs_copia:
        nueva_lista.append(p.stats[1:])
         

    if max_period == None:
        max_period = max(task[1] for task in tasks)
    else:
        max_period = max_period

    for i in range(max_period):
        tasks = sorted(tasks, key=lambda s: (s[2], s[3]))

        #Flags utilizadas para llevar control de reinicio por periodos
        flags = [0] * len(tasks)

        for proc in procs:
            proc.stats[2] += 1
            proc.stats[3].append(f"Iter {i+1}:\n")

        ''' #VERSION vieja de stats
        #Inicia aumentador de stats en caso de ser necesario
        procs_lista = []
        for p in procs:
            procs_lista.append(p.stats[1:])
        
        if nueva_lista == procs_lista and (i+1) != 1:
            for proc in procs:
                proc.stats[2] += 1
            procs_copia = copy.deepcopy(procs)
            nueva_lista = []
            for p in procs_copia:
                nueva_lista.append(p.stats[1:])
        else:
            procs_copia = copy.deepcopy(procs)
            nueva_lista = []
            for p in procs_copia:
                nueva_lista.append(p.stats[1:])
        #Final de aumentador de stads
        '''      
        print('')
        print(f'------- Iter:  {i+1} -------')

        #print(tasks)
        for task in tasks:

            if task[2]+1 <= i+1:
                if task[2]+1 == (i+1) and task[3] > 0:
                    #print(f'La tarea {task} no cumple con el deadline')
                    print(f"Deadline Miss. Pid: {task[0]}, rem: {task[3]}")
                    for proc in procs:
                        if proc.pid == task[0]:
                            proc.stats[0] += 1
                            proc.stats[3][i] += f"        Deadline miss with {proc.remaining_time} time remaining\n"


                    for x, t in enumerate(tasks):
                        if task == t:
                            if (i + 1) % t[1] == 0:
                                if flags[t[0]-1] == 0:
                                    #print(f'El proceso {t} se esta iniciando nuevamente por su periodo')
                                    print(f'Initializing process by period: Pid: {t[0]}')
                                    for proc in procs:
                                        if proc.pid == task[0]:
                                            proc.stats[3][i] += f"        Initializing process\n"
                                    flags[t[0]-1] = 1
                                    task[2] += task[1]
                                    for p, row in enumerate(start):
                                        if t[1] == row[1]:
                                            tasks[x][3] = start[p][3]
                    continue

                    
                if (i+1) % task[1] == 0:                        
                    for x, t in enumerate(tasks):
                        if task == t:
                            if flags[t[0]-1] == 0:
                                #print(f'El proceso {t} se esta iniciando nuevamente por su periodo')
                                print(f'Initializing process by period: Pid: {t[0]}')
                                for proc in procs:
                                    if proc.pid == task[0]:
                                        proc.stats[3][i] += f"        Initializing process\n"
                                flags[t[0]-1] = 1
                                task[2] += task[1]
                                for p, row in enumerate(start):
                                    if t[1] == row[1]:
                                        tasks[x][3] = start[p][3]
                continue
            
            if task[3] > 0:
                #print(f'Tarea {task}')
                print(f'(PID: {task[0]}, deadline: {task[2]}, time period: {task[1]}), remaining time: {task[3]}')
                task[3] -= 1
                
                if task[3] == 0:
                    task[2] += task[1]
                
                print(f'Giving CPU to pid: {task[0]}, rem: {task[3]}')
                
                for proc in procs:
                        if proc.pid == task[0]:
                            proc.stats[1] += 1
                            proc.stats[2] -= 1
                            proc.stats[3][i] += f"        Running on CPU\n"
                            if task[3] == 0:
                                proc.stats[3][i] += f"        Finished execution\n"
                        else:
                            proc.stats[3][i] += f"        Waiting for CPU\n"

    
                '''
                for proc in procs:
                        if proc.pid == task[0]:
                            proc.stats[1] += 1
                            #proc.stats[3][i+1] = "x"
                for proc in procs:
                        if proc.pid != task[0]:
                            proc.stats[2] += 1
                ''' 
                
                for x, t in enumerate(tasks):
                    if (i + 1) % t[1] == 0 and t[3]==0:
                        if flags[t[0]-1] == 0:
                            #tiene t[3]==0 porque sumo en el if anterior
                            #print(f'El proceso {t} se esta iniciando nuevamente por su periodo')
                            print(f'Initializing process by period: Pid: {t[0]}')
                            for proc in procs:
                                if proc.pid == t[0]:
                                    proc.stats[3][i] += f"        Initializing process\n"
                            flags[t[0]-1] = 1
                            for p, row in enumerate(start):
                                if t[1] == row[1]:
                                    tasks[x][3] = start[p][3]
                    
                    elif (i + 1) % t[1] == 0 :
                        if flags[t[0]-1] == 0:
                            #esto se coloca porque si alguien mas se debia reiniciar al haber un break lo mataria antes de hacerlo
                            #print(f'El proceso {t} se esta iniciando nuevamente por su periodo')
                            print(f'Initializing process by period: Pid: {t[0]}')
                            for proc in procs:
                                if proc.pid == t[0]:
                                    proc.stats[3][i] += f"        Initializing process\n"
                            flags[t[0]-1] = 1
                            t[2] += t[1]
                            for p, row in enumerate(start):
                                if t[1] == row[1]:
                                    tasks[x][3] = start[p][3]
                #print(f'Las tareas luego de iterar> {tasks}')'''
                break

            if max(task[3] for task in tasks) == 0:
                for x, t in enumerate(tasks):
                    if (i + 1) % t[1] == 0:
                        if flags[t[0]-1] == 0:
                            #print(f'El proceso {t} se esta iniciando nuevamente por su periodo')
                            print(f'Initializing process by period: Pid: {t[0]}')
                            for proc in procs:
                                if proc.pid == t[0]:
                                    proc.stats[3][i] += f"        Initializing process\n"
                            flags[t[0]-1] = 1
                            for p, row in enumerate(start):
                                if t[1] == row[1]:
                                    tasks[x][3] = start[p][3]
                    else:
                        for proc in procs:
                            if proc.pid == t[0]:
                                proc.stats[3][i] += f"        Waiting to reinitialize\n"
                tasks.sort(key=lambda x: x[2])
                '''
                for proc in procs:
                    proc.stats[2] += 1
                '''
                break

            if (i+1) % task[1] == 0:                        
                for x, t in enumerate(tasks):
                    if task == t:
                        if flags[t[0]-1] == 0:
                            #print(f'El proceso {t} se esta iniciando nuevamente por su periodo')
                            print(f'Initializing process by period: Pid: {t[0]}')
                            for proc in procs:
                                if proc.pid == t[0]:
                                    proc.stats[3][i] += f"        Initializing process\n"
                            flags[t[0]-1] = 1
                            for p, row in enumerate(start):
                                if t[1] == row[1]:
                                    tasks[x][3] = start[p][3]
        #print(tasks)

'''
#Ejemplo
tasks = [["Tarea 1", 20, 7, 3],   # (nombre, periodo, deadline, tiempo de ejecución)
         ["Tarea 2", 7, 4, 3],
         ["Tarea 3", 10, 8, 5]]
'''

#EDF_Periodic(tasks)
#edf_aperiodic(procs_2, deadline="start", unforced_idle_times=True)        
#rate_monotonic_scheduling(procs)

def configure_system(argv):
    print("Configuración del sistema:")
    # Alg selection
    t = -1
    arg_index = (argv.index('-a') if '-a' in argv else False)
    if arg_index:
        alg = argv[arg_index + 1]
        arg_index = None
        if not((alg == ('RMS')) or (alg == ('EDF-p')) or (alg == ('EDF-a'))):
            print("El algoritmo no es válido")
            sys.exit()
    else:
        while True:
            alg = str(input("Ingrese el algoritmo que desea utilizar (RMS, EDF-p, EDF-a): "))
            if alg == ('RMS') or alg == ('EDF-p') or alg == ('EDF-a'):
                break
            else:
                print("El algoritmo no es válido")
    alg_subtype_deadline = "end"
    if alg == ("EDF-a"):
        while True:
            alg_subtype_deadline = str(input("Deadline a usar (end, start, both): "))
            if alg_subtype_deadline == ('end') or alg_subtype_deadline == ('start') or alg_subtype_deadline == ('both'):
                break
            else:
                print("El tipo de deadline no es válido")

    unforced_idle_times = 0
    if alg == ("EDF-a"):
        unforced_idle_times = int(input("Unforced idle times? (1/0): "))
        
    # Proc input
    arg_index = (argv.index('-i') if '-i' in argv else False)
    if arg_index:
        path = argv[arg_index + 1]
        arg_index = None
        procs = read_input_file(path, alg)
    else:
        use_proc_file = int(input("Desea leer procesos de un archivo? (1/0): "))
        if use_proc_file:
            procs = read_input_file(str(input("Ingrese el nombre del archivo: ")), alg)
        else:
            procs = []
            proc_count = 0
            while True:
                flag = int(input("Desea agregar un proceso? (1/0): "))
                proc_count += 1
                if flag:
                    if alg == ("RMS"):
                        d = int(input("Ingrese el deadline del proceso: "))
                        t = int(input("Ingrese el tiempo de ejecución del proceso: "))
                        procs.append(Process(proc_count,0 ,d, t))
                    elif alg == ("EDF-p"):
                        p = int(input("Ingrese el periodo del proceso: "))
                        d = int(input("Ingrese el deadline del proceso: "))
                        t = int(input("Ingrese el tiempo de ejecución del proceso: "))
                        procs.append(Process(proc_count,p, d, t))
                    else: # EDF-a
                        a = int(input("Ingrese el tiempo de llegada del proceso: "))
                        t = int(input("Ingrese el tiempo de ejecución del proceso: "))
                        d_s = -1
                        d_e = -1
                        if alg_subtype_deadline == "start":
                            d_s = int(input("Ingrese el deadline de inicio del proceso: "))
                        elif alg_subtype_deadline == "end":
                            d_e = int(input("Ingrese el deadline de fin del proceso: "))
                        else:
                            d_s = int(input("Ingrese el deadline de inicio del proceso: "))
                            d_e = int(input("Ingrese el deadline de fin del proceso: "))
                        procs.append(Process(proc_count, 0, d_e, t, d_s, a))
                    print ("Proceso creado.")
                else:
                    break
    # Sim time
    arg_index = (argv.index('-t') if '-t' in argv else False)
    if arg_index:
        t = int(argv[arg_index + 1])
        arg_index = None
    else:
        if alg != ("EDF-a"):
            try:
                t = int(input("Ingrese el número de iteraciones que desea simular: "))
            except ValueError:
                t = 20

    # Output
    output_file = 0
    arg_index = (argv.index('-o') if '-o' in argv else False)
    if arg_index:
        output_file = argv[arg_index + 1]
        arg_index = None
    else:
        use_out_file = int(input("Desea escribir la salida en un archivo? (1/0): "))
        if use_out_file:
            # later we will use if output_file: ta ta ta.
            output_file = str(input("Ingrese el nombre del archivo: "))
    timeline = 0

    # timeline output
    arg_index = (argv.index('-tl') if '-tl' in argv else False)
    if arg_index:
        timeline = int(argv[arg_index + 1])
        arg_index = None
    else:
        timeline = int(input("Desea imprimir el timeline de cada proceso? (1/0): "))
    return (procs, alg, t, output_file, timeline, alg_subtype_deadline, unforced_idle_times)

def read_input_file(path, alg):
    procs = []
    if (os.path.isfile('./'+path)):
        f = open(path, "r")
        while True:
            line = f.readline().strip().split(',')
            #print(line)
            if  len(line) < 2:
                break
            line = [int(i) for i in line] # str to int
            if alg == ("RMS"):
                procs.append(Process(line[0],0,line[1],line[2]))
            elif alg == ("EDF-p"):
                procs.append(Process(line[0],line[1],line[2],line[3]))
            else: #EDF-a
                procs.append(Process(line[0],0,line[1],line[2],line[3],line[4]))
    else:
        print('No se encontró el archivo')
    return procs

def main():
    procs, alg, t, output_file, timeline, deadline_edf_a, unforced_idle_time = configure_system(sys.argv)
    if alg == 'RMS':
        rate_monotonic_scheduling(procs, t)

    elif alg == ("EDF-p"):
        tasks = []
        for proc in procs:
            tasks.append([proc.pid, proc.period, proc.deadline, proc.remaining_time])
        EDF_Periodic(tasks, procs, t)

    else: #EDF-a
        edf_aperiodic(procs, deadline_edf_a, unforced_idle_time)
    
    if output_file:
        f = open(output_file, "w")
        f.write("------- Stats -------\n")
        for proc in procs:
                f.write(f'''Proc {proc.pid}:
Deadline misses:       {proc.stats[0]}
Scheduled periods:     {proc.stats[1]} ({round(proc.stats[1]/t*100,2)} %)
Not-scheduled periods: {proc.stats[2]} ({round(proc.stats[2]/t*100,2)} %)\n''')
                if timeline:
                    f.write(("-------- Timeline --------\n"))
                    for iter in proc.stats[3]:
                        f.write(f"{iter}")
                f.write("---------------------\n")
#{"Timeline: " + str(proc.stats[3])[:].strip() if timeline else ""}\n---------------------\n''')
    # Print stats
    else:
        print("------- Stats -------")
        for proc in procs:
            print(f'''Proc {proc.pid}:
Deadline misses:       {proc.stats[0]}
Scheduled periods:     {proc.stats[1]} ({round(proc.stats[1]/t*100,2)} %)
Not-scheduled periods: {proc.stats[2]} ({round(proc.stats[2]/t*100,2)} %)\n''')
            if timeline:
                print("-------- Timeline --------\n")
                for iter in proc.stats[3]:
                    print(f"{iter}")
            print("---------------------\n")

#{"Timeline: " + str(proc.stats[3])[:].split(',') if timeline else ""}\n---------------------\n''')

if __name__ == "__main__":
    main()
