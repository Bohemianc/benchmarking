import os
import shutil
from itertools import product

import formatter
import utilities
import dlp_translater
from sampling_by_pres_mp import Sampling


# def unfolding_deep(seq_pres: list, seq_not_inverse: list, dic_pres: dict, rule_bkt: dict, fn_out_rules: str):
#     pt = seq_pres[-1]
#     if dic_pres[pt] not in rule_bkt:
#         return
#
#     for rule in rule_bkt[dic_pres[pt]]:
#         path, not_inverse = rule
#         for p in path[1:]:
#             if dic_pres[p] in rule_bkt:
#                 seq_pres.append(p)
#                 seq_not_inverse.append(not_inverse)
#                 unfolding_deep(seq, dic_pres, rule_bkt)
#             else:
#                 with open(fn_out_rules, "a", encoding="utf-8") as fo:
#                     f.write(dlp_translater.dlp_writer() + "\n")
#                 return
#
#
# def unfolding_bread():
#     pass
#
#
# def unfolding_rules(fn_src_rules: str, rule_len: int, dic_pres: dict, pts: list, fn_out_rules: str):
#     rules = dlp_translater.dlp_parser(fn_src_rules, rule_len)
#     rule_bkt = {}
#     for rule in rules:
#         path, not_inverse = rule
#         if dic_pres[path[0]] not in rule_bkt:
#             rule_bkt[dic_pres[path[0]]]=[]
#         rule_bkt[dic_pres[path[0]]].append(rule)
#
#     for pt in pts:
#         seq_pres = [pt]
#         seq_not_inverse = []
#         unfolding_search(seq_pres, seq_not_inverse, dic_pres, rule_bkt, fn_out_rules)


