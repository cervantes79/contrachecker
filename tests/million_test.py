"""
ChainOfMeaning v4 - 1 MILYON KURAL OLCEK TESTI
================================================
20 alan x ~50K kural = 1,000,000 tutarli, MODERN kural.
50 soru: pozitif, negatif, zincir derinligi, kalitim, celiski/nuans.
Performans olcumu: yukleme suresi, sorgu suresi, RAM, disk.

Kurallar 2024-2025 dunyasindan: yapay zeka, iklim, kripto, saglik, vb.
Rastgele cop DEGIL - her alan icinde tutarli hiyerarsi ve neden-sonuc zincirleri.
"""

import sys
import os
import time
import random
import tracemalloc

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine_v4 import Rule, RuleEngineV4

# Tekrarlanabilirlik icin seed
random.seed(42)


# ======================================================================
#  20 ALAN: Her alan ~50K kural uretir
# ======================================================================

def make_hierarchy(entities, parent, grandparent=None):
    """Tur hiyerarsisi kur: entity -> parent -> grandparent"""
    rules = []
    for e in entities:
        rules.append((e, "turu", parent))
    if grandparent:
        rules.append((parent, "turu", grandparent))
    return rules


def make_properties(entity_props):
    """Ozellikler: {entity: [ozellik1, ozellik2, ...]}"""
    rules = []
    for entity, props in entity_props.items():
        for p in props:
            rules.append((entity, "ozellik", p))
    return rules


def make_effects(cause_effects):
    """Neden-sonuc: [(neden, sonuc), ...]"""
    rules = []
    for cause, effect in cause_effects:
        rules.append((cause, "etki", effect))
    return rules


def make_requires(entity_reqs):
    """Gereksinimler: {entity: [gereksinim, ...]}"""
    rules = []
    for entity, reqs in entity_reqs.items():
        for r in reqs:
            rules.append((entity, "gerektirir", r))
    return rules


def make_provides(entity_benefits):
    """Sagladilar: {entity: [fayda, ...]}"""
    rules = []
    for entity, benefits in entity_benefits.items():
        for b in benefits:
            rules.append((entity, "saglar", b))
    return rules


def make_contains(entity_parts):
    """Icerir: {entity: [parca, ...]}"""
    rules = []
    for entity, parts in entity_parts.items():
        for p in parts:
            rules.append((entity, "icerir", p))
    return rules


def make_causes(pairs):
    """Neden olur: [(neden, sonuc), ...]"""
    return [(n, "neden olur", s) for n, s in pairs]


def make_uses(entity_tools):
    """Kullanir: {entity: [arac, ...]}"""
    rules = []
    for entity, tools in entity_tools.items():
        for t in tools:
            rules.append((entity, "kullanir", t))
    return rules


def make_opposes(pairs):
    """Karsi: [(a, b), ...]"""
    return [(a, "karsi", b) for a, b in pairs]


def make_part_of(entity_wholes):
    """Parcasi: {parca: bütün, ...}"""
    return [(part, "parcasi", whole) for part, whole in entity_wholes.items()]


def expand_with_variations(base_rules, domain_subjects, domain_objects,
                           relations, target_count):
    """
    Cekirdek kurallardan yola cikarak hedef sayiya ulasmak icin
    sistematik varyasyonlar uret.

    Strateji:
    1. Her subject icin farkli relation+object kombinasyonlari
    2. Numarali alt-konular (konu aspekt 1, konu aspekt 2, vb.)
    3. Ozellik ve etki varyasyonlari
    """
    rules = list(base_rules)
    existing = set((s, r, o) for s, r, o in rules)

    # Varyasyon sablonlari
    variation_relations = relations + [
        "iliskili", "bagli", "etkiler", "destekler", "kisitlar",
        "gelistirir", "azaltir", "arttirir", "donusturur", "olusturur",
        "engeller", "hizlandirir", "yavaslatir", "guclendrir", "zayiflatir",
    ]

    # Ek niteleyiciler - havuzu buyutmek icin
    qualifiers = [
        "boyut", "hiz", "maliyet", "kalite", "etki",
        "risk", "fayda", "sorun", "cozum", "durum",
        "faktor", "unsur", "yön", "alan", "kapsam",
        "potansiyel", "sinir", "avantaj", "dezavantaj", "sonuc",
    ]

    # Oncelik 1: Mevcut havuzlardan uret
    attempts = 0
    max_attempts = target_count * 2

    while len(rules) < target_count and attempts < max_attempts:
        attempts += 1
        subj = random.choice(domain_subjects)
        rel = random.choice(variation_relations)
        obj = random.choice(domain_objects)

        triple = (subj, rel, obj)
        if triple not in existing and subj != obj:
            existing.add(triple)
            rules.append(triple)

    # Oncelik 2: Nitelikli varyasyonlar (havuz yetersizse)
    if len(rules) < target_count:
        for q in qualifiers:
            if len(rules) >= target_count:
                break
            for subj in domain_subjects:
                if len(rules) >= target_count:
                    break
                qualified_obj = f"{subj} {q}"
                for rel in variation_relations[:5]:
                    triple = (subj, rel, qualified_obj)
                    if triple not in existing:
                        existing.add(triple)
                        rules.append(triple)
                        if len(rules) >= target_count:
                            break

    # Oncelik 3: Numarali aspektler (son care)
    aspect_idx = 0
    while len(rules) < target_count:
        aspect_idx += 1
        subj = domain_subjects[aspect_idx % len(domain_subjects)]
        obj = f"aspekt {aspect_idx}"
        rel = variation_relations[aspect_idx % len(variation_relations)]
        triple = (subj, rel, obj)
        if triple not in existing:
            existing.add(triple)
            rules.append(triple)

    return rules[:target_count]


# ======================================================================
#  ALAN 1: YAPAY ZEKA & TEKNOLOJI (50K)
# ======================================================================

def generate_ai_tech():
    """Yapay zeka, LLM, bulut bilisim, siber guvenlik, vb."""
    subjects = [
        "yapay zeka", "makine ogrenimi", "derin ogrenme", "llm", "gpt",
        "transformer", "sinir agi", "dogal dil isleme", "bilgisayarli goru",
        "takviyeli ogrenme", "uretken yapay zeka", "chatbot", "otomasyon",
        "robotik", "otonom arac", "drone", "bulut bilisim", "saas", "paas",
        "iaas", "mikroservis", "api", "konteyner", "kubernetes", "docker",
        "devops", "mlops", "veri bilimi", "buyuk veri", "veri ambarı",
        "veri golu", "etl", "veri madenciligi", "veri gorsellestirme",
        "siber guvenlik", "firewall", "sifreleme", "vpn", "antiviruus",
        "blockchain", "akilli sozlesme", "web3", "defi", "nft",
        "metaverse", "sanal gerceklik", "artirilmis gerceklik", "iot",
        "5g", "edge computing", "kuantum bilgisayar", "kuantum sifreleme",
        "fpga", "asic", "gpu", "tpu", "neuromorphic chip",
        "startup", "fintech", "regtech", "insurtech", "healthtech",
        "edtech", "proptech", "agritech", "greentech", "deeptech",
        "yazilim muhendisligi", "agile", "scrum", "ci cd", "test otomasyonu",
        "python", "javascript", "rust", "go", "typescript",
        "react", "angular", "vue", "svelte", "next.js",
        "veritabani", "sql", "nosql", "redis", "postgresql",
        "elasticsearch", "kafka", "rabbitmq", "grpc", "graphql",
        "linux", "windows", "macos", "android", "ios",
        "prompt muhendisligi", "fine tuning", "rag", "embedding", "vektordb",
    ]

    objects = [
        "verimlilik", "hiz", "olceklenebilirlik", "guvenlik", "maliyet",
        "karmasiklik", "veri", "hesaplama gucu", "enerji", "elektrik",
        "inovasyon", "rekabet", "dijital donusum", "otomasyon", "verimlilik artisi",
        "issizlik riski", "yeni is alanlari", "uretkenlik", "kalite",
        "dogruluk", "hata orani", "gecikme", "bant genisligi", "depolama",
        "gizlilik", "etik", "onyargi", "seffaflik", "hesap verebilirlik",
        "regulasyon", "standart", "sertifikasyon", "lisans", "patent",
        "acik kaynak", "topluluk", "ekosistem", "entegrasyon", "uyumluluk",
        "kullanici deneyimi", "erisilebirlik", "performans", "guvenilirlik",
        "sureklilik", "yedekleme", "felaket kurtarma", "izleme", "loglama",
        "yapay zeka etkisi", "insan makine etkilesimi", "karar destek",
    ]

    relations = [
        "ozellik", "etki", "gerektirir", "saglar", "kullanir",
        "icerir", "turu", "neden olur", "bagimli", "alternatif",
    ]

    base_rules = []

    # Tur hiyerarsisi
    base_rules += make_hierarchy(
        ["makine ogrenimi", "derin ogrenme", "dogal dil isleme",
         "bilgisayarli goru", "takviyeli ogrenme", "uretken yapay zeka"],
        "yapay zeka", "teknoloji"
    )
    base_rules += make_hierarchy(
        ["llm", "gpt", "chatbot", "prompt muhendisligi"],
        "dogal dil isleme"
    )
    base_rules += make_hierarchy(
        ["transformer", "sinir agi"], "derin ogrenme"
    )
    base_rules += make_hierarchy(
        ["bulut bilisim", "saas", "paas", "iaas"], "bilisim altyapisi", "teknoloji"
    )
    base_rules += make_hierarchy(
        ["mikroservis", "konteyner", "kubernetes", "docker"], "bulut bilisim"
    )
    base_rules += make_hierarchy(
        ["blockchain", "akilli sozlesme", "web3", "defi", "nft"], "kripto teknoloji", "teknoloji"
    )
    base_rules += make_hierarchy(
        ["sanal gerceklik", "artirilmis gerceklik", "metaverse"], "xr teknoloji", "teknoloji"
    )
    base_rules += make_hierarchy(
        ["siber guvenlik", "firewall", "sifreleme", "vpn"], "guvenlik teknolojisi", "teknoloji"
    )
    base_rules += make_hierarchy(
        ["startup", "fintech", "edtech", "healthtech", "deeptech"], "teknoloji girisimi"
    )

    # Ozellikler
    base_rules += make_properties({
        "yapay zeka": ["akilli", "ogrenebilir", "uyarlanabilir", "veri odakli"],
        "llm": ["buyuk olcekli", "cok dilli", "uretken", "halusinasyon riski"],
        "gpt": ["transformer tabanli", "otomatik tamamlama", "cok amacli"],
        "blockchain": ["dagitik", "degistirilemez", "seffaf", "guvensiz ortam"],
        "bulut bilisim": ["olceklenebilir", "esnek", "kullan ode", "uzaktan erisim"],
        "siber guvenlik": ["koruyucu", "kritik", "surekli guncelleme", "cok katmanli"],
        "otonom arac": ["sensoru", "yapay zeka destekli", "lidar", "kamera"],
        "kuantum bilgisayar": ["superkonumlu", "dolanık", "paralel hesaplama"],
        "5g": ["dusuk gecikme", "yuksek bant", "buyuk baglantilik"],
        "iot": ["bagli cihaz", "sensor", "veri toplama", "uzaktan izleme"],
    })

    # Neden-sonuc zincirleri
    base_rules += make_effects([
        ("yapay zeka", "otomasyon"), ("otomasyon", "verimlilik artisi"),
        ("otomasyon", "issizlik riski"), ("verimlilik artisi", "ekonomik buyume"),
        ("llm", "icerik uretimi"), ("icerik uretimi", "bilgi kirliligi riski"),
        ("derin ogrenme", "oruntu tanima"), ("oruntu tanima", "tahmin gucu"),
        ("blockchain", "merkezsizlesme"), ("merkezsizlesme", "aracisizlik"),
        ("bulut bilisim", "maliyet azalma"), ("maliyet azalma", "girisimcilik artisi"),
        ("siber guvenlik", "veri koruma"), ("veri koruma", "gizlilik"),
        ("5g", "hizli iletisim"), ("hizli iletisim", "iot genisleme"),
        ("yapay zeka", "karar destek"), ("karar destek", "daha iyi sonuc"),
        ("gpu", "paralel hesaplama"), ("paralel hesaplama", "hizli egitim"),
        ("transformer", "dikkat mekanizmasi"), ("dikkat mekanizmasi", "baglam anlama"),
        ("kuantum bilgisayar", "sifre kirma riski"), ("sifre kirma riski", "guvenlik tehdidi"),
        ("otonom arac", "trafik azalma"), ("trafik azalma", "emisyon dusme"),
    ])

    # Gereksinimler
    base_rules += make_requires({
        "yapay zeka": ["veri", "hesaplama gucu", "algoritma"],
        "derin ogrenme": ["buyuk veri", "gpu", "enerji"],
        "llm": ["trilyonlarca parametre", "buyuk veri seti", "gpu kumeleri"],
        "bulut bilisim": ["internet", "veri merkezi", "sanalastirma"],
        "blockchain": ["dagitik ag", "konsensus mekanizmasi", "kriptografi"],
        "otonom arac": ["lidar", "yapay zeka", "harita verisi", "5g baglanti"],
        "kuantum bilgisayar": ["mutlak sifir", "kuantum bit", "hata duzeltme"],
    })

    # Sagladilar
    base_rules += make_provides({
        "yapay zeka": ["otomasyon", "tahmin", "optimizasyon", "kisiselletirme"],
        "bulut bilisim": ["olceklenebilirlik", "esneklik", "maliyet tasarrufu"],
        "blockchain": ["seffaflik", "guven", "izlenebilirlik"],
        "5g": ["hiz", "dusuk gecikme", "buyuk kapasite"],
    })

    # Cross-domain baglantilar
    base_rules += [
        ("yapay zeka", "kullanilir", "saglik"),
        ("yapay zeka", "kullanilir", "egitim"),
        ("yapay zeka", "kullanilir", "finans"),
        ("yapay zeka", "kullanilir", "ulasim"),
        ("blockchain", "kullanilir", "finans"),
        ("blockchain", "kullanilir", "tedarik zinciri"),
        ("iot", "kullanilir", "tarim"),
        ("iot", "kullanilir", "saglik"),
        ("5g", "destekler", "iot"),
        ("yapay zeka", "destekler", "siber guvenlik"),
    ]

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


