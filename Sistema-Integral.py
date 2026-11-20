from abc import ABC, abstractmethod
from datetime import datetime


# Tratar exepciones 

class DatosInvalidosError(Exception):
    pass


class ServicioNoDisponibleError(Exception):
    pass


class ReservaInvalidaError(Exception):
    pass


class OperacionNoPermitidaError(Exception):
    pass

# Se guardan eventos y errores

def registrar_log(tipo, mensaje):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Se abre el archivo en modo "a" para agregar informacion
    # sin borrar los registros anteriores.
    with open("logs.txt", "a", encoding="utf-8") as archivo:
        archivo.write(f"[{fecha}] [{tipo}] {mensaje}\n")


# Clase abstracta

class Entidad(ABC):

    def __init__(self, identificacion):
        if not identificacion:
            raise DatosInvalidosError("La identificacion no puede estar vacia.")

        self._identificacion = identificacion

    @property
    def identificacion(self):
        return self._identificacion

    @abstractmethod
    def mostrar_informacion(self):
        pass


# Clase cliente, guarda datos personales y utiliza propiedades para proteger datos

class Cliente(Entidad):

    def __init__(self, identificacion, nombre, correo, telefono):
        super().__init__(identificacion)

        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise DatosInvalidosError("El nombre del cliente no es valido.")
        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if not isinstance(valor, str) or "@" not in valor or "." not in valor:
            raise DatosInvalidosError("El correo electronico no es valido.")
        self._correo = valor.strip()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if not str(valor).isdigit() or len(str(valor)) < 7:
            raise DatosInvalidosError("El telefono debe tener al menos 7 digitos.")
        self._telefono = str(valor)

    def mostrar_informacion(self):
        return (f"ID: {self.identificacion} | Nombre: {self.nombre} | "
                f"Correo: {self.correo} | Telefono: {self.telefono}")

class Servicio(ABC):

    def __init__(self, codigo, nombre, precio_base):
        if not codigo or not nombre:
            raise DatosInvalidosError("El codigo y el nombre son obligatorios.")

        if not isinstance(precio_base, (int, float)) or precio_base <= 0:
            raise DatosInvalidosError("El precio base debe ser mayor que cero.")

        self.codigo = codigo
        self.nombre = nombre
        self.precio_base = precio_base
        self.disponible = True

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        pass

    @abstractmethod
    def describir_servicio(self):
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        pass


# Reserva de salas, se calcula el precio por hora

class ReservaSala(Servicio):

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("La duracion de la sala debe ser positiva.")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)

        subtotal = self.precio_base * duracion
        total = subtotal + (subtotal * impuesto / 100) - descuento

        if total < 0:
            raise DatosInvalidosError("El descuento no puede superar el subtotal.")

        return total

    def describir_servicio(self):
        return f"Reserva de sala: {self.nombre}. Precio por hora: ${self.precio_base}"


# Alquiler de equipos, se calcula el precio por dia

class AlquilerEquipo(Servicio):

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("Los dias de alquiler deben ser positivos.")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)

        subtotal = self.precio_base * duracion
        total = subtotal + (subtotal * impuesto / 100) - descuento

        if total < 0:
            raise DatosInvalidosError("El descuento no puede superar el subtotal.")

        return total

    def describir_servicio(self):
        return f"Alquiler de equipo: {self.nombre}. Precio por dia: ${self.precio_base}"


# Asesorias, se calcula el precio por hora

