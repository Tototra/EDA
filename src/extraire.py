import json
import time
from donnees import load, PATTERNS_FILE
from binaps import BinaPs

D, movies, users = load()
start = time.time()
model = BinaPs(D.shape[1], seed=0).fit(D)
seconds = time.time() - start

patterns = sorted({tuple(sorted(F)) for F in model.patterns(0.5) if len(F) >= 4})
output = {"seconds": seconds, "patterns": [[int(movies.movie[j]) for j in F] for F in patterns]}
PATTERNS_FILE.write_text(json.dumps(output))
print(len(patterns), "motifs en", round(seconds, 1), "s")
