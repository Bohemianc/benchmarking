import time

from requests_html import HTMLSession
from requests import adapters
from tqdm import tqdm
import filtering
import multiprocessing as mp
import os
import json

session = HTMLSession()
adapter = adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
session.mount("https://", adapter)
url = "https://dbpedia.org/sparql"

# !!!be modified when running on other servers
proxy = {"http": "http://127.0.0.1:10809", "https": "http://127.0.0.1:10809"}

with open("meaningless_predicates.txt", "r", encoding="utf-8") as fmp:
    bad_predicates = fmp.readline()


# position
# 0: query by the subject
# 1: query by the predicate
# 2: query by the object
# 3: query by the subject and the predicate
# 4: query by the predicate and the object
def crawl(
        query: tuple,
        position: int,
        lock: mp.Lock = None,
        limit: int = 300,
        bad_requests_dir: str = ".",
        offset: int = 0
):
    # print(str(query)+" in crawl()")
    params = {
        "default-graph-uri": "http://dbpedia.org",
        # "query": "select " + e + " ?y ?z where { " + e + "?y ?z}",
        "format": "application/sparql-results+json",
        "timeout": "30000",
        "signal_void": "on",
        "signal_unconnected": "on",
    }
    # print(query)
    triple = query[0] + " " + query[1] + " " + query[2]
    query_str = "SELECT " + triple + " WHERE { " + triple + " "
    if position == 0 or position == 2:
        query_str += "FILTER (?y NOT IN (" + bad_predicates + "))"
    if position == 0 or position == 1 or position == 4:
        query_str += 'MINUS { FILTER regex(?z,"http://dbpedia.org/class/yago|http://www.wikidata.org/entity/")}'
    query_str += "} LIMIT " + str(limit)
    query_str += " OFFSET " + str(offset)

    params["query"] = query_str
    result = None
    while True:
        try:
            resp = session.get(url, params=params, timeout=35)
            # resp = session.get(url, params=params, proxies=proxy)
            result = resp.content.decode("utf-8")
            if "</html>" not in result:
                break
            else:
                print("There is a html file!")
                print(result)
                print("Sleeping...")
                time.sleep(60)
        except UnicodeDecodeError:
            if lock is not None:
                lock.acquire()
            with open(
                    # define TEST-ID first
                    os.path.join(bad_requests_dir, "bad_requests.txt"),
                    "a",
                    encoding="utf-8",
            ) as f:
                f.write(query_str + "\n")
            if lock is not None:
                lock.release()

            # record and give up this query
            break
        except Exception:
            print("Retrying to get facts...")

    indices = None
    if result is not None:
        try:
            result = json.loads(result)
            indices = result["head"]["vars"]
            result = result["results"]["bindings"]
        except json.decoder.JSONDecodeError:
            # sparql compile error
            if lock is not None:
                lock.acquire()
            with open(
                    os.path.join(bad_requests_dir, "bad_requests.txt"),
                    "a",
                    encoding="utf-8",
            ) as f:
                f.write(query_str + "\n")
            if lock is not None:
                lock.release()
            result = None
    if result is not None and len(result) == 0:
        result = None
    return result, indices


def crawl_mp(
        qu: mp.Queue,
        query: tuple,
        choice: int,
        lock: mp.Lock = None,
        limit: int = 10000,
        bad_requests_dir: str = ".",
        offset: int = 0
):
    result, indices = crawl(query, choice, lock, limit, bad_requests_dir, offset)
    if result is not None:
        qu.put((choice, result, indices))


def get_new_entities(fact: list, dic_e, pos: int):
    if pos == 0 or pos == 2:
        # get facts by entities
        if fact[2 - pos] not in dic_e:
            dic_e[fact[2 - pos]] = len(dic_e)
    elif pos == 1:
        # get facts by predicates
        for i in (0, 2):
            if fact[i] not in dic_e:
                dic_e[fact[i]] = len(dic_e)
    elif pos == 3:
        if fact[2] not in dic_e:
            dic_e[fact[2]] = len(dic_e)
    elif pos == 4:
        if fact[0] not in dic_e:
            dic_e[fact[0]] = len(dic_e)


def load_dict(dic: dict, file: str):
    with open(file, "r", encoding="utf-8") as f:
        for buf in f:
            k, v = buf.rsplit(" ", 1)
            dic[k] = v


def get_facts_by_predicate(p: str, outfile: str, limit: int = 1000, save_new_entities: bool = True):
    result, indices = crawl(("?x", p, "?z"), 1, None, limit)
    num_facts = 0
    if save_new_entities:
        dic_e = {}  # store new entities
    if result is not None:
        with open(outfile, "a", encoding="utf-8") as f_facts:
            for it in result:
                num_facts += 1
                fact, is_uri = filtering.extract_triple_from_json(it, indices)
                f_facts.write(filtering.get_ttl_str(fact))
                if save_new_entities and is_uri:
                    get_new_entities(fact, dic_e, 1)

    if save_new_entities:
        return dic_e
