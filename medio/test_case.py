def read_test_case(file_path:str) -> dict:
    num_m = 0
    maquinas = []
    tarefas = []
    with open(file_path, "r") as file:
        for i, line in enumerate(file):
            j = int(line)
            if i == 0:
                num_m = j
            elif i <= num_m:
                maquinas.append(j)
            elif i == num_m + 1:
                continue
            else:
                tarefas.append(j)
    
    return {"maquinas": maquinas, "tarefas": tarefas}
