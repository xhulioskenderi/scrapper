from multiprocessing import Process, Queue
import time
import queue
from kazoo.client import KazooClient


def worker(task_queue):
    while True:
        try:
            task = task_queue.get(timeout=3)  # timeout in seconds
        except queue.Empty:
            print("Worker: No more tasks to perform.")
            break

        task_id = task.get('id')
        task_type = task.get('type', 'default')

        print(f"Worker: Performing task_id {task_id}")

        if task_type == 'custom':
            custom_function()
        else:
            default_function()

def custom_function():
    
    time.sleep(1)  # Simulate some work

def default_function():
    print("Performing default function")
    time.sleep(1)  # Simulate some work

if __name__ == '__main__':
    task_queue = Queue()

    zk_client = KazooClient(hosts='127.0.0.1:2181')
    zk_client.start()

    # Create worker processes
    processes = []
    for _ in range(5):  # Number of worker processes
        p = Process(target=worker, args=(task_queue,))
        p.start()
        processes.append(p)

    # Simulate adding tasks to the queue
    for i in range(1, 21):  # 20 tasks
        new_task = {'id': i, 'type': 'custom' if i % 2 == 0 else 'default'}
        task_queue.put(new_task)

    # Wait for all worker processes to finish
    for p in processes:
        p.join()

    print("All tasks have been completed.")
