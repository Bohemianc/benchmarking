import re

pattern_csv = re.compile(r'"(.*?)","(.*?)","(.*?)"')
pattern_ttl_uri = re.compile(r"<(.*?)> <(.*?)> <(.*?)> .")
pattern_ttl_literals = re.compile(r'<(.*?)> <(.*?)> "(.*?)"(.*?) .')

replaces = [
    ("http://dbpedia.org/ontology/", "dbo:"),
    ("http://dbpedia.org/resource/", "dbr:"),
    ("http://dbpedia.org/property/", "dbp:"),
    ("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdf:"),
]


def replace_predicate(line: str):
    # it's ok the replace list is not complete.
    # it's just for speeding up regex matching or reducing memory cost.
    for t in replaces:
        line = line.replace(t[0], t[1])
    return line


def replace_predicate_inverse(fact: list):
    for i in range(3):
        for t in replaces:
            fact[i] = fact[i].replace(t[1], t[0], 1)


def replace_prefix_in_terms(term: str):
    for t in replaces:
        if t[1] in term:
            term = term.replace(t[1], t[0])
            uri = lambda x: "<" + x + ">"
            return uri(term)
    return term


def extract_triple(buf: str):
    # reg matching makes it slower
    buf = pattern_csv.findall(buf)
    if len(buf) == 1:
        return list(buf[0])


def wrap_fact(fact: list, is_uri: bool):
    uri = lambda x: "<" + x + ">"
    literal = lambda x: '"' + x + '"'

    for i in (0, 1):
        fact[i] = uri(fact[i])
    fact[2] = uri(fact[2]) if is_uri else literal(fact[2])


def extract_triple_from_ttl(buf: str):
    res = pattern_ttl_uri.findall(buf)
    if len(res) == 1:
        fact = list(res[0])
        wrap_fact(fact, True)
        return fact

    res = pattern_ttl_literals.findall(buf)
    if len(res) == 1:
        fact = list(res[0])
        wrap_fact(fact, False)
        return fact


def extract_triple_from_json(result, indices: list):
    # !!! modify it when getting facts by entities
    # May be the func need another param.
    # indices[pos] = "callret-" + str(pos)
    # print(result)
    # print(indices)
    is_uri = result[indices[2]]["type"] == "uri"
    fact = [result[indices[i]]["value"] for i in (0, 1, 2)]
    wrap_fact(fact, is_uri)
    return fact, is_uri


def get_ttl_str(fact: list):
    return fact[0] + " " + fact[1] + " " + repr(fact[2])[1:-1] + " .\n"


def write_dict(dic_e: dict, fn: str):
    with open(fn, "a", encoding="utf-8") as f:
        for k in dic_e:
            f.write(k + "\t" + str(dic_e[k]) + "\n")


def filter_fact(fact: list):
    with open("meaningless_predicates.txt", "r", encoding="utf-8") as f:
        bad_pres = f.readline()
    bad_pres = bad_pres.strip("\n").split(",")

    if (
            fact[1] not in bad_pres
            and "http://dbpedia.org/class/yago" not in fact[2]
            and "http://www.wikidata.org/entity" not in fact[2]
    ):
        return True
    return False
