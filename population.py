from copy import deepcopy
from random import randint, random, choices, choice, shuffle

class Individual:
    def __init__(self, tasks=None, random:bool=False):
        self.values = None
        self.fitness = 9999999
        self.fitness_up = True
        self.valid = False
        if random: self.random_values(tasks)

    def random_values(self, tasks:list[int]):
        self.values = []
        available_tasks = []
        for i, task in enumerate(tasks):
            if task[1] == 0:
                available_tasks.append(i+1)

        while available_tasks:
            next_task = choice(available_tasks)
            available_tasks.remove(next_task)
            self.values.append((next_task, choice(tasks[next_task-1][2])))
            for i, task in enumerate(tasks):
                if (task[1] == next_task):
                    available_tasks.append(i+1)
                    

    def copy(self):
        copy = Individual()
        copy.values = deepcopy(self.values)
        copy.fitness = self.fitness
        copy.fitness_up = self.fitness_up
        copy.valid = self.valid
        return copy

    def mutate(self, probabiity:float) -> None:
        if probabiity > random():
            self.fitness_up = True
            i, j = randint(1, len(self.values)) - 1, randint(1, len(self.values)) - 1
            self.values[i], self.values[j] = self.values[j], self.values[i]
        
    def cross_values(self, start:int, end:int, parent_a, parent_b):
        num_tasks = len(self.values)
        self.values = [None for _ in range(0, num_tasks)]
        
        index = start
        while index <= end:
            self.values[index] = parent_a.values[index]
            index += 1
        index %= num_tasks
        
        next_pos = index
        while next_pos != start:
            valid = 1
            for value in self.values:
                if parent_b.values[index] is None: print(parent_b.values)
                if value is None: continue
                if parent_b.values[index][0] == value[0]:
                    valid = 0
                    break

            if valid:
                self.values[next_pos] = parent_b.values[index]
                next_pos += 1
                next_pos %= num_tasks

            index += 1
            index %= num_tasks
            
        self.fitness_up = False

class Population:
    def __init__(self, size:int, prob_m:float, prob_c:int, elitism:bool,
                 tarefas:list[int], maquinas:list[int]):
        self.size = size
        self.num_tarefas = len(tarefas)
        self.tarefas = tarefas
        self.num_maq = maquinas
        self.individuals = [Individual(self.tarefas, True) for _ in range(0, size)]
        self.prob_m = prob_m
        self.prob_c = prob_c
        self.elitism = elitism
        self.update_fitness()
        self.elite = (min(self.individuals, key = lambda individual: individual.fitness)).copy()
        self.gen_elite = 0

    def get_fitness(self, values:list[int]):
        valid = True
        machines_time = [0] * self.num_maq
        available_tasks = []
        for i, task in enumerate(self.tarefas):
            if task[1] == 0:
                available_tasks.append((i+1, 0))

        for task in values:
            valid = False
            for a_task in available_tasks:
                if a_task[0] == task[0]:
                    valid = True
                    start_time = a_task[1]
            if valid:
                machines_time[task[1]] = max(machines_time[task[1]], start_time) + self.tarefas[task[0] - 1][0]
            else:
                machines_time[task[1]] += self.tarefas[task[0] - 1][0]
                    
            for i, n_task in enumerate(self.tarefas):
                if n_task[1] == task[0]:
                    available_tasks.append((i+1, machines_time[task[1]]))

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

    def parents_crossing(self, parents:list[Individual], pos:int):
        if (random() > self.prob_c):
            self.individuals[pos]     = parents[0]
            self.individuals[pos + 1] = parents[1]
            return
        
        start = randint(0, len(self.tarefas) - 2)
        end   = randint(start, len(self.tarefas) - 1)

        parents = [parents[0].copy(), parents[1].copy()]

        self.individuals[pos].cross_values(start, end, parents[0], parents[1])
        self.individuals[pos+1].cross_values(start, end, parents[1], parents[0])
    
    def pop_crossing(self):
        parents = self.choose_parents()
        for i in range(0, self.size - 1, 2):
            cur_parents = [parents[i], parents[i+1]]
            self.parents_crossing(cur_parents, i)
    
    def mutate(self):
        for individual in self.individuals:
            individual.mutate(self.prob_m)

    def update_generation(self, generation:int) -> None:
        self.pop_crossing()
        self.mutate()
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
        i = 0
        while i < self.size:
            if self.individuals[i].valid:
                i += 1
                continue
            idv_c = self.individuals[i].copy()

            j = 0
            while j < self.num_tarefas:
                k = j+1
                while k < self.num_tarefas:
                    idv_c.values[j], idv_c.values[k] = idv_c.values[k], idv_c.values[j]
                    idv_c.fitness_up = True
                    
                    self.update_individual_fitness(idv_c)
                    if (idv_c.valid):
                        self.individuals[i] = idv_c
                        return
                    
                    k+=1
                j += 1
            i += 1
    