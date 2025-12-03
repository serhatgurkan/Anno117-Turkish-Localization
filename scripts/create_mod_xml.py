#!/usr/bin/env python3
"""
Anno 117: Pax Romana - Türkçe Mod XML Oluşturucu

Bu script, çeviri dosyasından (turkish_translations.json) Anno 117 mod XML dosyası oluşturur.

Kullanım:
1. turkish_translations.json dosyasının bu script ile aynı klasörde olduğundan emin olun
2. python create_mod_xml.py çalıştırın
3. Oluşturulan mod klasörünü oyunun mods/ dizinine kopyalayın
"""
import json
from pathlib import Path


def fix_turkish_chars(text):
    """Türkçe karakterleri ASCII karşılıklarına çevir (oyun fontu desteklemediği için)"""
    replacements = {
        "ı": "i",
        "İ": "I",
        "ş": "s",
        "Ş": "S",
        "ğ": "g",
        "Ğ": "G",
        "ü": "u",
        "Ü": "U",
        "ö": "o",
        "Ö": "O",
        "ç": "c",
        "Ç": "C",
    }
    for tr_char, ascii_char in replacements.items():
        text = text.replace(tr_char, ascii_char)
    return text


def main():
    script_dir = Path(__file__).parent

    # Çevirileri yükle
    translations_file = script_dir / "turkish_translations.json"
    if not translations_file.exists():
        print("HATA: turkish_translations.json bulunamadı!")
        return

    with open(translations_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Checkpoint formatı veya düz dict formatı
    if "translations" in data:
        translations = data["translations"]
    else:
        translations = data

    print(f"Toplam çeviri: {len(translations)}")

    # Mod klasör yapısını oluştur
    mod_dir = script_dir.parent / "mod" / "data" / "base" / "config" / "gui"
    mod_dir.mkdir(parents=True, exist_ok=True)

    output_file = mod_dir / "texts_english.xml"

    # XML oluştur
    with open(output_file, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write("<!--\n")
        f.write("  Anno 117: Pax Romana - Türkçe Dil Paketi\n")
        f.write(f"  Çevrilen metin sayısı: {len(translations)}\n")
        f.write("  https://github.com/user/Anno117-Turkish-Localization\n")
        f.write("-->\n\n")

        f.write("<ModOps>\n")

        for line_id, tr_text in translations.items():
            # Türkçe karakterleri düzelt (font sorunu)
            tr_text = fix_turkish_chars(tr_text)

            # XML escape
            tr_escaped = (
                tr_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            tr_escaped = tr_escaped.replace('"', "&quot;")
            tr_escaped = tr_escaped.replace("\n", "&#10;").replace("\r", "")

            f.write(
                f'  <ModOp Type="Replace" Path="//Text[LineId=\'{line_id}\']/Text">\n'
            )
            f.write(f"    <Text>{tr_escaped}</Text>\n")
            f.write(f"  </ModOp>\n")

        f.write("</ModOps>\n")

    print(f"✓ XML oluşturuldu: {output_file}")
    print(f"\nMod klasörü: {mod_dir.parent.parent.parent.parent}")
    print("Bu klasörü oyunun mods/ dizinine kopyalayın.")


if __name__ == "__main__":
    main()
