import random
from colors import WARNING, RESET

def set_seed(seed: int):
    print(f"{WARNING}SEEDED RAND SET TO {seed}{RESET}")
    random.seed(seed)
