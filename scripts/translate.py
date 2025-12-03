#!/usr/bin/env python3
"""
Anno 117: Pax Romana - OpenAI API ile Paralel Türkçe Çeviri

Bu script, oyun metinlerini OpenAI API kullanarak Türkçeye çevirir.
50 paralel worker ile çalışarak çeviriyi hızlandırır.

Kullanım:
1. OPENAI_API_KEY ortam değişkenini ayarlayın veya scriptte tanımlayın
2. english_texts.json dosyasının bu script ile aynı klasörde olduğundan emin olun
3. python translate.py çalıştırın

Özellikler:
- Checkpoint sistemi: Kesintiye uğrasa bile kaldığı yerden devam eder
- Paralel işleme: 50 worker ile hızlı çeviri
- Otomatik yeniden deneme: Başarısız istekler 3 kez denenir
"""

import json
import time
import os
from pathlib import Path
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import threading

# API Key - ortam değişkeninden veya buraya yazın
API_KEY = os.environ.get("OPENAI_API_KEY") or "YOUR_API_KEY_HERE"

# Dosya yolları (script ile aynı klasör)
SCRIPT_DIR = Path(__file__).parent
INPUT_FILE = SCRIPT_DIR / "english_texts.json"
CHECKPOINT_FILE = SCRIPT_DIR / "turkish_translations.json"

# Ayarlar
BATCH_SIZE = 20  # Her istekte kaç metin
PARALLEL_WORKERS = 50  # Paralel worker sayısı
MODEL = "gpt-4o-mini"  # Kullanılacak model

# Thread-safe
lock = threading.Lock()
results_dict = {}


def load_checkpoint():
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"translated_ids": [], "translations": {}}


def save_checkpoint(checkpoint):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)


def translate_one_batch(client, batch_data):
    """Tek bir batch çevir"""
    batch_num, texts_batch = batch_data

    texts_for_api = [{"id": lid, "en": txt} for lid, txt in texts_batch]
    prompt = 'Translate "en" to Turkish as "tr". Return ONLY valid JSON array:\n\n'
    input_json = json.dumps(texts_for_api, ensure_ascii=False)

    for retry in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Oyun çevirmeni. JSON çevir. SADECE JSON döndür.",
                    },
                    {"role": "user", "content": prompt + input_json},
                ],
                max_completion_tokens=8192,
            )

            result_text = response.choices[0].message.content
            if not result_text:
                continue

            result_text = result_text.strip()

            # JSON çıkar
            if "```" in result_text:
                for part in result_text.split("```"):
                    part = part.strip()
                    if part.startswith("json"):
                        part = part[4:].strip()
                    if part.startswith("["):
                        result_text = part
                        break

            start = result_text.find("[")
            end = result_text.rfind("]")
            if start != -1 and end != -1:
                result_text = result_text[start : end + 1]

            result = json.loads(result_text)

            translations = {}
            for item in result:
                if "tr" in item and item["tr"]:
                    translations[item["id"]] = item["tr"]
                elif "en" in item:
                    translations[item["id"]] = item["en"]

            with lock:
                results_dict[batch_num] = (texts_batch, translations, True)

            return batch_num, len(translations)

        except Exception as e:
            if retry == 2:
                print(f"  Batch {batch_num} HATA: {e}")
                with lock:
                    results_dict[batch_num] = (texts_batch, {}, False)
                return batch_num, 0

    with lock:
        results_dict[batch_num] = (texts_batch, {}, False)
    return batch_num, 0


def main():
    global results_dict

    if API_KEY == "YOUR_API_KEY_HERE":
        print("HATA: API key ayarlanmamış!")
        print("OPENAI_API_KEY ortam değişkenini ayarlayın veya scriptte tanımlayın.")
        return

    print("=" * 70)
    print("Anno 117: Pax Romana - Türkçe Çeviri")
    print(f"({PARALLEL_WORKERS} paralel worker)")
    print("=" * 70)

    client = OpenAI(api_key=API_KEY)

    # Verileri yükle
    print("\nVeriler yükleniyor...")

    if not INPUT_FILE.exists():
        print(f"HATA: {INPUT_FILE} bulunamadı!")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        english_texts = json.load(f)

    checkpoint = load_checkpoint()
    translated_ids = set(checkpoint.get("translated_ids", []))
    translations = checkpoint.get("translations", {})

    print(f"Toplam metin: {len(english_texts)}")
    print(f"Önceden çevrilmiş: {len(translated_ids)}")

    # Çevrilecekleri bul
    texts_to_translate = [
        (lid, txt)
        for lid, txt in english_texts.items()
        if lid not in translated_ids and txt.strip()
    ]

    print(f"Çevrilecek: {len(texts_to_translate)}")

    if not texts_to_translate:
        print("\nTüm metinler zaten çevrilmiş!")
        return

    # Batch'lere böl
    batches = []
    for i in range(0, len(texts_to_translate), BATCH_SIZE):
        batch_num = len(batches) + 1
        batches.append((batch_num, texts_to_translate[i : i + BATCH_SIZE]))

    total_batches = len(batches)
    print(f"Toplam batch: {total_batches}")
    print(f"\nÇeviri başlıyor...\n")

    start_time = time.time()
    completed_count = 0
    failed_count = 0

    # Paralel gruplar halinde işle
    for group_start in range(0, len(batches), PARALLEL_WORKERS):
        group = batches[group_start : group_start + PARALLEL_WORKERS]
        results_dict = {}

        group_nums = [b[0] for b in group]
        print(f"  Grup başlıyor: Batch {min(group_nums)}-{max(group_nums)}", flush=True)

        # Paralel çalıştır
        with ThreadPoolExecutor(max_workers=PARALLEL_WORKERS) as executor:
            futures = [
                executor.submit(translate_one_batch, client, batch) for batch in group
            ]
            wait(futures, return_when=ALL_COMPLETED)

            for future in futures:
                try:
                    batch_num, count = future.result()
                except Exception as e:
                    print(f"    Hata: {e}", flush=True)

        # Checkpoint güncelle
        for batch_num, (texts_batch, batch_trans, success) in results_dict.items():
            if success and batch_trans:
                translations.update(batch_trans)
                for lid, _ in texts_batch:
                    translated_ids.add(lid)
                completed_count += 1
            else:
                failed_count += 1

        # Kaydet
        checkpoint["translated_ids"] = list(translated_ids)
        checkpoint["translations"] = translations
        save_checkpoint(checkpoint)

        # İlerleme
        done = completed_count + failed_count
        elapsed = time.time() - start_time
        if elapsed > 0 and done > 0:
            rate = done / elapsed * 60
            remaining = (total_batches - done) / rate if rate > 0 else 0
            pct = 100 * done / total_batches
            print(
                f"  ✓ Kaydedildi. Toplam: {len(translations)} | İlerleme: {pct:.1f}% | Kalan: ~{remaining:.1f} dk\n",
                flush=True,
            )

    # Sonuç
    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("TAMAMLANDI!")
    print("=" * 70)
    print(f"Toplam çeviri: {len(translations)}")
    print(f"Başarılı: {completed_count}, Başarısız: {failed_count}")
    print(f"Süre: {elapsed/60:.1f} dakika")


if __name__ == "__main__":
    main()