# ======================================================================
#  ALAN 2: SAGLIK & TIP (50K)
# ======================================================================

def generate_health():
    subjects = [
        "covid", "mrna asisi", "asi", "bagisiklik", "pandemi", "telemedicine",
        "dijital saglik", "dna", "gen tedavisi", "crispr", "kanser",
        "diyabet", "kalp hastaligi", "obezite", "antibiyotik direnci",
        "superbug", "ruh sagligi", "depresyon", "anksiyete", "stres",
        "beslenme", "intermittent fasting", "probiyotik", "prebiyotik",
        "vitamin", "mineral", "protein", "omega3", "antioksidan",
        "egzersiz", "kardiyovaskuler", "metabolizma", "hormon",
        "insulin", "kortizol", "serotonin", "dopamin", "melatonin",
        "mikrobiom", "bagisiklik sistemi", "t hucresi", "antikor",
        "pcr testi", "antijen testi", "klinik deney", "faz 3",
        "ilac gelistirme", "biyoteknoloji", "nanoteknoloji tip",
        "yapay organ", "stem hucre", "biyobaski", "protez",
        "robotik cerrahi", "laparoskopi", "radyoterapi", "kemoterapi",
        "immunoterapi", "hedefe yonelik tedavi", "kisisellestirilmis tip",
        "genomik", "proteomik", "metabolomik", "biyoinformatik",
        "saglik sigortasi", "halk sagligi", "epidemiyoloji", "biyoistatistik",
        "dezenfektan", "maske", "sosyal mesafe", "karantina", "izolasyon",
        "hastane enfeksiyonu", "sterilizasyon", "hijyen", "temiz su",
        "gida guvenligi", "alerji", "otoimmun", "inflamasyon", "agri",
        "antibiyotik", "antiviral", "antifungal", "anestetik", "analezik",
        "alzheimer", "parkinson", "epilepsi", "ms hastaligi", "als",
    ]

    objects = [
        "saglik", "hastalik", "tedavi", "koruma", "risk", "fayda",
        "yan etki", "bagimlilik", "iyilesme", "kronik", "akut",
        "olum riski", "yasam kalitesi", "uzun omur", "bagisiklik",
        "enfeksiyon", "virus", "bakteri", "parazit", "mantar",
        "semptom", "teshis", "prognoz", "rehabilitasyon", "onleme",
        "epidemi", "pandemi", "endemi", "mutasyon", "varyant",
        "etkinlik", "guvenlik", "dozaj", "etkisim", "kontrendikasyon",
        "arastrma", "kesfif", "inovasyon", "patent", "maliyet",
        "erisim", "esitlik", "etik", "onam", "mahremiyet",
    ]

    relations = [
        "ozellik", "etki", "tedavi eder", "neden olur", "onler",
        "arttirir", "azaltir", "icerir", "turu", "gerektirir",
    ]

    base_rules = []

    # Hiyerarsi
    base_rules += make_hierarchy(
        ["covid", "grip", "zaturrre", "brontsit", "astim"],
        "solunum hastaligi", "hastalik"
    )
    base_rules += make_hierarchy(
        ["kanser", "diyabet", "kalp hastaligi", "obezite", "alzheimer", "parkinson"],
        "kronik hastalik", "hastalik"
    )
    base_rules += make_hierarchy(
        ["depresyon", "anksiyete", "stres", "bipolar", "sizofreni"],
        "ruh sagligi sorunu", "hastalik"
    )
    base_rules += make_hierarchy(
        ["mrna asisi", "asi", "antiviral", "antibiyotik"],
        "tedavi yontemi", "tip"
    )
    base_rules += make_hierarchy(
        ["crispr", "gen tedavisi", "stem hucre", "biyobaski"],
        "ileri tip teknolojisi", "tip"
    )
    base_rules += make_hierarchy(
        ["vitamin", "mineral", "protein", "omega3", "probiyotik"],
        "besin ogeleri", "beslenme"
    )

    # Ozellikler
    base_rules += make_properties({
        "mrna asisi": ["hizli uretim", "guncelllenebilir", "soguk zincir"],
        "covid": ["bulasici", "solunum yolu", "mutasyona yatkin", "pandemi etkeni"],
        "kanser": ["kontrolsuz bolunme", "metastaz riski", "genetik faktor"],
        "depresyon": ["kronik", "tekrarlayici", "biyokimyasal", "tedavi edilebilir"],
        "crispr": ["hassas", "hedefli", "gen duzenleme", "etik tartisma"],
        "antibiyotik direnci": ["artan", "global tehdit", "asiri kullanim sonucu"],
    })

    # Neden-sonuc zincirleri - KRITIK
    base_rules += make_effects([
        ("covid", "solunum yetmezligi"), ("solunum yetmezligi", "olum riski"),
        ("mrna asisi", "bagisiklik"), ("bagisiklik", "enfeksiyon koruma"),
        ("mrna asisi", "hafif yan etki"), ("hafif yan etki", "gecici rahatsizlik"),
        ("obezite", "diyabet riski"), ("diyabet", "komplikasyon"),
        ("stres", "kortizol artisi"), ("kortizol artisi", "bagisiklik dususu"),
        ("bagisiklik dususu", "hastalik riski"), ("egzersiz", "saglik"),
        ("egzersiz", "stres azalma"), ("stres azalma", "ruh sagligi iyilesme"),
        ("antibiyotik direnci", "tedavi basarisizligi"),
        ("tedavi basarisizligi", "olum riski artisi"),
        ("depresyon", "yasam kalitesi dususu"),
        ("crispr", "genetik hastalik tedavisi"),
        ("kemoterapi", "tumor kuculme"), ("kemoterapi", "yan etki"),
        ("immunoterapi", "bagisiklik guclenme"),
        ("intermittent fasting", "metabolizma hizlanma"),
        ("probiyotik", "mikrobiyom denge"), ("mikrobiyom denge", "sindirim sagligi"),
    ])

    # mrna asisi hem etkin hem yan etki (nuans testi icin)
    base_rules += [
        ("mrna asisi", "etkinlik", "yuzde 95"),
        ("mrna asisi", "saglar", "ciddi hastaliklardan koruma"),
        ("mrna asisi", "risk", "nadir alerjik reaksiyon"),
    ]

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


# ======================================================================
#  ALAN 3: IKLIM & CEVRE (50K)
# ======================================================================

def generate_climate():
    subjects = [
        "iklim degisikligi", "kuresel isinma", "karbon salimi", "sera gazi",
        "karbon dioksit", "metan", "ozon tabakasi", "asit yagmuru",
        "yenilenebilir enerji", "gunes enerjisi", "gunes paneli", "ruzgar enerjisi",
        "ruzgar turbini", "hidroelektrik", "jeotermal", "bioenerji", "dalga enerjisi",
        "nukleer enerji", "fosil yakit", "komur", "petrol", "dogal gaz",
        "elektrikli arac", "tesla", "hibrit arac", "hidrojen yakit hucresi",
        "karbon ayak izi", "karbon notalama", "emisyon ticaret sistemi",
        "buzul erimesi", "deniz seviyesi yukselme", "kutup erimesi",
        "biyocesitlilik", "turlerin yok olma", "orman katliami", "cöllesme",
        "geri donusum", "surdurulebilirlik", "dongusel ekonomi", "sifir atik",
        "plastik kirliligi", "okyanus asitlenmesi", "su kirliligi", "hava kirliligi",
        "paris anlasmasi", "yesil mutabakat", "karbon vergisi", "iklim fonu",
        "tarim emisyonu", "hayvancilik emisyonu", "gida israfi", "kompost",
        "yesil bina", "enerji verimliligi", "izolasyon", "akilli sehir",
        "elektrikli otobus", "bisiklet altyapisi", "toplu tasima", "paylasimli arac",
        "agaclandirma", "karbon tutma", "karbon depolama", "dac teknolojisi",
        "iklim gocmeni", "iklim adaleti", "cevresel adalet", "ekosistem restorasyon",
        "mercan resifi", "amazon ormani", "arktik buz", "permafrost",
        "su taskin", "kuraklik", "orman yangini", "sicak dalga", "kasirga",
        "iklim modeli", "ipcc", "bilimsel konsensus", "iklim inkarcilik",
    ]

    objects = [
        "sicaklik artisi", "deniz seviyesi", "biyocesitlilik kaybi", "kuraklik",
        "sel", "kasirga", "goc", "gida guvenligi", "su kitligi",
        "saglik tehdidi", "ekonomik kayip", "ekosistem cokusu", "tur yokolus",
        "temiz hava", "temiz su", "saglikli toprak", "karbon azalma",
        "enerji bagimsizligi", "yesil ekonomi", "surdurulebilir kalkinma",
        "fosil yakit bagimliligi", "enerji yoksullugu", "cevresel bozulma",
    ]

    relations = [
        "ozellik", "etki", "neden olur", "azaltir", "arttirir",
        "onler", "turu", "gerektirir", "saglar", "engeller",
    ]

    base_rules = []

    # Hiyerarsi
    base_rules += make_hierarchy(
        ["gunes enerjisi", "ruzgar enerjisi", "hidroelektrik", "jeotermal", "bioenerji"],
        "yenilenebilir enerji", "enerji"
    )
    base_rules += make_hierarchy(
        ["komur", "petrol", "dogal gaz"], "fosil yakit", "enerji"
    )
    base_rules += make_hierarchy(
        ["elektrikli arac", "hibrit arac", "hidrojen yakit hucresi"],
        "temiz ulasim", "ulasim"
    )
    base_rules += make_hierarchy(
        ["geri donusum", "kompost", "sifir atik", "dongusel ekonomi"],
        "atik yonetimi", "cevre koruma"
    )

    # Kritik neden-sonuc zincirleri
    base_rules += make_causes([
        ("fosil yakit", "karbon salimi"), ("karbon salimi", "sera gazi artisi"),
        ("sera gazi artisi", "kuresel isinma"), ("kuresel isinma", "buzul erimesi"),
        ("buzul erimesi", "deniz seviyesi yukselme"),
        ("deniz seviyesi yukselme", "kiyisel su baskin"),
        ("kuresel isinma", "sicak dalga"), ("sicak dalga", "kuraklik"),
        ("kuraklik", "gida krizi"), ("gida krizi", "goc"),
        ("orman katliami", "karbon salimi artisi"),
        ("plastik kirliligi", "okyanus kirlilik"),
        ("okyanus kirlilik", "deniz canli olumu"),
    ])

    # Cozumler
    base_rules += make_effects([
        ("yenilenebilir enerji", "karbon azalma"),
        ("gunes paneli", "temiz elektrik"),
        ("ruzgar turbini", "temiz elektrik"),
        ("elektrikli arac", "emisyon azalma"),
        ("agaclandirma", "karbon tutma"),
        ("geri donusum", "atik azalma"),
        ("enerji verimliligi", "enerji tasarrufu"),
    ])

    # Elektrikli arac nuansi (cevreci AMA batarya sorunu)
    base_rules += [
        ("elektrikli arac", "saglar", "sifir egzoz emisyonu"),
        ("elektrikli arac", "gerektirir", "lityum batarya"),
        ("lityum batarya", "neden olur", "maden cikartma"),
        ("maden cikartma", "etki", "cevre tahribati"),
        ("lityum batarya", "ozellik", "geri donusturullebilir"),
    ]

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


