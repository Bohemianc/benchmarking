import time

import dlp_translater
import get_facts as q
import sampling_mp
import mapping
from embedding import train_embedding

# import hashlib
import os
import logging
import numpy as np
import heapq
import copy
from scipy import sparse
import gc


# def unique_facts(infile: str, outfile: str):
#     # limit: 6710w lines of data
#     def gen_md5(data):
#         md5 = hashlib.md5()
#         md5.update(data.encode("utf-8"))
#         return md5.hexdigest()
#
#     md5s = set()
#
#     with open(infile, "r", encoding="utf-8") as f1, open(
#             outfile, "a", encoding="utf-8"
#     ) as f2:
#         buf = f1.readlines()
#         md5 = gen_md5(buf)
#         if md5 not in md5s:
#             f2.write(buf)
#     print(len(md5s))


def cal_argument_embedding(
        embedding_ent: np.ndarray, embedding_pre: np.ndarray, facts: list
):
    embedding_arg_s = np.zeros(embedding_pre.shape, dtype=np.float32)
    embedding_arg_o = np.zeros(embedding_pre.shape, dtype=np.float32)
    num_pre = embedding_pre.shape[0]
    # !!!fact: h,t,r respectively for r(h,t)
    for cur_h, cur_t, cur_r in facts:
        if cur_r % 2 == 1:
            # the predicate is the inverse of the last one
            # half the time cost of argument embedding
            continue
        embedding_arg_s[cur_r] = np.add(embedding_arg_s[cur_r], embedding_ent[cur_h])
        embedding_arg_o[cur_r] = np.add(embedding_arg_o[cur_r], embedding_ent[cur_t])

    embedding_arg_s = embedding_arg_s / len(facts)
    embedding_arg_o = embedding_arg_o / len(facts)

    for i in range(1, num_pre, 2):
        embedding_arg_s[i] = embedding_arg_o[i - 1]
        embedding_arg_o[i] = embedding_arg_s[i - 1]

    return embedding_arg_s, embedding_arg_o


def cal_similarity(a: np.ndarray, b: np.ndarray, axis=None):
    return np.exp(-np.linalg.norm(a - b, axis=axis))


def refine_by_f1_score(pt: int, embedding_pre: np.ndarray, seq: list):
    candi_size = len(seq)
    path_encoding = []
    for i in range(candi_size):
        path_encoding.append(sum([embedding_pre[x] for x in seq[i]]))
    path_encoding = np.array(path_encoding)
    path_sim = list(cal_similarity(path_encoding, embedding_pre[pt], axis=1))
    # top_sim_values = heapq.nlargest(candi_size // 2, path_sim)
    # top_sim_keys = list(map(path_sim.index, top_sim_values))
    top_sim_keys = heapq.nlargest(
        candi_size // 2, range(len(path_sim)), path_sim.__getitem__
    )
    return list(map(seq.__getitem__, top_sim_keys))


def rule_search(
        pt: int,
        embedding_pre: np.ndarray,
        embedding_arg_s: np.ndarray,
        embedding_arg_o: np.ndarray,
        beam_size: int,
        rule_len: int,
):
    num_pre = embedding_arg_s.shape[0]
    candi_size = min(beam_size, num_pre)

    # store pathes, i.e., predicate sequences
    seq = []
    for i in range(candi_size):
        seq.append([])
        # seq[i].append(candi_keys[i])

    candi_keys = []
    candi_values = []
    # iteration
    for it in range(rule_len - 1):
        print("Finding predicate " + str(it) + "...")

        if it == 0:
            # calculate f2_loc(Pt^s,P1^s)
            # f2_loc.shape = (num_pres,)
            f2_loc = cal_similarity(embedding_arg_s[pt], embedding_arg_s, axis=1)
            f2_loc[pt] = 0.0
            # candi_values.shape = (candi_size,)
            # candi_values = heapq.nlargest(candi_size, f2_loc)
            # candi_keys = heapq.nlargest(candi_size, range(len(f2_loc)), f2_loc.take)
            # f2_loc=f2_loc.reshape((1,-1))
        else:
            # get the similarity matrix
            candi_embedding = np.array([embedding_arg_o[x] for x in candi_keys])
            print("Calculating the similarity matrix...")
            import gc

            gc.collect()
            # f2_loc.shape = (candi_size * num_pres)
            f2_loc = cal_similarity(
                embedding_arg_s.reshape(
                    (1, embedding_arg_s.shape[0], embedding_arg_s.shape[1])
                ),
                candi_embedding.reshape((candi_size, 1, candi_embedding.shape[1])),
                axis=2,
            )

            # to avoid two adjacent ps are the inverse of each other.
            for i in range(candi_size):
                pid = candi_keys[i]
                if pid % 2 == 0:
                    f2_loc[i][pid + 1] = 0.0
                else:
                    f2_loc[i][pid - 1] = 0.0

            f2_loc = np.array(candi_values).reshape(candi_size, 1) + f2_loc

        if it == rule_len - 2:
            # cal f1_loc(pn^o,pt^o)
            # if it==0:

            f2_loc_oo = cal_similarity(embedding_arg_o, embedding_arg_o[pt], axis=1)
            f2_loc_oo[pt] = 0.0
            f2_loc = f2_loc + f2_loc_oo.reshape((1, -1))
            del f2_loc_oo

        f2_loc = f2_loc.flatten()
        print("Finding top k values....")
        candi_values = heapq.nlargest(candi_size, f2_loc)
        print("Getting candicate keys...")
        candi_keys = heapq.nlargest(candi_size, range(len(f2_loc)), f2_loc.take)

        # be careful for deep copy of lists
        print("Updating the predicate sequence...")
        if it == 0:
            for i in range(candi_size):
                seq[i].append(candi_keys[i])
        else:
            seq_prime = copy.deepcopy(seq)

            seq = []
            for i in range(candi_size):
                x = candi_keys[i] // num_pre
                y = candi_keys[i] % num_pre
                seq.append(copy.deepcopy(seq_prime[x]))
                seq[i].append(y)
                candi_keys[i] = y
            del seq_prime
    print("Calculating f1 score...")
    return refine_by_f1_score(pt, embedding_pre, seq)


