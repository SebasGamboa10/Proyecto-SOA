from functools import cmp_to_key
import copy
import sys
import os.path

class CPU:
    def __init__(self, id, refs=[]):
        self.id = id
        self.pages = []
        self.arrival_times = [] # indexed in the same order as pages.]
        self.page_indexes = []
        #self.invalid_pages = []
        self.stats = [0,0,0] # page-faults, hits, invalidations 
        self.refs = refs # all future refs/ check if this declaration is ok

    def ref(self, page, config, time, mode='w'):
        
        if config[1] == 'OPTIMAL' and len(self.refs) > 0:
            self.refs.pop(0)
        
        # system recovers page
        # Page Invalidations TODO: stats[2]
        repl = int(config[-2])
        if bool(repl) == False or (bool(repl) == True and mode=='w'):
            recover_page(self.id, page, config)
            if (self.id not in page_refs[page][0]):
                page_refs[page][0].append(self.id) # the page_refs_mode was set inside the recover page function.
            page_refs[page][1] = 'w' if mode == 'w' else 'r'
        else:
            if (self.id not in page_refs[page][0]):
                page_refs[page][0].append(self.id)
            page_refs[page][1] = 'r'

        # if page not in CPU
        if not page in self.pages:
            # stats page-fault
            self.stats[0] += 1
            # if theres space in CPU
            if len(self.pages) < config[-4]:
                self.pages.append(page)
                self.arrival_times.append(time) 
            # else use page replacement alg
            else:
                replace_page(self, page, config, time)

            # keep track of frame index
            # config[-3] = total pages
            for i in range(int(config[-3])):
                if i in self.page_indexes:
                    pass
                else:
                    self.page_indexes.append(i)
                    break
            #print(f'CPU: {self.id} page indexes: {self.page_indexes}')

        else:
            # stats hit
            self.stats[1] += 1
            self.arrival_times[self.pages.index(page)] = time
        output_info(f'page_refs = {page_refs}')
        output_info('-------------------------------')
    
    #TODO: STORE
        
# NO BORRAR
page_refs = [] # NO BORRAR 
OUTPUT_FILENAME = 0
IS_UI = False
# NO BORRAR
 
# System functions

def output_info(message, new = False):
    if int(OUTPUT_FILENAME) == 0:
        print(message)
    else:
        _type = "w" if new else "+a"
        with open(OUTPUT_FILENAME, _type) as file:
            file.write(f"{str(message)}\n")

def recover_page(cpu_id, page, config):
    # find page in CPUs
    #if replication == False or (replication == True and mode=='w'):
    for cpu in config[0]:
        if not cpu.id == cpu_id: 
            if page in cpu.pages:
                i = cpu.pages.index(page)

                # recover pages from cpu.
                cpu.pages.pop(i)
                cpu.arrival_times.pop(i)
                cpu.page_indexes.pop(i)

                # system refs
                page_refs[page][0] = [] # remove references to all CPUs that have this page loaded
                #page_refs[page][1] = 'w' # page is now in writing mode

                # stats
                cpu.stats[2] += 1
            

def replace_page(cpu, page, config, time):
    # replace page in CPU.
    if config[1] == 'FIFO':
        FIFO(cpu, page, time)
    elif config[1]  == 'LRU':
        LRU(cpu, page, time)
    elif config[1]  == 'OPTIMAL':
        optimal(cpu, page, time)

def FIFO(cpu, page, time):
    # system refs
    #page_refs[page_refs.index(cpu.pages[0])][0].remove(cpu.id)
    page_refs[(cpu.pages[0])][0].remove(cpu.id)
    if len(page_refs[(cpu.pages[0])][0]) == 0:
        page_refs[(cpu.pages[0])][1] = ''

    # remove first element
    cpu.pages.pop(0)
    cpu.arrival_times.pop(0)
    cpu.page_indexes.pop(0)

    # add new page at the end of the list
    cpu.pages.append(page)
    cpu.arrival_times.append(time)

