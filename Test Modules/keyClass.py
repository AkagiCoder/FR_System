# Class that defines a key
class key:
    def __init__(self, num, code, dateCreate, timeCreate):
        self.num = num                     # Key's number indicating the position of the list
        self.code = code                   # Key's code
        self.dateCreate = dateCreate       # Date when the key was generated
        self.timeCreate = timeCreate       # Time when the key was generated
        
key1 = key("1", "55544", "today", "4:00")
print(key1.num)