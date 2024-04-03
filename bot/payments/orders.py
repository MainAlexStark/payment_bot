import threading
import time

class OrdersStorage:
    def __init__(self):
        self.storage = {}

    def add_element(self, key, value, expiration_time):
        self.storage[key] = {
            'value': value,
            'expiration_time': time.time() + expiration_time
        }
        # Создаем отдельный поток для удаления элемента после истечения времени
        threading.Thread(target=self.remove_element_after_timeout, args=(key, expiration_time)).start()

    def remove_element_after_timeout(self, key, timeout):
        time.sleep(timeout)
        del self.storage[key]

    def get_element(self, key):
        if key in self.storage:
            return self.storage[key]['value']
        return None

# Пример использования
orders = OrdersStorage()

