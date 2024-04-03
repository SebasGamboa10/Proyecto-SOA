class SystemConfiguration:
    def __init__(self, num_processes, message_queue_size, send_type, receive_type, **kwargs):
        self.num_processes = num_processes
        self.message_queue_size = message_queue_size
        self.send_type = send_type
        self.receive_type = receive_type


class Process:
    def __init__(self, name, pid, send_block, receive_block):
        self.name = name
        self.pid = pid
        self.send_block = send_block
        self.receive_block = receive_block
        self.message_queue = []
        self.log = {}

    def send_message(self, message, destination, blocking=None):
        if blocking=="blocking":
            destination.receive_message_blocking(message)
        else:
            destination.receive_message_nonblocking(message)

    def receive_message_blocking(self, message=None):
        print(message)
        if message is not None:
            self.message_queue.append(message)
        elif self.message_queue:
            return self.message_queue.pop(0)
        else:
            return None

    def receive_message_nonblocking(self, message=None):
        if message:
            self.message_queue.append(message)
        elif self.message_queue:
            return self.message_queue.pop(0)
        else:
            return "No hay mensajes disponibles"


def create_process(name, pid, send_block, receive_block):
    return Process(name, pid, send_block, receive_block)

def display(processes):
    print("Estado del sistema:")
    for pid, proceso in processes.items():
        print(f"ID del proceso: {pid}")
        print(f"Nombre del proceso: {proceso.name}")
        print(f"Bool Send: {proceso.send_block}")
        print(f"Bool receive: {proceso.receive_block}")
        print(f"log: {proceso.log}")

def configure_system():
    print("Configuración del sistema:")
    num_processes = int(input("Ingrese el número de procesos: "))
    message_queue_size = int(input("Ingrese el tamaño de la cola de mensajes: "))
    send_type = str(input("El send es blocking o nonblocking: "))
    receive_type = str(input("El receive es blocking o nonblocking: "))

    return SystemConfiguration(num_processes, message_queue_size,send_type, receive_type)

def main():
    processes = {}
    config = configure_system()
    time = 0
    while True: 
        command = input("Ingrese un comando (create, send, receive), 'display' para ver el estado o 'exit' para salir: ")

        if command == "exit":
            break


        elif command == "create":
            if config.num_processes > len(processes): 
                name = input("Ingrese el nombre del proceso: ")
                process_id = input("Ingrese el ID del proceso: ")
                send_block = None # aqui sería send_block = send_type? lo mismo abajo, bueno con un if blocking entonces true, y else non blocking
                receive_block = None

                new_process = create_process(name, process_id, send_block, receive_block)
                new_process.log[time] = 'Proceso creado'
                processes[new_process.pid] = new_process
            else:
                print("No es posible agregar procesos, se ha alcanzado el maximo")


        elif command == "send":
            process_id_send = input("Ingrese el ID del proceso envia el mensaje: ")
            process_id = input("Ingrese el ID del proceso al que desea enviar el mensaje: ")
            if process_id_send not in processes:
                print(f"Proceso {process_id_send} no existe")
            elif process_id not in processes:
                print(f"Proceso {process_id} no existe")
            else:
                send_block = processes[process_id_send].send_block # el comentario de arriba asumiendo que todos los procs tienen el mismo tipo

                if send_block is False or send_block is None:
                    message = input("Ingrese el mensaje: ")
                    processes[process_id_send].log[time] =  'Envié mensaje {} a proc {}'.format(message, process_id)
                    if config.send_type == 'blocking':
                        processes[process_id_send].send_block = True
                        processes[process_id_send].send_message(f"{message}", processes[process_id], blocking=config.receive_type)
                    else:
                        processes[process_id_send].send_message(f"{message}", processes[process_id], blocking=config.receive_type)
                else:
                    print("Actualmente el proceso tiene un envio activo que mantiene bloqueado")



        elif command == "receive":
            process_id = input("Ingrese el ID del proceso que recibe el mensaje: ")
            #FALTA VALIDAR DE QUIEN QUIERO RECIBIRLO
            if config.receive_type == 'blocking':
                received_message = processes[process_id].receive_message_blocking()
                if received_message:
                    print(f"Process {process_id} recibió el mensaje: {received_message}")
                    processes[process_id].log[time] = 'Recibí mensaje {}'.format(received_message)
                else:
                    print(f"Process {process_id} no recibió ningún mensaje.")
            else:
                received_message = processes[process_id].receive_message_nonblocking()
                print(f"Process {process_id} recibió el mensaje: {received_message}")
                processes[process_id].log[time] = 'Recibí mensaje {}'.format(received_message)


        elif command == "display":
            display(processes)

        time += 1

if __name__ == "__main__":
    main()