# recursion and terminating
# def unfolding(dic_pres: dict, dir_rules: str, fn_flat_rules: str, head: str, body: list, not_inverse: list,
#               limit_rules: int):
#     # len_rule = len(body) + 1  # todo
#     rules_bkt = []
#     rule_id_list = []
#     # print(body)
#     for p in body:
#         if p in dic_pres:
#             fn_sub_rules = os.path.join(dir_rules, "p" + str(dic_pres[p]), "rules.dlp")
#             unfolding(dic_pres, dir_rules, fn_sub_rules, )
#             # fn_rules = os.path.join(dir_rules, "p" + str(dic_pres[p]), "rules.dlp")
#             rules = dlp_translater.dlp_parser(fn_rules, len_rule, limit_rules)
#             rules_bkt.append(rules)
#             rule_id_list.append(range(-1, len(rules)))
#         else:
#             rule_id_list.append(range(-1, 0))
#
#     prod = list(product(*rule_id_list))
#     with open(fn_flat_rules, "w", encoding="utf-8") as f:
#         for r in prod:
#             sub_body = []
#             sub_not_inverse = []
#             for i, rid in enumerate(r):
#                 if rid == -1:
#                     sub_body.append(body[i])
#                     sub_not_inverse.append(not_inverse[i])
#                 else:
#                     sub_body.extend(rules_bkt[i][rid][0][1:])  # i know what it is :(
#                     sub_not_inverse.extend(rules_bkt[i][rid][1])
#             f.write(dlp_translater.dlp_writer(head, sub_body, sub_not_inverse))
#
#
# def sampling_for_query_answering(dic_pres: dict, dir_rules: str, fn_query: str, fn_facts: str,
#                                  limit: int = 100, limit_rules: int = 100000):
#     # load all the SPARQL queries
#     queries = []
#     with open(fn_query, "r", encoding="utf-8") as f:
#         for buf in map(str.split, f):
#             for i in (-4, -3, -2):
#                 buf[i] = filtering.replace_prefix_in_terms(buf[i])
#             if buf[-3] in dic_pres:
#                 fact = buf[-4], buf[-3], buf[-2]
#                 queries.append(fact)
#     print(f"#queries: {len(queries)}")
#
#     cnt = 0
#     for query in queries:
#         s, p, o = query
#         pid = dic_pres[p]
#         fn_rules = os.path.join(dir_rules, "p" + str(pid) + ",dlp")
#         rules = dlp_translater.dlp_parser(fn_rules, rule_len, limit_rules)
#
#         with open(fn_facts, "a", encoding="utf-8") as f:
#             if s == "?uri":
#                 for i, (pres, not_inverse) in enumerate(rules):
#                     pres.reverse()
#                     not_inverse.reverse()
#                     for j in range(len(rules[i][1])):
#                         rules[i][1][j] = not rules[i][1][j]
#
#             for pres, not_inverse in rules:
#                 rule_len = len(pres)
#                 new_entities = set()
#                 if s == "?uri":
#                     new_entities.add(o)
#                 else:
#                     new_entities.add(s)
#                 for i in range(rule_len - 1):
#                     dic_e = {}
#                     for ne in new_entities:
#                         if not_inverse[i]:
#                             pos = 3
#                             tup = (ne, pres[i + 1], "?z")
#                         else:
#                             pos = 4
#                             tup = ("?x", pres[i + 1], ne)
#                         print(tup)
#                         result, indices = q.crawl(tup, pos, limit=limit)
#
#                         if result is not None:
#                             print(f"#facts: {len(result)}")
#
#                             for fact in result:
#                                 fact, is_uri = filtering.extract_triple_from_json(fact, indices)
#                                 if is_uri:
#                                     q.get_new_entities(fact, dic_e, pos)
#                                 f.write(dlp_translater.get_dlp_str(fact))
#                                 f += 1
#                     new_entities.clear()
#                     for e in dic_e:
#                         new_entities.add(e)
#     return cnt
#
#
# # dic_pres: dict of all predicates (not only Pts)
# def sample_data(pts: list, dic_pres: dict, dir_root: str, dir_flat_rules: str, fn_src_queries: str, fn_data: str,
#                 rule_length: int, limit_rules: int):
#     # rule_length = 2  # todo
#     # unfolding rules to flat rules
#     for pid in range(len(pts)):
#         fn_flat_rules = os.path.join(dir_flat_rules, "p" + str(pid) + ".dlp")
#         fn_rules = os.path.join(dir_root, "p" + str(pid), "rules.dlp")
#         rules = dlp_translater.dlp_parser(fn_rules, rule_length, limit_rules)
#         for rule in rules:
#             body, not_inverse = rule[0][1:], rule[1]
#             unfolding(dic_pres, dir_root, fn_flat_rules, pts[pid], body, not_inverse, limit_rules)
#
#     # sampling according to flat rules and queries
#     return sampling_for_query_answering(dic_pres, dir_flat_rules, fn_src_queries, fn_data, 100, 100000)
def dfs(nodes: dict, visited: dict, bad_pairs: set, pt: str, max_dep: int):
    # rm_pres = set()
    dep = 0
    for p in nodes[pt]:
        if p not in nodes and (pt, p) not in bad_pairs:
            dep = 1
        elif p in nodes and (pt, p) not in bad_pairs:
            if visited[p] == 0:
                visited[p] = -1  # visiting
                dep = max(dep, dfs(nodes, visited, bad_pairs, p, max_dep) + 1)
                visited[p] = 1
                if dep > max_dep:
                    dep -= 1
                    bad_pairs.add((pt, p))
                # rm_pres.add(p)
            elif visited[p] == -1:  # recursion
                bad_pairs.add((pt, p))
                # rm_pres.add(p)
    return dep


