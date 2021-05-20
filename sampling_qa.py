import os
from itertools import product

import get_facts as q
import dlp_translater
import filtering
import utilities


def unfolding(dic_pres: dict, dir_rules: str, fn_flat_rules: str, head: str, body: list, not_inverse: list):
    len_rule = len(body) + 1  # todo
    rules_bkt = []
    rule_id_list = []
    print(body)
    for p in body:
        fn_query = os.path.join(dir_rules, "p" + str(dic_pres[p]), "rules.dlp")
        rules = dlp_translater.dlp_parser(fn_query, len_rule)
        rules_bkt.append(rules)
        rule_id_list.append(range(-1, len(rules)))
    prod = list(product(*rule_id_list))
    with open(fn_flat_rules, "w", encoding="utf-8") as f:
        for r in prod:
            sub_body = []
            sub_not_inverse = []
            for i, rid in enumerate(r):
                if rid == -1:
                    sub_body.append(body[i])
                    sub_not_inverse.append(not_inverse[i])
                else:
                    sub_body.extend(rules_bkt[i][rid][0][1:])  # i know what it is :(
                    sub_not_inverse.extend(rules_bkt[i][rid][1])
            f.write(dlp_translater.dlp_writer(head, sub_body, sub_not_inverse))


def sampling_for_query_answering(dic_pres: dict, dir_root: str, fn_query: str, fn_facts: str, rule_len: int,
                                 limit: int = 100):
    # load all the SPARQL queries
    queries = []
    with open(fn_query, "r", encoding="utf-8") as f:
        for buf in map(str.split, f):
            for i in (-4, -3, -2):
                buf[i] = filtering.replace_prefix_in_terms(buf[i])
            if buf[-3] in dic_pres:
                fact = buf[-4], buf[-3], buf[-2]
                queries.append(fact)
    print(f"#queries: {len(queries)}")

    for query in queries:
        s, p, o = query
        pid = dic_pres[p]
        dir_pre = os.path.join(dir_root, "p" + str(pid))
        fn_rules = os.path.join(dir_pre, "rules.dlp")
        rules = dlp_translater.dlp_parser(fn_rules, rule_len)

        with open(fn_facts, "a", encoding="utf-8") as f:
            if s == "?uri":
                for i, (pres, not_inverse) in enumerate(rules):
                    pres.reverse()
                    not_inverse.reverse()
                    for j in range(len(rules[i][1])):
                        rules[i][1][j] = not rules[i][1][j]

            for pres, not_inverse in rules:
                new_entities = set()
                if s == "?uri":
                    new_entities.add(o)
                else:
                    new_entities.add(s)
                for i in range(rule_len - 1):
                    dic_e = {}
                    for ne in new_entities:
                        if not_inverse[i]:
                            pos = 3
                            tup = (ne, pres[i + 1], "?z")
                        else:
                            pos = 4
                            tup = ("?x", pres[i + 1], ne)
                        print(tup)
                        result, indices = q.crawl(tup, pos, limit=limit)

                        if result is not None:
                            print(f"#facts: {len(result)}")

                            for fact in result:
                                fact, is_uri = filtering.extract_triple_from_json(fact, indices)
                                if is_uri:
                                    q.get_new_entities(fact, dic_e, pos)
                                f.write(dlp_translater.get_dlp_str(fact))
                    new_entities.clear()
                    for e in dic_e:
                        new_entities.add(e)


# dic_pres: dict of all predicates (not only Pts)
def sample_data(pts: list, dic_pres: dict, dir_root: str, dir_flat_rules: str, fn_src_queries: str, fn_data: str,
                rule_length: int):
    # rule_length = 2  # todo
    # unfolding rules to flat rules
    for pid in range(len(pts)):
        fn_flat_rules = os.path.join(dir_flat_rules, "p" + str(pid) + ".dlp")
        fn_rules = os.path.join(dir_root, "p" + str(pid), "rules.dlp")
        rules = dlp_translater.dlp_parser(fn_rules, rule_length)
        for rule in rules:
            body, not_inverse = rule[0][1:], rule[1]
            unfolding(dic_pres, dir_root, fn_flat_rules, pts[pid], body, not_inverse)

    # sample_queries(set(pts), fn_src_queries, fn_queries)
    # sampling according to flat rules and queries
    sampling_for_query_answering(dic_pres, dir_root, fn_src_queries, fn_data, rule_length, 100)


