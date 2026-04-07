# ChainOfMeaning - Claude Code Development Prompt

## PROJE BAĞLAMI

Bu proje, LLM'lere alternatif bir "mana motoru" geliştirmeyi amaçlıyor. Temel felsefe şu:

İnsan beyni bilgiyi token token tutmaz. Bir kitap okuduğunda kitabın tamamını değil, ondan çıkardığı **anlamı** tutar. Her yeni bilgi önceki anlamların **üzerine** inşa edilir. Bu, blockchain mantığına benzer: her blok öncekine referans verir, hiçbir karar sıfırdan başlamaz.

### LLM vs ChainOfMeaning Farkı

| LLM | ChainOfMeaning |
|-----|----------------|
| Token bazlı | Kural/anlam bazlı |
| Her seferinde sıfırdan işler | Kalıcı ve evrilen bir state tutar |
| Pattern matching | Kural zincirleme (muhakeme) |
| Hafızası yok (context window) | Sürekli büyüyen ve evrilen hafıza |
| Next token prediction | Kural aktivasyonu ve çıkarım |

### Temel Mekanizma

Bilgi "kural" olarak temsil edilir. Her kural: subject → relation → object. 
Örnek: "kırmızı → değerlendirme → iyidir", "porsche → bir → araba"

LSTM gate mantığı kurallar üzerinde çalışır:
- **Forget gate**: Yeni kural eskisiyle çelişiyorsa eskisini zayıflat
- **Input gate**: Yeni kuralı state'e entegre et, varsa güçlendir
- **Output gate**: Soru geldiğinde ilgili kuralları aktive et

Kurallar arasında zincirleme çıkarım yapılır: 
"porsche → renk → kırmızı" + "kırmızı → değerlendirme → iyidir" = "porsche dolaylı olarak iyidir"

### Kuralların Hiyerarşisi
Kurallar genel veya özel olabilir:
- Genel: "kırmızı iyidir" (her yerde geçerli)
- Özel: "kırmızı üstü açık Porsche iyidir" (dar kapsam)
Özel kurallar genel kurallardan türer. Genel kural değişirse altındaki özel kurallar etkilenir.

---

## MEVCUT KOD

```python
"""
ChainOfMeaning - LSTM-Style Rule Engine Simulation
Gate'ler sayısal değil, kurallar üzerinde çalışır.
"""

class Rule:
    def __init__(self, subject, relation, obj, confidence=1.0, source=None):
        self.subject = subject.lower()
        self.relation = relation.lower()
        self.obj = obj.lower()
        self.confidence = confidence
        self.source = source or "direct"
    
    def __repr__(self):
        return f"[{self.confidence:.1f}] {self.subject} --{self.relation}--> {self.obj}"
    
    def matches_topic(self, other):
        return self.subject == other.subject and self.relation == other.relation
    
    def contradicts(self, other):
        return self.matches_topic(other) and self.obj != other.obj


class RuleEngine:
    def __init__(self):
        self.state = []
        self.history = []
    
    def forget_gate(self, new_rule):
        forgotten = []
        for existing in self.state:
            if existing.contradicts(new_rule):
                old_conf = existing.confidence
                existing.confidence *= 0.3
                forgotten.append(f"  FORGET: '{existing}' güven düştü ({old_conf:.1f} → {existing.confidence:.1f})")
        return forgotten
    
    def input_gate(self, new_rule):
        integrated = []
        for existing in self.state:
            if existing.subject == new_rule.subject and \
               existing.relation == new_rule.relation and \
               existing.obj == new_rule.obj:
                old_conf = existing.confidence
                existing.confidence = min(1.0, existing.confidence + 0.2)
                integrated.append(f"  INPUT: '{existing}' güçlendi ({old_conf:.1f} → {existing.confidence:.1f})")
                return integrated
        self.state.append(new_rule)
        integrated.append(f"  INPUT: Yeni kural eklendi → '{new_rule}'")
        return integrated
    
    def output_gate(self, query_terms):
        activated = []
        terms = [t.lower() for t in query_terms]
        for rule in self.state:
            if rule.confidence < 0.2:
                continue
            relevance = 0
            if rule.subject in terms: relevance += 1
            if rule.obj in terms: relevance += 1
            for other_rule in self.state:
                if other_rule.obj == rule.subject and other_rule.subject in terms:
                    relevance += 0.5
                if rule.obj == other_rule.subject and other_rule.subject in terms:
                    relevance += 0.5
            if relevance > 0:
                activated.append((rule, relevance))
        activated.sort(key=lambda x: x[1] * x[0].confidence, reverse=True)
        return activated
    
    def ingest(self, new_rule):
        forget_log = self.forget_gate(new_rule)
        input_log = self.input_gate(new_rule)
        dead = [r for r in self.state if r.confidence < 0.1]
        for d in dead:
            self.state.remove(d)
    
    def query(self, question, terms):
        activated = self.output_gate(terms)
        if not activated:
            return None
        return self._chain_reasoning(terms, activated)
    
    def _chain_reasoning(self, terms, activated):
        conclusions = []
        for rule, _ in activated:
            conclusions.append({"type": "direct", "rule": rule, "confidence": rule.confidence})
        for r1, _ in activated:
            for r2, _ in activated:
                if r1.obj == r2.subject and r1 != r2:
                    chained_confidence = r1.confidence * r2.confidence
                    conclusions.append({
                        "type": "chained",
                        "chain": f"{r1.subject} → {r1.obj} → {r2.obj}",
                        "confidence": chained_confidence
                    })
        return conclusions
```

