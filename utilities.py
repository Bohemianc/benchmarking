import os


def merge_files(filenames: list, outfile: str):
    cnt = 0
    with open(outfile, "w", encoding="utf-8") as f1:
        for fn in filenames:
            cnt_s = 0
            if os.path.exists(fn):
                with open(fn, "r", encoding="utf-8") as f2:
                    for buf in f2:
                        f1.write(buf)
                        cnt_s += 1
                        cnt += 1
                print("#lines in " + fn + ": " + str(cnt_s))
            else:
                print(fn + " does not exist.")
            # f2.write("\n")  # if the last line of a file is not empty
    print("total lines: " + str(cnt))


def extract_lines(lines: str, infile: str, outfile: str):
    with open(infile, "r", encoding="utf-8") as f1, open(
            outfile, "w", encoding="utf-8"
    ) as f2:
        cnt = 0
        for buf in f1:
            cnt += 1
            if cnt in lines:
                f2.write(buf)


def get_partof_file(infile: str, outfile: str, left: int, right: int):
    with open(infile, "r", encoding="utf-8") as f1, open(
            outfile, "w", encoding="utf-8",
    ) as f2:
        for i in range(right):
            buf = f1.readline()
            if i >= left:
                f2.write(buf)


def get_lines(fn: str):
    with open(fn, "r", encoding="utf-8") as f:
        cnt = 0
        for _ in f:
            cnt += 1
        print(cnt)


if __name__ == "__main__":
    # dir_onto = "dbpedia\\ontology"
    # dir_info = "dbpedia\\infobox"

    # fns = [
    #     "instance-types_lang=en_specific.ttl",
    #     "instance-types_lang=en_transitive.ttl",
    #     "mappingbased-literals_lang=en.ttl",
    #     "mappingbased-objects_lang=en.ttl",
    #     "specific-mappingbased-properties_lang=en.ttl",
    # ]
    # paths = [os.path.join(dir_onto, x) for x in fns]
    # paths.append(os.path.join(dir_info, "infobox-properties_lang=en.ttl"))
    # fn_out = "dbpedia\\data4qa\\facts.ttl"
    # merge_files(paths, fn_out)
    # get_lines("dbpedia\\infobox\\infobox-properties_lang=en.ttl")
    # merge_files(["prefix.txt","facts.dlp"],"facts1.dlp")
    # get_partof_file("dbpedia\\data4qa\\facts_filtered.dlp", "0420.ttl", 0, 265)
    # get_lines("facts_full.dlp")
    # dir_root = "experiment3"
    # fns_facts = []
    # for i in (2, 5, 6):
    #     fn_rules = os.path.join(dir_root, "rules_e" + str(i) + ".dlp")
    #     get_partof_file(fn_rules, os.path.join(dir_root, "rules_exp3_e" + str(i) + ".dlp"), 0, 139)
    #     fns_facts.append(os.path.join(dir_root, "facts_e" + str(i) + ".dlp"))
    # merge_files(fns_facts, os.path.join(dir_root, "facts_exp3.dlp"))
    get_lines("facts_full.dlp")