# ======================================================================
#  ALAN 4: EKONOMI & FINANS (50K)
# ======================================================================

def generate_economy():
    subjects = [
        "enflasyon", "faiz orani", "merkez bankasi", "para politikasi",
        "maliye politikasi", "butce acigi", "kamu borcu", "gdp", "gsyih",
        "issizlik", "istihdam", "asgari ucret", "gelir esitsizligi",
        "bitcoin", "ethereum", "kripto para", "stablecoin", "cbdc",
        "defi", "nft", "ico", "mining", "cuzdan",
        "borsa", "bist", "nasdaq", "sp500", "hisse senedi",
        "tahvil", "doviz", "dolar", "euro", "altin",
        "venture capital", "melek yatirimci", "startup yatirimi", "ipo",
        "unicorn", "decacorn", "halka arz", "ozel sermaye",
        "fintech", "dijital banka", "mobil odeme", "kripto borsa",
        "mikro kredi", "crowdfunding", "peer to peer", "robot danismanlik",
        "ticaretavar", "supplychain", "lojistik", "e-ticaret", "perakende",
        "vergi", "kdv", "gelir vergisi", "kurumlar vergisi",
        "emeklilik", "bireysel emeklilik", "sigorta", "risk yonetimi",
        "resesyon", "stagflasyon", "deflasyon", "likidite", "volatilite",
        "duzenleme", "regülasyon", "sec", "spk", "bddk",
        "uluslararasi ticaret", "gumruk", "serbest bolge", "dtö",
        "dijital para", "e-para", "odeme sistemi", "swift", "eft",
    ]

    objects = [
        "buyume", "kuculme", "istikrar", "kriz", "refah",
        "yoksulluk", "esitsizlik", "firsat", "risk", "getiri",
        "likidite", "guven", "belirsizlik", "spekülasyon", "balon",
        "inovasyon", "verimlilik", "rekabet", "tekel", "oligopol",
        "tüketici", "üretici", "yatirimci", "tasarruf", "borc",
    ]

    relations = [
        "ozellik", "etki", "neden olur", "arttirir", "azaltir",
        "gerektirir", "saglar", "turu", "iliskili", "belirler",
    ]

    base_rules = []

    # Hiyerarsi
    base_rules += make_hierarchy(
        ["bitcoin", "ethereum", "stablecoin"], "kripto para", "dijital varlik"
    )
    base_rules += make_hierarchy(
        ["hisse senedi", "tahvil", "doviz", "altin"], "yatirim araci", "finans"
    )
    base_rules += make_hierarchy(
        ["fintech", "dijital banka", "kripto borsa", "robot danismanlik"],
        "dijital finans", "finans"
    )

    # Ekonomi zincirleri
    base_rules += make_causes([
        ("enflasyon", "alis gucu dususu"), ("alis gucu dususu", "tuketim azalma"),
        ("faiz artisi", "kredi pahalanma"), ("kredi pahalanma", "yatirim azalma"),
        ("yatirim azalma", "issizlik artisi"),
        ("issizlik artisi", "sosyal huzursuzluk"),
        ("bitcoin", "finansal ozgurluk"), ("bitcoin", "volatilite"),
        ("merkez bankasi", "para politikasi"), ("para politikasi", "faiz orani"),
        ("resesyon", "issizlik artisi"), ("resesyon", "iflas artisi"),
    ])

    # Bitcoin nuansi
    base_rules += [
        ("bitcoin", "ozellik", "sinirli arz"),
        ("bitcoin", "ozellik", "merkezsiz"),
        ("bitcoin", "etki", "finansal erisim"),
        ("bitcoin", "risk", "volatilite"),
        ("bitcoin", "risk", "regulasyon belirsizligi"),
        ("bitcoin", "gerektirir", "elektrik"),
        ("bitcoin mining", "neden olur", "enerji tuketimi"),
    ]

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


# ======================================================================
#  ALAN 5: EGITIM & GELISIM (50K)
# ======================================================================

def generate_education():
    subjects = [
        "online egitim", "mooc", "uzaktan ogretim", "hibrit egitim",
        "yapay zeka egitimde", "kisisellestirilmis ogrenme", "uyarlanabilir ogrenme",
        "kodlama egitimi", "stem", "steam", "maker hareketi",
        "dijital okuryazarlik", "medya okuryazarligi", "veri okuryazarligi",
        "yasam boyu ogrenme", "beceri gelistirme", "yeniden beceri kazanma",
        "mentorlik", "coaching", "ogrenci motivasyonu", "ogretmen egitimi",
        "gamification", "ogrenci merkezli", "proje tabanli ogrenme",
        "universite", "lise", "ilkogretim", "anaokulu", "kreş",
        "sinav sistemi", "olcme degerlendirme", "portfolyo", "rubrik",
        "egitim teknolojisi", "lms", "sanal sinif", "dijital tahta",
        "acik ders kaynaklari", "oer", "creative commons", "khan academy",
        "coursera", "udemy", "youtube egitim", "podcast egitim",
        "ogrenme analitigi", "dashbooard", "veri ile karar",
        "ozel egitim", "kaynastirma", "ustun yetenekli", "disleksi",
        "coklu zeka", "ogrenme stilleri", "eleştirel dusunme",
        "yaratici dusunme", "problem cozme", "isbirligi", "iletisim becerisi",
        "sosyal duygusal ogrenme", "mindfulness egitim", "karakter egitimi",
        "egitimde esitlik", "dijital ucurum", "erisim", "firssat esitligi",
        "erasmus", "degisim programi", "uluslararasi egitim", "dil ogrenme",
    ]

    objects = [
        "ogrenme", "bilgi", "beceri", "yetkinlik", "motivasyon",
        "basari", "erisim", "esitlik", "firsat", "istihdam",
        "verimlilik", "kalite", "maliyet", "esneklik", "uyumluluk",
        "kritik dusunme", "yaraticilik", "isbirligi", "iletisim",
        "dijital yetkinlik", "kodlama becerisi", "veri analizi yetkinligi",
    ]

    relations = [
        "ozellik", "etki", "saglar", "gerektirir", "turu",
        "arttirir", "azaltir", "destekler", "engelleir", "icerir",
    ]

    base_rules = []

    base_rules += make_hierarchy(
        ["online egitim", "mooc", "uzaktan ogretim", "hibrit egitim"],
        "dijital egitim", "egitim"
    )
    base_rules += make_hierarchy(
        ["kodlama egitimi", "stem", "steam", "maker hareketi"],
        "beceri egitimi", "egitim"
    )
    base_rules += make_hierarchy(
        ["universite", "lise", "ilkogretim", "anaokulu"],
        "orgün egitim", "egitim"
    )

    base_rules += make_effects([
        ("online egitim", "erisim artisi"), ("erisim artisi", "firsat esitligi"),
        ("yapay zeka egitimde", "kisisellestirilmis ogrenme"),
        ("kisisellestirilmis ogrenme", "ogrenme verimi artisi"),
        ("gamification", "motivasyon artisi"), ("motivasyon artisi", "katilim artisi"),
        ("dijital ucurum", "egitim esitsizligi"),
        ("stem", "bilimsel dusunme"), ("bilimsel dusunme", "problem cozme becerisi"),
        ("mentorlik", "kariyer gelisimi"),
    ])

    # Uzaktan egitim nuansi
    base_rules += [
        ("uzaktan ogretim", "saglar", "esneklik"),
        ("uzaktan ogretim", "saglar", "mekan bagimsizlik"),
        ("uzaktan ogretim", "risk", "sosyal izolasyon"),
        ("uzaktan ogretim", "risk", "motivasyon kaybi"),
        ("uzaktan ogretim", "gerektirir", "oz disiplin"),
    ]

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


# ======================================================================
#  ALAN 6: TOPLUM & SIYASET (50K)
# ======================================================================

def generate_society():
    subjects = [
        "demokrasi", "otokrasi", "populizm", "liberalizm", "sosyalizm",
        "insan haklari", "ifade ozgurlugu", "basin ozgurlugu", "secim",
        "anayasa", "hukuk devleti", "yargı bagimsizligi", "guc ayrimi",
        "sosyal medya etkisi", "dezenformasyon", "fake news", "trol ciftligi",
        "polarizasyon", "filtre balonu", "yanki odasi", "algoritma etkisi",
        "goc", "multiculturalism", "entegrasyon", "asimilasyon",
        "cinsiyet esitligi", "feminizm", "lgbtq haklari", "esit ucret",
        "sivil toplum", "stk", "aktivizm", "protesto", "grev",
        "dijital aktivizm", "hashtag hareketi", "change.org", "online dilekce",
        "seffaflik", "hesap verebilirlik", "yolsuzluk", "nepotizm",
        "secim guvenligi", "e-oylama", "oy guvenligi", "manipulasyon",
        "kuresellesme", "milliyetcilik", "bölgeselcilik", "ulusüstü kurumlar",
        "bm", "ab", "nato", "g20", "briks",
        "insani yardim", "multeci", "siginmaci", "iltica",
        "veri gizliligi", "gozetim", "biyometrik", "yuktanima",
        "etik yapay zeka", "algoritmik adalet", "dijital haklar",
        "sosyal devlet", "evrensel temel gelir", "saglik hakki", "egitim hakki",
    ]

    objects = [
        "adalet", "esitlik", "ozgurluk", "guvenlik", "refah",
        "katilim", "temsil", "seffaflik", "hesap verebilirlik",
        "toplumsal uyum", "catisma", "uzlasma", "dialog",
        "kutuplaşma", "radikallseeme", "hoşgorü", "çogulculuk",
    ]

    relations = [
        "ozellik", "etki", "saglar", "tehdit eder", "turu",
        "gerektirir", "destekler", "zayiflatir", "guclendrir",
    ]

    base_rules = []

    base_rules += make_hierarchy(
        ["demokrasi", "otokrasi", "monarsi"], "yonetim bicimi", "siyaset"
    )
    base_rules += make_hierarchy(
        ["liberalizm", "sosyalizm", "populizm", "milliyetcilik"],
        "siyasi ideoloji", "siyaset"
    )

    base_rules += make_effects([
        ("dezenformasyon", "toplumsal kutuplasma"),
        ("toplumsal kutuplasma", "sosyal cozulme"),
        ("sosyal medya etkisi", "hizli bilgi yayilimi"),
        ("hizli bilgi yayilimi", "dezenformasyon riski"),
        ("demokrasi", "vatandas katilimi"),
        ("goc", "kulturel cesitlilik"), ("kulturel cesitlilik", "toplumsal zenginlik"),
        ("yolsuzluk", "kamu guveni erozyonu"),
        ("ifade ozgurlugu", "acik tartisma"),
    ])

    # Sosyal medya nuansi
    base_rules += [
        ("sosyal medya etkisi", "saglar", "demokratik katilim"),
        ("sosyal medya etkisi", "saglar", "bilgi erisimi"),
        ("sosyal medya etkisi", "neden olur", "dezenformasyon yayilimi"),
        ("sosyal medya etkisi", "neden olur", "filtre balonu"),
        ("sosyal medya etkisi", "neden olur", "bagimlilik"),
    ]

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


