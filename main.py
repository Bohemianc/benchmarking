import os
import sys
# import get_facts as q
# import sampling_mp
import filtering
import utilities

name = lambda s, l: os.path.join("dataset", s + "_selected" + str(l) + ".txt")


def get_PE(fn_sparqls: str, fn_entity, fn_predicate):
    with open(fn_sparqls, "r", encoding="utf-8", ) as f1, open(
            fn_entity, "w", encoding="utf-8"
    ) as entity, open(fn_predicate, "w", encoding="utf-8") as predicate:
        se = set()
        sp = set()
        while True:
            buf = f1.readline()
            if len(buf) > 0:
                li = buf.split(" ")
                # print(li)
                if li[-2] != "?uri":
                    se.add(filtering.replace_prefix_in_terms(li[-2]))
                if li[-4] != "?uri":
                    se.add(filtering.replace_prefix_in_terms(li[-4]))
                sp.add(filtering.replace_prefix_in_terms(li[-3]))
            else:
                break
        for it in se:
            entity.write(it + "\n")
        for it in sp:
            predicate.write(it + "\n")


def select_queries(length: int):
    fn_sparqls = os.path.join("dataset", "sparqls.txt")
    fn_sparqls_selected = name("sparqls", length)
    utilities.get_partof_file(fn_sparqls, fn_sparqls_selected, 0, length)
    get_PE(fn_sparqls_selected, name("entities"), name("predicates"))


def elaborate_queries(lines: list):
    # index starting with 1
    fn_sparqls = os.path.join("dataset", "sparqls.txt")
    fn_sparqls_elaborate = os.path.join("dataset", "sparqls_elaborate.txt")
    fn_entities = os.path.join("dataset", "entities_elaborate.txt")
    fn_predicates = os.path.join("dataset", "predicates_elaborate.txt")

    utilities.extract_lines(lines, fn_sparqls, fn_sparqls_elaborate)
    get_PE(fn_sparqls_elaborate, fn_entities, fn_predicates)


if __name__ == "__main__":
    # dataset_dir = lambda x: os.path.join("dataset", x)
    # get_PE(dataset_dir("sparqls.txt"), dataset_dir("entities.txt"), dataset_dir("predicates.txt"))
    # test_version = "test_v4"
    # # ================================ #
    # # ======== read arguments ======== #
    # # ================================ #
    # test_id = sys.argv[1]
    # iteration = int(sys.argv[2])
    # limit = int(sys.argv[3])
    # target_pnames = []
    # with open(os.path.join("dataset", "predicates.txt"), "r") as fp:
    #     # for buf in fp:
    #     #     target_pnames.append(buf.strip("\n"))
    #     for i in range(1):
    #         target_pnames.append(fp.readline().strip("\n"))
    #
    # facts_fn="0426\\facts_0426.txt"
    # LIMIT_PREDICATE=5000
    # for pt in target_pnames:
    #     new_entities=set()
    #     new_entities.update(q.get_facts_by_predicate(pt, facts_fn, LIMIT_PREDICATE))
    #     s=sampling_mp.Sampling("0426",1,300,facts_fn)
    #     s.main(list(new_entities))
    j=lambda x,y:os.path.join(x,y)
    utilities.get_partof_file(j("dataset","sparqls.txt"),j("dataset","sparqls_top10.txt"),0,10)
    get_PE(j("dataset","sparqls_top10.txt"),j("dataset","entities_top10.txt"),j("dataset","predicates_top10.txt"))
