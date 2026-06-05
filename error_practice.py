def safe_divide(a,b):
    try:
        results = a / b
        return results
    except ZeroDivisionError:
        print(f"Cannot divide {a} by zero")
        return None
    except TypeError:
        print(f"Invalid types: cannot divide {type(a).__name__} by {type(b).__name__}")
        return None

print(safe_divide(10,2))
print(safe_divide(10,0))
print(safe_divide(10, 'x'))
print(safe_divide(100,4))