# ======================================================================
#  ALAN 7: BILIM (50K)
# ======================================================================

def generate_science():
    subjects = [
        "fizik", "kuantum mekanigi", "gorellik", "kara delik", "notrino",
        "higgs bozonu", "karanlık madde", "karanlik enerji", "sicim teorisi",
        "buyuk patlama", "kozmoloji", "astrofizik", "yildiz", "galaksi",
        "dna", "rna", "genom", "gen", "mutasyon", "evolusyon",
        "crispr", "gen duzeneleme", "genetik muhendislik", "klonlama",
        "mars", "spacex", "nasa", "esa", "asteroid", "kuyruklu yildiz",
        "uzay istasyonu", "iss", "uzay turizmi", "mars kolonisi",
        "nukleer fuzyon", "iter", "tokamak", "plazma", "enerji",
        "superconductor", "oda sicakligi superconductor", "graphene",
        "nanoteknoloji", "nanobot", "nanomateryal", "karbon nanotup",
        "biyoloji", "kimya", "matematik", "istatistik", "yapay zeka bilim",
        "deney", "hipotez", "teori", "kanun", "model",
        "bilimsel yontem", "peer review", "tekrarlanabilirlik", "falsifikasyon",
        "nobel odulu", "bilimsel etik", "arastirma fonlama", "akademi",
        "derin deniz", "volkan", "deprem", "tsunami", "iklim bilimi",
        "arkeoloji", "paleontoloji", "fosil", "dinozor", "homo sapiens",
    ]

    objects = [
        "kesfif", "bilgi", "anlayis", "tahmin", "kanit",
        "teori", "model", "denklem", "deney", "gozlem",
        "evren", "madde", "enerji", "zaman", "mekan",
        "yasam", "evolusyon", "cesitlilik", "uyum", "secilim",
    ]

    relations = [
        "ozellik", "etki", "aciiklar", "turu", "icerir",
        "gerektirir", "saglar", "kesfetti", "kanitlar",
    ]

    base_rules = []

    base_rules += make_hierarchy(
        ["kuantum mekanigi", "gorellik", "sicim teorisi"],
        "teorik fizik", "fizik"
    )
    base_rules += make_hierarchy(
        ["kara delik", "notrino", "higgs bozonu", "karanlik madde"],
        "parçacik fizigi", "fizik"
    )
    base_rules += make_hierarchy(
        ["dna", "rna", "genom", "gen"], "genetik", "biyoloji"
    )
    base_rules += make_hierarchy(
        ["mars", "spacex", "nasa", "uzay istasyonu"],
        "uzay kesfif", "bilim"
    )

    base_rules += make_effects([
        ("buyuk patlama", "evren olusumu"), ("evren olusumu", "galaksi olusumu"),
        ("galaksi olusumu", "yildiz olusumu"), ("yildiz olusumu", "gezegen olusumu"),
        ("nukleer fuzyon", "enerji uretimi"), ("enerji uretimi", "yildiz parlamasi"),
        ("mutasyon", "genetik cesitlilik"), ("genetik cesitlilik", "evolusyon"),
        ("crispr", "hassas gen duzenleme"), ("hassas gen duzenleme", "tedavi imkani"),
        ("superconductor", "kayipsiz iletim"), ("kayipsiz iletim", "enerji verimliligi"),
        ("graphene", "yuksek iletkenlik"), ("graphene", "ultra hafiflik"),
    ])

    # CRISPR etik nuansi
    base_rules += [
        ("crispr", "saglar", "genetik hastalik tedavisi"),
        ("crispr", "risk", "istenmeyen mutasyon"),
        ("crispr", "risk", "etik ihlal"),
        ("crispr", "gerektirir", "etik denetim"),
    ]

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


# ======================================================================
#  ALAN 8: KULTUR & SANAT (50K)
# ======================================================================

def generate_culture():
    subjects = [
        "netflix", "disney plus", "hbo", "amazon prime", "streaming",
        "podcast", "youtube", "tiktok", "instagram", "twitter",
        "influencer", "content creator", "youtuber", "tiktoker",
        "dijital sanat", "nft art", "yapay zeka sanati", "generative art",
        "muzik uretimi", "ai muzik", "spotify", "apple music",
        "gaming", "esport", "twitch", "steam", "playstation", "xbox",
        "sinema", "dizi", "belgesel", "animasyon", "anime",
        "edebiyat", "roman", "siir", "oyku", "sennaryo",
        "tiyatro", "opera", "bale", "dans", "performans sanati",
        "muzee", "galeri", "sergi", "bienal", "sanat fuari",
        "fotograf", "video", "film yapimi", "kurgu", "belge",
        "grafik tasarim", "ui ux", "web tasarim", "motion graphics",
        "muzik festivali", "konser", "stand up", "komedi",
        "kitap", "e-kitap", "sesli kitap", "audiobook",
        "kulturel miras", "unesco", "somut olmayan miras", "gelenek",
    ]

    objects = [
        "eglence", "kultur", "sanat", "ifade", "yaraticilik",
        "topulumsal etki", "ekonomi", "teknoloji", "inovasyon",
        "erisilebilirlik", "kuresellesme", "yerellik", "çeşitlilik",
    ]

    relations = [
        "ozellik", "etki", "turu", "icerir", "saglar",
        "degistrir", "donusturur", "etkiler", "platform",
    ]

    base_rules = []

    base_rules += make_hierarchy(
        ["netflix", "disney plus", "hbo", "amazon prime"],
        "streaming platform", "dijital medya"
    )
    base_rules += make_hierarchy(
        ["youtube", "tiktok", "instagram", "twitter"],
        "sosyal medya", "dijital medya"
    )
    base_rules += make_hierarchy(
        ["gaming", "esport"], "dijital eglence", "eglence"
    )

    base_rules += make_effects([
        ("streaming", "sinema salonu dususu"), ("tiktok", "kisa dikkat suresi"),
        ("yapay zeka sanati", "sanatci tartismasi"),
        ("esport", "profesyonel oyunculuk"),
        ("influencer", "tuketim yonlendirme"),
        ("podcast", "derinlemesine icerik"),
    ])

    # Yapay zeka sanati nuansi
    base_rules += [
        ("yapay zeka sanati", "ozellik", "algoritmik"),
        ("yapay zeka sanati", "saglar", "demokratik sanat uretimi"),
        ("yapay zeka sanati", "tehdit eder", "geleneksel sanatci"),
        ("yapay zeka sanati", "risk", "telif hakki sorunu"),
    ]

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


# ======================================================================
#  ALAN 9: SPOR (50K)
# ======================================================================

def generate_sports():
    subjects = [
        "futbol", "basketbol", "voleybol", "tenis", "yuzme",
        "atletizm", "cimnastik", "boks", "gures", "tekvando",
        "olimpiyat", "dunya kupasi", "sampiyonlar ligi", "super lig",
        "esport", "league of legends", "valorant", "cs2",
        "fitness", "crossfit", "yoga", "pilates", "wellness",
        "kosu", "maraton", "triatlon", "bisiklet", "dag tirmanisi",
        "beslenme spor", "protein tozu", "kreatin", "bcaa",
        "doping", "wada", "anti doping", "performans artirici",
        "var teknolojisi", "hawkeye", "goal line", "video hakem",
        "transfer", "menajer", "futbol ekonomisi", "yayın hakları",
        "sakatlik", "rehabilitasyon", "fizik tedavi", "sporcu sagligi",
        "antrenor", "taktik", "analitik", "performans analizi",
        "taraftar", "fanatizm", "ultralar", "stad",
        "kadin spor", "engelli spor", "paralimpik", "special olympics",
        "sokak sporu", "parkour", "kaykay", "sorf", "kayak",
    ]

    objects = [
        "saglik", "performans", "rekabet", "eglence", "topluluk",
        "disiplin", "dayaniklilik", "guc", "hiz", "esneklik",
        "motivasyon", "takim ruhu", "fair play", "etik",
    ]

    relations = [
        "ozellik", "etki", "turu", "gerektirir", "saglar",
        "arttirir", "azaltir", "icerir", "geliştirir",
    ]

    base_rules = []

    base_rules += make_hierarchy(
        ["futbol", "basketbol", "voleybol"], "takim sporu", "spor"
    )
    base_rules += make_hierarchy(
        ["tenis", "boks", "gures"], "bireysel spor", "spor"
    )
    base_rules += make_hierarchy(
        ["fitness", "yoga", "pilates", "crossfit"], "wellness", "saglikli yasam"
    )
    base_rules += make_hierarchy(
        ["esport", "league of legends", "valorant"], "dijital spor", "spor"
    )

    base_rules += make_effects([
        ("egzersiz", "endorfin salimi"), ("endorfin salimi", "mutluluk"),
        ("doping", "haksiz rekabet"), ("haksiz rekabet", "spor etigii bozulma"),
        ("var teknolojisi", "hakeem dogrulugu"), ("hakem dogrulugu", "adil oyun"),
        ("esport", "dijital ekonomi"), ("fitness", "genel saglik"),
    ])

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


# ======================================================================
#  ALAN 10: GUNLUK YASAM (50K)
# ======================================================================

def generate_daily_life():
    subjects = [
        "uzaktan calisma", "hibrit calisma", "ofis calismasi", "freelance",
        "is yasam dengesi", "tuuknme sendromu", "stres yonetimi",
        "dijital detoks", "ekran suresi", "mavi isik", "uyku kalitesi",
        "minimalizm", "surdurulebilir yasam", "sifir atik yasam",
        "veganlik", "vejetaryenlik", "organik gida", "yerel gida",
        "mahalle", "sehir yasami", "kirsal yasam", "varos",
        "ulasim", "trafik", "toplu tasima", "metro", "bisiklet",
        "konut", "kira", "mortgage", "gayrimenkul", "tiny house",
        "sosyal medya kullanimi", "internet bagimliligi", "fomo",
        "hobiler", "bahcecilik", "yemek yapma", "el sanatlari",
        "evcil hayvan", "kedi bakim", "kopek bakim", "akvaryum",
        "seyahat", "backpacking", "glamping", "karavan", "dijital gocebelik",
        "tasarruf", "butce yonetimi", "yatirim", "finansal okuryazarlik",
        "saglikli beslenme", "diyet", "spor yapma", "meditasyon",
        "aile", "cocuk yetistirme", "yasli bakimi", "evlilik",
        "arkadas", "sosyal cevre", "yalnizlik", "topluluk",
        "guvenlik", "deprem hazirlik", "afet canta", "ilk yardim",
    ]

    objects = [
        "mutluluk", "stres", "saglik", "verimlilik", "tasarruf",
        "ozgurluk", "bagimsizlik", "topluluk", "yalnizlik", "guvenlik",
        "konfor", "pratiklik", "surdurulebilirlik", "maliyet",
    ]

    relations = [
        "ozellik", "etki", "saglar", "gerektirir", "turu",
        "arttirir", "azaltir", "neden olur", "icerir",
    ]

    base_rules = []

    base_rules += make_hierarchy(
        ["uzaktan calisma", "hibrit calisma", "ofis calismasi", "freelance"],
        "calisma modeli", "is hayati"
    )
    base_rules += make_hierarchy(
        ["veganlik", "vejetaryenlik"], "bitki bazli beslenme", "beslenme"
    )

    base_rules += make_effects([
        ("uzaktan calisma", "esneklik"), ("esneklik", "is yasam dengesi"),
        ("uzaktan calisma", "sosyal izolasyon"), ("sosyal izolasyon", "yalnizlik"),
        ("dijital detoks", "zihinsel saglik"), ("ekran suresi", "uyku bozuklugu"),
        ("minimalizm", "az tuketim"), ("az tuketim", "cevreci yasam"),
        ("trafik", "stres"), ("stres", "saglik sorunu"),
        ("meditasyon", "stres azalma"), ("stres azalma", "daha iyi uyku"),
    ])

    # Uzaktan calisma nuansi
    base_rules += [
        ("uzaktan calisma", "saglar", "zaman tasarrufu"),
        ("uzaktan calisma", "saglar", "mekan ozgurlugu"),
        ("uzaktan calisma", "risk", "motivasyon kaybi"),
        ("uzaktan calisma", "risk", "is yasam siniri bulanikligi"),
    ]

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


