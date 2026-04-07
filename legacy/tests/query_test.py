"""
Sorgu testi - Mevcut DB'yi acar, sorgulari kosar.
Kural URETMEZ. DB yoksa hata verir.

Kullanim:
  python tools/generate_knowledge.py   # Once DB olustur (bir kere)
  python tests/query_test.py           # Sonra sorgula (istedigin kadar)
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine_v4 import RuleEngineV4

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rules", "knowledge.db")


def define_questions():
    """50 test sorusu — pozitif, negatif, zincir, kalitim, nuans."""
    return [
        # --- Pozitif (10) ---
        {"id": 1, "cat": "positive", "q": "Yapay zeka otomasyon saglar mi?", "terms": ["yapay zeka", "otomasyon"], "expect": True},
        {"id": 2, "cat": "positive", "q": "Spor saglikli midir?", "terms": ["spor", "saglikli"], "expect": True},
        {"id": 3, "cat": "positive", "q": "Bitcoin bir kripto para midir?", "terms": ["bitcoin", "kripto"], "expect": True},
        {"id": 4, "cat": "positive", "q": "Depresyon bir hastalik midir?", "terms": ["depresyon", "hastalik"], "expect": True},
        {"id": 5, "cat": "positive", "q": "Gunes enerji saglar mi?", "terms": ["gunes", "enerji"], "expect": True},
        {"id": 6, "cat": "positive", "q": "Internet iletisim saglar mi?", "terms": ["internet", "iletisim"], "expect": True},
        {"id": 7, "cat": "positive", "q": "Agac oksijen uretir mi?", "terms": ["agac", "oksijen"], "expect": True},
        {"id": 8, "cat": "positive", "q": "Egitim bilgi saglar mi?", "terms": ["egitim", "bilgi"], "expect": True},
        {"id": 9, "cat": "positive", "q": "Stres zararli midir?", "terms": ["stres", "zararli"], "expect": True},
        {"id": 10, "cat": "positive", "q": "Su hayati midir?", "terms": ["su", "hayati"], "expect": True},

        # --- Negatif (10) ---
        {"id": 11, "cat": "negative", "q": "Piyano bir hayvan midir?", "terms": ["piyano", "hayvan"], "expect": False},
        {"id": 12, "cat": "negative", "q": "Futbol matematik ogretir mi?", "terms": ["futbol", "matematik"], "expect": False},
        {"id": 13, "cat": "negative", "q": "Gitar bilgi saglar mi?", "terms": ["gitar", "bilgi"], "expect": False},
        {"id": 14, "cat": "negative", "q": "Boks huzur verir mi?", "terms": ["boks", "huzur"], "expect": False},
        {"id": 15, "cat": "negative", "q": "Kayak besleyici midir?", "terms": ["kayak", "besleyici"], "expect": False},
        {"id": 16, "cat": "negative", "q": "Terlik uzay arastirir mi?", "terms": ["terlik", "uzay"], "expect": False},
        {"id": 17, "cat": "negative", "q": "Sandalye tedavi eder mi?", "terms": ["sandalye", "tedavi"], "expect": False},
        {"id": 18, "cat": "negative", "q": "Bardak enerji uretir mi?", "terms": ["bardak", "enerji"], "expect": False},
        {"id": 19, "cat": "negative", "q": "Hali iklim degistirir mi?", "terms": ["hali", "iklim"], "expect": False},
        {"id": 20, "cat": "negative", "q": "Kalem hastalik tedavi eder mi?", "terms": ["kalem", "hastalik"], "expect": False},

        # --- Derin zincir (10) ---
        {"id": 21, "cat": "deep_chain", "q": "Spor guc saglar mi?", "terms": ["spor", "guc"], "expect": True},
        {"id": 22, "cat": "deep_chain", "q": "Egitim ozgurlestirir mi?", "terms": ["egitim", "ozgurlestirir"], "expect": True},
        {"id": 23, "cat": "deep_chain", "q": "Teknoloji iletisimi gelistirir mi?", "terms": ["teknoloji", "iletisim"], "expect": True},
        {"id": 24, "cat": "deep_chain", "q": "Uyku ogrenmeyi destekler mi?", "terms": ["uyku", "ogrenme"], "expect": True},
        {"id": 25, "cat": "deep_chain", "q": "Yagmur hayati midir?", "terms": ["yagmur", "hayati"], "expect": True},
        {"id": 26, "cat": "deep_chain", "q": "Egzersiz ruh sagligini iyilestirir mi?", "terms": ["egzersiz", "ruh sagligi"], "expect": True},
        {"id": 27, "cat": "deep_chain", "q": "Enflasyon huzursuzluga neden olur mu?", "terms": ["enflasyon", "huzursuzluk"], "expect": True},
        {"id": 28, "cat": "deep_chain", "q": "Bulut bilisim girisimciligi destekler mi?", "terms": ["bulut bilisim", "girisimcilik"], "expect": True},
        {"id": 29, "cat": "deep_chain", "q": "Dijital ucurum esitsizlige neden olur mu?", "terms": ["dijital ucurum", "esitsizlik"], "expect": True},
        {"id": 30, "cat": "deep_chain", "q": "Antibiyotik direnci olumu arttirir mi?", "terms": ["antibiyotik direnci", "olum"], "expect": True},

        # --- Kalitim (10) ---
        {"id": 31, "cat": "inheritance", "q": "LLM veri gerektirir mi?", "terms": ["llm", "veri"], "expect": True},
        {"id": 32, "cat": "inheritance", "q": "Ethereum merkezsiz midir?", "terms": ["ethereum", "merkezsiz"], "expect": True},
        {"id": 33, "cat": "inheritance", "q": "Gunes paneli temiz enerji uretir mi?", "terms": ["gunes paneli", "temiz enerji"], "expect": True},
        {"id": 34, "cat": "inheritance", "q": "Ransomware siber tehdit midir?", "terms": ["ransomware", "siber tehdit"], "expect": True},
        {"id": 35, "cat": "inheritance", "q": "Yoga saglikli midir?", "terms": ["yoga", "saglikli"], "expect": True},
        {"id": 36, "cat": "inheritance", "q": "Netflix dijital medya midir?", "terms": ["netflix", "dijital medya"], "expect": True},
        {"id": 37, "cat": "inheritance", "q": "Depresyon bir hastalik midir?", "terms": ["depresyon", "hastalik"], "expect": True},
        {"id": 38, "cat": "inheritance", "q": "Konteyner gemisi ticaret yapar mi?", "terms": ["konteyner gemisi", "ticaret"], "expect": True},
        {"id": 39, "cat": "inheritance", "q": "Bugday bir bitki midir?", "terms": ["bugday", "bitki"], "expect": True},
        {"id": 40, "cat": "inheritance", "q": "Kodlama egitimi beceri kazandirir mi?", "terms": ["kodlama egitimi", "beceri"], "expect": True},

        # --- Nuans/Celiski (10) ---
        {"id": 41, "cat": "nuance", "q": "Elektrikli araclar cevreci midir?", "terms": ["elektrikli arac", "cevreci"], "expect": "nuance"},
        {"id": 42, "cat": "nuance", "q": "Kripto para gelecek midir?", "terms": ["kripto", "gelecek"], "expect": "nuance"},
        {"id": 43, "cat": "nuance", "q": "Yapay zeka sanati gercek sanat midir?", "terms": ["yapay zeka", "sanat"], "expect": "nuance"},
        {"id": 44, "cat": "nuance", "q": "Nukleer enerji guvenli midir?", "terms": ["nukleer enerji", "guvenli"], "expect": "nuance"},
        {"id": 45, "cat": "nuance", "q": "Kemoterapi faydali mi?", "terms": ["kemoterapi", "faydali"], "expect": "nuance"},
        {"id": 46, "cat": "nuance", "q": "Online egitim kaliteli mi?", "terms": ["online egitim", "kaliteli"], "expect": "nuance"},
        {"id": 47, "cat": "nuance", "q": "Goc topluma faydali mi?", "terms": ["goc", "faydali"], "expect": "nuance"},
        {"id": 48, "cat": "nuance", "q": "Sosyal medya ruh sagligi icin zararli mi?", "terms": ["sosyal medya", "ruh sagligi"], "expect": "nuance"},
        {"id": 49, "cat": "nuance", "q": "GDO guvenli midir?", "terms": ["gdo", "guvenli"], "expect": "nuance"},
        {"id": 50, "cat": "nuance", "q": "Doping sporculara yardimci mi?", "terms": ["doping", "yardimci"], "expect": "nuance"},
    ]


def evaluate_result(question, results):
    """Sonucu degerlendir."""
    if results is None:
        results = []

    has_results = len(results) > 0
    expect = question["expect"]

    if expect is True:
        # Pozitif: sonuc bulmali
        return "GECTI" if has_results else "KALDI"
    elif expect is False:
        # Negatif: sonuc BULMAMALI veya irrelevant olmali
        # Eger terimlerden ikisi de ayni chain'de geciyorsa yanlis pozitif
        terms = [t.lower() for t in question["terms"]]
        for r in results:
            text = r.get("chain", str(r.get("rule", ""))).lower()
            if all(t in text for t in terms):
                return "YANLIS POZITIF"
        return "GECTI"
    elif expect == "nuance":
        # Nuans: birden fazla perspektif olmali
        return "GECTI" if len(results) >= 2 else "KALDI"


def main():
    # DB kontrol
    if not os.path.exists(DB_PATH):
        print(f"HATA: DB bulunamadi: {DB_PATH}")
        print(f"Once calistir: python tools/generate_knowledge.py")
        sys.exit(1)

    print("=" * 70)
    print("  CHAINOFMEANING SORGU TESTI")
    print("  DB'den yukle, sorgula, raporla.")
    print("=" * 70)

    # Motor yukle
    print(f"\n[1/3] Motor yukleniyor: {DB_PATH}")
    t_load = time.time()
    engine = RuleEngineV4(db_path=DB_PATH, taxonomy_threshold=0.3)
    load_time = time.time() - t_load

    state_size = len(engine.state)
    tree_nodes = engine.decision_tree.get_node_count()
    tree_roots = engine.decision_tree.get_branch_count()
    tree_depth = engine.decision_tree.get_tree_depth()

    print(f"  Kural: {state_size:,}")
    print(f"  Yukleme: {load_time:.2f}s")
    print(f"  Decision tree: {tree_nodes} node, {tree_roots} root, depth={tree_depth}")
    print(f"  Domain sayisi: {len(engine._by_domain)}")

    # Sorgular
    print(f"\n[2/3] Sorgular calistiriliyor...")
    questions = define_questions()

    results_by_cat = {"positive": [], "negative": [], "deep_chain": [], "inheritance": [], "nuance": []}
    query_times = []

    for q in questions:
        t = time.time()
        results = engine.query(q["q"], q["terms"])
        elapsed = (time.time() - t) * 1000
        query_times.append(elapsed)

        verdict = evaluate_result(q, results or [])
        result_count = len(results) if results else 0
        results_by_cat[q["cat"]].append(verdict)

        symbol = "+" if verdict == "GECTI" else ("!" if verdict == "YANLIS POZITIF" else "X")
        print(f"  [{symbol}] {q['id']:2d}. [{q['cat']:12s}] {verdict:16s} | {q['q'][:50]:50s} ({result_count} sonuc, {elapsed:.1f}ms)")

    # Rapor
    print(f"\n[3/3] Rapor")
    print("=" * 70)

    total_pass = 0
    total_fail = 0
    total_fp = 0

    for cat, verdicts in results_by_cat.items():
        passed = verdicts.count("GECTI")
        failed = verdicts.count("KALDI")
        fp = verdicts.count("YANLIS POZITIF")
        total_pass += passed
        total_fail += failed
        total_fp += fp
        print(f"  {cat:15s}: {passed}/{len(verdicts)} gecti, {fp} yanlis pozitif")

    print(f"\n  TOPLAM: {total_pass}/50 gecti, {total_fp} yanlis pozitif")
    print(f"\n  PERFORMANS:")
    print(f"    Yukleme: {load_time:.2f}s")
    print(f"    Ort. sorgu: {sum(query_times)/len(query_times):.1f}ms")
    print(f"    Max sorgu: {max(query_times):.1f}ms")
    print(f"    Min sorgu: {min(query_times):.1f}ms")
    print(f"    Toplam sorgu: {sum(query_times)/1000:.2f}s")
    print("=" * 70)

    engine.store.close()


if __name__ == "__main__":
    main()