def sample_queries(set_pts: set, fn_query: str, fn_out: str):
    with open(fn_query, "r", encoding="utf-8") as f1, open(fn_out, "w", encoding="utf-8") as f2:
        for buf in f1:
            pre = filtering.replace_prefix_in_terms(buf.split()[-3])
            if pre in set_pts:
                f2.write(buf)


# deprecated
def merge_rules(dir_pres: str, num_pres: int, fn_rules: str):
    fns = []
    for i in range(num_pres):
        fns.append(os.path.join(dir_pres, "p" + str(i), "rules.dlp"))
    utilities.merge_files(fns, fn_rules)


def hash_path(path: list, dic_p: dict):
    n = len(dic_p)
    res = 0
    for p in path:
        res = res * n + dic_p[p]
    return res


def search_rules(searched: set, dir_p: str, dic_p: dict, path: list, rule_len: int, rule_dep: int, fn_out: str):
    print(path)
    pname = path[-1]
    pid = dic_p[pname]
    fn_rules = os.path.join(dir_p, "p" + str(pid), "rules.dlp")
    if not os.path.exists(fn_rules):
        return

    rules = dlp_translater.dlp_parser(fn_rules, rule_len)
    for rule in rules:
        pres, not_inverse = rule[0][1:], rule[1]
        not_recursive = True
        for pre in pres:
            if pre in path:
                not_recursive = False
                break
        if not_recursive:
            with open(fn_out, "a", encoding="utf-8") as fo:
                if pname.replace("ontology","property") not in dic_p:
                    fo.write(dlp_translater.dlp_writer(pname, pres, not_inverse))
                    # print("a rule!")
            if len(path) < rule_dep:
                for pre in pres:
                    if pre in dic_p:
                        path_new = path.copy()
                        path_new.append(pre)
                        hash_value = hash_path(path_new, dic_p)
                        if hash_value not in searched:
                            searched.add(hash_value)
                            # print(searched)
                            search_rules(searched, dir_p, dic_p, path_new, rule_len, rule_dep, fn_out)
                            print(hash_value)


def merge_rules_without_recursion(dir_pres: str, dic_p: dict, pts: list, fn_out_rules: str, rule_len: int,
                                  rule_dep: int):
    if os.path.exists(fn_out_rules):
        os.remove(fn_out_rules)

    for pt in pts:
        pid = dic_p[pt]
        # fn_rules = os.path.join(dir_pres, "p" + str(pid), "rules.dlp")
        # with open(fn_rules, "r", encoding="utf-8") as fr, open(fn_out_rules, "a", encoding="utf-8") as fo:
        #     for buf in fr:
        #         fo.write(buf)
        s = set()
        s.add(hash_path([pt],dic_p))
        search_rules(s, dir_pres, dic_p, [pt], rule_len, rule_dep, fn_out_rules)

# def unify_dbo_dbp()

if __name__ == "__main__":
    dir_root = "test_v7_e10"
    rule_len = 2
    rule_dep = 5
    dir_rules = os.path.join(dir_root, "rules")
    dir_flat_rules = os.path.join(dir_root, "flat_rules")
    dir_data = os.path.join(dir_root, "data")
    dir_queries = os.path.join(dir_root, "queries")
    fn_src_queries = os.path.join("dataset", "sparqls_top10.txt")
    # fn_queries = os.path.join(dir_queries, "queries.txt")
    fn_data = os.path.join(dir_data, "facts.dlp")
    fn_rules = os.path.join(dir_rules, "rules.dlp")  # merged rules

    # store all the predicates in the phase of rule learning
    dic_p = {}
    with open(os.path.join(dir_root, "predicates.txt")) as f:
        for buf in f:
        # for _ in range(10):
        #     buf=f.readline()
            k, v = buf.strip("\n").split()
            dic_p[k] = int(v)

    pts = []
    with open(os.path.join("dataset", "predicates_top10.txt")) as f:
        for buf in f:
            pts.append(buf.strip("\n"))

    # sample_data(pts, dic_p, dir_root, dir_flat_rules, fn_src_queries, fn_data, rule_len)
    # merge_rules(dir_root, 10, fn_rules)
    merge_rules_without_recursion(dir_root, dic_p, pts, fn_rules, rule_len, rule_dep)
