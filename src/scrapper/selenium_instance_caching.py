class CustomCache:
    def __init__(self, capacity) -> None:
        self.cache = {}
        self.capacity = capacity


    def get(self, key):
       return self.cache.get(key, None)
    
    def put(self, key, value):
        if len(self.cache) >= self.capacity:
            raise RuntimeError("Cache is at capacity")
        self.cache[key] = value

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]
        else:
            raise KeyError(f"No such '{key}' in cache")
    
    def is_full(self):
        return len(self.cache) == self.capacity
    