def merge_and_check(dir_pres: str, dic_p: dict, pts: list, fn_out_rules: str, rule_len: int,
                    rule_dep: int, limit_rules):
    if os.path.exists(fn_out_rules):
        os.remove(fn_out_rules)

    nodes = dict()
    for pt in dic_p:
        pid = dic_p[pt]
        # format_pt = formatter.format_uri(pt, True)
        format_pt = pt
        fn_rules = os.path.join(dir_pres, "p" + str(pid), "rules.dlp")
        rules = dlp_translater.dlp_parser(fn_rules, rule_len, limit_rules)
        for rule in rules:
            pres, _ = rule
            if format_pt not in nodes:
                nodes[format_pt] = set()
            for p in pres[1:]:
                # nodes[format_pt].add(formatter.format_uri(p, True))
                nodes[format_pt].add(p)

    visited = dict()
    for p in dic_p:
        # visited[formatter.format_uri(p, True)] = 0
        visited[p] = 0

    bad_pairs = set()
    for p1 in pts:
        for p2 in pts:
            # bad_pairs.add((formatter.format_uri(p1, True), formatter.format_uri(p2, True)))
            p1_prime = p1
            if "dbpedia.org/ontology/" in p1:
                p1_prime = p1.replace("dbpedia.org/ontology/", "dbpedia.org/property/")
            elif "dbpedia.org/property" in p1:
                p1_prime = p1.replace("dbpedia.org/property/", "dbpedia.org/ontology/")

            p2_prime = p2
            if "dbpedia.org/ontology/" in p2:
                p2_prime = p2.replace("dbpedia.org/ontology/", "dbpedia.org/property/")
            elif "dbpedia.org/property" in p2:
                p2_prime = p2.replace("dbpedia.org/property/", "dbpedia.org/ontology/")

            bad_pairs.add((p1, p2))
            bad_pairs.add((p1, p2_prime))
            bad_pairs.add((p2_prime, p2))
            bad_pairs.add((p1_prime, p2_prime))

    max_dep = 0
    for pt in nodes:
        # format_pt = formatter.format_uri(pt, True)
        format_pt = pt
        visited[format_pt] = -1
        cur_dep = dfs(nodes, visited, bad_pairs, format_pt, rule_dep)
        max_dep = max(max_dep, cur_dep)
        visited[format_pt] = 1
        if cur_dep == rule_dep:
            print(pt)
        if pt in pts:
            print(pt, cur_dep)

        # for it in bad_pairs:
        #     nodes[it[0]].remove(it[1])
    num_rules = 0
    for pt in dic_p:
        pid = dic_p[pt]
        fn_rules = os.path.join(dir_pres, "p" + str(pid), "rules.dlp")
        rules = dlp_translater.dlp_parser(fn_rules, rule_len, limit_rules)
        for rule in rules:
            pres, not_inverse = rule
            flag = True
            for p in pres[1:]:
                # if (formatter.format_uri(pt, True), formatter.format_uri(p, True)) in bad_pairs:
                if (pt, p) in bad_pairs:
                    flag = False
                    break
            if flag:
                num_rules += 1
                with open(fn_out_rules, "a", encoding="utf-8") as fr:
                    fr.write(dlp_translater.dlp_writer(pt, pres[1:], not_inverse))

    return max_dep, num_rules


def hash_path(path: list, dic_p: dict):
    n = len(dic_p)
    res = 0
    for p in path:
        res = res * n + dic_p[p]
    return res


def search_rules(is_ok: dict, dir_p: str, dic_p: dict, path: list, rule_len: int, rule_dep: int,
                 fn_out: str,
                 limit_rules: int = 100000):
    # if len(is_ok) == 1156: # todo
    #     return
    if len(path) >= 2 * rule_len:
        return
    pname = path[-1]
    pid = dic_p[pname]
    fn_rules = os.path.join(dir_p, "p" + str(pid), "rules.dlp")
    if not os.path.exists(fn_rules):
        return

    rules = dlp_translater.dlp_parser(fn_rules, rule_len, limit_rules)
    for rule in rules:
        pres, not_inverse = rule[0][1:], rule[1]
        not_recursive = True
        for pre in pres:
            if pre in path:
                not_recursive = False
                is_ok[(pname, tuple(pres), tuple(not_inverse))] = False
                break
        if not_recursive:
            if len(path) > rule_dep and path[-2] < path[-1]:
                is_ok[(pname, tuple(pres), tuple(not_inverse))] = False
            if (pname, tuple(pres), tuple(not_inverse)) not in is_ok:
                is_ok[(pname, tuple(pres), tuple(not_inverse))] = True
            # if len(path) < rule_dep:
            for pre in pres:
                if pre in dic_p:
                    path_new = path.copy()
                    path_new.append(pre)
                    search_rules(is_ok, dir_p, dic_p, path_new, rule_len, rule_dep, fn_out,
                                 limit_rules)