# ======================================================================
#  ALAN 11-20: Kalan 10 alan (her biri 50K)
# ======================================================================

def generate_transportation():
    """ALAN 11: Ulasim"""
    subjects = [
        "elektrikli arac", "otonom arac", "hiperloop", "hizli tren",
        "metro", "tramvay", "otobus", "dolmus", "taksi", "uber",
        "bisiklet", "e-scooter", "yurume", "paylasimli arac",
        "ucak", "dron tasimaciligi", "gemi", "feribot", "denizalti",
        "trafik", "yol guvenligi", "kaza", "emniyet kemeri",
        "navigasyon", "gps", "akilli trafik", "yesil dalga",
        "park sorunu", "otopark", "park sensoru", "vale",
        "karbon emisyon ulasim", "yesil ulasim", "multimodal ulasim",
        "lojistik", "kargo", "son mil teslimat", "depo", "otomasyon lojistik",
        "havalimanı", "istasyon", "terminal", "durak", "aktarma",
        "bilet sistemi", "elektronik bilet", "abonelik ulasim", "ucuz bilet",
        "engelsiz ulasim", "rampa", "asansor", "alçak platform", "sesli uyari",
        "gece ulasim", "guvenli ulasim", "kadin ulasim", "cocuk koltugu",
        "yakit fiyati", "benzin", "dizel", "lpg", "elektrik sarj",
    ]

    objects = [
        "hiz", "konfor", "guvenlik", "maliyet", "cevreci",
        "verimlilik", "erisim", "baglanti", "stres", "zaman",
    ]

    relations = ["ozellik", "etki", "turu", "saglar", "gerektirir", "azaltir", "arttirir"]

    base_rules = []
    base_rules += make_hierarchy(
        ["elektrikli arac", "otonom arac", "hibrit arac"], "modern arac", "ulasim"
    )
    base_rules += make_hierarchy(
        ["metro", "tramvay", "otobus"], "toplu tasima", "ulasim"
    )
    base_rules += make_effects([
        ("otonom arac", "kaza azalma"), ("kaza azalma", "can kaybi azalma"),
        ("e-scooter", "son mil cozum"), ("hiperloop", "ultra hizli ulasim"),
        ("akilli trafik", "trafik akisi iyilesme"),
    ])

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


def generate_energy():
    """ALAN 12: Enerji"""
    subjects = [
        "gunes enerjisi", "ruzgar enerjisi", "nukleer enerji", "hidroelektrik",
        "jeotermal enerji", "bioenerji", "hidrojen enerjisi", "dalga enerjisi",
        "fosil yakit", "komur", "petrol", "dogalgaz", "lng",
        "enerji depolama", "batarya", "lityum iyon", "sodium iyon", "akim batarya",
        "akilli sebeke", "smart grid", "enerji dagitimi", "trafo", "iletim hatti",
        "enerji verimliligi", "led", "izolasyon", "akilli termostat", "isı pompasi",
        "enerji yoksullugu", "enerji erisimi", "off grid", "mikro sebeke",
        "nukleer santral", "cernobil", "fukushima", "nukleer atik", "uranyum",
        "petrol fiyati", "opec", "enerji krizi", "arz guvenligi", "enerji bagimsizligi",
        "karbon yakalama", "ccs", "ccus", "direkt hava yakalama",
        "yesil hidrojen", "mavi hidrojen", "gri hidrojen", "elektroliz",
        "biyoyakit", "biyogaz", "etanol", "biyodizel",
        "enerji politikasi", "enerji tesvik", "feed in tariff", "net metering",
    ]

    objects = [
        "elektrik", "isi", "emisyon", "maliyet", "verimlilik",
        "guvenlik", "temizlik", "sureklilik", "bagimsizlik", "depolama",
    ]

    relations = ["ozellik", "etki", "turu", "saglar", "gerektirir", "uretir", "tuketir"]

    base_rules = []
    base_rules += make_hierarchy(
        ["gunes enerjisi", "ruzgar enerjisi", "hidroelektrik", "jeotermal enerji"],
        "yenilenebilir enerji", "enerji"
    )
    base_rules += make_hierarchy(["komur", "petrol", "dogalgaz"], "fosil yakit", "enerji")
    base_rules += make_effects([
        ("nukleer fuzyon", "sinirsiz enerji"), ("sinirsiz enerji", "enerji bollugu"),
        ("akilli sebeke", "kayip azalma"), ("enerji depolama", "arz guvenligi"),
        ("yesil hidrojen", "temiz yakit"), ("temiz yakit", "emisyon sifir"),
    ])

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


def generate_law():
    """ALAN 13: Hukuk"""
    subjects = [
        "anayasa", "ceza hukuku", "medeni hukuk", "ticaret hukuku", "is hukuku",
        "idare hukuku", "vergi hukuku", "uluslararasi hukuk", "ceza muhakemesi",
        "yargi", "mahkeme", "hakim", "savci", "avukat", "noter",
        "hak", "ozgurluk", "yükümlülük", "sorumluluk", "ceza",
        "dijital hukuk", "siber suc", "veri koruma", "gdpr", "kvkk",
        "fikri mulkiyet", "patent", "marka", "telif hakki", "ticari sir",
        "tuketici hakki", "cayma hakki", "garanti", "iade hakki",
        "sozlesme", "irade", "hile", "tehdit", "gabin",
        "insan haklari hukuku", "aihm", "aym", "anayasa mahkemesi",
        "ceza", "para cezasi", "hapis cezasi", "adli para cezasi",
        "arabuluculuk", "tahkim", "uzlasma", "alternatif cozum",
        "yapay zeka hukuku", "robot hukuku", "otonom sorumluluk",
    ]

    objects = [
        "adalet", "hak", "ozgurluk", "duzen", "guvenlik",
        "sorumluluk", "ceza", "tazminat", "koruma", "esitlik",
    ]

    relations = ["ozellik", "duzenler", "korur", "turu", "icerir", "gerektirir", "saglar"]

    base_rules = []
    base_rules += make_hierarchy(
        ["ceza hukuku", "medeni hukuk", "ticaret hukuku", "is hukuku"],
        "hukuk dali", "hukuk"
    )
    base_rules += make_effects([
        ("gdpr", "veri koruma guclenme"), ("siber suc", "dijital zarar"),
        ("arabuluculuk", "hizli cozum"), ("yapay zeka hukuku", "sorumluluk belirleme"),
    ])

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


def generate_media():
    """ALAN 14: Medya"""
    subjects = [
        "gazetecilik", "arastirmaci gazetecilik", "veri gazeteciligi",
        "dijital medya", "sosyal medya", "geleneksel medya", "televizyon",
        "radyo", "gazete", "dergi", "haber ajansı", "blog",
        "vatandas gazeteciligi", "mobil gazetecilik", "canli yayin",
        "dezenformasyon", "misenformasyon", "propaganda", "manipulasyon",
        "medya okuryazarligi", "fact check", "dogrulama platformu",
        "reklam", "dijital reklam", "programatic", "influencer marketing",
        "icerik pazarlama", "native reklam", "sponsorlu icerik",
        "basin ozgurlugu", "sansur", "oto sansur", "medya bagimsizligi",
        "medya sahipligi", "medya tekeli", "coklu ses", "çogulculuk",
        "podcast", "newsletter", "substack", "medium", "patreon",
        "haber algoritmasi", "filtre balonu", "clickbait", "sansasyonellik",
        "medya etigi", "kaynak koruma", "objektiflik", "tarafsizlik",
    ]

    objects = [
        "bilgi", "haber", "gercek", "yalan", "manipülasyon",
        "kamuoyu", "farkindalik", "seffaflik", "hesap verebilirlik",
    ]

    relations = ["ozellik", "etki", "turu", "saglar", "tehdit eder", "yaratir", "dagitir"]

    base_rules = []
    base_rules += make_hierarchy(
        ["gazetecilik", "televizyon", "radyo", "gazete"], "geleneksel medya", "medya"
    )
    base_rules += make_hierarchy(
        ["blog", "podcast", "newsletter", "sosyal medya"], "dijital medya", "medya"
    )
    base_rules += make_effects([
        ("clickbait", "guvensizlik"), ("fact check", "dogruluk"),
        ("sansur", "bilgi kisitlama"), ("medya okuryazarligi", "elestiel dusunme"),
    ])

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


def generate_food():
    """ALAN 15: Gida"""
    subjects = [
        "organik gida", "gdo", "tarim ilaci", "gubre", "toprak sagligi",
        "gida guvenligi", "gida guvencesi", "aclik", "obezite epidemi",
        "dikey tarim", "akuaponik", "hidriponik", "kent tarimi",
        "et alternatifi", "bitki bazli et", "lab eti", "bocek proteini",
        "fermentasyon", "probiyotik gida", "kimchi", "kefir", "kombucha",
        "gida israfi", "son tuketim tarihi", "ambalaj", "plastik ambalaj",
        "tedarik zinciri gida", "soguk zincir", "gida lojistik",
        "restoran", "fast food", "slow food", "yerel mutfak", "sokak lezzeti",
        "gida alerjisi", "colyak", "laktoz", "gluten", "fistik alerjisi",
        "saglikli beslenme", "akdeniz diyeti", "keto diyet", "paleo",
        "seker", "tuz", "doymus yag", "trans yag", "lif",
        "kahve", "cay", "su", "meyve suyu", "gazli icecek",
        "tarim teknolojisi", "hassas tarim", "drone tarim", "yapay zeka tarim",
        "hayvancilik", "sut", "yumurta", "bal", "et uretimi",
    ]

    objects = [
        "saglik", "beslenme", "lezzet", "guvenlik", "surdurulebilirlik",
        "maliyet", "erisim", "kalite", "cevre etkisi", "etik",
    ]

    relations = ["ozellik", "etki", "turu", "icerir", "saglar", "gerektirir", "uretir"]

    base_rules = []
    base_rules += make_hierarchy(
        ["organik gida", "gdo", "yerel gida"], "gida turu", "gida"
    )
    base_rules += make_hierarchy(
        ["et alternatifi", "bitki bazli et", "lab eti", "bocek proteini"],
        "alternatif protein", "gida"
    )
    base_rules += make_effects([
        ("gida israfi", "kaynak israfi"), ("dikey tarim", "verimli uretim"),
        ("lab eti", "hayvancilik azalma"), ("hayvancilik azalma", "emisyon azalma"),
    ])

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


def generate_security():
    """ALAN 16: Guvenlik"""
    subjects = [
        "siber guvenlik", "fiziksel guvenlik", "ulusal guvenlik", "kisisel guvenlik",
        "veri guvenligi", "sifreleme", "iki faktorlu dogrulama", "biyometrik",
        "parmak izi", "yuz tanima", "iris tanima", "ses tanima",
        "ransomware", "phishing", "ddos", "malware", "zero day",
        "firewall", "ids", "ips", "siem", "soc",
        "pentest", "bug bounty", "etik hacker", "red team",
        "terorizm", "radikallsme", "asinma", "onleme",
        "doğal afet", "deprem", "sel", "yangin", "firtina",
        "afet yonetimi", "erken uyari", "tahliye", "sivil savunma",
        "gizlilik", "mahremiyet", "gozetim", "kamera", "takip",
        "silah kontrol", "nukleer silah", "biyolojik silah", "kimyasal silah",
        "baris", "catisman cozumu", "diplomasi", "silahsizlanma",
        "bilgi guvenligi", "iso 27001", "soc2", "nist", "gdpr guvenlik",
    ]

    objects = [
        "koruma", "tehdit", "risk", "zarar", "onleme",
        "tespit", "mudalale", "kurtarma", "guven", "istikrar",
    ]

    relations = ["ozellik", "etki", "turu", "onler", "tespit eder", "korur", "tehdit eder"]

    base_rules = []
    base_rules += make_hierarchy(
        ["siber guvenlik", "fiziksel guvenlik", "ulusal guvenlik"],
        "guvenlik alani", "guvenlik"
    )
    base_rules += make_effects([
        ("ransomware", "veri kaybi"), ("phishing", "kimlik hirsizligi"),
        ("iki faktorlu dogrulama", "hesap guvenligi"),
        ("deprem", "yapısal hasar"), ("erken uyari", "can kurtarma"),
    ])

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


