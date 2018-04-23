predator-prey-life
==================
Original project by Iurii Piurbeev (https://github.com/yurap/predator-prey-life)
<img src="https://github.com/GeorgeFedoseev/predator-prey-life/raw/master/screenshot.jpeg" height=400>


Simple python script modelling predator-prey ocean system. Ocean is represented with 2d cell system.
Each cell can contain either one of predator, prey, obstacle or be empty.

The script uses the tkinter graphics interface: red cells are predators, green are prey,
black are obstacles and blue are empty.

Each time tick all cells are processed:

1. Each creature can make a move to a neighbour cell.
2. Predator eats prey if they happen to come to one cell.
3. If predator stays hungry for some time - he dies.
4. After some time each creature produces a child to a neighnour cell.
5. If that cell is not empty - the child dies.
