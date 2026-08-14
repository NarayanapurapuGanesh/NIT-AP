"""Misconception bank — domain-specific misconceptions the AI student can present.
Faculty's ability to detect and correct these is a key teaching quality signal.
"""


MISCONCEPTION_BANK: dict[str, list[dict]] = {
    "Object-Oriented Programming": [
        {"misconception": "So inheritance and polymorphism are basically the same thing, right?",
         "correct_concept": "Inheritance is about code reuse via parent-child relationships; polymorphism is about objects of different types responding to the same interface differently.",
         "category": "OOP"},
        {"misconception": "Abstract classes and interfaces are the same, just different syntax?",
         "correct_concept": "Abstract classes can have implementation and state; interfaces define contracts without implementation (though modern languages blur this).",
         "category": "OOP"},
        {"misconception": "Encapsulation just means making everything private, right?",
         "correct_concept": "Encapsulation is about bundling data and methods that operate on it, controlling access. It's not about making everything private but about hiding internal state and exposing a clean interface.",
         "category": "OOP"},
        {"misconception": "Method overloading and method overriding are the same thing?",
         "correct_concept": "Overloading is same method name with different parameters (compile-time); overriding is redefining a parent method in a child class (runtime polymorphism).",
         "category": "OOP"},
    ],
    "Data Structures": [
        {"misconception": "Arrays and linked lists have the same performance, just different syntax?",
         "correct_concept": "Arrays have O(1) random access but O(n) insertion; linked lists have O(n) access but O(1) insertion at known positions. Fundamentally different trade-offs.",
         "category": "Data Structures"},
        {"misconception": "A stack and a queue work the same way, just with different names?",
         "correct_concept": "Stack is LIFO (Last In, First Out); Queue is FIFO (First In, First Out). They have opposite ordering semantics.",
         "category": "Data Structures"},
        {"misconception": "Hash tables always have O(1) lookup, so they're always the best choice?",
         "correct_concept": "Hash tables have O(1) average case but O(n) worst case due to collisions. They also don't maintain order and have overhead for hash computation.",
         "category": "Data Structures"},
        {"misconception": "Binary search trees are always balanced, right?",
         "correct_concept": "Unbalanced BSTs can degrade to O(n) operations. Self-balancing trees (AVL, Red-Black) maintain balance guarantees but BSTs don't inherently.",
         "category": "Data Structures"},
    ],
    "Algorithms": [
        {"misconception": "O(n log n) and O(n²) are basically the same for small inputs?",
         "correct_concept": "While they may perform similarly for very small n, the growth rates are fundamentally different. O(n²) becomes impractical much sooner as n grows.",
         "category": "Algorithms"},
        {"misconception": "Recursion and iteration always produce the same performance?",
         "correct_concept": "Recursion has call stack overhead and can cause stack overflow. Some recursive solutions are O(2^n) without memoization while iterative versions are O(n).",
         "category": "Algorithms"},
        {"misconception": "Greedy algorithms always give the optimal solution?",
         "correct_concept": "Greedy algorithms give locally optimal choices but don't always yield globally optimal solutions. They work for specific problems with optimal substructure.",
         "category": "Algorithms"},
    ],
    "Database Systems": [
        {"misconception": "NoSQL databases are always faster than SQL databases?",
         "correct_concept": "Performance depends on the use case. SQL databases excel at complex queries and ACID transactions; NoSQL at horizontal scaling and flexible schemas.",
         "category": "Databases"},
        {"misconception": "Normalization always improves database performance?",
         "correct_concept": "Normalization reduces redundancy but can hurt read performance due to joins. Denormalization is sometimes preferred for read-heavy workloads.",
         "category": "Databases"},
        {"misconception": "Indexes make everything faster, so we should index every column?",
         "correct_concept": "Indexes speed up reads but slow down writes and consume storage. Over-indexing can degrade overall performance.",
         "category": "Databases"},
    ],
    "Operating Systems": [
        {"misconception": "A process and a thread are the same thing?",
         "correct_concept": "A process has its own memory space and resources; threads share the process's memory. Context switching between processes is more expensive.",
         "category": "OS"},
        {"misconception": "Virtual memory gives you unlimited RAM?",
         "correct_concept": "Virtual memory uses disk as an extension of RAM, but disk access is orders of magnitude slower. Excessive virtual memory use causes thrashing.",
         "category": "OS"},
    ],
    "Computer Networks": [
        {"misconception": "TCP and UDP do basically the same thing?",
         "correct_concept": "TCP provides reliable, ordered delivery with connection management; UDP is connectionless and unreliable but faster. Different use cases entirely.",
         "category": "Networks"},
        {"misconception": "HTTPS is just HTTP with a lock icon?",
         "correct_concept": "HTTPS uses TLS/SSL for encryption, authentication, and integrity. It protects against eavesdropping, tampering, and impersonation.",
         "category": "Networks"},
    ],
    "Machine Learning": [
        {"misconception": "More data always leads to better models?",
         "correct_concept": "Data quality matters more than quantity. Noisy, biased, or irrelevant data can hurt model performance. Feature engineering and data cleaning are crucial.",
         "category": "ML"},
        {"misconception": "Deep learning is always better than traditional ML?",
         "correct_concept": "Deep learning requires large datasets and compute. For smaller datasets or interpretable models, traditional ML (Random Forest, SVM) often outperforms.",
         "category": "ML"},
    ],
    "Software Engineering": [
        {"misconception": "Writing more code means more progress?",
         "correct_concept": "Code quality matters more than quantity. Well-designed systems often have less code. Refactoring to simplify is a sign of progress.",
         "category": "SE"},
        {"misconception": "Unit tests are enough to guarantee software quality?",
         "correct_concept": "Unit tests verify individual components but miss integration issues, performance problems, and real-world usage patterns. A comprehensive test strategy includes integration, E2E, and performance tests.",
         "category": "SE"},
    ],
    "Mathematics": [
        {"misconception": "Correlation implies causation?",
         "correct_concept": "Correlation measures statistical association but doesn't establish cause-effect. Confounding variables can create spurious correlations.",
         "category": "Math"},
        {"misconception": "A larger sample always means a more accurate result?",
         "correct_concept": "Sample size matters but so does sampling method. A biased large sample can be worse than a well-designed small sample.",
         "category": "Math"},
    ],
    "Electronics": [
        {"misconception": "Voltage and current are the same thing?",
         "correct_concept": "Voltage is the potential difference (pressure); current is the flow of charge. Ohm's Law (V=IR) relates them through resistance.",
         "category": "Electronics"},
    ],
    "Physics": [
        {"misconception": "Heavier objects fall faster than lighter ones?",
         "correct_concept": "In a vacuum, all objects fall at the same rate regardless of mass. Air resistance affects different objects differently in practice.",
         "category": "Physics"},
    ],
}


