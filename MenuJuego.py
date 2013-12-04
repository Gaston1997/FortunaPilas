import pilas
import random
from pilas.actores import Bomba
from pilas.actores import Estrella
from Pjs import Zac
from Piedra import Piedra

class PiedraConMovimiento(Piedra): 
    #Esto hace que algunas bombas se muevan sobre el eje X

    def __init__(self, x=0, y=0):
        Piedra.__init__(self, x, y)

    def actualizar(self):
        self.x += 5
        #self.y += 1

        if self.x > 450:
            self.x = -450

class Enemigo(Piedra):
    #Esto nos permite crear nuevas bombas

    def __init__(self):
        Piedra.__init__(self)
        self.izquierda = random.randint(-490, 490)
        self.y = random.randint(-330, 330)

    def actualizar(self):
        self.x -= 0
        Piedra.actualizar(self)
    
        if self.x > 490:
            self.x = -490


pilas.iniciar(1000,640)

'''Musica'''
musica = pilas.musica.cargar("Musica.mp3")#Cargamos la musica
musica.reproducir()#Reproducimos la musica


class EscenaDeMenu(pilas.escena.Base):
    #Menu

    def __init__(self):
        pilas.escena.Base.__init__(self)

    def iniciar(self):

        fondo = pilas.fondos.DesplazamientoHorizontal()
        fondo.agregar('fondomenu.jpg',y=0,velocidad=1000)

        opciones = [
		    ('Comenzar a jugar', self.comenzar),
		    ('Salir', self.salir)]

        self.menu = pilas.actores.Menu(opciones)

    def comenzar(self):
        #Esto nos manda a la escena de juegos
        pilas.cambiar_escena(EscenaDeJuego())
    
    def salir(self):
        #Esto nos cierra el juego si seleccionamos salir
        import sys
        sys.exit(0)


class EscenaDeJuego(pilas.escena.Base):
    #Escena de juego

    def __init__(self):
        pilas.escena.Base.__init__(self)

    def iniciar(self):

        '''Mapa'''
        mapa = pilas.actores.MapaTiled('mapa.tmx')#Cargamos el mapa

        '''Fondo'''
        fondo = pilas.fondos.DesplazamientoHorizontal()#Definimos la poscicion del fondo
        fondo.agregar('fondojuego.jpg', y=-0, x=0 ,velocidad=1000)#Cargamos el fondo

        #Jugador
        self.Jugador = Zac(mapa, x=0, y=-230) #Por algun bug , que no conosco y no encuentro el error mi personaje no camina , pero si remplazamos el Actor al siguiente funciona perfectamente
	#self.Jugador = pilas.actores.Martian(mapa, x=0 , y=-230)
        self.Jugador.aprender(pilas.habilidades.SeMantieneEnPantalla)
        self.Puntos = pilas.actores.Puntaje(x=-360 , y=287)
        pilas.actores.Sonido()
        self.Vida = pilas.actores.Puntaje(x=-415 , y=265)

        #Estrellas
        estrellas = pilas.actores.Estrella(x=random.randrange(-480,480) , y=random.randrange(-285,320)) * 5
        estrellas.escala = 0.50
        estrellas.radio_de_colision=20

        #Bombas
        B1 = PiedraConMovimiento(x=random.randrange(-480,480) , y=125)
        B2 = PiedraConMovimiento(x=random.randrange(-480,480) , y=-40)
        B3 = PiedraConMovimiento(x=-480 , y=-260)

        piedras = [B1,B2,B3]
        enemigos = []

        #Funciones

        def agarrar(Jugador, estrellas):
            #Funcion que permite agarrar las estrellas y nos aumenta 1 punto en el contador del puntaje y las vidas
            estrellas.eliminar()
            self.Puntos.aumentar(1)
            CantPuntos = self.Puntos.obtener()
            if (CantPuntos == 3):
                self.Vida.aumentar(1)
            if (CantPuntos == 5):
                pilas.avisar("Ganaste. Toque M -> Menu , R -> Reintentar")
                estrellas.eliminar()
                B1.explotar()
                B2.explotar()
                B3.explotar()
            
        def explotar_bomba (Jugador , piedras):
            #Funcion que permite que las bombas nos maten
            piedras.explotar()
            piedras.eliminar()
            self.Vida.aumentar(-1)
            CantVida = self.Vida.obtener()
            if (CantVida < 0): #if que si nos quedan 0 vidas nos muramos
                self.Vida = 0
                pilas.avisar("Perdiste. Toque M -> Menu , R -> Reintentar")

                Jugador.eliminar()

                #Esto genera que al morir desaparescan las estrellas y las bombas
                estrellas.eliminar()
                B1.explotar()
                B2.explotar()
                B3.explotar()

                #Esto genera que las bombas en la lista enemigos , exploten
                h=0 
                for h in enemigos :
                    enemigos[h].explotar()
               

        #Funcion que permite que las bombas se creen automaticamente
        '''Codigo de Renzo Sartore'''
        class tiempo():
            #Esto genera que las bombas cada ves tarden mas en aparecer

            def __init__(self,value=1.0):
                self.value = value

            def incrementar(self):
                if (self.value < 5):
                    self.value = self.value + 1

            def dameTiempo(self):
                return self.value

        tiempo = tiempo()

        def crear_enemigo():
            CantPuntos = self.Puntos.obtener()
            if (CantPuntos > 0 or CantPuntos == 0):
                enemigos = Enemigo()
                piedras.append(enemigos)
                tiempo.incrementar()
                #print tiempo.dameTiempo            
                pilas.mundo.agregar_tarea(tiempo.dameTiempo(), crear_enemigo)
                #pilas.mundo.agregar_tarea(2, crear_enemigo)
            '''Hasta aca'''

        #Establecemos las escenas
        pilas.escena_actual().colisiones.agregar(self.Jugador, estrellas, agarrar)
        pilas.escena_actual().colisiones.agregar(self.Jugador, piedras, explotar_bomba)
        crear_enemigo()

        #Para volver al menu
        pilas.avisar("Pulsa la tecla 'M' para regresar al menu...")

        pilas.eventos.pulsa_tecla.conectar(self.cuando_pulsa_tecla)
    def cuando_pulsa_tecla(self, evento):
        if evento.texto == u'm':
            pilas.cambiar_escena(EscenaDeMenu())

        #Para reintentar una vez que morimos sin necesidad de ir al menu
        pilas.eventos.pulsa_tecla.conectar(self.cuando_pulsa_teclaR)
    def cuando_pulsa_teclaR(self, evento):
        if evento.texto == u'r':
            pilas.cambiar_escena(EscenaDeJuego())
	
# Carga la nueva escena
pilas.cambiar_escena(EscenaDeMenu())
pilas.ejecutar()
