"""
Her senaryo icin: kurallar, sorgular, beklenen davranislar.
Motor ciktisi bunlarla karsilastirilacak.
"""


def scenario_a_contradiction():
    """Celiskili Yonetimi: Kahve saglikli mi?"""
    return {
        "name": "Senaryo A - Celiski Yonetimi",
        "description": "Dogrudan ve dolayli celiskiyi tespit edebiliyor mu?",
        "rules": [
            ("kahve", "etki", "saglikli"),
            ("kafein", "etki", "zararli"),
            ("kahve", "icerir", "kafein"),
        ],
        "queries": [
            {
                "question": "Kahve hakkinda ne biliyorsun?",
                "terms": ["kahve"],
                "expected": {
                    "mechanical": {
                        "description": "3 kural state'e eklenmeli. forget_gate celiskiyi GORMEMELI (farkli subject).",
                        "check_rules_count": 3,
                        "check_no_confidence_drop": True,
                    },
                    "inference": {
                        "description": "Dogrudan 'kahve→saglikli' ve zincir 'kahve→kafein→zararli' donmeli.",
                        "expect_direct": ["kahve --etki--> saglikli"],
                        "expect_chains": ["kahve -> kafein -> zararli"],
                    },
                    "meaning": {
                        "description": "Celiski raporlanmali: kahve hem saglikli hem zararli (dolayli).",
                        "expect_contradiction_detected": True,
                    },
                },
            }
        ],
        "predictions": {
            "mechanical": "PASS",
            "inference": "PARTIAL",
            "meaning": "FAIL",
        },
    }


def scenario_b_deep_chaining():
    """Derin Zincirleme: Sokrates empati gelistirir mi?"""
    return {
        "name": "Senaryo B - Derin Zincirleme (4 adim)",
        "description": "4 adimlik zinciri kurabiliyor mu?",
        "rules": [
            ("sokrates", "turu", "insan"),
            ("insan", "ozellik", "olumlu"),
            ("olumlu", "deneyim", "aci"),
            ("aci", "gelistirir", "empati"),
        ],
        "queries": [
            {
                "question": "Sokrates empati gelistirir mi?",
                "terms": ["sokrates", "empati"],
                "expected": {
                    "mechanical": {
                        "description": "4 kural state'e eklenmeli, conflict yok.",
                        "check_rules_count": 4,
                        "check_no_confidence_drop": True,
                    },
                    "inference": {
                        "description": "Tam zincir: sokrates→insan→olumlu→aci→empati",
                        "expect_direct": [],
                        "expect_chains": [
                            "sokrates -> insan -> olumlu -> aci -> empati"
                        ],
                        "min_chain_depth": 4,
                    },
                    "meaning": {
                        "description": "Sokrates'in empati gelistirdigi sonucuna varabilmeli.",
                        "expect_conclusion_links": ["sokrates", "empati"],
                    },
                },
            }
        ],
        "predictions": {
            "mechanical": "PASS",
            "inference": "FAIL",
            "meaning": "FAIL",
        },
    }


def scenario_c_hierarchy():
    """Hiyerarsi: Yesil elma saglikli mi?"""
    return {
        "name": "Senaryo C - Hiyerarsi / Kalitim",
        "description": "Tur hiyerarsisi uzerinden ozellik kalitimi yapabiliyor mu?",
        "rules": [
            ("meyve", "etki", "saglikli"),
            ("elma", "turu", "meyve"),
            ("yesil elma", "tadi", "eksi"),
        ],
        "queries": [
            {
                "question": "Yesil elma saglikli mi?",
                "terms": ["yesil elma", "saglikli"],
                "expected": {
                    "mechanical": {
                        "description": "3 kural state'e eklenmeli.",
                        "check_rules_count": 3,
                        "check_no_confidence_drop": True,
                    },
                    "inference": {
                        "description": "Zincir: yesil elma→elma→meyve→saglikli. Baglanti yok.",
                        "expect_direct": [],
                        "expect_chains": [
                            "yesil elma -> elma -> meyve -> saglikli"
                        ],
                        "requires_substring_matching": True,
                    },
                    "meaning": {
                        "description": "Tur hiyerarsisi uzerinden kalitim.",
                        "expect_inheritance": True,
                    },
                },
            }
        ],
        "predictions": {
            "mechanical": "PASS",
            "inference": "FAIL",
            "meaning": "FAIL",
        },
    }


