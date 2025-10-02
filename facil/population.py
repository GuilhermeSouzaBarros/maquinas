from copy import deepcopy
from random import randint, random, choices

class Individual:
    def __init__(self, num_tasks:int=0, num_machines:int=0, random:bool=False):
        self.values = None
        self.fitness = 9999999
        self.fitness_up = True
        if random: self.random_values(num_tasks, num_machines)

    def random_values(self, num_tasks:int = 0, num_machines:int = 0):
        self.values = [randint(0, num_machines - 1) for _ in range(num_tasks)]

    def copy(self):
        copy = Individual()
        copy.values = deepcopy(self.values)
        copy.fitness = self.fitness
        copy.fitness_up = self.fitness_up
        return copy

    def mutate(self, num_maq:int, probabiity:float) -> None:
        if probabiity > random():
            self.fitness_up = True
            self.values[randint(0, len(self.values) - 1)] = randint(0, num_maq-1)

    def value_from_parents(self, num_objs:int, parents) -> None:
        i = 0
        while i < num_objs:
            self.fitness_up = True
            self.values[i] = parents[randint(0, 1)].values[i]
            i += 1

class Population:
    def __init__(self, size:int, prob_m:float, prob_c:int, elitism:bool,
                 tarefas:list[int], num_maquinas:list[int]):
        self.size = size
        self.num_tarefas = len(tarefas)
        self.tarefas = tarefas
        self.num_maq = num_maquinas
        self.individuals = [Individual(self.num_tarefas, self.num_maq, True) for _ in range(0, size)]
        self.prob_m = prob_m
        self.prob_c = prob_c
        self.elitism = elitism
        self.update_fitness()
        self.elite = (min(self.individuals, key = lambda individual: individual.fitness)).copy()
        self.gen_elite = 0
        

    def get_fitness(self, values:list[int]):
            machines_time = [0] * self.num_maq
            for v in values:
                machines_time[v] += self.tarefas[v]
            return max(machines_time)
    
    def update_individual_fitness(self, individual:Individual):
        if individual.fitness_up:
            individual.fitness = self.get_fitness(individual.values)
            individual.fitness_up = False

    def update_fitness(self) -> None:
        for individual in self.individuals:
            self.update_individual_fitness(individual)

    def choose_parents(self) -> list[Individual]:
        sorted_individuals = sorted(self.individuals, key = lambda x: x.fitness, reverse=True)
        weights = [(x * (1 + 4 if x > 0 else 0)) for x in range(1, self.size + 1)]
        return choices(sorted_individuals, weights, k=self.size)

    def pop_crossing(self):
        parents = self.choose_parents()
        for i in range(0, self.size - 1, 2):
            cur_parents = [parents[i], parents[i+1]]
            if (random() < self.prob_c):
                self.individuals[i].value_from_parents(self.num_tarefas, cur_parents)
            else:
                self.individuals[i] = cur_parents[0]
            
            if (random() < self.prob_c):
                self.individuals[i + 1].value_from_parents(self.num_tarefas, cur_parents)
            else:
                self.individuals[i] = cur_parents[1]

            self.individuals[i].mutate(self.num_maq, self.prob_m)
            self.individuals[i+1].mutate(self.num_maq, self.prob_m)

    def update_generation(self, generation:int) -> None:
        self.pop_crossing()
        self.update_fitness()
        self.local_search()
        cur_elite = (min(self.individuals, key = lambda individual: individual.fitness)).copy()
        
        if cur_elite.fitness < self.elite.fitness:
            self.elite = cur_elite
            self.gen_elite = generation
        elif self.elitism:
            self.individuals[0] = self.elite.copy()

    def local_search(self):
        for idv in self.individuals:
            copy = Individual()
            copy = deepcopy(idv)

            i = randint(0, len(idv.values))
            j = randint(0, len(idv.values))

            if i > j:
                i, j = j, i

            sorted_range = sorted(copy.values[i:j])
            copy.values[i:j] = sorted_range

            copy.fitness = self.get_fitness(copy.values)

            if copy.fitness < idv.fitness:
                idv.fitness = copy.fitness
                idv.values = copy.values
                        
            sorted_range = sorted(copy.values[i:j], reverse=True)
            copy.values[i:j] = sorted_range

            copy.fitness = self.get_fitness(copy.values)

            if copy.fitness < idv.fitness:
                idv.fitness = copy.fitness
                idv.values = copy.values
                        