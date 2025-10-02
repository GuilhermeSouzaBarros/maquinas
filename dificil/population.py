from copy import deepcopy
from random import randint, random, choices

class Individual:
    def __init__(self, num_tasks:int=0, num_machines:int=0, random:bool=False):
        self.values = None
        self.fitness = 9999999
        self.fitness_up = True
        self.valid = False
        if random: self.random_values(num_tasks, num_machines)

    def random_values(self, num_tasks:int = 0, num_machines:int = 0):
        self.values = [] * num_machines
        for i in range(1, num_tasks+1):
            self.values[randint(0, num_machines-1)].append(i)
    
    def copy(self):
        copy = Individual()
        copy.values = deepcopy(self.values)
        copy.fitness = self.fitness
        copy.fitness_up = self.fitness_up
        copy.valid = self.valid
        return copy

    def mutate(self, num_maq:int, num_task:int, probabiity:float) -> None:
        if probabiity > random():
            self.fitness_up = True
            remove_task = randint(1, num_task)
            for value in self.values:
                if remove_task in value:
                    value.remove(remove_task)

            insert_to = randint(0, num_maq-1)
            self.values[insert_to].insert(randint(0, len(self.values[insert_to])))

    def value_from_parents(self, num_objs:int, parents) -> None:
        self.random_values(num_objs, num)
        #i = 0
        #while i < num_objs:
        #    self.fitness_up = True
        #    self.values[i] = parents[randint(0, 1)].values[i]
        #    i += 1

    def get_fitness(self, values:list[int]):
        machines_time = [0] * self.num_maq
        for v in values:
            machines_time[v] += self.tarefas[v]
        return max(machines_time)


class Population:
    def __init__(self, size:int, prob_m:float, prob_c:int, elitism:bool,
                 tarefas:list[int], maquinas:list[int]):
        self.size = size
        self.num_tarefas = len(tarefas)
        self.tarefas = tarefas
        self.num_maq = maquinas
        self.individuals = [Individual(self.num_tarefas, self.num_maq, True) for _ in range(0, size)]
        self.prob_m = prob_m
        self.prob_c = prob_c
        self.elitism = elitism
        self.update_fitness()
        self.elite = (min(self.individuals, key = lambda individual: individual.fitness)).copy()
        self.gen_elite = 0

    def get_fitness(self, values:list[int]):
        valid = True
        machines_time = [0] * self.num_maq
        for v in values: 
            machines_time[v] += self.tarefas[v]
            if (self.tarefas[v] > self.maq[v]): valid = False
        return max(machines_time) ** (1 if valid else 2), valid
    
    def update_individual_fitness(self, individual:Individual):
        if individual.fitness_up:
            individual.fitness, individual.valid = self.get_fitness(individual.values)
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
        self.update_fitness()

        cur_elite = (min(self.individuals, key = lambda individual: individual.fitness)).copy()
        if cur_elite.valid and cur_elite.fitness < self.elite.fitness:
            self.elite = cur_elite
            self.gen_elite = generation
        elif self.elitism:
            self.individuals[0] = self.elite.copy()
    
    def local_search(self):
        for idv in self.individuals:
            if idv.valid: continue
            idv.fitness_up = True
            i = 0
            while i < self.num_tarefas:
                if self.tarefas[i] > self.maq[idv.values[i]]:
                    idv.values[i] = randint(0, self.num_maq-1)
                else:
                    i += 1
                        