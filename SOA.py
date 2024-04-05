import sys
import os.path

processes = {}

class SystemConfiguration:
    def __init__(self, num_processes, message_queue_size, send_type, receive_type, addressing_type, confirmation_of_arrival, **kwargs):
        self.num_processes = num_processes
        self.message_queue_size = message_queue_size
        self.send_type = send_type
        self.receive_type = receive_type
        self.addressing_type = addressing_type
        self.confirmation_of_arrival = confirmation_of_arrival

class Message:
    def __init__(self, content, priority=0):
        self.content = content
        self.priority = priority

class Process:
    def __init__(self, name, pid, send_block, receive_block, config):
        self.name = name
        self.pid = pid
        self.send_block = send_block
        self.receive_block = receive_block
        self.message_queue = []
        self.log = {}
        self.log_queue = {}
        self.config = config

    def send_message(self, message, destination, blocking=None, priority=0):
        # validacion de tamano de colas
        if (len(self.message_queue) < self.config.message_queue_size):
            if blocking=="blocking":
                destination.receive_message_blocking(message, priority)
            else:
                destination.receive_message_nonblocking(message, priority)
        else:
            print(f'No hay espacio disponible en la cola para enviar mensaje {message}')
            self.log[max(self.log)] = self.log[max(self.log)] + " ERROR: COLA ESTABA LLENA"
            

    def receive_message_blocking(self, message=None, priority=0):
        #print(message)
        #if (len(self.message_queue) < self.config.message_queue_size):
        if message is not None:
            self.message_queue.append((message, priority))
        elif self.message_queue:
            self.message_queue.sort(key=lambda x: x[1], reverse=True)
            return self.message_queue.pop(0)[0]
        else:
            return None
        #else: 
        #    print(f"No hay espacio en cola disponible para enviar {message}")
        #    return None


    def receive_message_nonblocking(self, message=None, priority=0):
        #if (len(self.message_queue) < self.config.message_queue_size):
        if message:
            self.message_queue.append((message, priority))
        elif self.message_queue:
            self.message_queue.sort(key=lambda x: x[1], reverse=True)
            return self.message_queue.pop(0)[0]
        else:
            return "No hay mensajes disponibles"
        #else: 
        #    print(f"No hay espacio en cola disponible para enviar {message}")
        #    return self.message_queue.pop(0)



def create_process(name, pid, send_block, receive_block, config):
    return Process(name, pid, send_block, receive_block, config)

def display(processes):
    print("Estado del sistema:")
    for pid, proceso in processes.items():
        print('')
        print('--------------------------------------')
        print('--------------------------------------')
        print('--------Detalles del Proceso---------')
        print(f"ID del proceso: {pid}")
        print(f"Nombre del proceso: {proceso.name}")
        print(f"Send Blocking Estado Actual: {proceso.send_block}")
        print(f"Receive Blocking Estado Actual: {proceso.receive_block}")
        print('')
        print('--------Log del Proceso---------')
        #print(f"log: {proceso.log}")
        for key, value in proceso.log.items():
            print("Timestamp: {} | {}".format(key, value))
        print('')
        print('--------Cola del Proceso---------')
        for key, value in proceso.log_queue.items():
            print("Timestamp: {} | {}".format(key, value))
        print('')
        print('--------Cola Actual del Proceso---------')
        for message, priority in proceso.message_queue:
            print(f"Mensaje: {message} | Prioridad: {priority}")
        print('--------------------------------------')
        print('--------------------------------------')
        print('')


def configure_system():
    print("Configuración del sistema:")
    num_processes = int(input("Ingrese el número de procesos: "))
    message_queue_size = int(input("Ingrese el tamaño de la cola de mensajes: "))
    send_type = str(input("El send es blocking o nonblocking: "))
    receive_type = str(input("El receive es blocking o nonblocking: "))
    addressing_type = str(input("El direccionamiento es directo o indirecto: "))
    confirmation_of_arrival = bool(input("Desea que se requieran pruebas de llegada de mensajes? (digite 0 para NO y 1 para SI): ")) 

    return SystemConfiguration(num_processes, message_queue_size,send_type, receive_type, addressing_type, confirmation_of_arrival)