class Asesoria(Servicio):

    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            raise DatosInvalidosError("Las horas de asesoria deben ser positivas.")

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        self.validar_parametros(duracion)

        subtotal = self.precio_base * duracion
        total = subtotal + (subtotal * impuesto / 100) - descuento

        if total < 0:
            raise DatosInvalidosError("El descuento no puede superar el subtotal.")

        return total

    def describir_servicio(self):
        return f"Asesoria: {self.nombre}. Precio por hora: ${self.precio_base}"

    def cancelar(self):
        if self.estado == "Cancelada":
            raise OperacionNoPermitidaError("La reserva ya fue cancelada.")

        self.estado = "Cancelada"
        registrar_log("EVENTO", f"Reserva {self.identificacion} cancelada.")
        return "Reserva cancelada correctamente."

    def procesar(self):
        # Se muestra try, except, else y finally.
        try:
            resultado = self.confirmar()

        except (OperacionNoPermitidaError, ServicioNoDisponibleError,
                DatosInvalidosError) as error:
            registrar_log("ERROR", f"Error al procesar reserva {self.identificacion}: {error}")
            raise ReservaInvalidaError(
                "No fue posible procesar la reserva."
            ) from error

        else:
            registrar_log("EVENTO", f"Procesamiento exitoso de reserva {self.identificacion}.")
            return resultado

        finally:
            registrar_log("EVENTO", f"Finalizo el intento de procesar reserva {self.identificacion}.")

    def mostrar_informacion(self):
        return (f"Reserva: {self.identificacion} | Cliente: {self.cliente.nombre} | "
                f"Servicio: {self.servicio.nombre} | Duracion: {self.duracion} | "
                f"Estado: {self.estado} | Costo: ${self.costo:,.2f}")


# Listas donde se guarda la informacion para no utiliza db

clientes = []
servicios = []
reservas = []


# Registrar y buscar informacion

def registrar_cliente(cliente):
    for cliente_guardado in clientes:
        if cliente_guardado.identificacion == cliente.identificacion:
            raise DatosInvalidosError("Ya existe un cliente con esa identificacion.")

    clientes.append(cliente)
    registrar_log("EVENTO", f"Cliente registrado: {cliente.nombre}")
    print("Cliente registrado correctamente.")


def buscar_cliente(identificacion):
    for cliente in clientes:
        if cliente.identificacion == identificacion:
            return cliente

    raise DatosInvalidosError("No se encontro el cliente solicitado.")

def mostrar_sistema():
    print("\n========== CLIENTES ==========")
    for cliente in clientes:
        print(cliente.mostrar_informacion())

    print("\n========== SERVICIOS ==========")
    for servicio in servicios:
        print(servicio.describir_servicio())

    print("\n========== RESERVAS ==========")
    for reserva in reservas:
        print(reserva.mostrar_informacion())

# Se ejecutan pruebas yse toman errores

