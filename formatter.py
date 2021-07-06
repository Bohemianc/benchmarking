import os
import dlp_translater
import sampling_qa

ill_chars = '\/:*?"<>|,'


def format_uri(uri: str, is_pre: bool):
    if "/" in uri:
        uri = uri.split("/")[-1][:-1]
    for ch in ill_chars:
        uri = uri.replace(ch, "")
    if not is_pre:
        uri = '"' + uri + '"'
    return uri


def filter_items_in_csv(s: str):
    if '"' in s:
        s = s.replace('"', '')
        s = s.replace('\\', '')
        return '"' + s + '"'
    return s


def format_data_csv(dir_in: str):
    dir_out = os.path.join(dir_in, "csv")
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)
    fins = os.listdir(dir_in)
    for fin in fins:
        if "." in fin and fin != "name.dlp":
            fout = fin[:fin.rfind(".")] + ".csv"
            facts = dlp_translater.dlp2facts(os.path.join(dir_in, fin))
            with open(os.path.join(dir_out, fout), "w", encoding="utf-8") as f:
                num_lines = 0
                for fact in facts:
                    s, p, o = fact
                    s = s.replace(',', '')
                    o = o.replace(',', '')
                    s = filter_items_in_csv(s)
                    o = filter_items_in_csv(o)
                    f.write(s + "," + o + "\n")
                    num_lines += 1
                # print(f"{os.path.join(dir_out, fout)}: {num_lines}")
    print("Finished formatting data to CSV.")


# remove "\"*"
def format_data_dlp(dir_in: str):
    dir_out = os.path.join(dir_in, "dlp")
    if not os.path.exists(dir_out):
        os.mkdir(dir_out)
    fins = os.listdir(dir_in)
    for fin in fins:
        if "." in fin and fin != "name.dlp":
            facts = dlp_translater.dlp2facts(os.path.join(dir_in, fin))
            with open(os.path.join(dir_out, fin), "w", encoding="utf-8") as f:
                num_lines = 0
                for fact in facts:
                    s, p, o = fact
                    if '"' in o:
                        o = o.replace('\\', '')
                        o = o.replace('"', '')
                        o = o.replace('*', '')
                        o = '"' + o + '"'
                    f.write(dlp_translater.get_dlp_str([s, p, o]))
                    num_lines += 1
                # print(f"{os.path.join(dir_out, fin)}: {num_lines}")
    print("Finished formatting data to DLGP.")


if __name__ == "__main__":
    format_data_csv(os.path.join("test_v9_e2", "data"))
    sampling_qa.lessen_facts(os.path.join("test_v9_e2", "data", "csv"), os.path.join("test_v9_e2", "data", "csv1"),
                             5000000, os.path.join("test_v9_e2", "results.txt"))
