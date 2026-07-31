"""
Classifies the teaching topic based on visual OCR data.
"""

def classify_topic(raw_text: str) -> str:
    """
    Classifies OCR text into an educational topic.
    """
    text = raw_text.lower()
    
    topics = {
        "Programming": ["code", "function", "var", "def", "class", "public", "void", "return"],
        "Networking": ["tcp", "ip", "router", "switch", "osi", "packet", "subnet", "topology"],
        "DBMS": ["sql", "database", "select", "where", "join", "table", "schema", "query"],
        "Operating Systems": ["kernel", "process", "thread", "memory", "cpu", "deadlock", "mutex"],
        "Machine Learning": ["model", "training", "loss", "gradient", "neural", "epoch", "dataset"],
        "AI": ["agent", "search", "heuristic", "state", "reinforcement", "reward"],
        "Mathematics": ["theorem", "proof", "integral", "derivative", "matrix", "vector", "equation"],
        "Physics": ["force", "mass", "velocity", "acceleration", "gravity", "energy", "joule"],
        "Chemistry": ["molecule", "atom", "reaction", "bond", "acid", "base", "ph"],
        "Civil": ["concrete", "beam", "load", "stress", "strain", "structure"],
        "Mechanical": ["thermodynamics", "engine", "gear", "torque", "fluid", "pressure"],
        "Electrical": ["voltage", "current", "resistance", "circuit", "ohm", "capacitor", "inductor"]
    }
    
    best_topic = "General"
    max_matches = 0
    
    for topic, keywords in topics.items():
        matches = sum(1 for kw in keywords if kw in text)
        if matches > max_matches:
            max_matches = matches
            best_topic = topic
            
    return best_topic
