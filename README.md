# Carcassonne

## 1. Introducción

Carcassonne es un juego de mesa de estrategia, donde los jugadores construyen un mapa usando losetas, en las cuales estan representadas caminos, pueblos, ciudades o monasterios. Cada jugador busca, colocando losetas, cerrar caminos o ciudades para ganar puntos. Cabe resaltar que estas losetas se deben conectar siguiendo una lógica, las losetas contiguas a una loseta deben mantener la lógica del mundo, esto es:
- No colocar contiguamente una loseta de ciudad al lado de una de camino, haciendo que los caminos solo se puedan conectar con otros caminos, y las ciudades con otras ciudades.

Este juego puede entenderse como un problema de busqueda, donde cada movimiento hecho afecta el mundo, siendo así, el colocamineto de las losetas es fundemental para maximizar la puntuación del jugador, por esta razon la implementación de algoritmos como **Minimax** y **Expectimax** pueden ayudar a modelar la mejor manera en la que dos jugadores juegues Carcassonne.

Este proyecto, como se mencionó anteriormente tiene como objetivo mostrar el uso de los algoritmos en el juego de Carcassonne, encontrando la mejor manera de jugar el juego, estimando cual puede ser la siguiente loseta que salga y ya teniendo una loseta cual es la mejor manera de colocarla para maximizar el puntaje de un jugador al mismo tiempo que intetna minimizar el del rival.

Los principales objetivos son:

- Analizar la dinámica del juego desde un punto de vista de la Inteligencia Artificial.
- Implementar estrategias automatizadas que optimicen las decisiones de colocación de losetas.
- Comparar los dos algoritmos y determinar cual es el que mejor se acopla al juego

La motivación práctica es descubrir cómo, al modelar este juego, se pueden estudiar diferentes maneras de entender lo que al inicio parece solo un juego para divertirse, pero que también permite analizar diferentes aplicaciones de la IA.


---

## 2. Definición del problema

Se plantea una cuadricula, sobre la cual se pondrán las losetas, para esto se tendrá una loseta inicial, la cuál será: 

<img width="90" height="90" alt="image" src="https://github.com/user-attachments/assets/a7e50bb3-4d34-4bd2-9628-d7f0278bcdcc" />

Se escoge esta loseta dado que, independientemente de cuál loseta salga, siempre hay una jugada posible.

Adicionalmente, estas losetas van a tener una representación en el computador, la cual se verá:
<img width="1873" height="494" alt="image" src="https://github.com/user-attachments/assets/f398128f-8ba6-4d3d-b8d0-e139f220c00d" />

Donde:
- C = Ciudad
- R = Camino
- T = Pueblo
- M = Monasterio

Cabe resaltar que las representaciones mostradas serían las de las siguientes losetas respectivamente:

<img width="91" height="89" alt="image" src="https://github.com/user-attachments/assets/50568bd4-1d9b-494a-8428-53bef2fcf7f4" />
<img width="90" height="90" alt="image" src="https://github.com/user-attachments/assets/59e4c2da-34a8-4a58-b442-e287a9da6bb5" />
<img width="90" height="89" alt="image" src="https://github.com/user-attachments/assets/f3725423-2dee-406f-8353-0937994f7e16" />


Teniendo esto en cuenta, cada jugador puede decidir colocar su loseta de alguna manera, siempre buscando ganar el juego. 



---


## 3. Objetivos

1. **Determinar si se cerró alguna ciudad o camino:**
    - Fundamental para poder determinar en que momento se ganan puntos.
    - En el caso de las ciudades, se revisará que, para que una ciudad se considere completa, la ciudad está rodeada por muros.
    - En el caso de los caminos, se revisará que, para que un camino se consideré completo, el camino salga de un pueblo, una ciudad o un monasterio y llegue a otro pueblo, ciudad o monasterio, haciendo que el camino tenga inicio y final.
2. **Habiendo cerrado ciudad o camino, otorgar una recompensa:**
    - Si se cerró una ciudad, se otorgaran dos puntos por cada loseta usada para cerrar la ciudad.
    - Si se cerró un camino, se otorgara un punto por cada loseta usada para cerrar el camino.
    - Estas recompensas se darán al jugador que cierra la ciudad o el camino.
3. **Definir turnos y movimientos:**
    - En todo momento se sabe cual de los dos jugadores debe hacer alguna jugada en un determinado turno.
    - En el turno de cualquier jugador se buscará maximizar la puntuación propia, al mismo tiempo que se minimiza la del rival
  

---


## 4. Definición de estados

A pesar de que se quieren resolver principalmente tres objetivos, se necesitaran dos clases de problemas para diferenciar la definición de estados, esto dado que el segundo objetivo no requiere de definir estados:

En el caso del primer objetivo, el estado inicial será cualquier loseta con camino o ciudad, el estado actual sería la n-esima loseta con camino o ciudad.

En el caso del tercer pbjetivo, el estado inicial seriá la loseta inicial con una pila, representado las losetas sin usar, el estado actual sería el juego luego de haber hecho n jugadas, habiendo alternado turnos.


---


## 5. Definición de función sucesora

Para el caso del primer objetivo, se implementará un algoritmo **BFS** para determinar si algún camino o ciudad cerró, para esto, la función sucesora devolvería las losetas vecinas que estén conectadas mediante algun camino o ciudad.

Para el tercer objetivo, la función sucesora define cómo se pasa del estado actual del juego a los posibles estados siguientes, según las jugadas válidas del jugador que tiene el turno, es decir, muestra todos los posibles cambios del tablero luego de colocar una loseta de manera válida.


---


## 6. Prueba de objetivo

En caso del tercer objetivo, la prueba de objetivo sería:
- No quedan losetas por jugar, el juego terminó.
- Ningún jugador puede hacer una jugada legal.
Dicho de otra forma, no puedo seguir expandiendo el árbol.

En caso del primer objetivo, la prueba de objetivo sería: 
Revisar si al entrar al estado actual se cerró algún camino o ciudad, esto es: Para los caminos, todo camino está conectado a otro, hasta encontrar uno conectado a alguna ciudad, pueblo o monasterio. Para las ciudades, toda loseta con una ciudad está conectada entre si, esto es si no hay algún lado abierto.
  






This repository implements a simplification of the Carcassonne game with the objectives of applying minimax and expectimax algorithms for multiagents. It's the second project of the course Introduction to AI at UNAL.
