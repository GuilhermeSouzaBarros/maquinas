from population import Population
from matplotlib import pyplot
from test_case import read_test_case

from sys import argv
import time

NUM_POPULATION = 50
NUM_GENERATION = 50

PROB_MUTATION = 0.05
PROB_CROSS    = 0.8

ELITISM = True

def main():
    test_case = read_test_case(argv[1])
    start_time = time.perf_counter()
    population = Population(NUM_POPULATION, PROB_MUTATION, PROB_CROSS, ELITISM,
                            test_case["tarefas"], len(test_case["maquinas"]))
    
    best_values = []
    for generation in range(0, NUM_GENERATION):
        population.update_generation(generation)
        best_values.append(population.elite.fitness)
    
        stale = generation - population.gen_elite
        if (stale > 6): population.prob_m = 10 * PROB_MUTATION
        elif (stale > 3): population.prob_m = 5 * PROB_MUTATION
        else: population.prob_m = PROB_MUTATION
        population.prob_m = min(8, population.prob_m)

    end_time = time.perf_counter()
    print("Resultado válido:", "Sim" if population.elite.valid else "Não")
    print("Makespan:", population.elite.fitness)
    print("Tempo gasto:", end_time - start_time, "segundos.")
    print("Ordem [formato (Item, Máquina)]: ", population.elite.values)

    pyplot.plot(best_values, linestyle="solid", color="r")

    pyplot.xlabel("Geração")
    pyplot.ylabel("Aptidão")
    pyplot.title("Teste")
    pyplot.show()

if __name__ == "__main__":
    main()
