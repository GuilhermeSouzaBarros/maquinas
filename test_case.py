def read_test_case(file_path:str) -> dict:
    num_m = 0
    maquinas = []
    tarefas = []
    with open(file_path, "r") as file:
        for i, line in enumerate(file):
            if i <= num_m:
                j = int(line)
                if i == 0: num_m = j
                else: maquinas.append(j)
            else:
                if i == num_m + 1:
                    continue
                else:
                    j, k = map(int, line.split())
                    tarefas.append([j, k])
    
    for tarefa in tarefas:
        tarefa.append([])
        for i, maq in enumerate(maquinas):
            if not maq or tarefa[1] <= maq:
                tarefa[2].append(i)

    return {"maquinas": maquinas, "tarefas": tarefas}
