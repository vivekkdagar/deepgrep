# benchmark_full.py
import random
import string
import time
import tracemalloc

from deepgrep.core.engine import find_matches
from deepgrep.core.history import SearchHistoryDB
from deepgrep.core.semantic_engine import SemanticEngine


# ----------------------
# Helper functions
# ----------------------
def random_line(length=1000):
    return ''.join(random.choices(string.ascii_letters + " ", k=length))

def generate_lines(n=10000, length=1000):
    return [random_line(length) for _ in range(n)]

def complex_pattern():
    # pattern with capture groups, alternations, quantifiers
    return r"(\w+)\s+\1|foo(bar)?|a.*b+"

# ----------------------
# Engine + Matcher Benchmark
# ----------------------
lines = generate_lines(1000, 500)  # reduce if memory is too high
pattern = complex_pattern()

print("=== Engine/Matcher Benchmark ===")
tracemalloc.start()
start = time.time()
match_count = sum(len(find_matches(line, pattern)) for line in lines)
end = time.time()
mem_current, mem_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"Matches found: {match_count}")
print(f"Time: {end - start:.2f}s, Current Mem: {mem_current/1e6:.2f}MB, Peak Mem: {mem_peak/1e6:.2f}MB")

# ----------------------
# History DB Benchmark
# ----------------------
print("\n=== History DB Benchmark ===")
db = SearchHistoryDB()
start = time.time()
for i in range(1000):
    db.log_search(pattern, random.randint(0, 10), ["file1", "file2"])
end = time.time()
print(f"Logged 1000 searches in {end - start:.2f}s")

# Read recent & top patterns
start = time.time()
recent = db.get_recent(50)
top = db.get_top_patterns(50)
end = time.time()
print(f"Retrieved recent & top patterns in {end - start:.2f}s")

# ----------------------
# Semantic Engine Benchmark
# ----------------------
print("\n=== Semantic Engine Benchmark ===")
semantic = SemanticEngine()
large_text = " ".join(generate_lines(500, 50))  # 25k words ~ manageable
keywords = ["test", "random", "engine", "performance"]

start = time.time()
for kw in keywords:
    matches = semantic.find_semantic_matches(large_text, kw)
end = time.time()
print(f"Semantic matches for {len(keywords)} keywords done in {end - start:.2f}s")