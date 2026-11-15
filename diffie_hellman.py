from diffie_hellman_algorithms import *
import time

def verify_solution(a, g, h, p):
    return pow(g, a, p) == h


def main():
    input_file = input("Filename: ")
    input_path = f"sets/{input_file}"

    with open(input_path, "r") as f:
        p, g, h = [int(a) for a in f.readline().split()]

    method = input("Select method (SM = Shanks, RP = rho Pollard): ")
    if method not in {"SM", "RP"}:
        return

    if method == "SM":
        print("Shanks method attack...")
        # Few minutes - problem with RAM memory (~100GB)
        start_time = time.perf_counter()
        result = shanks_method(g,h,p)
    elif method == "RP":
        print("Rho Pollard algorithm attack...")
        #About (1-3 hours - depends of proccesor quality)
        start_time = time.perf_counter()
        result = pollard_rho_algorithm(g,h,p)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    verify = verify_solution(result, g, h, p)

    output_path = f"output/{input_file[:-4]}_{method}.txt"

    with open(output_path, "w") as f:
        f.write(f"p = {p}, g = {g}, h = {h}\n")
        f.write(f"a = {result}\nelapsed time: {elapsed_time}\n")
        f.write(f"verification: {verify}")

    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()