def LRU(cpu, page, time):    
    # Find and remove least recently used page
    lru = cpu.arrival_times.index(min(cpu.arrival_times))
    
    # system refs
    #page_refs[page_refs.index(cpu.pages[lru])][0].remove(cpu.id)
    page_refs[(cpu.pages[lru])][0].remove(cpu.id)
    if len(page_refs[(cpu.pages[lru])][0]) == 0:
        page_refs[(cpu.pages[lru])][1] = ''

    cpu.pages.pop(lru)
    cpu.arrival_times.pop(lru)
    cpu.page_indexes.pop(lru)
                
    # add new element at the end of the list
    cpu.pages.append(page)
    cpu.arrival_times.append(time)

def optimal(cpu, page, time):
    # find the page that won't be used for the longest period of time
    ref_times = []
    replaced = False

    for ref in range(len(cpu.refs)):
        cpu.refs[ref] = int(cpu.refs[ref])
    output_info(f'OPTIMAL: {cpu.refs}')

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
            #page_refs[page_refs.index(cpu.pages.index(page_aux))][0].remove(cpu.id)
            page_refs[page_aux][0].remove(cpu.id)
            if len(page_refs[page_aux][0]) == 0:
                page_refs[(page_aux)][1] = ''
            
            cpu.arrival_times.pop(cpu.pages.index(page_aux))
            cpu.page_indexes.pop(cpu.pages.index(page_aux))
            cpu.pages.remove(page_aux)
                
            # add new page
            cpu.pages.append(page)
            cpu.arrival_times.append(time)
            break
    
    if replaced == False:
        # remove page 
        #index = ref_times.index(max(ref_times))s
        #index = ref_times[max(ref_times)] 
        index = cpu.refs[max(ref_times)] # index es una página!! no un índice.
        output_info(f'ref_times = {ref_times}')
        # system refs

        #page_refs[page_refs.index(cpu.pages[index])][0].remove(cpu.id)
        #page_refs[page_refs.index(ref_times[index])][0].remove(cpu.id)
        page_refs[index][0].remove(cpu.id)
        if len(page_refs[page_aux][0]) == 0:
            page_refs[(page_aux)][1] = ''

        #cpu.arrival_times.pop(index)
        #cpu.arrival_times.pop(cpu.pages.index(ref_times[index]))
        cpu.arrival_times.pop(cpu.pages.index(index))
        cpu.page_indexes.pop(cpu.pages.index(index))
        #cpu.pages.remove(ref_times[index])
        cpu.pages.remove(index)
        #cpu.pages.pop(index)
        # add new page
        cpu.pages.append(page)
        cpu.arrival_times.append(time)
            
def print_cpus(cpus):
    for cpu in cpus:
        page_indexes = ""
        if IS_UI:
            page_indexes = f", page_indexes: {cpu.page_indexes}"
        output_info(f"(ID: {cpu.id}, pages: {cpu.pages}, arrival times: {cpu.arrival_times}{page_indexes}), stats: {cpu.stats}")  
    
### TODO: Config system and read from file.

def configure_system(argv):

    print("Configuración del sistema:")

    # total pages
    total_pages = 0
    pages_per_node = 0

    cpus = []
    
    if ('--ui' in argv):
        # total pages
        if ('-p' in argv):
            total_pages = int(argv[argv.index('-p') + 1])
        # pages_per_node
        if ('-q' in argv):
            pages_per_node = int(argv[argv.index('-q') + 1])
        # pages_per_node
        if ('-n' in argv):
            total_cpus = int(argv[argv.index('-n') + 1])
            for i in range(total_cpus):
                cpus.append(CPU(i))


    if (not '-i' in argv and '--ui' not in argv):
        total_pages = int(input("Ingrese el número total de páginas del sistema: "))
        pages_per_node = int(input("Ingrese el número de frames por CPU: "))
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
    
    path = None
    arg_index = (argv.index('-i') if '-i' in argv else False)
    if arg_index:
        path = argv[arg_index + 1]
        arg_index = None
        #cpus = read_input_file(path, alg)
    else:
        use_input_file = int(input("Desea leer procesos de un archivo? (1/0): "))
        if use_input_file:
            path = input("Ingrese el nombre del archivo: ")
            #cpus = read_input_file(str(input("Ingrese el nombre del archivo: ")), alg)
        else:
            while True:
                flag = int(input("Desea agregar un cpu? (1/0): "))
                if flag:
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
        d = argv[arg_index + 1]
        arg_index = None
    else:
        d = int(input("Desea replicación?: "))
        

    return (cpus, alg, output_file, pages_per_node, total_pages, d, path)

