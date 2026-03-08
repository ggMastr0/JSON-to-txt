#!/usr/bin/env python3
# usage:
#   python3 json_to_txt.py input.json output.txt
#   python3 json_to_txt.py input.txt  output.txt   (se dentro c'è comunque JSON)

import json
import re
import sys
from pathlib import Path

def load_json_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def parse_json(raw: str):
    # se hai incollato in .txt con eventuale sporcizia prima/dopo, prova a isolare il blocco JSON
    raw = raw.strip()
    if not raw.startswith("{"):
        i = raw.find("{")
        j = raw.rfind("}")
        if i != -1 and j != -1 and j > i:
            raw = raw[i:j+1]
    return json.loads(raw)

def normalize_whitespace(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()

def main():
    if len(sys.argv) != 3:
        print("usage: python3 json_to_txt.py input.json output.txt", file=sys.stderr)
        sys.exit(2)

    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    raw = load_json_text(in_path)
    data = parse_json(raw)

    lines = []
    quizzes = data.get("quizzes", [])

    q_counter = 0
    for quiz in quizzes:
        title = normalize_whitespace(str(quiz.get("title", "")))
        questions = quiz.get("questions", [])

        if title:
            lines.append(title)
            lines.append("")  # blank line

        for q in questions:
            q_counter += 1
            qtext = normalize_whitespace(str(q.get("text", "")))
            choices = q.get("choices", [])
            correct = q.get("correctIndexes", [])

            lines.append(f"{q_counter}. {qtext}")

            for i, ch in enumerate(choices, start=1):
                ctext = normalize_whitespace(str(ch.get("text", "")))
                lines.append(f"   {i}) {ctext}")

            # opzionale: stampa la soluzione (commenta questo blocco se non la vuoi)
            if isinstance(correct, list) and len(correct) > 0:
                # correctIndexes sono 0-based nel JSON -> converti a 1-based per output umano
                corr_1based = [str(x + 1) for x in correct if isinstance(x, int)]
                if corr_1based:
                    lines.append(f"   RISPOSTA: {', '.join(corr_1based)}")

            lines.append("")  # blank line tra domande

    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()