---

## SENİN GÖREVİN

Bu projeyi derinlemesine analiz et, test et ve geliştir. Aşağıdaki adımları sırayla takip et:

### ADIM 1: Mevcut Sistemin Kritik Analizi
- Mevcut kodun gerçekten LSTM gate mantığını doğru uygulayıp uygulamadığını analiz et
- Kuralların "üzerine inşa" mantığı mı yoksa "yanına ekleme" mantığı mı çalışıyor, bunu tespit et
- Graph traversal ile gerçek kural zincirleme arasındaki farkı ortaya koy
- Eksikleri ve yanlışları listele

### ADIM 2: Kapsamlı Test Senaryoları
Şu senaryoları test et:

**Senaryo A - Çelişki Yönetimi:**
1. "Kahve sağlıklıdır" kuralını yükle
2. "Kafein zararlıdır" kuralını yükle  
3. "Kahve kafein içerir" kuralını yükle
4. Sor: "Kahve içmeli miyim?"
→ Sistem çelişkiyi nasıl yönetiyor? Zincirleme çıkarım doğru mu?

**Senaryo B - Derin Zincirleme:**
1. "Sokrates insandır" 
2. "İnsan ölümlüdür"
3. "Ölümlü olan acı çeker"
4. "Acı çeken empati geliştirir"
5. Sor: "Sokrates empati geliştirir mi?"
→ 4 adımlık zinciri kurabiliyor mu?

**Senaryo C - Hiyerarşi:**
1. "Meyve sağlıklıdır" (genel)
2. "Elma bir meyvedir"
3. "Yeşil elma ekşidir" (özel)
4. Sor: "Yeşil elma sağlıklı mıdır?"
→ Genel kuralı özel duruma uygulayabiliyor mu?

**Senaryo D - Zaman İçinde Evrilme:**
1. 10 kitap simüle et, her biri birbiriyle çelişen ve destekleyen kurallar içersin
2. Aynı soruyu her kitaptan sonra sor
3. Güven skorlarının evrilmesini görselleştir
→ Sistem gerçekten "öğreniyor" mu yoksa sadece sayaç mı tutuyor?

**Senaryo E - Stres Testi:**
1. 1000 kural yükle
2. Performansı ölç
3. Çıkarım kalitesinin kural sayısıyla nasıl değiştiğini ölç

### ADIM 3: Problemleri Tespit Et ve Çözüm Öner
Her test sonucunda:
- Neyin çalışıp neyin çalışmadığını raporla
- Çalışmayan her şey için somut çözüm öner
- Çözümü implemente et ve tekrar test et

### ADIM 4: Mimari İyileştirmeler
Testlerden çıkan sonuçlara göre:
- Gate fonksiyonlarını iyileştir
- Zincirleme çıkarım mekanizmasını derinleştir (şu an sadece 2 adım, N adım olmalı)
- Kural hiyerarşisi ekle (genel/özel kurallar)
- Kuralların "üzerine inşa" mantığını gerçekten implement et (şu an yanına ekleme yapıyor)
- Forget gate'in daha sofistike çalışmasını sağla (şu an sadece doğrudan çelişki buluyor)

### ADIM 5: Karşılaştırmalı Analiz
- Aynı soruları bir LLM'e de sor (API ile)
- ChainOfMeaning'in cevaplarıyla karşılaştır
- Hangi durumlarda CoM daha iyi, hangilerinde daha kötü?
- Bu karşılaştırmadan çıkan dersleri mimari iyileştirmeye geri besle

### ADIM 6: Sonuç Raporu
Tüm bulgularını şu formatta raporla:
- Mevcut durum değerlendirmesi
- Test sonuçları özeti
- Yapılan iyileştirmeler
- Kalan açık problemler
- Sonraki adımlar için öneriler

---

## ÖNEMLİ NOTLAR

- Bu bir research projesi. Hata yapmaktan korkma, her hata bir öğrenme.
- Her adımda kodunu çalıştır ve sonuçları göster.
- Kurallar arasındaki ilişkiyi graph traversal olarak değil, gerçek muhakeme olarak düşün. Fark önemli.
- Sistemin amacı bilgiyi "olduğu gibi saklamak" değil, "yorumlayıp üzerine inşa etmek". Bu felsefeyi her kararında göz önünde bulundur.
- Türkçe yorum yaz, İngilizce kod yaz.
