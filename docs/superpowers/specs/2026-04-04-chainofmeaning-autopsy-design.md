# ChainOfMeaning Otopsi Testi - Tasarim Dokumani

## Amac

Mevcut ChainOfMeaning prototipini hicbir sey degistirmeden 5 senaryo ile test etmek. Her senaryo icin beklenen davranis tanimlanir, motor ciktisi ile karsilastirilir, 3 katmanli degerlendirme yapilir. Sonuclar, cozum tasariminin temelini olusturur.

## Yaklasim: Otopsi Raporu + Beklenen Davranis Karsilastirmasi

- Kodu olduğu gibi calistir, hicbir seyi duzeltme
- Her senaryo icin beklenen dogru davranisi tanimla
- Motor ciktisi vs beklenen davranis tablosu cikar
- Mock yok, assert yok — gercek calistirma, durust karsilastirma

## Proje Yapisi

```
chainofmeaning/
├── src/
│   └── engine.py              # Mevcut Rule + RuleEngine kodu (dokunulmadan)
├── tests/
│   └── autopsy.py             # 5 senaryoyu kosan test runner
├── expected/
│   └── scenarios.py           # Her senaryo icin beklenen davranis tanimlari
├── reports/
│   └── (otopsi raporu buraya yazilacak)
└── chainofmeaning-claude-code-prompt.md
```

## Degerlendirme Cercevesi

Her senaryo 3 katmanda degerlendirilir:

| Katman | Ne Olculur | PASS | PARTIAL | FAIL |
|--------|-----------|------|---------|------|
| Mekanik Dogruluk | Gate'ler dogru tetikleniyor mu? Confidence skorlari mantikli mi? | Tum gate'ler beklendigi gibi calisir | Bazi gate'ler dogru, bazi sorunlu | Gate'ler yanlis tetikleniyor veya tetiklenmiyor |
| Cikarim Kalitesi | Zincirleme sonuclar mantikli mi? Dogru cevaba ulasiyor mu? | Beklenen cikarim tamamen yapildi | Kismi cikarim var ama eksik | Cikarim yok veya yanlis |
| Anlam Testi | Bilgiyi yorumluyor mu, yoksa sadece graf yurume mi? | Yeni bilgi eski bilgiyle anlamli etkilesim kuruyor | Mekanik etkilesim var ama yorumlama yok | Sadece veri depolama, etkilesim yok |

## Senaryo Tanimlari

### Senaryo A — Celiskili Yonetimi

**Kurallar:**
- "kahve → etki → saglikli"
- "kafein → etki → zararli"
- "kahve → icerir → kafein"

**Soru:** "kahve" hakkinda ne biliyorsun?

**Beklenen davranis:**
- Mekanik: 3 kural eklenmeli, forget gate "kahve→etki→saglikli" ile "kafein→etki→zararli" arasinda dogrudan celiski GORMEMELI (farkli subject) — bu bir limit tespiti
- Cikarim: "kahve→kafein→zararli" zinciri kurulmali, ayni zamanda "kahve→saglikli" dogrudan kurali da donmeli
- Anlam: Sistem celiskiyi fark etmeli ve raporlamali — "kahve hem saglikli (dogrudan) hem zararli (dolayliyla kafein uzerinden)"

**Tahmin:** Mekanik PASS, Cikarim PARTIAL (2 adim zincir kurulabilir ama celiski tespiti yok), Anlam FAIL

### Senaryo B — Derin Zincirleme (4 adim)

**Kurallar:**
- "sokrates → turu → insan"
- "insan → ozellik → olumlü"
- "olumlü → deneyim → aci"
- "aci → gelistirir → empati"

**Soru:** "sokrates" ve "empati" iliskisi?

**Beklenen davranis:**
- Mekanik: 4 kural state'e eklenmeli, conflict yok
- Cikarim: Sokrates→insan→olumlü→aci→empati tam zinciri kurulmali
- Anlam: "Sokrates empati gelistirir cunku insan, olumlü, aci ceker" seklinde anlam zinciri

**Tahmin:** Mekanik PASS, Cikarim FAIL (kod sadece 2 adim zincirliyor), Anlam FAIL

### Senaryo C — Hiyerarsi / Kalitim

**Kurallar:**
- "meyve → etki → saglikli"
- "elma → turu → meyve"
- "yesil elma → tadi → eksi"

**Soru:** "yesil elma saglikli mi?"

**Beklenen davranis:**
- Mekanik: 3 kural eklenmeli
- Cikarim: "yesil elma" → ... → "meyve" → "saglikli" zinciri kurulmali. Bunun icin "yesil elma" ile "elma" arasinda baglanti gerekir (mevcut kodda yok) ve "turu" iliskisinin inheritance anlamina geldigi bilinmeli
- Anlam: Tur hiyerarsisi uzerinden ozellik kalitimi

**Tahmin:** Mekanik PASS, Cikarim FAIL (inheritance yok, "yesil elma" ve "elma" ayri entity'ler), Anlam FAIL

### Senaryo D — Zaman Icinde Evrilme (10 kitap)

**Kurallar:** 10 kitap seti, her biri 3-5 kural. Konu: "teknoloji iyi mi kotu mu?"
- Kitap 1-3: Teknoloji olumlu (verimlilik, iletisim, saglik)
- Kitap 4-6: Teknoloji olumsuz (bagimlilik, issizlik, yalnizlik)
- Kitap 7-8: Dengeli gorusler
- Kitap 9-10: Teknoloji sartli olumlu ("bilinçli kullanim iyidir")

**Soru (her kitaptan sonra):** "Teknoloji iyi midir?"

**Beklenen davranis:**
- Mekanik: Confidence skorlari her kitapla degismeli
- Cikarim: Kitap 1-3'te yuksek olumlu, 4-6'da dusus, 7-10'da nuansli cevap
- Anlam: Sistem gercekten "gorusunu degistiriyor" mu yoksa sadece son eklenen kurala mi yakin?

**Tahmin:** Mekanik PARTIAL (confidence degisiyor ama mekanik — 0.3 carpma/0.2 ekleme), Cikarim PARTIAL, Anlam FAIL (sayac tutma, ogrenme degil)

### Senaryo E — Stres Testi (1000 kural)

**Kurallar:** 1000 otomatik uretilen kural (konu gruplari: hayvanlar, renkler, sehirler, meslekler)

**Olcumler:**
- Ingest suresi (1000 kural yukleme)
- Query suresi (farkli karmasiklikta 10 sorgu)
- Bellek kullanimi
- Cikarim kalitesi (kural sayisi arttikca dogruluk dusiyor mu?)

**Beklenen davranis:**
- Mekanik: O(n²) performans bekleniyor (output_gate icindeki ic ice dongu)
- Cikarim: Kural sayisi arttikca irrelevant sonuclar artabilir (noise)
- Anlam: Olcek buyudugunde anlam kalitesi nasil etkilenir?

**Tahmin:** Mekanik PARTIAL (calisir ama yavas), Cikarim PARTIAL (noise artar), Anlam FAIL

## Sonraki Adim

Otopsi raporu tamamlandiktan sonra, sonuclara dayanarak:
1. Motorun guclu ve zayif yanlari belirlenir
2. Zayif yanlara yonelik cozum mimarisi tasarlanir
3. Cozum implement edilir ve ayni senaryolarla tekrar test edilir
