from functools import cmp_to_key
import copy
import sys
import os.path

class CPU:
    def __init__(self, id):
        self.id = id
        self.pages = []
        self.arrival_times = [] # indexed in the same order as pages.]
        #self.invalid_pages = []
        self.stats = [0,0,0] # page-faults, hits, invalidations 
        self.refs = [[]] # all future refs/ check if this declaration is ok

    # COMENTARIO PARA MIS BROSKIS: Esto del mode no sé si va a existir o si write es hacer STORE
    def load(self, page, mode='w'):
        # system recovers page
        # CPU comunica a otros CPU que invaliden sus copias locales de la página y espera confirmación. 
        if replication == False or (replication == True and mode=='w'):
            recover_page(page)
            page_refs[page_refs.index(page)][0].append(self.id) # the page_refs_mode was set inside the recover page function.
        else:
            page_refs[page_refs.index(page)][0].append(self.id)
            page_refs[page_refs.index(page)][1] = 'r'

        # if page not in CPU
        if not page in self.pages:
            # stats page-fault
            self.stats[0] += 1
            # if theres space in CPU
            if len(self.pages) < pages_per_node:
                self.pages.append(page)
                self.arrival_times.append(time)
            
            # else use page replacement alg
            else:
                replace_page(self, page)
        else:
            # stats hit
            self.stats[1] += 1
    
    #TODO: STORE
        
# Globals -> move to config?
cpus = []
pages = []
time = 0
alg = 'FIFO'
replication = False
page_refs = [] # [3],id,[w] # aunque el id lo podemos sacar del indice y ya
pages_per_node = 0
 
# System functions

def recover_page(page):
    # find page in CPUs
    #if replication == False or (replication == True and mode=='w'):
    for cpu in cpus:
        if page in cpu.pages:
            i = cpu.pages.index(page)
            # TODO: STORE o solo pop??
            # recover pages from cpu.
            cpu.pages.pop(i)
            cpu.arrival_times.pop(i)

            # system refs
            page_refs[page_refs.index(page)][0] = [] # remove references to all CPUs that have this page loaded
            page_refs[page_refs.index(page)][1] = 'w' # page is now in writing mode
            

def replace_page(cpu, page):
    # replace page in CPU.
    if cpu.config.alg == 'FIFO':
        FIFO(cpu, page)
    elif cpu.config.alg == 'LRU':
        LRU(cpu, page)
    elif cpu.config.alg == 'optimal':
        optimal(cpu, page)

def FIFO(cpu, page):
    # system refs
    page_refs[page_refs.index(cpu.pages[0])][0].remove(cpu.id)

    # remove first element
    cpu.pages.pop(0)
    cpu.arrival_times.pop(0)

    # add new page at the end of the list
    cpu.pages.append(page)
    cpu.arrival_times.append(time)

def LRU(cpu, page):    
    # Find and remove least recently used page
    lru = cpu.arrival_times.index(min(cpu.arrival_times))
    
    # system refs
    page_refs[page_refs.index(cpu.pages[lru])][0].remove(cpu.id)
    
    cpu.pages.pop(lru)
    cpu.arrival_times.pop(lru)

    # add new element at the end of the list
    cpu.pages.append(page)
    cpu.arrival_times.append(time)

def optimal(cpu, page):
    # find the page that won't be used for the longest period of time
    ref_times = []
    replaced = False
    for page_aux in cpu.pages:
        # if the page will be referenced again
        if page_aux in cpu.refs:
            # record when the page will be referenced next
            ref_times.append(cpu.refs.index(page_aux))
        
        # else remove that page
        elif replaced == False:
            # remove page that won't be used again
            replaced = True

            # system refs
            page_refs[page_refs.index(cpu.pages.index(page_aux))][0].remove(cpu.id)

            cpu.arrival_times.remove(cpu.pages.index(page_aux))
            cpu.pages.remove(page_aux)
            # add new page
            cpu.pages.append(page)
            cpu.arrival_times.append(time)
            break

    if replaced == False:
        # remove page
        index = ref_times.index(max(ref_times))
        # system refs
        page_refs[page_refs.index(cpu.pages[index])][0].remove(cpu.id)

        cpu.arrival_times.pop(index)
        cpu.pages.pop(index)
        # add new page
        cpu.pages.append(page)
        cpu.arrival_times.append(time)
            
def print_cpus(cpus):
    for cpu in cpus:
        print(f"(ID: {cpu.id}, pages: {cpu.pages}, arrival times: {cpu.arrival_times}), stats: {cpu.stats}")  
    
