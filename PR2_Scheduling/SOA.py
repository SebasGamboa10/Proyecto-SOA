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
# sched_time = LCM of the time period of all procs. #TODO: verificar con el prof.
def rate_monotonic_scheduling(procs, sched_time = None, steps = 15):
    active_procs = []
    
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
        # (shortest time_period first)
        unfinished_procs = [proc for proc in procs if proc.remaining_time > 0]
        print_procs(unfinished_procs)
        if unfinished_procs:    
            current_proc = min(unfinished_procs, key=lambda x: x.time_period)
            current_proc.remaining_time -= 1
            print(f"Giving CPU to pid: {current_proc.pid}, rem: {current_proc.remaining_time}")
        
rate_monotonic_scheduling(procs)

