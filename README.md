# Proyecto Sistemas Operativos Avanzados

Este proyecto es parte del curso de Sistemas Operativos Avanzados y ha sido desarrollado por Sebastián Gamboa y Josef Ruzicka.

## Detalles del Proyecto

El proyecto consiste en construir un sistema de simulación de Message Passing que permite:

- Configurar el sistema a utilizar seleccionando los parámetros de la siguiente tabla, además de otros parámetros generales que puedan ser necesarios como el número de procesos, el tamaño de la cola de mensajes, entre otros.

  ![Diseño de características de sistemas de mensajes](Design Characteristics of Message Systems.jpg)

- Tener una línea de comandos que permita ejecutar comandos `create()`, `send()` y `receive()`, con los parámetros respectivos.

- Simular la ejecución de los comandos, pudiendo el usuario escoger el momento para ver el estado `display()`, incluyendo los procesos (cada proceso y cada cola tendría una ventana, donde muestra el log de eventos del proceso o de la cola), ya sea después de cada comando o después de N comandos. El programa puede usarse en modo interactivo o batch (donde se lee la información de archivos de texto).

  **Nota:** Instrucciones brindadas por el profesor.

## Instrucciones de uso

El simulador de Message Passing cuenta con 2 opciones de ejecución:

### Modo Interactivo:

La ejecución del programa se realiza mediante el comando:

```bash
python3 SOA.py


