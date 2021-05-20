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

# todo: unify the pattern to match rules of any length
pattern_rules=re.compile(r'(\S*?)\((.*?),(.*?)\)')
# pattern_2 = re.compile(r'(.*?)\((.*?),(.*?)\) :- (.*?)\((.*?),(.*?)\)\.')
# pattern_3 = re.compile(r'(.*?)\((.*?),(.*?)\) :-[ (.*?)\((.*?),(.*?)\),]* (.*?)\((.*?),(.*?)\)\.')
# pattern_4 = re.compile(r'(.*?)\((.*?),(.*?)\) :- (.*?)\((.*?),(.*?)\), (.*?)\((.*?),(.*?)\), (.*?)\((.*?),(.*?)\)\.')


def dlp_parser(fn: str, rl: int):
    res = []
    params = ["X"]
    for i in range(1, rl - 1):
        params.append("Z" + str(i))
    with open(fn, "r", encoding="utf-8") as f:
        for buf in f:
            result = pattern_rules.findall(buf.strip("\n"))
            try:
                item1 = [tup[0] for tup in result]
            except Exception:
                print("Error when matching rules in dlp_parser()!")
                print(fn)
                print(result)
                exit(111)
            item2 = []
            for i in range(1, rl):
                item2.append(result[i][1] == params[i - 1])
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
    # # === get data for query answering ===
    # dir_onto = "dbpedia\\ontology"
    # dir_info = "dbpedia\\infobox"
    #
    # fns = [
    #     # "instance-types_lang=en_specific.ttl",
    #     # "instance-types_lang=en_transitive.ttl",
    #     # "mappingbased-literals_lang=en.ttl",
    #     "mappingbased-objects_lang=en.ttl",
    #     # "specific-mappingbased-properties_lang=en.ttl",
    # ]
    # paths = [os.path.join(dir_onto, x) for x in fns]
    # # paths.append(os.path.join(dir_info, "infobox-properties_lang=en.ttl"))
    # # for f in paths:
    # #     print(f)
    # #     ttl2dlp(f, "dbpedia\\data4qa\\facts_mapping.dlp")
    # # ttl2dlp("test_v5\\p0_lp10000\\facts.ttl","dbpedia\\data4qa\\facts_p0.dlp")
    #
    # ttl2dlp("0422\\facts.ttl", "0422\\facts.dlp")
    # # delete lines including '\' in *.dlp
    # delete_illigal_lines(
    #     "0422\\facts.dlp", "0422\\facts_p0_10000.dlp"
    # )
    # rules = dlp_parser(os.path.join("test_v7_e3","p0","rules.dlp"), 3)
    # print(rules)
    # print(len(rules), len(rules[0]), len(rules[0][0]))
    rules=dlp_parser("1.txt",5)
    print(rules[0])
