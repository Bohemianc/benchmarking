import os
import sys


def cal_results_for_graal(fn: str):
    time = []
    mem = []
    with open(fn, "r", encoding="utf-8") as f:
        for i, buf in enumerate(f):
            if i > 20 and i % 7 == 4:
                time.append(int(buf.split()[1]))
            if i > 20 and i % 7 == 5:
                mem.append(int(buf.split()[1]))
    print(time)
    print(mem)
    print(f"mean time of {fn}: {sum(time) // len(time) / 1000}")
    print(f"mean memory size of {fn}: {sum(mem) // len(mem)}")


def cal_results_for_drewer(fn: str):
    time = []
    mem = []
    with open(fn, "r", encoding="utf-8") as f:
        for i, buf in enumerate(f):
            if i != 0 and i % 8 == 0:
                time.append(int(buf.split()[-2]))
            if i != 1 and i % 8 == 1:
                mem.append(int(buf.split()[-2]) * (-1) / 1024.0 // 1024)
    print(time)
    print(mem)
    print(f"mean time of {fn}: {sum(time) // len(time) / 1000}")
    print(f"mean memory size of {fn}: {sum(mem) // len(mem)}")


if __name__ == "__main__":
    args = sys.argv[1:]
    try:
        for i, arg in enumerate(args):
            if "-" not in arg:
                continue
            if arg == "-d":
                fn = args[i + 1]
                cal_results_for_drewer(os.path.join("results", fn))
            elif arg == "-g":
                fn = args[i + 1]
                cal_results_for_graal(os.path.join("results", fn))
            else:
                print("Parameter Error!")
                exit(0)
    except ValueError:
        print("Result Error!")
        exit(0)
