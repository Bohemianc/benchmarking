import filtering
import get_facts as q

import datetime
import multiprocessing as mp
import queue
from threading import Thread
import os
import time


class Sampling:
    def __init__(self, out_dir, max_iteration, limit_answer, max_new_entities,fn_facts):
        self.out_dir = out_dir
        self.file_facts = fn_facts
        self.file_log = os.path.join(out_dir, "requests.txt")
        self.file_new_entities = os.path.join(out_dir, "new_entities.txt")
        self.file_bad_requests = os.path.join(out_dir, "bad_requests.txt")
        self.max_iteration = max_iteration
        self.limit_answer = limit_answer
        self.max_new_entities=max_new_entities

    def add_thread(
            self,
            q_threads: queue.Queue,
            qu: mp.Queue,
            lock: mp.Lock,
            query: tuple,
            choice: int,
    ):
        # print(str(query)+" add a thread")
        t = Thread(
            target=q.crawl_mp,
            args=(qu, query, choice, lock, self.limit_answer, self.out_dir),
        )
        # print(str(query)+" added")
        t.start()
        # print(str(query)+" started")
        q_threads.put(t)

    def producer(self, entities: list, q_facts: mp.Queue, lock: mp.Lock):
        print("Producer started.")

        num_entities = len(entities)
        num_threads = 100
        num_entities_per_it = num_threads // 2
        num_finished = 0
        # print("here -2")
        q_threads = queue.Queue()
        # print("here -1")
        for j in range(min(num_entities_per_it, num_entities - num_finished)):
            e = entities[j]
            # print(f"here 0: {j} {e}")
            # print("here 0.0")
            self.add_thread(
                q_threads, q_facts, lock, (e, "?y", "?z"), 0,
            )
            # print("here 0.5")
            self.add_thread(
                q_threads, q_facts, lock, ("?x", "?y", e), 2,
            )
            # print("here 1.0")
            num_finished += 1
        # print("here 1")
        while not q_threads.empty():
            # print("here 2")
            q_threads.get().join()
            # print("here 3")
            if num_finished < num_entities:
                e = entities[num_finished]
                self.add_thread(
                    q_threads, q_facts, lock, (e, "?y", "?z"), 0,
                )
            # print("here 4")
            q_threads.get().join()
            # print("here 5")
            if num_finished < num_entities:
                e = entities[num_finished]
                self.add_thread(
                    q_threads, q_facts, lock, ("?x", "?y", e), 2,
                )
                num_finished += 1
                if num_finished % 1000 == 0:
                    print("Producer: %d/%d" % (num_finished, num_entities))

        # all requests has been posted and returned.
        q_facts.put(None)
        print("Producer stopped.")

    def consumer(self, q_facts: mp.Queue, dic_e):
        num_facts = 0
        num_entities = 0
        cnt = 0
        while True:
            item = q_facts.get()
            cnt += 1

            if item is None:
                print("Consumer stopped.")
                with open(
                        os.path.join(self.out_dir, "result.txt"), "a", encoding="utf-8"
                ) as f_result:
                    f_result.write("#facts: %d\n" % num_facts)
                    f_result.write("#entities: %.1f\n" % round(num_entities / 2.0, 1))
                    f_result.write("#new entities: %d\n" % len(dic_e))
                break

            e = None
            with open(self.file_facts, "a", encoding="utf-8") as f_facts:
                for it in item[1]:
                    num_facts += 1
                    fact, is_uri = filtering.extract_triple_from_json(it, item[2])
                    f_facts.write(filtering.get_ttl_str(fact))
                    if is_uri:
                        q.get_new_entities(fact, dic_e, item[0])
                    e = fact[item[0]]

            if e is not None:
                num_entities += 1
                with open(self.file_log, "a", encoding="utf-8") as flog:
                    flog.write(e + " " + str(item[0]) + "\n")
            if cnt % 1000 == 0:
                print("Consumer: " + str(cnt))

    def main(self, entities: list):
        q_facts = mp.Queue(maxsize=100)

        iteration = 0
        while iteration < self.max_iteration:
            iteration += 1
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            print("=== iteration %d, #entities %d ===" % (iteration, len(entities)))

            manager = mp.Manager()
            lock = mp.Lock()  # lock for writing requests.txt
            dic_e = manager.dict()  # type: # Dictproxy rather that dict
            p_producer = mp.Process(
                target=self.producer, args=(entities, q_facts, lock)
            )
            p_consumer = mp.Process(target=self.consumer, args=(q_facts, dic_e))

            start_time = time.time()
            p_producer.start()
            p_consumer.start()

            p_producer.join()
            p_consumer.join()
            end_time = time.time()

            with open(
                    os.path.join(self.out_dir, "result.txt"), "a", encoding="utf-8"
            ) as f_result:
                f_result.write("running time(s): %d\n" % (end_time - start_time))
            print("running time(s): %d" % (end_time - start_time))
            dic_e = dict(dic_e)
            # filtering.write_dict(dic_e, self.file_new_entities)

            entities = list(dic_e)
            if len(entities) > self.max_new_entities:
                entities = entities[:self.max_new_entities]