### TODO: Config system and read from file.

def configure_system(argv):

    print("Configuración del sistema:")
    # Alg selection
    arg_index = (argv.index('-a') if '-a' in argv else False)
    if arg_index:
        alg = argv[arg_index + 1]
        arg_index = None
        if not((alg == ('FIFO')) or (alg == ('LRU')) or (alg == ('OPTIMAL'))):
            print("El algoritmo no es válido")
            sys.exit()
    else:
        while True:
            alg = str(input("Ingrese el algoritmo que desea utilizar (FIFO, LRU, OPTIMAL): "))
            if alg == ('FIFO') or alg == ('LRU') or alg == ('OPTIMAL'):
                break
            else:
                print("El algoritmo no es válido")

    '''

    arg_index = (argv.index('-s') if '-s' in argv else False)
    alg_subtype_deadline = "end"
    if alg == ("EDF-a"):
        if arg_index:
            alg_subtype_deadline = argv[arg_index + 1]
            arg_index = None
            if alg_subtype_deadline == ('end') or alg_subtype_deadline == ('start') or alg_subtype_deadline == ('both'):
                pass
            else:
                print("El tipo de deadline no es válido")
                sys.exit()
        else:
            while True:
                alg_subtype_deadline = str(input("Deadline a usar (end, start, both): "))
                if alg_subtype_deadline == ('end') or alg_subtype_deadline == ('start') or alg_subtype_deadline == ('both'):
                    break
                else:
                    print("El tipo de deadline no es válido")


    arg_index = (argv.index('-u') if '-u' in argv else False)
    unforced_idle_times = 0
    if alg == ("EDF-a"):
        if arg_index:
            unforced_idle_times = int(argv[arg_index + 1])
            arg_index = None
        else:
            unforced_idle_times = int(input("Unforced idle times? (1/0): "))
        
    '''
    
    # Proc input
    arg_index = (argv.index('-i') if '-i' in argv else False)
    if arg_index:
        path = argv[arg_index + 1]
        arg_index = None
        cpus = read_input_file(path, alg)
    else:
        use_proc_file = int(input("Desea leer procesos de un archivo? (1/0): "))
        if use_proc_file:
            cpus = read_input_file(str(input("Ingrese el nombre del archivo: ")), alg)
        else:
            cpus = []
            while True:
                flag = int(input("Desea agregar un proceso? (1/0): "))
                if flag:
                    if alg == ("FIFO"):
                        id = int(input("Ingrese el id del cpu: "))
                        cpus.append(CPU(id))
                    elif alg == ("LRU"):
                        id = int(input("Ingrese el id del cpu: "))
                        cpus.append(CPU(id))
                    else: #optimo
                        id = int(input("Ingrese el id del cpu: "))
                        cpus.append(CPU(id))
                    print ("Configurado con exito.")
                else:
                    break

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

    # replication
    arg_index = (argv.index('-d') if '-d' in argv else False)
    if arg_index:
        #output_file = argv[arg_index + 1]
        #arg_index = None
    else:
        d = int(input("Desea replicación?: "))
        

    return (cpus, alg, output_file, d)

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

def main(argv=None):

    # help
    if '-h' in sys.argv: 
        print('''
------------              
Help: 
------------
Running the program from command line:
Run the program with the following line: python3 SOA.py -t iterations -a algorithm -i input_file -o output_file -tl show_timeline (-u unforced_idle_times -s deadline)
with: 
-t:  int (number of iterations to simulate)
-a:  str (algorithm to use (RMS, EDF-p or EDF-a))
-i:  str (path to input file to read processes)
     input file format: 
        for RMS:   PID, Deadline, Duration.
        for EDF-p: PID, Period, Deadline, Duration.
        for EDF-a: PID, End Deadline, Duration, Start Deadline, Arrival Time.
-o:  str (path to output file)
-tl: int (flag to show each process' timeline, input 1 to show, or 0 to ignore)
-s EDF-a ONLY: deadline [start, end, both]
-u EDF-a ONLY: unblocked idle times [1, 0]
------------              
Running the program from GUI:
Run the program with the following line: python3 window.py
------------  
              ''')
        sys.exit()
    
    # get args from terminal or GUI
    #print(argv)
    if argv:
        cpus = configure_system(argv)
    else:
        cpus = configure_system(sys.argv)
    

    
    if output_file:
        



if __name__ == "__main__":
    main()
