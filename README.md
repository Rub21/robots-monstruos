## Simulación Robots vs Monstruos


## Ejecucion en terminal

```sh
python main.py
```

. = libre, # = vacía, R = robot, M = monstruo

VISTA XY (Frontal)    VISTA XZ (Lateral)    VISTA YZ (Superior)
============================================================
    0 1 2 3 4 5 6 7     0 1 2 3 4 5 6 7     0 1 2 3 4 5 6 7
 0  . . . . . # M .  0  . . . . . . . #  0  . . . . . . . .
 1  # . . . # . . .  1  . . . . # # # .  1  . . . . # . . .
 2  . . . . . # . .  2  # . . # . . . .  2  . . . . . # . #
 3  # . . . . . . .  3  # . . . . . . .  3  . # . # # . . .
 4  . # . # . # # .  4  . M . . . . . .  4  . M . . . . . .
 5  . . . . . . . .  5  . . . M . # . #  5  . . . # # . . .
 6  # # . . # # . #  6  . . # . # . # #  6  . # . . # . . #
 7  # . . # . . . #  7  . . . # . . . #  7  . . . . . . . .

Robots activos: 3 | Monstruos activos: 5
============================================================


## Ejecucion en 3d

```sh
3d.py
```