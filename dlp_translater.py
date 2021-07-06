import traceback

import filtering
import os


def get_dlp_str(fact: list):
    # fact[2]=fact[2].replace()
    return fact[1] + "(" + fact[0] + "," + fact[2] + ") .\n"


def ttl2dlp(infile: str, outfile: str):
    with open(infile, "r", encoding="utf-8") as f1, open(
            outfile, "w", encoding="utf-8"
    ) as f2:
        cnt = 0
        for buf in f1:
            fact = filtering.extract_triple_from_ttl(buf)
            if fact is not None:
                cnt += 1
                f2.write(get_dlp_str(fact))
        print("#facts: " + str(cnt))


def ttl2dlp_with_filtering(infile: str, outfile: str):
    with open(infile, "r", encoding="utf-8") as f1, open(
            outfile, "w", encoding="utf-8"
    ) as f2:
        cnt = 0
        tot = 0
        for buf in f1:
            tot += 1
            fact = filtering.extract_triple_from_ttl(buf)
            if fact is not None:
                if filtering.filter_fact(fact):
                    cnt += 1
                    f2.write(get_dlp_str(fact))
    print(f"after filtering: {cnt}/{tot}")


# deprecated
def rule2dlp(infilelist: list, outfile: str):
    total = 0
    num_valid_rules = 0
    with open(outfile, "w", encoding="utf-8") as f2:
        for infile in infilelist:
            cur_num_vr = 0
            with open(infile, "r", encoding="utf-8") as f1:
                pt = f1.readline().split(" ")[0]
                num = int(f1.readline().strip("\n").split(" ")[-1])
                total += num
                # print(pt, num)
                for _ in range(num):
                    buf = f1.readline().split(" ")
                    atom = [buf[-6], buf[-3]]
                    is_inverse = ["^-1" in buf[x] for x in (-5, -2)]
                    params = ["(X,Z)", "(Z,Y)"]

                    # recursion is not allowed.
                    if atom[0] == pt or atom[1] == pt:
                        continue

                    # process the case that the predicate is inverse.
                    if is_inverse[0]:
                        params[0] = "(Z,X)"
                    if is_inverse[1]:
                        params[1] = "(Y,Z)"

                    num_valid_rules += 1
                    cur_num_vr += 1
                    f2.write(
                        pt
                        + "(X,Y) :- "
                        + atom[0]
                        + params[0]
                        + ", "
                        + atom[1]
                        + params[1]
                        + ".\n"
                    )
                print("%d/%d" % (cur_num_vr, num))
        # vertebrate(X) :- animal(X), has_part(X,Y), skeleton(Y).
    print("total: %d/%d" % (num_valid_rules, total))


def delete_illigal_lines(infile: str, outfile: str):
    with open(infile, "r", encoding="utf-8") as f1, open(
            outfile, "w", encoding="utf-8"
    ) as f2:
        for buf in f1:
            if "\\" not in buf:
                f2.write(buf)


import re

# match rules of any length
pattern_rules = re.compile(r'(\S*?)\((.*?),(.*?)\)')
pattern_facts_dlp = re.compile(r'(<.*?>)\((<.*?>),(.*)\)')


# pattern_2 = re.compile(r'(.*?)\((.*?),(.*?)\) :- (.*?)\((.*?),(.*?)\)\.')
# pattern_3 = re.compile(r'(.*?)\((.*?),(.*?)\) :-[ (.*?)\((.*?),(.*?)\),]* (.*?)\((.*?),(.*?)\)\.')
# pattern_4 = re.compile(r'(.*?)\((.*?),(.*?)\) :- (.*?)\((.*?),(.*?)\), (.*?)\((.*?),(.*?)\), (.*?)\((.*?),(.*?)\)\.')


def dlp2fact(line: str):
    # print(line)
    result = pattern_facts_dlp.findall(line)
    if len(result) > 0:
        return [result[0][1], result[0][0], result[0][2]]
    return None


def dlp2facts(infile: str):
    facts = []
    with open(infile, "r", encoding="utf-8") as f:
        for buf in f:
            fact = dlp2fact(buf.strip("\n"))
            if fact is not None:
                facts.append(fact)
    return facts


def dlp_parser(fn: str, rl: int, limit_rules: int = 100000):
    res = []
    params = ["X"]
    for i in range(1, rl - 1):
        params.append("Z" + str(i))
    with open(fn, "r", encoding="utf-8") as f:
        # for buf in f:
        file = f.readlines()
        for i in range(min(len(file), limit_rules)):
            buf = file[i]
            result = pattern_rules.findall(buf.strip("\n"))
            try:
                item1 = [tup[0] for tup in result]
            except Exception:
                print("Error when matching rules in dlp_parser()!")
                print(fn)
                print(result)
                exit(111)
            item2 = []
            for j in range(1, rl):
                # print(result, params, i)
                item2.append(result[j][1] == params[j - 1])
            res.append([item1, item2])
    return res


def dlp_writer(pt: str, pres: list, not_inverse: list):
    path_len = len(pres)
    if path_len == 1:
        params = [["X", "Y"]]
    else:
        params = [["X", "Z1"]]
        for i in range(1, path_len - 1):
            params.append(["Z" + str(i), "Z" + str(i + 1)])
        params.append(["Z" + str(path_len - 1), "Y"])

    str_rule = pt + "(X,Y) :- "
    for i in range(path_len):
        str_rule += pres[i] + "("
        if not not_inverse[i]:
            params[i][0], params[i][1] = params[i][1], params[i][0]
        str_rule += params[i][0] + "," + params[i][1]
        if i == path_len - 1:
            str_rule += ").\n"
        else:
            str_rule += "), "
    return str_rule


if __name__ == "__main__":
    # print(dlp_parser(os.path.join("test_v8","p0","rules.dlp"),2)[0][0])
    pass