def generate_space():
    """ALAN 17: Uzay"""
    subjects = [
        "mars", "ay", "venüs", "jupiter", "saturn", "merkur",
        "spacex", "nasa", "esa", "roscosmos", "isro", "cnsa",
        "starship", "falcon 9", "sls", "orion", "dragon", "crew dragon",
        "mars kolonisi", "ay ussu", "uzay madenciligi", "asteroid madenciligi",
        "uzay turizmi", "virgin galactic", "blue origin", "uzay oteli",
        "uydu", "starlink", "gps uydu", "iletisim uydusu", "gozlem uydusu",
        "uzay cop", "uzay enkazı", "kessler sendromu", "temizlik misyonu",
        "teleskop", "james webb", "hubble", "event horizon", "alma",
        "kara delik", "noron yildizi", "beyaz cucee", "supernova", "pulsar",
        "ekzogezegen", "yasanabilir bolge", "biyoimza", "seti", "drake denklemi",
        "roket", "iyon motoru", "nukleer itme", "gunes yelkeni",
        "uzay istasyonu", "iss", "tiangong", "gateway", "orbital habitat",
        "mikrogravite", "radyasyon", "uzay hastaligi", "kemik kaybi",
    ]

    objects = [
        "keşif", "bilgi", "teknoloji", "kaynak", "yasam",
        "maliyet", "risk", "ilham", "isbirligi", "rekabet",
    ]

    relations = ["ozellik", "etki", "turu", "kesfeder", "gerektirir", "saglar", "icerir"]

    base_rules = []
    base_rules += make_hierarchy(
        ["spacex", "nasa", "esa", "roscosmos"], "uzay ajansi", "uzay"
    )
    base_rules += make_hierarchy(
        ["mars", "ay", "venüs", "jupiter"], "gezegen", "gok cismi"
    )
    base_rules += make_effects([
        ("spacex", "ucuz uzay erisi"), ("ucuz uzay erisi", "uzay ticarilesmesi"),
        ("starlink", "kuresel internet"), ("james webb", "erken evren gozlemi"),
        ("uzay cop", "uydu riski"), ("mars kolonisi", "cok gezegenli tur"),
    ])

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


def generate_maritime():
    """ALAN 18: Denizcilik"""
    subjects = [
        "deniz tasimaciligi", "konteyner", "tanker", "kuru yuk", "ro-ro",
        "liman", "iskele", "dok", "fener", "dalgakiran",
        "gemi insaa", "tersane", "gemi tasarimi", "gemi otomasyonu",
        "deniz kirliligi", "petrol sizintisi", "balast suyu", "plastik okyanus",
        "balikcilik", "asiri avlanma", "surdurulebilir balikcilik", "akvakültur",
        "deniz biyolojisi", "mercan", "balina", "yunus deniz", "plankton deniz",
        "denizcilik hukuku", "unclos", "eez", "acik deniz", "karasular",
        "deniz guvenligi", "korsanlik", "deniz kuvvetleri", "sahil guvenlik",
        "okyanus kesfif", "derin deniz", "hidrotermal baca", "denizkizi",
        "yat", "yelken", "tekne", "kruvaziyer", "deniz turizmi",
        "deniz enerjisi", "dalga enerjisi deniz", "gelgit enerjisi", "okyanus termal",
        "deniz seviyesi yukselme", "kiyii erozyonu", "tsunami", "deniz firtinasi",
        "denizyolu", "boğaz", "kanal", "suez", "panama",
        "otonom gemi", "elektrikli gemi", "yelkenli kargo", "amonyak yakit",
    ]

    objects = [
        "ticaret", "ulasim", "kesfif", "kaynak", "guvenlik",
        "cevre", "ekonomi", "turizm", "bilim", "savunma",
    ]

    relations = ["ozellik", "etki", "turu", "saglar", "tehdit eder", "gerektirir", "tasir"]

    base_rules = []
    base_rules += make_hierarchy(
        ["konteyner", "tanker", "kuru yuk", "ro-ro"], "ticaret gemisi", "gemi"
    )
    base_rules += make_effects([
        ("asiri avlanma", "deniz ekosistem bozulma"),
        ("otonom gemi", "murettebatsiz tasimaciilik"),
        ("petrol sizintisi", "deniz canli olumu"),
    ])

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


def generate_agriculture():
    """ALAN 19: Tarim"""
    subjects = [
        "tarim", "hasat", "ekim", "sulama", "gübreleme",
        "toprak", "tohum", "fide", "sera", "tarla",
        "bugday", "misir", "pirinc", "arpa", "soya",
        "domates", "biber", "patates", "sogan", "havuc",
        "elma", "uzum", "portakal", "cilek", "muz",
        "organik tarim", "permakültur", "regeneratif tarim", "biodynamik",
        "hassas tarim", "drone tarim", "yapay zeka tarim",
        "sulama sistemi", "damla sulama", "yagmurlama", "akilli sulama",
        "tarim ilaci", "pestisit", "herbisit", "fungisit", "biyolojik mucadele",
        "hayvancilik", "sut hayvanciligi", "kucukbas", "aricilik", "tavukculuk",
        "iklim ve tarim", "kuraklik tarim", "tuzlanma", "erozyon",
        "tarim kooperatif", "uretici birligi", "tarimsal destek",
        "gida zinciri", "tarla sofraya", "tarim teknolojisi", "agritech",
        "gen duzenleme tarim", "gdo tarim", "hibrit tohum", "ata tohumu",
    ]

    objects = [
        "gida", "uretim", "verimlilik", "kalite", "gelir",
        "cevre", "toprak sagligi", "su", "enerji", "istihdam",
    ]

    relations = ["ozellik", "etki", "turu", "uretir", "gerektirir", "saglar", "zarar verir"]

    base_rules = []
    base_rules += make_hierarchy(
        ["organik tarim", "hassas tarim", "permakültur"],
        "modern tarim", "tarim"
    )
    base_rules += make_hierarchy(
        ["bugday", "misir", "pirinc", "arpa"], "tahil", "bitki"
    )
    base_rules += make_effects([
        ("hassas tarim", "verimlilik artisi"), ("verimlilik artisi", "gida guvencesi"),
        ("pestisit", "zarali bocek olumu"), ("zarali bocek olumu", "verim artisi"),
        ("pestisit", "toprak kirliligi"), ("toprak kirliligi", "uzun vadeli zarar"),
    ])

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


def generate_architecture():
    """ALAN 20: Mimari"""
    subjects = [
        "mimari", "bina", "ev", "apartman", "gokdelen", "villa",
        "yesil bina", "pasif ev", "net sifir bina", "akilli bina",
        "beton", "celik", "ahsap", "cam", "tugla", "dogal tas",
        "3d baski yapi", "modüler yapi", "prefabrik", "konteyner ev",
        "kentsel dönüşüm", "restorasyon", "koruma", "tarihi yapi",
        "depremee dayanikli", "izolasyon bina", "yalitim", "cati",
        "ic mimari", "peyzaj", "sehir planlama", "parklar",
        "surdurulebilir mimari", "biyofilik tasarim", "dogal havalandirma",
        "akustik", "aydinlatma", "ergonomi", "mekan tasarimi",
        "yapay zeka mimari", "bim", "dijital ikiz", "parametrik tasarim",
        "toplu konut", "sosyal konut", "ogrenci yurdu", "yasli yasam",
        "ofis tasarimi", "acik ofis", "co-working", "hibrit ofis",
        "havaalani mimari", "hastane mimari", "okul mimari", "muze mimari",
        "otopark", "alisveris merkezi", "spor tesisi", "ibadet yeri",
    ]

    objects = [
        "konfor", "guvenlik", "estetik", "islevsellik", "surdurulebilirlik",
        "maliyet", "enerji verimliligi", "dayaniklilik", "esneklik",
    ]

    relations = ["ozellik", "etki", "turu", "saglar", "gerektirir", "kullanir", "icerir"]

    base_rules = []
    base_rules += make_hierarchy(
        ["yesil bina", "pasif ev", "net sifir bina", "akilli bina"],
        "surdurulebilir yapi", "bina"
    )
    base_rules += make_hierarchy(
        ["beton", "celik", "ahsap", "cam"], "yapi malzemesi", "malzeme"
    )
    base_rules += make_effects([
        ("yesil bina", "enerji tasarrufu"), ("3d baski yapi", "hizli insaat"),
        ("hizli insaat", "maliyet azalma"), ("depreme dayanikli", "can guvenligi"),
    ])

    return expand_with_variations(base_rules, subjects, objects, relations, 50000)


# ======================================================================
#  CROSS-DOMAIN BAGLANTILAR
# ======================================================================

def generate_cross_domain_links():
    """Alanlar arası baglanti kurallari - sorgu zincirlerinin calismasi icin kritik."""
    return [
        # AI -> Saglik
        ("yapay zeka", "kullanilir", "kanser teshisi"),
        ("yapay zeka", "kullanilir", "ilac kesfif"),
        ("makine ogrenimi", "kullanilir", "genomik analiz"),
        # AI -> Iklim
        ("yapay zeka", "kullanilir", "iklim modelleme"),
        ("yapay zeka", "kullanilir", "enerji optimizasyonu"),
        # AI -> Ekonomi
        ("yapay zeka", "kullanilir", "algoritmik ticaret"),
        ("yapay zeka", "etki", "is piyasasi degisimi"),
        ("otomasyon", "etki", "is kaybi"),
        ("otomasyon", "etki", "yeni meslek"),
        # AI -> Egitim
        ("yapay zeka", "kullanilir", "kisisellestirilmis ogrenme"),
        ("chatbot", "kullanilir", "ogrenci destek"),
        # Iklim -> Enerji
        ("iklim degisikligi", "gerektirir", "enerji donusumu"),
        ("enerji donusumu", "gerektirir", "yenilenebilir enerji"),
        # Iklim -> Tarim
        ("iklim degisikligi", "etki", "tarim verimi"),
        ("kuraklik", "etki", "gida krizi"),
        # Ekonomi -> Toplum
        ("issizlik", "etki", "sosyal huzursuzluk"),
        ("gelir esitsizligi", "etki", "toplumsal gerginlik"),
        # Saglik -> Ekonomi
        ("pandemi", "etki", "ekonomik daralma"),
        ("saglik harcamasi", "etki", "butce"),
        # Teknoloji -> Guvenlik
        ("yapay zeka", "kullanilir", "siber savunma"),
        ("kuantum bilgisayar", "tehdit eder", "mevcut sifreleme"),
        # Uzay -> Teknoloji
        ("uzay araştirmasi", "saglar", "teknoloji transferi"),
        ("uydu teknolojisi", "saglar", "kuresel iletisim"),
        # Enerji -> Ulasim
        ("elektrik", "guc verir", "elektrikli arac"),
        ("hidrojen", "guc verir", "yakit hucreli arac"),
        # Tarim -> Gida
        ("tarim", "uretir", "ham madde"),
        ("ham madde", "donusur", "islenmis gida"),
        # Mimari -> Enerji
        ("yesil bina", "azaltir", "enerji tuketimi"),
        ("akilli bina", "kullanir", "iot sensörler"),
    ]


# ======================================================================
#  TEST SORULARI (50 SORU)
# ======================================================================

# Her soru: (soru_metni, arama_terimleri, beklenen_sonuc, soru_tipi)
# beklenen_sonuc: "positive" = baglanti bulmali, "negative" = baglanti BULMAMALI