def get_total_refs_from_file(path, config, IS_UI):
    total_refs = []
    filepath = './'+path if not IS_UI else path
    if (os.path.isfile(filepath)):
        f = open(path, "r")
        line = f.readline().strip().split(',')
        cpu_count = int(line[-1]) if not IS_UI else len(config[0])
        total_pages = int(line[0]) if not IS_UI else config[-3]
        pages_per_node = int(line[1]) if not IS_UI else config[-4]
        for i in range(cpu_count):
            total_refs.append([])
        while True:
            line = f.readline().strip().split(',')
            if len(line) < 2:
                break
            total_refs[int(line[0])].append(line[1])
    return total_refs, total_pages, pages_per_node


def read_input_file(config, time):
    filepath = './'+config[-1] if not IS_UI else config[-1]
    if (os.path.isfile(filepath)):
        f = open(config[-1], "r")
        line = f.readline() # to ignore config line
        while True:
            #line = f.readline().strip().split(',')
            #print(line)
            line = f.readline().strip()
            if len(line.split(',')) < 2:
                break
            #line = [int(i) for i in line] # str to int
            step(config,line,time)
            time += 1
            # llamar ref del CPU correcto.
            #procs.append(Process(line[0],0,line[1],line[2]))
    else:
        print(f'No se encontró el archivo')
    #return procs

def print_help():
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


def step(config, string, time):
    split_string = string.split(',') # [cpu.id, page, mode]
    # find cpu.id in global cpus
    for cpu in config[0]:
        if cpu.id == int(split_string[0]):
            cpu.ref(int(split_string[1]), config, time, split_string[2])

    print_cpus(config[0])

def main(argv=None):
    # help
    if '-h' in sys.argv: 
        print_help()
        sys.exit()

    global IS_UI
    IS_UI = '--ui' in sys.argv
    
    time = 0
    # get args from terminal or GUI
    #print(argv)
    if argv:
        cpus = configure_system(argv)
    else:
        config = configure_system(sys.argv)
        global OUTPUT_FILENAME 
        OUTPUT_FILENAME = config[2]
        output_info(config, True)
        print(config)
        # if using input file
        if config[-1]:
            # create ref list. list of lists for each cpu and ref.
            if config[1] == 'OPTIMAL':
                total_refs, total_pages, pages_per_node = get_total_refs_from_file(config[-1], config, IS_UI)
                config = list(config)
                config[-3] = total_pages
                config[-4] = pages_per_node
                # create cpus
                cpus = []
                for i in range(len(total_refs)):
                    cpus.append(CPU(i,total_refs[i]))
                config[0] = cpus

            #page_refs = [] 
            for i in range(int(config[-3])):
                page_refs.append([[], ''])
            # run simulation
            read_input_file(config,time)
        else:
            # create pages.
            pages_refs = [] 
            for i in range(int(config[-3])):
                page_refs.append([[], ''])
            while True:
                string = input("Ingrese la referencia que desea simular o 0 para finalizar. (formato: <CPU id>,<page>,<mode>)")
                if string == '0':
                    break
                else:
                    step(config, string, time)
                    time += 1
    
    #if output_file:
        



if __name__ == "__main__":
    main()