def ejecutar_pruebas():

    print("\n======================================")
    print(" SISTEMA INTEGRAL SOFTWARE FJ")
    print("======================================")

    # Cliente ok
    try:
        cliente1 = Cliente("101", "Carlos Perez", "carlos@gmail.com", "3001234567")
        registrar_cliente(cliente1)
    except Exception as error:
        registrar_log("ERROR", f"Operacion 1: {error}")
        print("Error en operacion 1:", error)

    # Correo invalido
    try:
        cliente_malo = Cliente("102", "Ana Lopez", "correo_incorrecto", "3101234567")
        registrar_cliente(cliente_malo)
    except Exception as error:
        registrar_log("ERROR", f"Operacion 2: {error}")
        print("Error esperado en operacion 2:", error)

    # Cliente invalido
    try:
        cliente2 = Cliente("103", "Maria Gomez", "maria@gmail.com", "3201234567")
        registrar_cliente(cliente2)
    except Exception as error:
        registrar_log("ERROR", f"Operacion 3: {error}")
        print("Error en operacion 3:", error)

    # Crea y registra reserva
    try:
        sala = ReservaSala("S01", "Sala principal", 50000)
        registrar_servicio(sala)
    except Exception as error:
        registrar_log("ERROR", f"Operacion 4: {error}")
        print("Error en operacion 4:", error)

    # Crea y registra alquiler
    try:
        equipo = AlquilerEquipo("E01", "Proyector", 30000)
        registrar_servicio(equipo)
    except Exception as error:
        registrar_log("ERROR", f"Operacion 5: {error}")
        print("Error en operacion 5:", error)

    # Crea y registra asesoria
    try:
        asesoria = Asesoria("A01", "Asesoria de software", 80000)
        registrar_servicio(asesoria)
    except Exception as error:
        registrar_log("ERROR", f"Operacion 6: {error}")
        print("Error en operacion 6:", error)

    # Se intenta crear con precio invalido
    try:
        servicio_malo = ReservaSala("S02", "Sala incorrecta", -10000)
        registrar_servicio(servicio_malo)
    except Exception as error:
        registrar_log("ERROR", f"Operacion 7: {error}")
        print("Error esperado en operacion 7:", error)

    # Crear reserva ok
    try:
        reserva1 = Reserva("R01", cliente1, sala, 2)
        registrar_reserva(reserva1)
    except Exception as error:
        registrar_log("ERROR", f"Operacion 8: {error}")
        print("Error en operacion 8:", error)

    # Se confirma reserva
    try:
        print(reserva1.procesar())
    except ReservaInvalidaError as error:
        registrar_log("ERROR", f"Operacion 9: {error}")
        print("Error en operacion 9:", error)

    # Calcula precio con impuesto y descuento
    try:
        total = reserva1.calcular_total(19, 5000)
        print(f"Costo con impuesto y descuento: ${total:,.2f}")
        registrar_log("EVENTO", "Se calculo un costo con impuesto y descuento.")
    except Exception as error:
        registrar_log("ERROR", f"Operacion 10: {error}")
        print("Error en operacion 10:", error)

    # Reserva con duracion invalida
    try:
        reserva_mala = Reserva("R02", cliente2, equipo, 0)
        registrar_reserva(reserva_mala)
    except Exception as error:
        registrar_log("ERROR", f"Operacion 11: {error}")
        print("Error esperado en operacion 11:", error)

    # Reserva con precio invalido
    try:
        asesoria.disponible = False
        reserva2 = Reserva("R03", cliente2, asesoria, 1)
        registrar_reserva(reserva2)
        print(reserva2.procesar())
    except Exception as error:
        registrar_log("ERROR", f"Operacion 12: {error}")
        print("Error esperado en operacion 12:", error)

    # Camcelar reserva
    try:
        print(reserva1.cancelar())
    except Exception as error:
        registrar_log("ERROR", f"Operacion 13: {error}")
        print("Error en operacion 13:", error)

    # Intenta cancelar la misma reserva
    try:
        print(reserva1.cancelar())
    except Exception as error:
        registrar_log("ERROR", f"Operacion 14: {error}")
        print("Error esperado en operacion 14:", error)

    # Busca cliente inexistente
    try:
        buscar_cliente("999")
    except Exception as error:
        registrar_log("ERROR", f"Operacion 15: {error}")
        print("Error esperado en operacion 15:", error)

    # Demuestra uso de try, except, else, finally
    try:
        cliente_encontrado = buscar_cliente("101")
        print("\nCliente encontrado:", cliente_encontrado.nombre)

    except DatosInvalidosError as error:
        registrar_log("ERROR", f"Busqueda de cliente: {error}")
        print("Error:", error)

    else:
        print("La busqueda se realizo correctamente.")

    finally:
        print("Finalizo la operacion de busqueda.")
        registrar_log("EVENTO", "Finalizo la busqueda de cliente.")

    # Se muestran todos los objetos que quedaron guardados.
    mostrar_sistema()

    print("\n======================================")
    print(" FIN DE LAS PRUEBAS DEL SISTEMA")
    print("Los eventos y errores estan en logs.txt")
    print("======================================")

if __name__ == "__main__":
    try:
        ejecutar_pruebas()

    except Exception as error:
        registrar_log("ERROR GENERAL", str(error))
        print("Ocurrio un error general:", error)

    finally:
        print("\nEl programa ha finalizado.")
        
