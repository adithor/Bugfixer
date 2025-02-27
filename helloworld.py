def explain_fibonacci():
    """Explains what a Fibonacci number is and provides examples."""
    print("A Fibonacci number is a number in the Fibonacci sequence, a series where each number is the sum of the two preceding ones, usually starting with 0 and 1.")
    print("\nExamples of Fibonacci numbers: 0, 1, 1, 2, 3, 5, 8, 13...")


def print_first_n_fibonacci(n):
    """Prints the first n Fibonacci numbers."""
    a, b = 0, 1
    for _ in range(n):
        print(a, end=" ")
        a, b = b, a + b
    print()


explain_fibonacci()
print("\nFirst 5 Fibonacci numbers:")
print_first_n_fibonacci(5)