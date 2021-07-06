import os
import logging
import sys

import filtering
import formatter
import rule_learning
import sampling_qa


def get_ents_and_pres(fn_sparqls: str, fn_entity, fn_predicate):
    with open(fn_sparqls, "r", encoding="utf-8", ) as f1, open(
            fn_entity, "w", encoding="utf-8"
    ) as entity, open(fn_predicate, "w", encoding="utf-8") as predicate:
        se = set()
        sp = set()
        for buf in f1:
            li = buf.split(" ")
            for i in range(5, len(li) - 1, 4):
                if "?" not in li[i]:
                    se.add(filtering.replace_prefix_in_terms(li[i]))
                if "?" not in li[i + 2]:
                    se.add(filtering.replace_prefix_in_terms(li[i + 2]))
                sp.add(filtering.replace_prefix_in_terms(li[i + 1]))
        for it in se:
            entity.write(it + "\n")
        for it in sp:
            predicate.write(it + "\n")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ====================== set or input parameters ===================================== #
    test_id = "test_v9_e6_bm=100"
    dataset_dir = lambda x: os.path.join("dataset", x)
    # NUM_QUERIES = 10
    # parameters of rule learning
    BEAM_SIZE = 100
    RULE_LEN = 3  # greater or equal to 2
    RULE_DEP = 10
    LIMIT_SAMPLING = 100
    LIMIT_PREDICATE = 1000
    MAX_NEW_ENTITIES = 3000
    # parameters of merging rules and sampling4qa
    LIMIT_RULES = 10
    # input parameters
    # args = sys.argv[1:]
    # try:
    #     for i, arg in enumerate(args):
    #         if "-" not in arg:
    #             continue
    #         if arg == "-d":
    #             test_id = args[i + 1]
    #         elif arg == "-nq":
    #             NUM_QUERIES = int(args[i + 1])
    #         elif arg == "-bs":
    #             BEAM_SIZE = int(args[i + 1])
    #         elif arg == "-rl":
    #             RULE_LEN = int(args[i + 1])
    #         elif arg == "-rd":
    #             RULE_DEP = int(args[i + 1])
    #         elif arg == "-ls":
    #             LIMIT_SAMPLING = int(args[i + 1])
    #         elif arg == "-lp":
    #             LIMIT_PREDICATE = int(args[i + 1])
    #         elif arg == "-mne":
    #             MAX_NEW_ENTITIES = int(args[i + 1])
    #         elif arg == "-lr":
    #             LIMIT_RULES = int(args[i + 1])
    #         else:
    #             print("Parameter Error!")
    #             exit(0)
    # except ValueError:
    #     print("Parameter Error!")
    #     exit(0)

    if not os.path.exists(test_id):
        os.mkdir(test_id)
    dir_data = os.path.join(test_id, "data")
    dir_rules = os.path.join(test_id, "rules")
    fn_rules = os.path.join(dir_rules, "rules_lr=" + str(LIMIT_RULES) + ".dlp")
    if not os.path.exists(dir_rules):
        os.mkdir(dir_rules)
    MAX_ITERATION = max(1, RULE_LEN - 2)

    postfix_str = "1961-5.txt"
    fn_src_queries = dataset_dir("sparql" + postfix_str)
    fn_q_pres = dataset_dir("predicates" + postfix_str)
    fn_q_ents = dataset_dir("entities" + postfix_str)

    # record settings
    fn_result_total = os.path.join(test_id, "results.txt")
    with open(fn_result_total, "a", encoding="utf-8") as f_result:
        f_result.write(f"query file: {fn_src_queries}\n")
        f_result.write(f"beam size: {BEAM_SIZE}\n")
        f_result.write(f"rule length: {RULE_LEN}\n")
        f_result.write(f"rule depth: {RULE_DEP}\n")
        f_result.write(f"limit (predicates): {LIMIT_PREDICATE}\n")
        f_result.write(f"limit (sampling by entities): {LIMIT_SAMPLING}\n")
        f_result.write(f"max new entities: {MAX_NEW_ENTITIES}\n")
        f_result.write(f"limit rules: {LIMIT_RULES}\n")
        f_result.write("\n")
    # ====================== select queries and get pres and entities ==================== #
    # utilities.get_partof_file(dataset_dir("sparqls.txt"), fn_src_queries, 0, NUM_QUERIES)
    get_ents_and_pres(fn_src_queries, fn_q_ents, fn_q_pres)

    # ====================== rule learning =============================================== #
    rule_learning.rule_learning(test_id, fn_q_pres, fn_q_ents, BEAM_SIZE, RULE_LEN, RULE_DEP, MAX_ITERATION,
                                LIMIT_SAMPLING, LIMIT_PREDICATE,
                                MAX_NEW_ENTITIES, LIMIT_RULES)

    # =========== merge rules, eliminating recursion and sampling for query answering ==== #
    # store all the predicates in the phase of rule learning
    logging.info("Begin to merge rules without recursion.")
    dic_p = {}
    # rule_learning() stores the pre dict in "predicates.txt"
    with open(os.path.join(test_id, "predicates.txt"), "r", encoding="utf-8") as f:
        for buf in f:
            k, v = buf.strip("\n").split()
            dic_p[k] = int(v)

    # pres in queries
    pts = []
    with open(fn_q_pres, "r", encoding="utf-8") as f:
        for buf in f:
            pts.append(buf.strip("\n"))

    true_rd, num_rules = sampling_qa.merge_and_check(test_id, dic_p, pts, fn_rules, RULE_LEN, RULE_DEP,
                                                     LIMIT_RULES)
    with open(fn_result_total, "a", encoding="utf-8") as fo:
        fo.write(f"#rules without recursion: {num_rules}\n")
        fo.write(f"#true rule depth: {true_rd}\n")
        fo.write("\n")
    logging.info("End to merge rules without recursion.")

    # logging.info("Begin to sampling data.")
    # sampled_pres = set(os.listdir("data"))
    # sampling_qa.sampling_for_query_answering(test_id, "data", sampled_pres, fn_result_total, fn_rules, RULE_LEN)
    # sampling_qa.get_data(test_id, 5000000)
    # logging.info("End to sampling data.")
