from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import shutil
from collections import Counter
from pathlib import Path

import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Dust Front RTS_Data"
ASSETS = DATA / "resources.assets"
TRANSLATIONS = ROOT / "translations.json"
FONT = ROOT / "tools" / "assets" / "DustFront-CN-subset.otf"
DUMMY_DLLS = ROOT / "tools" / "vendor" / "Il2CppDumper" / "DummyDll"
PATCH_ROOT = ROOT / "dist" / "Dust Front RTS Chinese Patch"
PATCH_ASSETS = PATCH_ROOT / "Dust Front RTS_Data" / "resources.assets"

TARGETS = {
    "Localization_DUST_FRONT - Tutorial-locals": "tutorial",
    "Localization_DUST_FRONT - Main": "main",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def tokens(value: str) -> Counter[str]:
    return Counter(re.findall(r"<[^>\r\n]+>|\{\d+\}", value))


def make_generator() -> TypeTreeGenerator:
    generator = TypeTreeGenerator("2020.3.3f1")
    for dll in sorted(DUMMY_DLLS.glob("*.dll")):
        generator.load_dll(dll.read_bytes())
    return generator


def translate_text_asset(data: object, translations: dict[str, dict[str, str]]) -> tuple[int, int]:
    name = str(getattr(data, "m_Name"))
    section = TARGETS[name]
    rows = list(csv.reader(io.StringIO(data.m_Script, newline="")))
    if rows[0] != ["Keys", "Russian", "English"]:
        raise ValueError(f"Unexpected header in {name}: {rows[0]!r}")

    changed = 0
    for row in rows[1:]:
        if len(row) != 3:
            raise ValueError(f"Malformed row in {name}: {row!r}")
        key, original, _ = row
        if key not in translations[section]:
            raise KeyError(f"Missing translation for {section}:{key}")
        translated = translations[section][key]
        if tokens(original) != tokens(translated):
            raise ValueError(
                f"Formatting tokens changed for {section}:{key}: "
                f"{tokens(original)} -> {tokens(translated)}"
            )
        row[2] = translated
        changed += 1

    output = io.StringIO(newline="")
    csv.writer(output, lineterminator="\r\n").writerows(rows)
    data.m_Script = output.getvalue()
    return changed, len(rows) - 1


def patch_font(env: object) -> int:
    font_data = list(FONT.read_bytes())
    font_object = None
    for obj in env.objects:
        if obj.type.name != "Font":
            continue
        data = obj.read()
        if obj.path_id == 190 or getattr(data, "m_Name", "") == "LiberationSans":
            font_object = (obj, data)
            break
    if font_object is None:
        raise RuntimeError("LiberationSans Font object was not found")

    obj, data = font_object
    data.m_FontData = font_data
    data.m_FontNames = ["Noto Sans CJK SC"]
    obj.save_typetree(data)

    fallback = None
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        head = obj.parse_monobehaviour_head()
        if obj.path_id == 12341 and head.m_Script.m_PathID == 652:
            fallback = obj
            break
    if fallback is None:
        raise RuntimeError("LiberationSans SDF fallback asset was not found")

    node = fallback.generate_monobehaviour_node()
    fallback_data = fallback.parse_as_dict(node)
    source_font = fallback_data["m_SourceFontFile"]
    if source_font["m_PathID"] != 190:
        raise RuntimeError(f"Unexpected TMP fallback source font: {source_font!r}")
    fallback_data["m_FaceInfo"]["m_FamilyName"] = "Noto Sans CJK SC"
    fallback_data["m_CreationSettings"]["sourceFontFileName"] = "DustFront-CN-subset.otf"
    fallback.save_typetree(fallback_data, node)
    return len(font_data)


def main() -> None:
    translations = json.loads(TRANSLATIONS.read_text(encoding="utf-8"))
    source_hash = sha256(ASSETS)
    generator = make_generator()
    env = UnityPy.load(str(ASSETS))
    env.typetree_generator = generator

    translated = {}
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        name = str(getattr(data, "m_Name", ""))
        if name not in TARGETS:
            continue
        count, total = translate_text_asset(data, translations)
        obj.save_typetree(data)
        translated[name] = {"translated": count, "total": total, "path_id": obj.path_id}

    font_bytes = patch_font(env)
    PATCH_ASSETS.parent.mkdir(parents=True, exist_ok=True)
    PATCH_ASSETS.write_bytes(env.file.save())

    shutil.copy2(TRANSLATIONS, PATCH_ROOT / "translations.json")
    shutil.copy2(ROOT / "patch" / "install.ps1", PATCH_ROOT / "install.ps1")
    shutil.copy2(ROOT / "patch" / "uninstall.ps1", PATCH_ROOT / "uninstall.ps1")
    shutil.copy2(ROOT / "patch" / "README.md", PATCH_ROOT / "README.md")
    shutil.copy2(ROOT / "tools" / "assets" / "OFL.txt", PATCH_ROOT / "OFL.txt")

    manifest = {
        "game": "Dust Front RTS",
        "unity": "2020.3.3f1",
        "source_resource": "Dust Front RTS_Data/resources.assets",
        "source_sha256": source_hash,
        "patched_sha256": sha256(PATCH_ASSETS),
        "text_assets": translated,
        "embedded_font": "Noto Sans CJK SC subset",
        "embedded_font_bytes": font_bytes,
        "source_font_license": "SIL Open Font License 1.1; see OFL.txt",
    }
    (PATCH_ROOT / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
