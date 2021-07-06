import dlp_translater
import filtering
import formatter
import get_facts as q

import multiprocessing as mp
import queue
from threading import Thread
import os
import time


class Sampling:
    def __init__(self, dir_data: str, fn_result: str):
        self.dir_data = dir_data
        self.fn_result = fn_result
        # self.dir_data_self=dir_data_self

    def add_thread(
            self,
            q_threads: queue.Queue,
            qu: mp.Queue,
            query: tuple,
            choice: int,
            offset: int
    ):
        print(str(query) + " offset = " + str(offset))
        t = Thread(
            target=q.crawl_mp,
            args=(qu, query, choice, None, 10000, ".", offset),
        )
        time.sleep(0.02)
        t.start()
        q_threads.put(t)

    def producer(self, pres: list, q_facts: mp.Queue, pre_to_offset, lock: mp.Lock):
        print("Producer started.")

        num_pres = len(pres)
        max_threads = 100
        num_finished = 0
        q_threads = queue.Queue()
        for j in range(min(max_threads, num_pres)):
            p = pres[j]
            lock.acquire()
            offset = pre_to_offset[p]
            lock.release()
            self.add_thread(
                q_threads, q_facts, ("?x", p, "?z"), 1, offset
            )
            num_finished += 1

        while not q_threads.empty():
            q_threads.get().join()
            if num_finished < num_pres:
                p = pres[num_finished]
                lock.acquire()
                offset = pre_to_offset[p]
                lock.release()
                self.add_thread(
                    q_threads, q_facts, ("?x", p, "?z"), 1, offset
                )
                num_finished += 1

        # all requests has been posted and returned.
        q_facts.put(None)
        print("Producer stopped.")

    def consumer(self, q_facts: mp.Queue, next_pres, pre_to_offset, tot_facts, lock: mp.Lock()):
        while True:
            item = q_facts.get()

            if item is None:
                print("Consumer stopped.")
                print("next_pres: " + str(len(next_pres)))
                break

            pre = "<" + item[1][0][item[2][1]]["value"] + ">"
            file_facts1 = os.path.join(self.dir_data, formatter.format_uri(pre, True) + ".dlp")
            # file_facts2=os.path.join(self.dir_data_self,formatter.format_uri(pre,True)+".dlp")
            with open(file_facts1, "a", encoding="utf-8") as f_facts:
                num_facts = len(item[1])
                tot_facts[0] += num_facts
                if num_facts == 10000:
                    next_pres.append(pre)
                    # print(f"next_pres.append({pre}) len(next_pres)={len(next_pres)}")
                    lock.acquire()
                    pre_to_offset[pre] += 10000
                    lock.release()

                for it in item[1]:
                    fact, _ = filtering.extract_triple_from_json(it, item[2])
                    f_facts.write(dlp_translater.get_dlp_str(fact))
                print("#facts: " + str(tot_facts[0]))

    def main(self, pres: list):
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        start_time = time.time()

        manager = mp.Manager()
        lock = mp.Lock()
        pre_to_offset = manager.dict()
        tot_facts = manager.list()
        tot_facts.append(0)
        for p in pres:
            pre_to_offset[p] = 0

        while len(pres) > 0:
            print("====== #pres: " + str(len(pres)) + " =======")
            q_facts = mp.Queue(maxsize=100)
            next_pres = manager.list()
            p_producer = mp.Process(
                target=self.producer, args=(pres, q_facts, pre_to_offset, lock)
            )
            p_consumer = mp.Process(target=self.consumer, args=(q_facts, next_pres, pre_to_offset, tot_facts, lock))
            p_producer.start()
            p_consumer.start()
            p_producer.join()
            p_consumer.join()
            pres = list(set(list(next_pres))).copy()
            # print(len(pres), len(next_pres))

        end_time = time.time()

        with open(
                self.fn_result, "a", encoding="utf-8"
        ) as f_result:
            f_result.write("running time(s): %d\n" % (end_time - start_time))
            f_result.write("max offset: %d\n" % max(pre_to_offset.values()))
        print("running time(s): %d" % (end_time - start_time))
        return tot_facts[0]
