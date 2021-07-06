import os
import shutil


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


# [left,right)
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
    return cnt


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
    # tot = 0
    # for pid in range(10):
    #     fn_rules = os.path.join("test_v8_e3", "p" + str(pid), "rules.dlp")
    #     if os.path.exists(fn_rules):
    #         tot += get_lines(fn_rules)
    #     else:
    #         print(fn_rules+" does not exist.")
    # print(tot)

    # fin = os.path.join("test_v8", "data", "facts_unlimit.dlp")
    # fout = os.path.join("test_v8", "data", "facts_unlimited.dlp")
    # get_partof_file(fin, fout, 43613730, 56155009)

    # move data files to the same dir
    data_files = os.listdir("data")
    fns1 = os.listdir(os.path.join("test_v8_e1", "data"))
    cnt = 0
    for fn in fns1:
        if not fn in data_files:
            src = os.path.join("test_v8_e1", "data", fn)
            dst = os.path.join("data", fn)
            shutil.move(src, dst)
            cnt += 1
    print(cnt)
