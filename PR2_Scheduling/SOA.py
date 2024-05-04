import copy

class Process:
    def __init__(self, pid, deadline, time_period):
        self.pid = pid
        self.time_period = time_period
        self.deadline = deadline
        self.remaining_time = time_period

def print_procs(procs):
    for proc in procs:
        print(f"(PID: {proc.pid}, deadline: {proc.deadline}, time period: {proc.time_period}), remaining time: {proc.remaining_time}")  
    
procs = [Process(1,4,1),Process(2,5,2),Process(3,7,2)]
#print_procs(procs)

# procs: list of processes, each a tuple (or dict) of (ID, time_period, deadline, time_remaining)
def rate_monotonic_scheduling(procs, steps = 15):
    # simulate
    for i in range(steps):
        print("------- Iter: ", i, "-------")
        # get deadline misses
        for proc in procs:
            if i > 0 and i % proc.deadline == 0:
                if proc.remaining_time > 0: 
                    # TODO: log deadline miss.
                    print(f"Deadline Miss. Pid: {proc.pid}, rem: {proc.remaining_time}")
                # reset procs
                proc.remaining_time = proc.time_period
                #print_procs([proc])

        # schedule proc
        unfinished_procs = [proc for proc in procs if proc.remaining_time > 0]
        print_procs(unfinished_procs)
        if unfinished_procs:
            # (shortest time_period first)    
            current_proc = min(unfinished_procs, key=lambda x: x.time_period)
            current_proc.remaining_time -= 1
            print(f"Giving CPU to pid: {current_proc.pid}, rem: {current_proc.remaining_time}")

def EDF_Periodic(tasks):
    
    start = copy.deepcopy(tasks)
    max_period = max(task[1] for task in tasks)


    for i in range(max_period):
        tasks = sorted(tasks, key=lambda s: abs((i + 1)  - s[2]))

        print(f'Iteracion {i+1}')
        for task in tasks:

            if task[2] < i+1:
                print(f'La tarea {task} no cumple con el deadline')

                for x, t in enumerate(tasks):
                    if task == t:
                        if (i + 1) % t[1] == 0:
                            print(f'El proceso {t} se esta iniciando nuevamente por su periodo')
                            task[2] += task[1]
                            for p, row in enumerate(start):
                                if t[1] == row[1]:
                                    tasks[x][3] = start[p][3]
                continue
            
            if task[3] > 0:
                print(f'Tarea {task}')
                task[3] -= 1
                
                if task[3] == 0:
                    task[2] += task[1]
                    
                for x, t in enumerate(tasks):
                    if (i + 1) % t[1] == 0 and t[3] == 0:
                        print(f'El proceso {t} se esta iniciando nuevamente por su periodo')
                        for p, row in enumerate(start):
                            if t[1] == row[1]:
                                tasks[x][3] = start[p][3]
                print(f'Las tareas luego de iterar> {tasks}')
                break

            if max(task[3] for task in tasks) == 0:
                for x, t in enumerate(tasks):
                    if (i + 1) % t[1] == 0:
                        print(f'El proceso {t} se esta iniciando nuevamente por su periodo')
                        for p, row in enumerate(start):
                            if t[1] == row[1]:
                                tasks[x][3] = start[p][3]
                tasks.sort(key=lambda x: x[2])
                break

            if (i+1) % task[1] == 0:                        
                for x, t in enumerate(tasks):
                    if task == t:
                        print(f'El proceso {t} se esta iniciando nuevamente por su periodo')
                        for p, row in enumerate(start):
                            if t[1] == row[1]:
                                tasks[x][3] = start[p][3]

    print("Todas las tareas han sido completadas.")



tasks = [["Tarea 1", 20, 7, 3],   # (nombre, periodo, deadline, tiempo de ejecución)
         ["Tarea 2", 5, 4, 2],
         ["Tarea 3", 10, 8, 2]]

EDF_Periodic(tasks)



        
#rate_monotonic_scheduling(procs)

