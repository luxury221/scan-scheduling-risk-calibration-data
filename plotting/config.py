from pathlib import Path
import json
HERE = Path(__file__).resolve().parent
def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))