def merge_rules_without_recursion(dir_pres: str, dic_p: dict, pts: list, fn_out_rules: str, rule_len: int,
                                  rule_dep: int, limit_rules: int = 100000):
    if os.path.exists(fn_out_rules):
        os.remove(fn_out_rules)

    tot_rules = 0
    is_ok = dict()
    for pt in pts:
        # s = set()
        # s.add(hash_path([pt], dic_p))
        search_rules(is_ok, dir_pres, dic_p, [pt], rule_len, rule_dep, fn_out_rules, limit_rules)
    with open(fn_out_rules, "w", encoding="utf-8") as fo:
        for tup in is_ok:
            v = is_ok[tup]
            if v:
                tot_rules += 1
                fo.write(dlp_translater.dlp_writer(*tup))
    return tot_rules


def cal_depth_search(nodes: dict, pt: str):
    if pt not in nodes:
        return 0
    dep = 0
    for p in nodes[pt]:
        dep = max(dep, cal_depth_search(nodes, p) + 1)
    return dep


def cal_depth(fn_rules: str, rule_len: int):
    rules = dlp_translater.dlp_parser(fn_rules, rule_len)
    pts = set()
    nodes = dict()
    for rule in rules:
        pres, _ = rule
        pt = pres[0]
        pts.add(pt)
        if pt not in nodes:
            nodes[pt] = set()
        for p in pres[1:]:
            nodes[pt].add(p)

    ans = 0
    for pt in pts:
        # temp = cal_depth_search(nodes, pt)
        # if temp == 2:
        #     print(pt)
        ans = max(ans, cal_depth_search(nodes, pt))

    return ans


def get_pres_from_rules(fn_rules: str, rule_len: int, limit_rules):
    rules = dlp_translater.dlp_parser(fn_rules, rule_len, limit_rules)
    set_pres = set()
    for pres, not_inverse in rules:
        for p in pres:
            set_pres.add(p)
    return set_pres


# don't tell the difference between relevant facts and irrelevant ones.
def sampling_for_query_answering(test_id: str, dir_data: str, sampled_pres: set, fn_result: str, fn_rules: str,
                                 rule_len: int,
                                 limit_rules: 100000):
    cnt_facts = 0
    dir_data_self = os.path.join(test_id, "data")
    if os.path.exists(dir_data_self):
        shutil.rmtree(dir_data_self)
    os.mkdir(dir_data_self)

    set_pres = get_pres_from_rules(fn_rules, rule_len, limit_rules)
    li_pres = []
    for p in set_pres:
        data_fn = formatter.format_uri(p, True) + ".dlp"
        if data_fn not in sampled_pres:
            li_pres.append(p)
        else:
            cnt_facts += utilities.get_lines(os.path.join(dir_data, data_fn))
    if len(li_pres) > 0:
        sampling = Sampling(dir_data, fn_result)
        cnt_facts += sampling.main(li_pres)
    with open(fn_result, "a", encoding="utf-8") as f:
        f.write("#facts (inaccurate): %d\n" % cnt_facts)

    # store data in test_id/data/
    for p in set_pres:
        data_fn = formatter.format_uri(p, True) + ".dlp"
        shutil.copyfile(os.path.join(dir_data, data_fn), os.path.join(dir_data_self, data_fn))
    return cnt_facts


def get_num_of_facts(dir_data: str):
    li = os.listdir(dir_data)
    num = 0
    for it in li:
        if "." in it:
            num += utilities.get_lines(os.path.join(dir_data, it))
    return num


