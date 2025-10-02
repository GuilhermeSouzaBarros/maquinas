def read_test_case(file_path:str) -> dict:
    num_m = 0
    tarefas = []
    with open(file_path, "r") as file:
        for i, line in enumerate(file):
            j, k = map(int, line.split())
            if i == 0:
                num_m = k
            else:
                tarefas.append([j, k])
    
    return {"maquinas": num_m, "tarefas": tarefas}