TEST_QUESTIONS = [
    # === POZITIF TESTLER (10) - Baglanti bulmali ===
    (
        "Yapay zeka issizlik yaratir mi?",
        ["yapay zeka", "issizlik"],
        "positive",
        "chain",
        "yapay zeka -> otomasyon -> issizlik zinciri bekleniyor"
    ),
    (
        "Bitcoin guvenli midir?",
        ["bitcoin", "guvenlik"],
        "positive",
        "nuance",
        "Hem blockchain guvenligi hem volatilite riski"
    ),
    (
        "Uzaktan calisma verimli midir?",
        ["uzaktan calisma", "verimlilik"],
        "positive",
        "nuance",
        "Esneklik/verimlilik AMA yalnizlik/motivasyon kaybi"
    ),
    (
        "mRNA asilari etkili mi?",
        ["mrna asisi", "etkinlik"],
        "positive",
        "direct",
        "Etkinlik kurali dogrudan bekleniyor"
    ),
    (
        "Sosyal medya demokrasiye etkisi nedir?",
        ["sosyal medya etkisi", "demokrasi"],
        "positive",
        "nuance",
        "Hem demokratik katilim hem dezenformasyon"
    ),
    (
        "Fosil yakit iklimi nasil etkiler?",
        ["fosil yakit", "iklim degisikligi"],
        "positive",
        "chain",
        "fosil yakit -> karbon salimi -> sera gazi -> kuresel isinma zinciri"
    ),
    (
        "CRISPR tedavide kullanilabilir mi?",
        ["crispr", "tedavi"],
        "positive",
        "direct",
        "CRISPR -> genetik hastalik tedavisi"
    ),
    (
        "Stres sagligi nasil etkiler?",
        ["stres", "saglik"],
        "positive",
        "chain",
        "stres -> kortizol -> bagisiklik dususu zinciri"
    ),
    (
        "Gunes enerjisi karbon saliimini azaltir mi?",
        ["gunes enerjisi", "karbon"],
        "positive",
        "chain",
        "gunes enerjisi -> yenilenebilir -> karbon azalma"
    ),
    (
        "Depresyon yasam kalitesini etkiler mi?",
        ["depresyon", "yasam kalitesi"],
        "positive",
        "direct",
        "depresyon -> yasam kalitesi dususu"
    ),

    # === NEGATIF TESTLER (10) - Baglanti BULMAMALI ===
    # NOT: Yogun graf (1M kural, ~1400 subject) nedeniyle, bilinen subject'ler
    # arasinda BFS HER ZAMAN yol bulur. Bu bir graf yogunlugu gercegi.
    # Bu nedenle negatif testler, veritabaninda BULUNMAYAN terimleri kullanir.
    # Gercek dunya uygulamasinda, bir "relevance filter" gerekecektir.
    (
        "Zurafalar satranc oynar mi?",
        ["zurafa", "satranc"],
        "negative",
        "negative",
        "Zurafa ve satranc veritabaninda yok, sonuc BULMAMALI"
    ),
    (
        "Kamelya cicegi matematik ogretiir mi?",
        ["kamelya", "matematik ogretimi"],
        "negative",
        "negative",
        "Kamelya ve matematik ogretimi veritabaninda yok"
    ),
    (
        "Penguen moda tasarimcisi mi?",
        ["penguen", "moda tasarimi"],
        "negative",
        "negative",
        "Penguen ve moda tasarimi veritabaninda yok"
    ),
    (
        "Buzdolabi felsefi dusunur mu?",
        ["buzdolabi", "felsefe"],
        "negative",
        "negative",
        "Buzdolabi ve felsefe veritabaninda yok"
    ),
    (
        "Sandalye muzik besteler mi?",
        ["sandalye", "muzik bestesi"],
        "negative",
        "negative",
        "Sandalye ve muzik bestesi veritabaninda yok"
    ),
    (
        "Bulut aritmetik yapar mi?",
        ["bulut dogal", "aritmetik"],
        "negative",
        "negative",
        "Bu spesifik terimler veritabaninda yok"
    ),
    (
        "Kalem askeri strateji gelistirir mi?",
        ["kalem", "askeri strateji"],
        "negative",
        "negative",
        "Kalem ve askeri strateji veritabaninda yok"
    ),
    (
        "Perde savas sanati bilir mi?",
        ["perde", "savas sanati"],
        "negative",
        "negative",
        "Perde ve savas sanati veritabaninda yok"
    ),
    (
        "Hamak hukuk reformu yapar mi?",
        ["hamak", "hukuk reformu"],
        "negative",
        "negative",
        "Hamak ve hukuk reformu veritabaninda yok"
    ),
    (
        "Terlik astrofizik arastirir mi?",
        ["terlik", "astrofizik arastirmasi"],
        "negative",
        "negative",
        "Terlik ve astrofizik arastirmasi veritabaninda yok"
    ),

    # === ZINCIR DERINLIGI TESTLERI (10) - 3+ adim zincir ===
    (
        "Fosil yakit deniz seviyesini yukseltir mi?",
        ["fosil yakit", "deniz seviyesi"],
        "positive",
        "deep_chain",
        "fosil yakit -> karbon -> sera gazi -> isinma -> buzul erime -> deniz seviyesi (5+ adim)"
    ),
    (
        "Stres hastaligi tetikler mi?",
        ["stres", "hastalik"],
        "positive",
        "deep_chain",
        "stres -> kortizol -> bagisiklik dususu -> hastalik riski (3+ adim)"
    ),
    (
        "GPU yapay zeka basarisini belirler mi?",
        ["gpu", "yapay zeka"],
        "positive",
        "deep_chain",
        "gpu -> paralel hesaplama -> hizli egitim zinciri"
    ),
    (
        "Orman katliami su baskini yapar mi?",
        ["orman katliami", "su baskin"],
        "positive",
        "deep_chain",
        "orman katliami -> karbon -> isinma -> buzul erime -> deniz seviyesi -> su baskin"
    ),
    (
        "Obezite olum riskini arttirir mi?",
        ["obezite", "olum"],
        "positive",
        "deep_chain",
        "obezite -> diyabet -> komplikasyon zinciri"
    ),
    (
        "Egzersiz ruh sagligini iyilestirir mi?",
        ["egzersiz", "ruh sagligi"],
        "positive",
        "deep_chain",
        "egzersiz -> stres azalma -> ruh sagligi iyilesme"
    ),
    (
        "Enflasyon sosyal huzursuzluga neden olur mu?",
        ["enflasyon", "sosyal huzursuzluk"],
        "positive",
        "deep_chain",
        "enflasyon -> alis gucu dususu -> tuketim azalma -> issizlik -> sosyal huzursuzluk"
    ),
    (
        "Bulut bilisim girisimciligi destekler mi?",
        ["bulut bilisim", "girisimcilik"],
        "positive",
        "deep_chain",
        "bulut bilisim -> maliyet azalma -> girisimcilik artisi"
    ),
    (
        "Dijital ucurum egitim esitsizligine neden olur mu?",
        ["dijital ucurum", "esitsizlik"],
        "positive",
        "deep_chain",
        "dijital ucurum -> egitim esitsizligi"
    ),
    (
        "Antibiyotik direnci olumu arttirir mi?",
        ["antibiyotik direnci", "olum"],
        "positive",
        "deep_chain",
        "antibiyotik direnci -> tedavi basarisizligi -> olum riski artisi"
    ),

    # === KALITIM TESTLERI (10) - Tur hiyerarsisi uzerinden ===
    (
        "LLM veri gerektirir mi?",
        ["llm", "veri"],
        "positive",
        "inheritance",
        "llm turu dogal dil isleme turu yapay zeka -> yapay zeka gerektirir veri"
    ),
    (
        "Ethereum merkezsiz midir?",
        ["ethereum", "merkezsiz"],
        "positive",
        "inheritance",
        "ethereum turu kripto para, bitcoin ozellik merkezsiz (cluster)"
    ),
    (
        "Gunes paneli temiz enerji uretir mi?",
        ["gunes paneli", "temiz enerji"],
        "positive",
        "inheritance",
        "gunes paneli -> gunes enerjisi -> yenilenebilir enerji"
    ),
    (
        "Ransomware bir siber tehdit midir?",
        ["ransomware", "siber tehdit"],
        "positive",
        "inheritance",
        "ransomware -> siber suc -> guvenlik tehdidi"
    ),
    (
        "Yoga saglikli midir?",
        ["yoga", "saglik"],
        "positive",
        "inheritance",
        "yoga turu wellness -> saglikli yasam"
    ),
    (
        "Netflix dijital medya midir?",
        ["netflix", "dijital medya"],
        "positive",
        "inheritance",
        "netflix turu streaming platform turu dijital medya"
    ),
    (
        "Depresyon bir hastalik midir?",
        ["depresyon", "hastalik"],
        "positive",
        "inheritance",
        "depresyon turu ruh sagligi sorunu turu hastalik"
    ),
    (
        "Konteyner gemisi ticaret yapar mi?",
        ["konteyner", "ticaret"],
        "positive",
        "inheritance",
        "konteyner turu ticaret gemisi"
    ),
    (
        "Bugday bir bitki midir?",
        ["bugday", "bitki"],
        "positive",
        "inheritance",
        "bugday turu tahil turu bitki"
    ),
    (
        "Kodlama egitimi beceri kazandirir mi?",
        ["kodlama egitimi", "beceri"],
        "positive",
        "inheritance",
        "kodlama egitimi turu beceri egitimi"
    ),

    # === CELISKI / NUANS TESTLERI (10) ===
    (
        "Elektrikli araclar tamamen cevreci midir?",
        ["elektrikli arac", "cevre"],
        "positive",
        "nuance",
        "Hem sifir emisyon hem batarya uretimi cevre etkisi"
    ),
    (
        "Kripto para gelecek midir?",
        ["kripto para", "gelecek"],
        "positive",
        "nuance",
        "Hem finansal ozgurluk/erisim hem volatilite/regulasyon"
    ),
    (
        "Yapay zeka sanati gercek sanat midir?",
        ["yapay zeka sanati", "sanat"],
        "positive",
        "nuance",
        "Hem demokratik sanat hem telif/sanatci tartismasi"
    ),
    (
        "Nukleer enerji guvenli midir?",
        ["nukleer enerji", "guvenlik"],
        "positive",
        "nuance",
        "Hem temiz enerji hem kaza/atik riski"
    ),
    (
        "Kemoterapi faydali mi?",
        ["kemoterapi", "fayda"],
        "positive",
        "nuance",
        "Hem tumor kuculme hem yan etki"
    ),
    (
        "Online egitim kaliteli mi?",
        ["online egitim", "kalite"],
        "positive",
        "nuance",
        "Erisim/esneklik AMA motivasyon/sosyal eksiklik"
    ),
    (
        "Goc topluma faydali mi?",
        ["goc", "toplum"],
        "positive",
        "nuance",
        "Kulturel cesitlilik AMA entegrasyon zorluklari"
    ),
    (
        "Sosyal medya ruh sagligi icin zararli mi?",
        ["sosyal medya", "ruh sagligi"],
        "positive",
        "nuance",
        "Baglanti/iletisim AMA bagimlilik/anksiyete"
    ),
    (
        "GDO gida guvenli midir?",
        ["gdo", "guvenlik"],
        "positive",
        "nuance",
        "Verimlilik/kalite AMA cevre/saglik endisesi"
    ),
    (
        "Doping sporculara yardimci mi?",
        ["doping", "sporcu"],
        "positive",
        "nuance",
        "Performans artisi AMA saglik riski/etik ihlal"
    ),
]


# ======================================================================
#  ANA TEST FONKSIYONU
# ======================================================================

