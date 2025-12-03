# Anno 117: Pax Romana - Türkçe Yerelleştirme

Anno 117: Pax Romana için topluluk tarafından yapılmış Türkçe dil paketi.

## 📊 İstatistikler

- **Çevrilen metin:** 33,270
- **Çeviri yöntemi:** OpenAI GPT API (paralel işleme)
- **Çeviri süresi:** ~20 dakika (50 paralel worker)

## 📦 Kurulum

### Hazır Mod (Kolay Yol)

1. `mod/` klasörünü indirin
2. Oyun dizinindeki `mods/` klasörüne kopyalayın:
   ```
   C:\Program Files (x86)\Steam\steamapps\common\Anno 117 - Pax Romana\mods\
   ```
3. Klasör adını `[Localization] Turkish` olarak değiştirin
4. Oyunu başlatın

### Elle Derleme

Eğer çevirileri kendiniz güncellemek isterseniz:

1. `scripts/` klasöründeki dosyaları indirin
2. Bağımlılıkları yükleyin:
   ```bash
   pip install openai
   ```
3. (Opsiyonel) Kendi çevirinizi yapmak için:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   python translate.py
   ```
4. Mod XML dosyasını oluşturun:
   ```bash
   python create_mod_xml.py
   ```
5. `mod/` klasörünü oyunun `mods/` dizinine kopyalayın

## 📁 Dosya Yapısı

```
Anno117-Turkish-Localization/
├── mod/                          # Hazır mod dosyaları
│   ├── modinfo.json             # Mod bilgileri
│   └── data/base/config/gui/
│       └── texts_english.xml    # Çeviri XML dosyası
│
├── scripts/                      # Araçlar
│   ├── translate.py             # OpenAI ile çeviri scripti
│   ├── create_mod_xml.py        # Mod XML oluşturucu
│   ├── english_texts.json       # Orijinal İngilizce metinler
│   └── turkish_translations.json # Türkçe çeviriler
│
└── README.md
```

## ⚠️ Bilinen Sorunlar

### Türkçe Karakterler

Oyunun fontu Türkçe karakterleri (ş, ğ, ü, ö, ç, ı, İ) desteklememektedir. Bu nedenle çeviriler ASCII karakterlere dönüştürülmüştür:

| Orijinal | Dönüştürülmüş |
| -------- | ------------- |
| ş, Ş     | s, S          |
| ğ, Ğ     | g, G          |
| ü, Ü     | u, U          |
| ö, Ö     | o, O          |
| ç, Ç     | c, C          |
| ı, İ     | i, I          |

## 🔧 Teknik Detaylar

- **Oyun sürümü:** Anno 117: Pax Romana (Anno 8)
- **Mod formatı:** Anno Mod Loader (ModOps XML)
- **XPath:** `//Text[LineId='xxx']/Text` ile metin değiştirme
- **API:** OpenAI GPT-4o-mini

## 📜 Lisans

Bu proje MIT lisansı altında sunulmaktadır. Oyun içerikleri Ubisoft'a aittir.

## 🤝 Katkıda Bulunma

Çeviri hatalarını düzeltmek veya iyileştirmeler önermek için:

1. Issue açın
2. Pull request gönderin
3. `turkish_translations.json` dosyasını düzenleyin ve `create_mod_xml.py` çalıştırın

---

_Bu çeviri OpenAI API kullanılarak otomatik olarak yapılmıştır. Hatalar içerebilir._

## ☕ Destek

Projeyi beğendiyseniz bana bir kahve ısmarlayabilirsiniz:

<a href="https://www.buymeacoffee.com/serhatgurkan"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=☕&slug=serhatgurkan&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff" /></a>