def lessen_facts(dir_in: str, dir_out: str, num_out: int, fn_result):
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)

    num_in = get_num_of_facts(dir_in)
    print("#facts before lessening: " + str(num_in))
    with open(fn_result, "a", encoding="utf-8") as fr:
        fr.write("#facts before lessening: " + str(num_in) + "\n")

    tot = 0
    li = os.listdir(dir_in)
    fns = []
    for it in li:
        if "." in it:
            fns.append(it)

    for i, fn in enumerate(fns):
        fin = os.path.join(dir_in, fn)
        fout = os.path.join(dir_out, fn)
        lines1 = utilities.get_lines(fin)
        lines2 = int(1.0 * num_out / num_in * lines1 + 0.5)
        if i + 1 == len(fns):
            lines2 = num_out - tot
        utilities.get_partof_file(fin, fout, 0, lines2)
        tot += lines2
    print("#facts after lessening: " + str(tot))


def get_data(test_id: str, num_out: str):
    dir_data = os.path.join(test_id, "data")
    formatter.format_data_csv(dir_data)
    formatter.format_data_dlp(dir_data)
    fn_result = os.path.join(test_id, "results.txt")
    lessen_facts(os.path.join(dir_data, "dlp"), os.path.join(dir_data, "dlp1"), num_out, fn_result)
    lessen_facts(os.path.join(dir_data, "csv"), os.path.join(dir_data, "csv1"), num_out, fn_result)


if __name__ == "__main__":
    lrs = [None] * 7
    lrs[1] = [3]
    lrs[2] = [3, 2]
    lrs[3] = [3]
    lrs[4] = [100, 8, 5, 3]
    lrs[5] = [10, 5, 3, 2, 1]
    lrs[6] = [8, 5, 3, 2, 1]
    rds = [0, 1, 5, 10, 1, 5, 10]
    rls = [0, 2, 2, 2, 3, 3, 3]
    test_ids = ["", "test_v9_e1", "test_v9_e2_lr=3", "test_v9_e3", "test_v9_e4_bm=200", "test_v9_e5", "test_v9_e6_lr=8"]
    fn_rules = ["", "rules_1_lr=30.dlp", "rules_lr=3.dlp", "rules_1_lr=3.dlp", "rules_1_lr=100.dlp", "rules_1_lr=1.dlp",
                "rules_3_lr=2.dlp"]
    # true_lrs = [0, 30, 3, 3,]
    #
    # pres = []
    # with open(os.path.join("dataset", "predicates1961-5.txt"), "r", encoding="utf-8") as f1:
    #     for buf in f1:
    #         pres.append(buf.strip("\n"))
    #
    # for i in range(6, 7):
    #     test_id = test_ids[i]
    #     dic_p = dict()
    #     with open(os.path.join(test_id, "predicates.txt"), "r", encoding="utf-8") as fp:
    #         for buf in fp:
    #             k, v = buf.split()
    #             dic_p[k] = int(v)
    #
    #     for lr in lrs[i]:
    #         fn_out_rules = os.path.join(test_id, "rules", "rules_5_lr=" + str(lr) + ".dlp")
    #         print("e" + str(i), "lr=" + str(lr),
    #               merge_and_check(test_id, dic_p, pres, fn_out_rules, rls[i], rds[i], lr))

    # cut down the data size of e4 to 1000000 for drewer
    # get_data("test_v9_e5",5000000)
    # lessen_facts(os.path.join("test_v9_e5", "data", "csv"), os.path.join("test_v9_e4", "data", "csv2"), 50000,
    #              os.path.join("test_v9_e4", "results.txt"))
    # for i in range(6, 7):
    #     print(test_ids[i])
    #     test_id = test_ids[i]
    #     sampled_pres = set(os.listdir("data"))
    #     sampling_for_query_answering(test_id, "data", sampled_pres, os.path.join(test_id, "results.txt"),
    #                                  os.path.join(test_id, "rules", fn_rules[i]), rls[i], 100000)
    #     get_data(test_id, 5000000)
    lessen_facts(os.path.join(test_ids[6], "data", "csv"), os.path.join(test_ids[6], "data", "csv6"), 20000000,
                 os.path.join(test_ids[6], "results.txt"))
    lessen_facts(os.path.join(test_ids[6], "data", "dlp"), os.path.join(test_ids[6], "data", "dlp6"), 20000000,
                 os.path.join(test_ids[6], "results.txt"))
    # print(cal_depth(os.path.join("test_v9_e2","rules","rules_newmc_lr=2.dlp"),2))