def scenario_d_evolution():
    """Zaman Icinde Evrilme: 10 kitap ile gorusun degisimi."""
    books = [
        {
            "name": "Kitap 1: Dijital Cag",
            "rules": [
                ("teknoloji", "saglar", "verimlilik"),
                ("verimlilik", "etki", "olumlu"),
                ("internet", "saglar", "iletisim"),
            ],
        },
        {
            "name": "Kitap 2: Saglik Devrimi",
            "rules": [
                ("teknoloji", "gelistirir", "tip"),
                ("tip", "etki", "hayat kurtarir"),
                ("teknoloji", "etki", "faydali"),
            ],
        },
        {
            "name": "Kitap 3: Egitim ve Teknoloji",
            "rules": [
                ("teknoloji", "destekler", "egitim"),
                ("egitim", "etki", "olumlu"),
                ("teknoloji", "etki", "gerekli"),
            ],
        },
        {
            "name": "Kitap 4: Dijital Bagimlilik",
            "rules": [
                ("teknoloji", "yaratir", "bagimlilik"),
                ("bagimlilik", "etki", "zararli"),
                ("sosyal medya", "azaltir", "dikkat"),
            ],
        },
        {
            "name": "Kitap 5: Issizlik Krizi",
            "rules": [
                ("otomasyon", "yaratir", "issizlik"),
                ("issizlik", "etki", "olumsuz"),
                ("teknoloji", "etki", "tehlikeli"),
            ],
        },
        {
            "name": "Kitap 6: Yalnizlik Cagi",
            "rules": [
                ("teknoloji", "azaltir", "sosyal bag"),
                ("yalnizlik", "etki", "zararli"),
                ("teknoloji", "etki", "yikici"),
            ],
        },
        {
            "name": "Kitap 7: Dengeli Bakis",
            "rules": [
                ("teknoloji", "hem", "faydali"),
                ("teknoloji", "hem", "riskli"),
                ("denge", "etki", "onemli"),
            ],
        },
        {
            "name": "Kitap 8: Elestirisel Dusunce",
            "rules": [
                ("teknoloji", "gerektirir", "elestiri"),
                ("bilinc", "etki", "koruyucu"),
                ("teknoloji", "etki", "notr"),
            ],
        },
        {
            "name": "Kitap 9: Bilincli Kullanim",
            "rules": [
                ("bilincli kullanim", "yapar", "teknoloji"),
                ("bilincli kullanim", "etki", "olumlu"),
                ("teknoloji", "etki", "iyi (sartli)"),
            ],
        },
        {
            "name": "Kitap 10: Gelecek Vizyonu",
            "rules": [
                ("teknoloji", "potansiyel", "buyuk"),
                ("sorumluluk", "etki", "belirleyici"),
                ("teknoloji", "etki", "umut verici"),
            ],
        },
    ]

    return {
        "name": "Senaryo D - Zaman Icinde Evrilme",
        "description": "10 kitap boyunca ayni soruya verilen cevap nasil evriliyor?",
        "books": books,
        "query_after_each_book": {
            "question": "Teknoloji iyi midir?",
            "terms": ["teknoloji"],
        },
        "expected": {
            "mechanical": {
                "description": "Her kitaptan sonra confidence skorlari degismeli.",
            },
            "inference": {
                "description": "Kitap 1-3 olumlu, 4-6 olumsuz, 7-10 nuansli.",
                "expected_trend": [
                    "olumlu", "olumlu", "olumlu",
                    "karisik", "olumsuz", "olumsuz",
                    "dengeli", "dengeli",
                    "sartli olumlu", "sartli olumlu",
                ],
            },
            "meaning": {
                "description": "Sistem gercekten gorusunu evriltiyor mu yoksa sayac mi tutuyor?",
            },
        },
        "predictions": {
            "mechanical": "PARTIAL",
            "inference": "PARTIAL",
            "meaning": "FAIL",
        },
    }


def scenario_e_stress():
    """Stres Testi: 1000 kural ile performans."""
    import random

    random.seed(42)

    subjects_pool = {
        "hayvanlar": ["kedi", "kopek", "kus", "balik", "at", "tavsan", "aslan", "kartal", "yunus", "fil"],
        "renkler": ["kirmizi", "mavi", "yesil", "sari", "siyah", "beyaz", "turuncu", "mor", "pembe", "gri"],
        "sehirler": ["istanbul", "ankara", "izmir", "bursa", "antalya", "trabzon", "konya", "adana", "samsun", "eskisehir"],
        "meslekler": ["doktor", "ogretmen", "muhendis", "avukat", "asci", "pilot", "hemsire", "mimar", "sanatci", "sporcu"],
    }

    relations = ["etki", "ozellik", "icerir", "turu", "bulunur", "kullanir", "uretir", "gerektirir", "destekler", "saglar"]
    objects = ["iyi", "kotu", "hizli", "yavas", "buyuk", "kucuk", "onemli", "zor", "kolay", "faydali"]

    rules = []
    all_subjects = []
    for category, items in subjects_pool.items():
        all_subjects.extend(items)

    for i in range(1000):
        subject = random.choice(all_subjects)
        relation = random.choice(relations)
        obj = random.choice(objects)
        rules.append((subject, relation, obj))

    test_queries = [
        {"question": "Kedi hakkinda ne biliyorsun?", "terms": ["kedi"]},
        {"question": "Istanbul ve doktor iliskisi?", "terms": ["istanbul", "doktor"]},
        {"question": "Kirmizi iyi midir?", "terms": ["kirmizi", "iyi"]},
        {"question": "Hayvanlar hakkinda genel bilgi", "terms": ["kedi", "kopek", "kus"]},
        {"question": "Meslekler ve ozellikler", "terms": ["doktor", "ogretmen", "onemli"]},
        {"question": "Sehirler ve etkileri", "terms": ["istanbul", "ankara", "iyi"]},
        {"question": "Tek terim sorgusu", "terms": ["aslan"]},
        {"question": "Cok terimli sorgu", "terms": ["kedi", "kirmizi", "istanbul", "doktor", "iyi"]},
        {"question": "Var olmayan terim", "terms": ["uzayli"]},
        {"question": "Tum renkler", "terms": ["kirmizi", "mavi", "yesil", "sari", "siyah"]},
    ]

    return {
        "name": "Senaryo E - Stres Testi (1000 kural)",
        "description": "1000 kural ile performans ve cikarim kalitesi.",
        "rules": rules,
        "queries": test_queries,
        "expected": {
            "mechanical": {
                "description": "O(n^2) performans bekleniyor.",
            },
            "inference": {
                "description": "Kural sayisi arttikca noise artabilir.",
            },
            "meaning": {
                "description": "Olcek buyudugunde anlam kalitesi nasil etkilenir?",
            },
        },
        "predictions": {
            "mechanical": "PARTIAL",
            "inference": "PARTIAL",
            "meaning": "FAIL",
        },
    }
