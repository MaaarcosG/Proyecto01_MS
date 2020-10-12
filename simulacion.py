#from tools import Distribuciones
import simpy
import random as rnd
import numpy as np

class Distribuciones():
    def exponencial_simulator():
        # configuraciones necesaria para definir las distribuciones
        x = -1
        exponencial_inversa = lambda x,l: -np.log(1-x)/l
        lambda_hora = 100/3600
        while x == -1:
            s = rnd.uniform(0,1)
            u = rnd.uniform(0,1)
            valor_exponencial = exponencial_inversa(s,lambda_hora)/(lambda_hora*exponencial_inversa(s,1))
            if(u<valor_exponencial):
                x = exponencial_inversa(s, lambda_hora)
        return x
    
    def poisson_simulator():
        # configuraciones necesaria para definir las distribuciones
        x = 0
        lambda_hora = 100/3600
        p = np.exp(-lambda_hora)
        u = rnd.uniform(0,1)
        s = p
        while u>s:
            x += 1
            s += p
            p = p*(lambda_hora/x)
        return x

class Cajero(object):
    def __init__(self, env, numeros_cajero):
        self.env = env
        self.numeros_cajero = numeros_cajero
        #self.action = env.process(self.run())
        self.res = simpy.Resource(env, capacity=1)
        self.cola = 0
        self.duration = 0
        self.client_time = []
        self.client_served = 0
        self.timeout = []
    
    # funcion para cliente ya atendido, se elimina de la cola.
    def attended(self, client, duration):
        yield self.env.timeout(self.duration)
        self.client_served += 1
        self.cola -= 1
        self.timeout.append(duration)

    # se agrega una cliente a la cola
    def queue(self):
        self.cola += 1

    # determinamos el tiempo de atencion a cliente
    def attend(self, duration):
        self.duration = duration
        self.client_time.append(duration)

# simulacion de la llegada a la tienda del cliente
class Cliente():
    def client(env, clients, duration, cajas):
        queue_short = cajas[0]
        for i in cajas:
            if i.cola < i.cola:
                queue_short = i
        # https://simpy.readthedocs.io/en/latest/api_reference/simpy.resources.html
        with queue_short.res.request() as req:
            arrive_client = env.now
            print("%d: %s hace cola en la caja %d " % (arrive_client, clients, queue_short.numeros_cajero))
            queue_short.queue()
            yield req
            queue_short.attend(duration)
            time_wait = env.now - arrive_client
            yield env.process(queue_short.attended(clients, time_wait))
    
    def setup(env, cajas):
        clients = 0
        while True:
            value = Distribuciones.poisson_simulator()
            for k in range(value):
                clients += 1
                yield env.timeout(1)
                env.process(Cliente.client(env, 'Client %d' % clients, Distribuciones.exponencial_simulator(), cajas))


if __name__ == "__main__":
    #print('modelo_simulacion\Scripts\activate.bat')
    enviroment = simpy.Environment()
    number_cajas = input('Ingrese el numero de las cajas: ')
    number_cajas = int(number_cajas)
    cajas = [Cajero(enviroment, i) for i in range(1,number_cajas+1)]
    enviroment.process(Cliente.setup(enviroment, cajas))
    enviroment.run(until=3600*4)


