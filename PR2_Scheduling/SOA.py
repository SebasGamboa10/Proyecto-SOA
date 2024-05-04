from functools import cmp_to_key
import copy

class Process:
    def __init__(self, pid, deadline, time_period, deadline_start=-1, arrival_time=-1):
        self.pid = pid
        self.time_period = time_period
        self.deadline = deadline
        self.remaining_time = time_period
        self.deadline_start = deadline_start
        self.arrival_time = arrival_time

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
                print(f"[Step: {step}] Task {procs_map[running_task].pid} assigned to CPU.")
        else:
            earliest_deadline = get_earliest_deadline(procs_map, ready_tasks)
            running_task = earliest_deadline[1]
            ready_tasks.discard(running_task)
            print(f"[Step: {step}] Task {procs_map[running_task].pid} assigned to CPU.")
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
                print(f"[Step: {step}] Task {procs_map[running_task].pid} finished.")
                running_task = None
                if tasks_to_process == 0:
                    continue
                    
        arrived_tasks = arrival_map.get(step)
        if arrived_tasks:
            for arrived_task in  arrived_tasks:
                print(f"[Step: {step}] Arrived task: {arrived_task}")
                deadline_check = step <= procs_map[arrived_task].deadline_start if deadline != "end" else step < procs_map[arrived_task].deadline
                if deadline_check:
                    print(f"[Step: {step}] Task {arrived_task} ready.")
                    ready_tasks.add(arrived_task)
                else:
                    print(f"[Step: {step}] Task {arrived_task} will not run.")

        running_task, execution_plan_indx =  edf_define_running_task( \
            running_task, ready_tasks, unforced_idle_times, execution_plan_start_d, step, procs_map, execution_plan_indx)

        # Check deadlines
        deadlined_start_tasks = deadline_start_map.get(step)
        deadlined_end_tasks = deadline_end_map.get(step)
        if deadline != "end" and deadlined_start_tasks:
            for deadlined_task in deadlined_start_tasks:
                if procs_map[deadlined_task].remaining_time == procs_map[deadlined_task].time_period and running_task != deadlined_task:
                    print(f"[Step: {step}] Missed deadline for {deadlined_task}.")
                    tasks_to_process -= 1
                    ready_tasks.discard(deadlined_task)

        if deadline != "start" and deadlined_end_tasks:
            for deadlined_task in deadlined_end_tasks:
                if procs_map[deadlined_task].remaining_time != 0:
                    print(f"[Step: {step}] Missed end deadline for {deadlined_task}.")
                    tasks_to_process -= 1
                    if running_task == deadlined_task:
                        print(f"[Step: {step}] Task {procs_map[running_task].pid} killed.")
                        running_task = None
                        running_task, execution_plan_indx =  \
                            edf_define_running_task(running_task, ready_tasks, unforced_idle_times, execution_plan_start_d, step, procs_map, execution_plan_indx)
                    ready_tasks.discard(deadlined_task)
    
procs_2 = [
    Process("A", 130, 20, 110, 10),
    Process("B", 40, 20, 20, 20),
    Process("C", 60, 20, 50, 40),
    Process("D", 100, 20, 90, 50),
    Process("E", 80, 20, 70, 60)
]

edf_aperiodic(procs_2, deadline="start", unforced_idle_times=True)
# rate_monotonic_scheduling(procs)

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

