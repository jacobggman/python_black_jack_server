import threading
import random
import time

lock = threading.Lock()
cv = threading.Condition(lock)
items = dict()


# Consume one item
def get(num):
    with cv:
        while num not in items:
            cv.wait()
        print(f"{num} get: f{items[num]}")
        del items[num]


def create():
    # Produce one item
    while True:
        with cv:
            ran = random.randint(1, 10)
            print(f"create {ran}")
            items[ran] = random.random()
            cv.notify_all()
        time.sleep(0.5)


def await_for_num(num):
    with cv:
        while num not in items:
            cv.wait()
        n = items[num]
        del items[num]
        return n

create_t = threading.Thread(target=create)
get_t1 = threading.Thread(target=get, args=(1,))
get_t5 = threading.Thread(target=get, args=(5,))
get_t9 = threading.Thread(target=get, args=(9,))
create_t.start()
get_t1.start()
get_t5.start()
get_t9.start()
print("4 waited for: ", await_for_num(4))
print("3 waited for: ", await_for_num(3))
a = input()