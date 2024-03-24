class SystemConfiguration:
    def __init__(self, num_processes, message_queue_size, **kwargs):
        self.num_processes = num_processes
        self.message_queue_size = message_queue_size

class Process:
    def __init__(self, name, pid):
        self.name = name
        self.pid = pid

def create_process(name, pid):
    return Process(name, pid)

def send_message(process_id, message):
    print(f"Enviando mensaje al proceso {process_id}: {message}")

def receive_message(process_id):
    print(f"Recibiendo mensaje del proceso {process_id}")

def display(processes):
    print("Estado del sistema:")
    print(processes)

def configure_system():
    print("Configuración del sistema:")
    num_processes = int(input("Ingrese el número de procesos: "))
    message_queue_size = int(input("Ingrese el tamaño de la cola de mensajes: "))
    return SystemConfiguration(num_processes, message_queue_size)

def main():
    processes = []
    system_config = configure_system()

    while True:
        command = input("Ingrese un comando (create, send, receive), 'display' para ver el estado o 'exit' para salir: ")

        if command == "exit":
            break
        elif command == "create":
            name = input("Ingrese el nombre del proceso: ")
            process_id = input("Ingrese el ID del proceso: ")
            new_process = create_process(name, process_id)
            processes.append(new_process)
        elif command == "send":
            process_id = input("Ingrese el ID del proceso al que desea enviar el mensaje: ")
            message = input("Ingrese el mensaje: ")
            send_message(process_id, message)
        elif command == "receive":
            process_id = input("Ingrese el ID del proceso del que desea recibir el mensaje: ")
            receive_message(process_id)
        elif command == "display":
            display(processes)

if __name__ == "__main__":
    main()

