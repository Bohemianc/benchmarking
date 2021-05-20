from tqdm import tqdm
import filtering


def map2id(infile: str, outfile_e: str, outfile_p: str, outfile_f: str):
    dict_entity = {}
    dict_predicate = {}
    facts = []

    with open(infile, "r", encoding="utf-8") as f:
        for buf in tqdm(f):
            fact = filtering.extract_triple_from_ttl(buf)
            if fact is not None:
                for i in (0, 2):
                    if not fact[i] in dict_entity:
                        dict_entity[fact[i]] = len(dict_entity)
                if not fact[1] in dict_predicate:
                    dict_predicate[fact[1]] = len(dict_predicate)
                    dict_predicate[fact[1] + "^-1"] = len(dict_predicate)
                h = dict_entity[fact[0]]
                r = dict_predicate[fact[1]]
                t = dict_entity[fact[2]]
                facts.append((h, t, r))
                facts.append((t, h, r + 1))

    print("#mapped entities: " + str(len(dict_entity)))
    print("#mapped predicates: " + str(len(dict_predicate)))
    print("#facts: " + str(len(facts)))

    with open(outfile_e, "w", encoding="utf-8") as f:
        f.write(str(len(dict_entity)) + "\n")
    filtering.write_dict(dict_entity, outfile_e)

    with open(outfile_p, "w", encoding="utf-8") as f:
        f.write(str(len(dict_predicate)) + "\n")
    filtering.write_dict(dict_predicate, outfile_p)

    with open(outfile_f, "w", encoding="utf-8") as f:
        f.write(str(len(facts)) + "\n")
        for fact in facts:
            h, t, r = fact
            f.write(str(h) + "\t" + str(t) + "\t" + str(r) + "\n")

    return dict_entity, dict_predicate, facts
