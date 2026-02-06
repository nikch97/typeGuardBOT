def greet(name: str):
    print("Hello", name)

def safe_greet(name: str):
    if not isinstance(name, str):
        raise TypeError("name must be a string")
    print("Hello", name)

def add(a: int, b: int):
    return a + b
