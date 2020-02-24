from ortools.linear_solver import pywraplp


def create_data_model():
    """Stores the data for the problem."""
    data = dict()
    data['obj_coeffs'] = [
        [0, -1, -1, 1],  # Zwiebeln
        [-1, 0, 0, -1],  # Zucchini
        [-1, 0, 0, 0],  # Tomaten
        [1, -1, 0, 0]  # Bohnen
    ]  # Zw Zu  T  B


    data['u_bounds'] = [2, 2, 2, 3]
    data['l_bounds'] = [0, 0, 0, 3]

    return data


def main():
    # Anzahl der Positionen im Beet
    length_field = [0, 1, 2, 3, 4]
    plant_kinds = ['Zwiebeln', 'Zucchini', 'Tomaten', 'Bohnen']

    data = create_data_model()

    # Create the linear solver with the GLOP backend.
    solver = pywraplp.Solver('simple_mip_program',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    infinity = solver.infinity()

    # v - Anzahl vollständiger Setzlinge von Pflanzenart p
    v = {}
    for p in range(0, len(plant_kinds)):
        v[p] = solver.IntVar(0, infinity, 'v[%i]' % p)

    # a - binär variable wenn Pflanzeart p an Stelle x gepflanzt wird
    a = {}
    for p in range(0, len(plant_kinds)):
        for x in length_field:
            a[(p, x)] = solver.BoolVar('a[%i][%i]' % (p, x))

    # Binär: Wenn Pflanzenart p vor Pflanzenart q in x-Richtung auf dem Feld geplanzt (1) wird sonst null
    y = {}
    for p in range(len(plant_kinds)):
        for q in range(len(plant_kinds)):
            for x in length_field:
                y[(p, q, x)] = solver.BoolVar('y[%i][%i][%i]' % (p, q, x))

    objective = solver.Objective()
    for p in range(len(plant_kinds)):
        for q in range(len(plant_kinds)):
            #            if p == q:
            #                pass
            #            else:
            for x in length_field:
                objective.SetCoefficient(y[(p, q, x)], data['obj_coeffs'][p][q])

    # Das ganze Beet muss genutzt werden
    solver.Add(sum([v[p] for p in range(0, len(plant_kinds))]) == len(length_field))

    # Es muss von jeder Pflanzenart die Mindestanzahl an Setzlingen erreicht werden
    for p in range(len(plant_kinds)):
        solver.Add(v[p] >= data['l_bounds'][p])

    # Es darf von jeder Pflanzenart maximal die Höchstzahl an Setzlingen erreicht werden
    for p in range(len(plant_kinds)):
        solver.Add(v[p] <= data['u_bounds'][p])

    # Nur ein Setzling pro Feld
    for x in length_field:
        solver.Add(sum([a[(p, x)] for p in range(len(plant_kinds))]) <= 1)

    # Die Anzahl der Setzlinge pro Pflanzenart bestimmen
    for p in range(len(plant_kinds)):
        solver.Add(sum([a[(p, x)] for x in length_field]) == v[p])

    # Kopplung vorgänger Nachfolgerbeziehung
    for x in length_field[:-1]:
        for p in range(0, len(plant_kinds)):
            for q in range(0, len(plant_kinds)):
                solver.Add(a[(p, x)] + a[(q, x + 1)] <= y[(p, q, x)] + 1)

    # Stelle sicher, dass es nur die relevante Beziehung Vorgänger-Nachfolgerbeziehung gewählt wird (in Verbindung mit Min. der Zielfunktion)
    for x in length_field[:-1]:
        solver.Add(sum([y[(p, q, x)] for p in range(len(plant_kinds)) for q in range(len(plant_kinds))]) <= 1)

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        for x in range(0, 5):
            # print(plant_kinds[int(sum([(a[(p, x)].solution_value() * p) for p in range(0, len(plant_kinds))]))])
            plant_list = [a[(p, x)].solution_value() for p in range(len(plant_kinds))]
            print([plant_kinds[index] for index, value in enumerate(plant_list) if value > 0])
            print("---")

        print('Objective value =', solver.Objective().Value())
        for p in range(0, len(plant_kinds)):
            print(plant_kinds[p], ' = ', v[p].solution_value())
        print()
        print('Problem solved in %f milliseconds' % solver.wall_time())
        print('Problem solved in %d iterations' % solver.iterations())
        print('Problem solved in %d branch-and-bound nodes' % solver.nodes())
        print(sum([y[(p, q, x)].solution_value()
                   for x in length_field
                   for q in range(0, len(plant_kinds))
                   for p in range(0, len(plant_kinds))]))
    else:
        print('Objective value =', solver.Objective().Value())
        print('The problem does not have an optimal solution.')


if __name__ == '__main__':
    main()