def main():
    while True:
        processes = {}
        time = 0
        batch = False
        #batch config
        if (len(sys.argv) == 2):
            if (os.path.isfile('./'+sys.argv[1])):
                f = open(sys.argv[1], "r")
                batch = True
            else: 
                print('El archivo batch no es válido, se ejecutará el programa en modo interactivo')
        
        if batch:
            line = f.readline().strip().split(',')
            config = SystemConfiguration(int(line[0]), int(line[1]), line[2], line[3], line[4], line[5])
        else:
            config = configure_system()

        # Create mailbox if required
        if (config.addressing_type == 'indirect' or config.addressing_type == 'i'):
            processes['mailbox'] = create_process('Mailbox', 'mailbox', send_block=None, receive_block=None, config=config)
        
        while True: 
            if batch:
                line = f.readline().strip().split(',')
                command = line[0]
            else:
                command = input("Ingrese un comando (create, send, receive), 'display' para ver el estado, 'reset' para resetear la configuración o 'exit' para salir: ")

            if command == "exit":
                exit()


            elif command == "create":
                if config.num_processes > len(processes): 
                    if batch:
                        name = line[1]
                        process_id = int(line[2])
                    else:
                        name = input("Ingrese el nombre del proceso: ")
                        process_id = input("Ingrese el ID del proceso: ")
                    
                    # validacion de existencia
                    if process_id  in processes:
                        print(f"Proceso {process_id} ya existe")
                    else:
                        send_block = None
                        receive_block = None

                        new_process = create_process(name, process_id, send_block, receive_block, config)
                        new_process.log[time] = 'Proceso creado'
                        processes[new_process.pid] = new_process
                else:
                    print("No es posible agregar procesos, se ha alcanzado el maximo")


            elif command == "send":
                if batch:
                    process_id_send = int(line[1])
                    process_id = int(line[2])
                else:    
                    process_id_send = input("Ingrese el ID del proceso envia el mensaje: ")
                    process_id = input("Ingrese el ID del proceso al que desea enviar el mensaje: ")
                if process_id_send not in processes:
                    print(f"Proceso {process_id_send} no existe")
                elif process_id not in processes:
                    print(f"Proceso {process_id} no existe")
                else:

                    send_block = processes[process_id_send].send_block
                    if processes[process_id_send].receive_block != True:
                        if send_block is False or send_block is None:
                            if batch:
                                message = line[3]
                                if (len(line) == 5):
                                    priority = line[4]
                                else: 
                                    priority = 0
                            else:
                                message = input("Ingrese el mensaje: ")
                                priority = input("Ingrese la prioridad donde 1 es alta y 0 baja: ")
                                message = f'{process_id_send}, {process_id}, ' + message
                            processes[process_id_send].log[time] =  'Envié mensaje {} a proc {}'.format(message, process_id)
                            processes[process_id].log_queue[time] = message
                            if config.send_type == 'blocking':
                                processes[process_id_send].send_block = True
                            #mailbox (explicit)
                            if (config.addressing_type == 'indirect' or config.addressing_type == 'i'):
                                # formato sender_id, rec_id, message
                                processes[process_id_send].send_message(f"{message}", processes['mailbox'], blocking=config.receive_type, priority=priority)
                                received_message = processes['mailbox'].receive_message_nonblocking()
                                processes['mailbox'].log[time] = 'Recibí mensaje {}'.format(received_message)
                                processes['mailbox'].log_queue[time] = received_message
                                ##
                                processes['mailbox'].send_message(f"{received_message}", processes[process_id], blocking=config.receive_type, priority=priority)
                                processes['mailbox'].log[time] = processes['mailbox'].log[time] + ". " + 'Envié mensaje {} a proc {}'.format(message, process_id) ##REVISAR LA IMPRESION
                                processes[process_id].log_queue[time] = received_message

                            # direct send
                            else:
                                processes[process_id_send].send_message(f"{message}", processes[process_id], blocking=config.receive_type, priority=priority)
                        else:
                            print("Actualmente el proceso tiene un envio activo que mantiene bloqueado")
                    else:
                        processes[process_id_send].log[time] =  'Se intentó hacer envió pero proceso está bloquedo por receive'
                        print("Actualmente el proceso se encuentra bloqueado por receive")



            elif command == "receive":
                if batch: 
                    process_id = int(line[1])
                else:
                    process_id = input("Ingrese el ID del proceso que recibe el mensaje: ")
                
                # validacion de existencia
                if process_id not in processes:
                    print(f"Proceso {process_id} no existe")
                else:
                
                    #FALTA VALIDAR DE QUIEN QUIERO RECIBIRLO
                    if config.receive_type == 'blocking':
                        received_message = processes[process_id].receive_message_blocking()
                        if received_message:
                            print(f"Process {process_id} recibió el mensaje: {received_message}")
                            processes[process_id].log[time] = 'Recibí mensaje {}'.format(received_message)
                            if ',' in received_message:
                                split = received_message.split(',')
                                process_id_send_extracted = split[0].strip()
                                if (config.confirmation_of_arrival):
                                    processes[process_id].send_message(f"Proceso {process_id} recibió mi mensaje", processes[process_id_send_extracted], blocking='nonblocking', priority=0)
                                    processes[process_id_send_extracted].receive_message_nonblocking()
                                    processes[process_id_send_extracted].log[time] = f'Proceso {process_id} Prueba de llegada'
                                    processes[process_id_send_extracted].log_queue[time] = f'Proceso {process_id} Prueba de llegada'
                                    processes[process_id].log[time] = processes[process_id].log[time] + ". " + f'Envié Prueba de llegada a  {process_id_send_extracted}'
                                processes[process_id_send_extracted].send_block = False
                                processes[process_id].receive_block = False
                        else:
                            processes[process_id].receive_block = True
                            print(f"Process {process_id} no recibió ningún mensaje.")
                            processes[process_id].log[time] =  f'Process {process_id} no recibió ningún mensaje --> Proceso bloquedo por receive'
                    # Non blocking
                    else:
                        received_message = processes[process_id].receive_message_nonblocking() 
                        if received_message:
                            print(f"Process {process_id} recibió el mensaje: {received_message}")
                            processes[process_id].log[time] = 'Recibí mensaje {}'.format(received_message)
                            if ',' in received_message:
                                split = received_message.split(',')
                                process_id_send_extracted = split[0].strip()
                                if (config.confirmation_of_arrival):
                                    processes[process_id].send_message(f"Proceso {process_id} recibió mi mensaje", processes[process_id_send_extracted], blocking='nonblocking', priority=0)
                                    processes[process_id_send_extracted].receive_message_nonblocking()
                                    processes[process_id_send_extracted].log[time] = f'Proceso {process_id} Prueba de llegada'
                                    processes[process_id_send_extracted].log_queue[time] = f'Proceso {process_id} Prueba de llegada'
                                    processes[process_id].log[time] = processes[process_id].log[time] + ". " + f'Envié Prueba de llegada a  {process_id_send_extracted}'
                                processes[process_id_send_extracted].send_block = False
                                                        
            elif command == "display":
                display(processes)

            elif command == "reset":
                break

            time += 1

if __name__ == "__main__":
    main()