def get_misconceptions_for_subject(subject: str) -> list[dict]:
    """Get relevant misconceptions for a given subject.
    Uses fuzzy matching to find the best category.
    """
    subject_lower = subject.lower()

    for category, misconceptions in MISCONCEPTION_BANK.items():
        if category.lower() in subject_lower or subject_lower in category.lower():
            return misconceptions

    # Try keyword matching
    keyword_map = {
        "oop": "Object-Oriented Programming",
        "object oriented": "Object-Oriented Programming",
        "java": "Object-Oriented Programming",
        "python": "Object-Oriented Programming",
        "c++": "Object-Oriented Programming",
        "data structure": "Data Structures",
        "array": "Data Structures",
        "tree": "Data Structures",
        "graph": "Data Structures",
        "sorting": "Algorithms",
        "searching": "Algorithms",
        "dynamic programming": "Algorithms",
        "sql": "Database Systems",
        "database": "Database Systems",
        "dbms": "Database Systems",
        "os": "Operating Systems",
        "process": "Operating Systems",
        "thread": "Operating Systems",
        "network": "Computer Networks",
        "tcp": "Computer Networks",
        "http": "Computer Networks",
        "machine learning": "Machine Learning",
        "ml": "Machine Learning",
        "deep learning": "Machine Learning",
        "neural": "Machine Learning",
        "software": "Software Engineering",
        "testing": "Software Engineering",
        "design pattern": "Software Engineering",
        "math": "Mathematics",
        "statistics": "Mathematics",
        "probability": "Mathematics",
        "circuit": "Electronics",
        "digital": "Electronics",
        "physics": "Physics",
        "mechanics": "Physics",
    }

    for keyword, category in keyword_map.items():
        if keyword in subject_lower:
            return MISCONCEPTION_BANK.get(category, [])

    # Default: return a mix
    all_misconceptions = []
    for misconceptions in MISCONCEPTION_BANK.values():
        all_misconceptions.extend(misconceptions[:1])
    return all_misconceptions
