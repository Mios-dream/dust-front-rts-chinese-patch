from __future__ import annotations

import csv
import json
from pathlib import Path

import UnityPy


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "Dust Front RTS_Data" / "resources.assets"
OUT = ROOT / "work" / "localization-original"
TARGETS = {
    "Localization_DUST_FRONT - Tutorial-locals",
    "Localization_DUST_FRONT - Main",
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    env = UnityPy.load(str(ASSETS))
    extracted: dict[str, dict[str, object]] = {}

    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        name = str(getattr(data, "m_Name", ""))
        if name not in TARGETS:
            continue

        rows = list(csv.reader(data.m_Script.splitlines(keepends=True)))
        filename = "tutorial.csv" if "Tutorial" in name else "main.csv"
        (OUT / filename).write_text(data.m_Script, encoding="utf-8", newline="")
        extracted[name] = {
            "path_id": obj.path_id,
            "filename": filename,
            "rows": len(rows) - 1,
            "header": rows[0],
        }

    (OUT / "manifest.json").write_text(
        json.dumps(extracted, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(extracted, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