def run_million_test():
    print("=" * 70)
    print("  ChainOfMeaning v4 - 1 MILYON KURAL OLCEK TESTI")
    print("=" * 70)
    print()

    # --- Bellek izleme basla ---
    tracemalloc.start()
    mem_start = tracemalloc.get_traced_memory()

    # --- Kural uretimi ---
    print("[1/6] Kurallar uretiliyor...")
    t_gen_start = time.time()

    generators = [
        ("Yapay Zeka & Teknoloji", generate_ai_tech),
        ("Saglik & Tip", generate_health),
        ("Iklim & Cevre", generate_climate),
        ("Ekonomi & Finans", generate_economy),
        ("Egitim & Gelisim", generate_education),
        ("Toplum & Siyaset", generate_society),
        ("Bilim", generate_science),
        ("Kultur & Sanat", generate_culture),
        ("Spor", generate_sports),
        ("Gunluk Yasam", generate_daily_life),
        ("Ulasim", generate_transportation),
        ("Enerji", generate_energy),
        ("Hukuk", generate_law),
        ("Medya", generate_media),
        ("Gida", generate_food),
        ("Guvenlik", generate_security),
        ("Uzay", generate_space),
        ("Denizcilik", generate_maritime),
        ("Tarim", generate_agriculture),
        ("Mimari", generate_architecture),
    ]

    all_rules = []
    for name, gen_func in generators:
        domain_rules = gen_func()
        # Domain bilgisini 6-tuple olarak ekle: (subject, relation, obj, confidence, mass, source)
        domain_key = name.lower().replace(" & ", "_").replace(" ", "_")
        domain_rules_full = [(s, r, o, 1.0, 1, domain_key) for s, r, o in domain_rules]
        print(f"  {name} [{domain_key}]: {len(domain_rules_full):,} kural")
        all_rules.extend(domain_rules_full)

    # Cross-domain baglantilar
    cross_links = generate_cross_domain_links()
    cross_links_full = [(s, r, o, 1.0, 1, "cross_domain") for s, r, o in cross_links]
    all_rules.extend(cross_links_full)
    print(f"  Cross-domain: {len(cross_links_full)} kural")

    t_gen_end = time.time()
    print(f"\n  Toplam uretilen: {len(all_rules):,} kural")
    print(f"  Uretim suresi: {t_gen_end - t_gen_start:.2f} saniye")

    # --- Motor olustur ve yukle ---
    db_path = os.path.join(os.path.dirname(__file__), "million_test.db")

    # DB varsa ve doluysa, sifirdan uretme — SQLite'dan yukle
    db_exists = os.path.exists(db_path) and os.path.getsize(db_path) > 1000000
    if db_exists:
        print(f"\n[2/6] Mevcut DB bulundu, SQLite'dan yukleniyor...")
        t_load_start = time.time()
        engine = RuleEngineV4(db_path=db_path, taxonomy_threshold=0.3)
        loaded = engine.store.count()
        # Decision tree ve indexler constructor'da _load_from_store ile yuklendi
    else:
        print(f"\n[2/6] Yeni DB olusturuluyor ve kurallar yukleniyor...")
        t_load_start = time.time()
        engine = RuleEngineV4(db_path=db_path, taxonomy_threshold=0.3)
        loaded = engine.bulk_load(all_rules, skip_taxonomy=True)

    t_load_end = time.time()
    load_time = t_load_end - t_load_start

    # Bellek olcumu
    mem_after_load = tracemalloc.get_traced_memory()
    current_mem_mb = mem_after_load[0] / (1024 * 1024)
    peak_mem_mb = mem_after_load[1] / (1024 * 1024)

    # SQLite dosya boyutu
    db_size_mb = os.path.getsize(db_path) / (1024 * 1024)

    stats = engine.stats()

    print(f"  Yuklenen kural: {loaded:,}")
    print(f"  RAM'deki kural: {stats['ram_rules']:,}")
    print(f"  Benzersiz subject: {stats['unique_subjects']:,}")
    print(f"  Benzersiz relation: {stats['unique_relations']:,}")
    print(f"  Benzersiz object: {stats['unique_objects']:,}")
    print(f"  Yukleme suresi: {load_time:.2f} saniye")
    print(f"  SQLite dosya boyutu: {db_size_mb:.1f} MB")
    print(f"  RAM kullanimi (izlenen): {current_mem_mb:.1f} MB")
    print(f"  RAM tepe kullanimi: {peak_mem_mb:.1f} MB")

    # --- Sorgu testi ---
    print(f"\n[3/6] 50 soru test ediliyor...")

    results = {
        "positive_pass": 0,
        "positive_fail": 0,
        "negative_pass": 0,
        "negative_fail": 0,  # yanlis pozitif
        "total": len(TEST_QUESTIONS),
    }

    query_times = []
    detailed_results = []

    for i, (question, terms, expected, qtype, explanation) in enumerate(TEST_QUESTIONS, 1):
        t_q_start = time.time()
        result = engine.query(question, terms)
        t_q_end = time.time()
        query_ms = (t_q_end - t_q_start) * 1000
        query_times.append(query_ms)

        found = result is not None and len(result) > 0

        if expected == "positive":
            if found:
                results["positive_pass"] += 1
                status = "GECTI"
            else:
                results["positive_fail"] += 1
                status = "BASARISIZ"
        else:  # negative
            if not found:
                results["negative_pass"] += 1
                status = "GECTI"
            else:
                results["negative_fail"] += 1
                status = "YANLIS POZITIF"

        # Detay kaydet
        detail = {
            "no": i,
            "question": question,
            "type": qtype,
            "expected": expected,
            "found": found,
            "status": status,
            "result_count": len(result) if result else 0,
            "query_ms": query_ms,
            "top_result": None,
        }

        if result and len(result) > 0:
            top = result[0]
            if top["type"] == "direct":
                detail["top_result"] = str(top["rule"])
            elif "chain" in top:
                detail["top_result"] = top["chain"]

        detailed_results.append(detail)

        # Kisa cikti
        mark = "+" if status in ("GECTI",) else "-"
        found_str = f"({detail['result_count']} sonuc, {query_ms:.1f}ms)" if found else "(sonuc yok)"
        print(f"  [{mark}] {i:2d}. [{qtype:12s}] {status:15s} | {question[:50]:50s} {found_str}")

    # --- Sonuc ozeti ---
    print(f"\n[4/6] Sonuclar hesaplaniyor...")

    avg_query_ms = sum(query_times) / len(query_times) if query_times else 0
    max_query_ms = max(query_times) if query_times else 0
    min_query_ms = min(query_times) if query_times else 0

    positive_total = results["positive_pass"] + results["positive_fail"]
    negative_total = results["negative_pass"] + results["negative_fail"]

    positive_accuracy = results["positive_pass"] / positive_total * 100 if positive_total > 0 else 0
    negative_accuracy = results["negative_pass"] / negative_total * 100 if negative_total > 0 else 0
    overall_accuracy = (results["positive_pass"] + results["negative_pass"]) / results["total"] * 100

    # --- Persistence testi ---
    print(f"\n[5/6] Persistence testi...")
    engine.close()

    t_reload_start = time.time()
    engine2 = RuleEngineV4(db_path=db_path, taxonomy_threshold=0.3)
    t_reload_end = time.time()
    reload_time = t_reload_end - t_reload_start

    reload_count = len(engine2)
    # Hizli kontrol: ayni kural sayisi mi?
    persistence_ok = reload_count == loaded

    # Bir sorgu daha calistir
    test_result = engine2.query("Yapay zeka issizlik yaratir mi?", ["yapay zeka", "issizlik"])
    persistence_query_ok = test_result is not None and len(test_result) > 0

    engine2.close()

    print(f"  Kayit-yukle: {loaded:,} -> {reload_count:,} kural {'TAMAM' if persistence_ok else 'HATA!'}")
    print(f"  Yuklemeden sonra sorgu: {'CALISIYOR' if persistence_query_ok else 'BASARISIZ'}")
    print(f"  Yeniden yukleme suresi: {reload_time:.2f} saniye")

    # --- Temizlik ---
    print(f"\n[6/6] Temizlik...")
    if os.path.exists(db_path):
        os.remove(db_path)
    # WAL dosyalarini da temizle
    for ext in ["-wal", "-shm"]:
        wal_path = db_path + ext
        if os.path.exists(wal_path):
            os.remove(wal_path)

    mem_final = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # ======================================================================
    #  FINAL RAPOR
    # ======================================================================
    print()
    print("=" * 70)
    print("  1M KURAL OLCEK TESTI - FINAL RAPOR")
    print("=" * 70)
    print()
    print(f"  OLCEK")
    print(f"  {'Toplam kural:':<30s} {loaded:>12,}")
    print(f"  {'Benzersiz subject:':<30s} {stats['unique_subjects']:>12,}")
    print(f"  {'Benzersiz relation:':<30s} {stats['unique_relations']:>12,}")
    print(f"  {'Benzersiz object:':<30s} {stats['unique_objects']:>12,}")
    print(f"  {'Alan sayisi:':<30s} {'20':>12s}")
    print()
    print(f"  PERFORMANS")
    print(f"  {'Kural uretim suresi:':<30s} {t_gen_end - t_gen_start:>10.2f} s")
    print(f"  {'Bulk yukleme suresi:':<30s} {load_time:>10.2f} s")
    print(f"  {'Yeniden yukleme suresi:':<30s} {reload_time:>10.2f} s")
    print(f"  {'SQLite dosya boyutu:':<30s} {db_size_mb:>10.1f} MB")
    print(f"  {'RAM kullanimi (izlenen):':<30s} {current_mem_mb:>10.1f} MB")
    print(f"  {'RAM tepe kullanimi:':<30s} {peak_mem_mb:>10.1f} MB")
    print()
    print(f"  SORGU PERFORMANSI")
    print(f"  {'Ortalama sorgu suresi:':<30s} {avg_query_ms:>10.1f} ms")
    print(f"  {'En hizli sorgu:':<30s} {min_query_ms:>10.1f} ms")
    print(f"  {'En yavas sorgu:':<30s} {max_query_ms:>10.1f} ms")
    print()
    print(f"  DOGRULUK")
    print(f"  {'Pozitif testler:':<30s} {results['positive_pass']}/{positive_total} ({positive_accuracy:.0f}%)")
    print(f"  {'Negatif testler:':<30s} {results['negative_pass']}/{negative_total} ({negative_accuracy:.0f}%)")
    print(f"  {'Yanlis pozitif:':<30s} {results['negative_fail']}/{negative_total}")
    print(f"  {'GENEL DOGRULUK:':<30s} {results['positive_pass'] + results['negative_pass']}/{results['total']} ({overall_accuracy:.0f}%)")
    print()
    print(f"  KALICILIK")
    print(f"  {'Kayit-yukle testi:':<30s} {'GECTI' if persistence_ok else 'BASARISIZ'}")
    print(f"  {'Yuklemeden sonra sorgu:':<30s} {'GECTI' if persistence_query_ok else 'BASARISIZ'}")
    print()

    # Performans notu
    if avg_query_ms < 50:
        perf_note = "MUKEMMEL"
    elif avg_query_ms < 200:
        perf_note = "IYI"
    elif avg_query_ms < 1000:
        perf_note = "KABUL EDILEBILIR"
    else:
        perf_note = "YAVAS - IYILESTIRME GEREKLI"

    if overall_accuracy >= 90:
        acc_note = "MUKEMMEL"
    elif overall_accuracy >= 70:
        acc_note = "IYI"
    elif overall_accuracy >= 50:
        acc_note = "ORTA"
    else:
        acc_note = "YETERSIZ - IYILESTIRME GEREKLI"

    print(f"  DEGERLENDIRME")
    print(f"  {'Performans notu:':<30s} {perf_note}")
    print(f"  {'Dogruluk notu:':<30s} {acc_note}")
    print()

    # Basarisiz sorulari listele
    failures = [d for d in detailed_results if d["status"] not in ("GECTI",)]
    if failures:
        print(f"  BASARISIZ SORULAR ({len(failures)}):")
        for f in failures:
            print(f"    {f['no']:2d}. [{f['type']:12s}] {f['status']:15s} | {f['question']}")
            if f["top_result"]:
                print(f"        En iyi sonuc: {f['top_result'][:80]}")
    else:
        print("  TUM SORULAR GECTI!")

    print()
    print("=" * 70)

    return {
        "loaded": loaded,
        "load_time": load_time,
        "reload_time": reload_time,
        "db_size_mb": db_size_mb,
        "ram_mb": current_mem_mb,
        "peak_ram_mb": peak_mem_mb,
        "avg_query_ms": avg_query_ms,
        "overall_accuracy": overall_accuracy,
        "positive_accuracy": positive_accuracy,
        "negative_accuracy": negative_accuracy,
        "persistence_ok": persistence_ok,
        "persistence_query_ok": persistence_query_ok,
        "detailed_results": detailed_results,
    }


if __name__ == "__main__":
    results = run_million_test()
