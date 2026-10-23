from __future__ import annotations

import csv
import json
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "assets" / "NotoSansCJKsc-Regular.otf"
TARGET = ROOT / "tools" / "assets" / "DustFront-CN-subset.otf"


def main() -> None:
    translations = json.loads((ROOT / "translations.json").read_text(encoding="utf-8"))
    characters = set(chr(codepoint) for codepoint in range(32, 127))
    characters.update("，。！？：；（）【】《》“”‘’、—…·「」『』+-×÷%<>/\\#@&*()[]{}=_.:")

    for section in ("tutorial", "main"):
        for value in translations[section].values():
            characters.update(value.replace("\\n", "\n"))

    for filename in ("tutorial.csv", "main.csv"):
        with (ROOT / "work" / "localization-original" / filename).open(
            encoding="utf-8", newline=""
        ) as handle:
            for row in csv.DictReader(handle):
                characters.update(row["Russian"])
                characters.update(row["English"])

    unicodes = {ord(char) for char in characters if ord(char) >= 32}
    font = TTFont(str(SOURCE))
    options = subset.Options()
    options.layout_features = ["*"]
    options.name_IDs = ["*"]
    options.recommended_glyphs = True
    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=unicodes)
    subsetter.subset(font)
    font.save(str(TARGET))
    print(f"characters={len(unicodes)} glyphs={len(font.getGlyphOrder())}")
    print(f"source_bytes={SOURCE.stat().st_size} target_bytes={TARGET.stat().st_size}")


if __name__ == "__main__":
    main()