def get_relevant_predicates(pt: int, seq: list):
    rel_pres = set()
    rel_pres.add(pt)
    for path in seq:
        for p in path:
            rel_pres.add(p)
    return rel_pres


def evaluate(pt: int, num_ent: int, seq: list, facts: list):
    rules = []

    # key:p  value:sparse matrix
    mat_s_pres = {}
    rel_predicates = get_relevant_predicates(pt, seq)
    for p in rel_predicates:
        mat_s_pres[p] = sparse.dok_matrix((num_ent, num_ent), dtype=np.int8)

    for cur_h, cur_t, cur_r in facts:
        if cur_r in rel_predicates:
            mat_s_pres[cur_r][cur_h, cur_t] = 1

    for path in seq:
        mat_s_path = mat_s_pres[path[0]].copy()
        for i in range(1, len(path)):
            mat_s_path = mat_s_path.dot(mat_s_pres[path[i]])
        # num_body = (mat_path >= 1).astype(np.int_).sum()
        mat_s_path = mat_s_path.todok()
        # Will it be faster if search mat_s_path
        for k in mat_s_pres[pt].keys():
            if k in mat_s_path.keys():
                rules.append(path)
                break
    return rules


def save_rules(fn: str, pt: int, rules: list, predicates: list):
    with open(fn, "w", encoding="utf-8") as f:
        print(rules)
        for rule in rules:
            path_len = len(rule)
            if path_len == 1:
                params = [["X", "Y"]]
            else:
                params = [["X", "Z1"]]
                for i in range(1, path_len - 1):
                    params.append(["Z" + str(i), "Z" + str(i + 1)])
                params.append(["Z" + str(path_len - 1), "Y"])

            f.write(predicates[pt] + "(X,Y) :- ")
            for i in range(path_len):
                # print(i)
                p = rule[i]
                f.write(predicates[p // 2 * 2] + "(")
                if p % 2 == 1:
                    params[i][0], params[i][1] = params[i][1], params[i][0]
                f.write(params[i][0] + "," + params[i][1])
                if i == path_len - 1:
                    f.write(").\n")
                else:
                    f.write("), ")


def rule_learning(test_id: str, fn_pre: str, fn_ent: str, beam_size: int, rule_len: int, rule_dep: int,
                  max_iteration: int, limit_sampling: int, limit_predicate: int, max_new_entities: int,
                  limit_rules: int):
    fn_pres_dic = os.path.join(test_id, "predicates.txt")
    fn_learned_pres = os.path.join(test_id, "learned_predicates.log")
    # dict of predicates: (pre_name,pre_id)
    pred_ids = {}

    # get predicates and entities in question dataset
    logging.info("Begin to load target predicates and seed entities.")
    target_pnames = []
    with open(fn_pre, "r") as fp:
        for buf in fp:
            target_pnames.append(buf.strip("\n"))

    num_preds = 0
    for pt in target_pnames:
        pred_ids[pt] = num_preds
        num_preds += 1

    seed_entities = []
    with open(fn_ent, "r", encoding="utf-8") as fe:
        for buf in fe:
            seed_entities.append(buf.strip("\n"))
    logging.info("End to load target predicates and seed entities.")

    tot_time = 0
    tot_rules = 0

    for depth in range(rule_dep):
        with open(fn_pres_dic, "w", encoding="utf-8") as f:
            for pre in pred_ids:
                f.write(pre + " " + str(pred_ids[pre]) + "\n")

        for cnt in range(len(target_pnames)):
            start = time.time()
            p = target_pnames[cnt]
            pid = pred_ids[p]
            with open(fn_learned_pres, "a", encoding="utf-8") as f:
                f.write(f"{pid} {p}\n")
            pt = 0  # the id of Pt in relation.txt is always 0.
            logging.info("Begin to learn rules of Pt " + str(pid) + " " + p + ", depth=" + str(depth))
            # pt = pts_id[cnt]
            facts_dir = os.path.join(test_id, "p" + str(pid))
            if not os.path.exists(facts_dir):
                # continue
                os.mkdir(facts_dir)
            facts_fn = os.path.join(facts_dir, "facts.ttl")
            fn_ent = os.path.join(facts_dir, "entity2id.txt")
            fn_pre = os.path.join(facts_dir, "relation2id.txt")
            fn_tra = os.path.join(facts_dir, "train2id.txt")
            fn_rules = os.path.join(facts_dir, "rules.dlp")
            fn_result = os.path.join(facts_dir, "result.txt")

            new_entities = set()
            new_entities.update(seed_entities)
            # entities in the query need to be added.

            logging.info("Begin to get facts by Pt " + str(pid) + ".")
            new_entities.update(q.get_facts_by_predicate(p, facts_fn, limit_predicate))
            logging.info("End to get facts by Pt " + str(pid) + ".")

            gc.collect()
            # new_entities = ["dbr:Sint_Maarten"]
            logging.info("Begin to sample by new entities.")
            s = sampling_mp.Sampling(facts_dir, max_iteration, limit_sampling, max_new_entities, facts_fn)
            s.main(list(new_entities))
            logging.info("End to sample by new entities.")

            # unique facts
            # it doesn't matter much that there exists duplicate facts.

            logging.info("Begin to map to ids from names.")
            entities, predicates, facts = mapping.map2id(facts_fn, fn_ent, fn_pre, fn_tra)
            entities = list(entities)
            predicates = list(predicates)
            with open(fn_result, "a", encoding="utf-8") as f_result:
                f_result.write(f"#facts: {len(facts) // 2}\n")
                f_result.write(f"#distinct entities: {len(entities)}\n")
                f_result.write(f"#distinct predicates: {len(predicates) // 2}\n")
            logging.info("End to map to ids from names.")

            logging.info("Begin to train embeddings.")
            embedding_ent, embedding_pre = train_embedding.trainModel(facts_dir + "/")
            print()
            logging.info("End to train embeddings.")

            logging.info("Begin to rule search.")
            embedding_arg_s, embedding_arg_o = cal_argument_embedding(
                embedding_ent, embedding_pre, facts
            )
            seq = rule_search(
                pt, embedding_pre, embedding_arg_s, embedding_arg_o, beam_size, rule_len
            )
            logging.info("End to rule search.")

            logging.info("Begin to evaluate rules.")
            rules = evaluate(pt, len(entities), seq, facts)
            logging.info("End to evaluate rules.")

            logging.info("Begin to save rules.")
            print(len(rules))
            tot_rules += len(rules)
            save_rules(fn_rules, pt, rules, predicates)
            logging.info("End to save rules.")

            end = time.time()
            with open(fn_result, "a", encoding="utf-8") as f_result:
                f_result.write(f"time: {end - start}\n")
                tot_time += end - start

            # remove useless files
            os.remove(os.path.join(facts_dir, "facts.ttl"))
            os.remove(os.path.join(facts_dir, "entity2id.txt"))
            os.remove(os.path.join(facts_dir, "relation2id.txt"))
            os.remove(os.path.join(facts_dir, "train2id.txt"))
            os.remove(os.path.join(facts_dir, "test2id.txt"))
            os.remove(os.path.join(facts_dir, "valid2id.txt"))
            os.remove(os.path.join(facts_dir, "type_constrain.txt"))

        # updating target predicates with predicates in the rule body.
        target_pnames_copy = []
        for pn in target_pnames:
            pid = pred_ids[pn]
            fn_rules = os.path.join(test_id, "p" + str(pid), "rules.dlp")
            parsed_rules = dlp_translater.dlp_parser(fn_rules, rule_len, limit_rules)
            for pres, _ in parsed_rules:
                for p in pres:
                    if p not in pred_ids:
                        target_pnames_copy.append(p)
                        pred_ids[p] = num_preds
                        num_preds += 1
        target_pnames = target_pnames_copy.copy()
        print(target_pnames)

    # update predicate dict
    # with open(fn_pres_dic, "w", encoding="utf-8") as f:
    #     for pre in pred_ids:
    #         f.write(pre + " " + str(pred_ids[pre]) + "\n")

    # record results
    fn_result_total = os.path.join(test_id, "results.txt")
    with open(fn_result_total, "a", encoding="utf-8") as f_result:
        f_result.write(f"total rules: {tot_rules}\n")
        f_result.write(f"time(s) for rule learning: {tot_time}\n")
        f_result.write("\n")
