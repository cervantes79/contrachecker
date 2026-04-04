"""
ChainOfMeaning v3 OTOPSI RAPORU
Auto-taxonomy, smart gates, rule mass motoru.
Her senaryoyu calistirir, motor ciktisini beklenen davranisla karsilastirir.
Mock yok, assert yok — gercek calistirma, durust karsilastirma.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine_v3 import Rule, RuleEngineV3 as RuleEngine
from expected.scenarios import (
    scenario_a_contradiction,
    scenario_b_deep_chaining,
    scenario_c_hierarchy,
    scenario_d_evolution,
    scenario_e_stress,
)


# --- Yardimci fonksiyonlar ---

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_subheader(text):
    print(f"\n--- {text} ---")


def print_rule_state(engine):
    print(f"\n  State ({len(engine.state)} kural):")
    for r in engine.state:
        print(f"    {r}")


def print_conclusions(conclusions):
    if conclusions is None:
        print("  Sonuc: None (hicbir kural aktive olmadi)")
        return
    print(f"  Sonuc ({len(conclusions)} cikarim):")
    for c in conclusions:
        if c["type"] == "direct":
            print(f"    [DOGRUDAN] {c['rule']} (guven: {c['confidence']:.2f})")
        elif c["type"] == "chained":
            print(f"    [ZINCIR]   {c['chain']} (guven: {c['confidence']:.2f})")


def print_taxonomy_state(engine):
    print(f"\n  Taxonomy:")
    print(f"    {engine.taxonomy}")


def evaluate_layer(layer_name, status, detail):
    symbol = {"PASS": "+", "PARTIAL": "~", "FAIL": "X"}
    print(f"  [{symbol[status]}] {layer_name}: {status} - {detail}")
    return status


# --- Senaryo A ---

def run_scenario_a():
    scenario = scenario_a_contradiction()
    print_header(scenario["name"])
    print(f"  {scenario['description']}")

    engine = RuleEngine()

    # Kurallari yukle
    print_subheader("Kural Yukleme")
    for s, r, o in scenario["rules"]:
        rule = Rule(s, r, o)
        print(f"\n  Yukleniyor: {rule}")
        engine.ingest(rule)
    print_rule_state(engine)
    print_taxonomy_state(engine)

    # Sorgu
    q = scenario["queries"][0]
    print_subheader(f"Sorgu: {q['question']}")
    conclusions = engine.query(q["question"], q["terms"])
    print_conclusions(conclusions)

    # Degerlendirme
    print_subheader("Degerlendirme")
    expected = q["expected"]

    # Katman 1: Mekanik
    rules_count = len(engine.state)
    expected_count = expected["mechanical"]["check_rules_count"]
    # v3: indirect contradiction may cause confidence drop on saglikli
    saglikli_rules = [r for r in engine.state if r.obj == "saglikli"]
    saglikli_conf = saglikli_rules[0].confidence if saglikli_rules else None

    if rules_count == expected_count:
        m = evaluate_layer("Mekanik Dogruluk", "PASS",
            f"{rules_count} kural eklendi. "
            f"{'Indirect contradiction saglikli confidence=' + f'{saglikli_conf:.2f}' if saglikli_conf and saglikli_conf < 1.0 else 'Forget gate dogrudan celiski gormedi (dogru, cunku farkli subject).'}")
    elif rules_count > 0:
        m = evaluate_layer("Mekanik Dogruluk", "PARTIAL",
            f"Beklenen {expected_count} kural, bulunan {rules_count}.")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "FAIL",
            f"Beklenen {expected_count} kural, bulunan {rules_count}.")

    # Katman 2: Cikarim
    has_direct_kahve = False
    has_chain_kahve_kafein = False
    if conclusions:
        for c in conclusions:
            if c["type"] == "direct" and "kahve" in str(c.get("rule", "")):
                has_direct_kahve = True
            if c["type"] == "chained" and "kahve" in c.get("chain", "") and "kafein" in c.get("chain", ""):
                has_chain_kahve_kafein = True

    if has_direct_kahve and has_chain_kahve_kafein:
        i = evaluate_layer("Cikarim Kalitesi", "PASS",
            "Hem dogrudan 'kahve' kurali hem de 'kahve->kafein' zinciri bulundu.")
    elif has_direct_kahve or has_chain_kahve_kafein:
        found = "dogrudan kural" if has_direct_kahve else "zincir"
        missing = "zincir" if has_direct_kahve else "dogrudan kural"
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            f"{found} bulundu ama {missing} eksik.")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL",
            "Ne dogrudan kural ne de zincir bulundu.")

    # Katman 3: Anlam — v3: indirect contradiction should cause confidence DROP
    contradiction_detected = False
    confidence_dropped = False

    if conclusions:
        positive = any("saglikli" in str(c.get("rule", "")) or "saglikli" in c.get("chain", "") for c in conclusions)
        negative = any("zararli" in str(c.get("rule", "")) or "zararli" in c.get("chain", "") for c in conclusions)
        if positive and negative:
            contradiction_detected = True

    # Check if indirect contradiction caused confidence drop on saglikli
    if saglikli_conf is not None and saglikli_conf < 1.0:
        confidence_dropped = True

    if contradiction_detected and confidence_dropped:
        a = evaluate_layer("Anlam Testi", "PASS",
            f"Dolayli celiski tespit edildi VE confidence dustu (saglikli: {saglikli_conf:.2f}). "
            f"Sistem kahve->kafein->zararli zincirini gorup saglikli'yi sorguluyor!")
    elif contradiction_detected:
        a = evaluate_layer("Anlam Testi", "PARTIAL",
            "Hem olumlu hem olumsuz sonuc var ama confidence dusmedi — celiski raporlanmiyor.")
    else:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Celiski tespit edilemedi.")

    return {"mechanical": m, "inference": i, "meaning": a}


# --- Senaryo B ---

def run_scenario_b():
    scenario = scenario_b_deep_chaining()
    print_header(scenario["name"])
    print(f"  {scenario['description']}")

    engine = RuleEngine()

    print_subheader("Kural Yukleme")
    for s, r, o in scenario["rules"]:
        rule = Rule(s, r, o)
        print(f"\n  Yukleniyor: {rule}")
        engine.ingest(rule)
    print_rule_state(engine)
    print_taxonomy_state(engine)

    q = scenario["queries"][0]
    print_subheader(f"Sorgu: {q['question']}")
    conclusions = engine.query(q["question"], q["terms"])
    print_conclusions(conclusions)

    print_subheader("Degerlendirme")
    expected = q["expected"]

    # Katman 1: Mekanik
    rules_count = len(engine.state)
    expected_count = expected["mechanical"]["check_rules_count"]
    if rules_count == expected_count:
        m = evaluate_layer("Mekanik Dogruluk", "PASS",
            f"{rules_count} kural eklendi, conflict yok.")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "FAIL",
            f"Beklenen {expected_count} kural, bulunan {rules_count}.")

    # Katman 2: Cikarim — 4 adimlik zincir kurulabiliyor mu?
    max_chain_depth = 0
    links_sokrates_empati = False
    if conclusions:
        for c in conclusions:
            if c["type"] == "chained":
                depth = c["chain"].count("->")
                max_chain_depth = max(max_chain_depth, depth)
                if "sokrates" in c["chain"] and "empati" in c["chain"]:
                    links_sokrates_empati = True

    if links_sokrates_empati:
        i = evaluate_layer("Cikarim Kalitesi", "PASS",
            f"Sokrates->empati zinciri kuruldu! Derinlik: {max_chain_depth}")
    elif max_chain_depth >= 2:
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            f"Zincir var ama sokrates->empati baglanamadi. Max derinlik: {max_chain_depth}")
    elif max_chain_depth > 0:
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            f"Sadece {max_chain_depth} adimlik zincir kuruldu. 4 adim gerekiyor.")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL",
            "Hicbir zincir kurulamadi.")

    # Katman 3: Anlam
    if links_sokrates_empati:
        a = evaluate_layer("Anlam Testi", "PASS",
            "Sokrates'ten empatiye anlam zinciri kuruldu.")
    elif conclusions and len(conclusions) > 0:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Bazi kurallar aktive oldu ama sokrates->empati anlam baglantisi kurulamadi.")
    else:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Hicbir anlam cikarimi yapilmadi.")

    return {"mechanical": m, "inference": i, "meaning": a}


# --- Senaryo C ---

def run_scenario_c():
    scenario = scenario_c_hierarchy()
    print_header(scenario["name"])
    print(f"  {scenario['description']}")

    engine = RuleEngine()

    print_subheader("Kural Yukleme")
    for s, r, o in scenario["rules"]:
        rule = Rule(s, r, o)
        print(f"\n  Yukleniyor: {rule}")
        engine.ingest(rule)
    print_rule_state(engine)
    print_taxonomy_state(engine)

    q = scenario["queries"][0]
    print_subheader(f"Sorgu: {q['question']}")
    conclusions = engine.query(q["question"], q["terms"])
    print_conclusions(conclusions)

    print_subheader("Degerlendirme")

    # Katman 1: Mekanik
    rules_count = len(engine.state)
    if rules_count == 3:
        m = evaluate_layer("Mekanik Dogruluk", "PASS",
            f"{rules_count} kural eklendi.")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "FAIL",
            f"Beklenen 3 kural, bulunan {rules_count}.")

    # Katman 2: Cikarim
    links_to_saglikli = False
    has_any_chain = False
    if conclusions:
        for c in conclusions:
            if c["type"] == "chained":
                has_any_chain = True
                chain = c["chain"]
                if "saglikli" in chain and ("elma" in chain or "meyve" in chain):
                    links_to_saglikli = True

    if links_to_saglikli:
        i = evaluate_layer("Cikarim Kalitesi", "PASS",
            "Saglikli sonucuna tur hiyerarsisi uzerinden ulasildi!")
    elif has_any_chain:
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            "Bazi zincirler var ama saglikli baglantisi yok.")
    elif conclusions and len(conclusions) > 0:
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            "Dogrudan kurallar bulundu ama zincir kurulamadi.")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL",
            "Hicbir sonuc donmedi.")

    # Katman 3: Anlam
    if links_to_saglikli:
        a = evaluate_layer("Anlam Testi", "PASS",
            "Tur hiyerarsisi uzerinden kalitim yapildi.")
    else:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Inheritance mantigi yok. 'yesil elma' ve 'elma' ayri entity olarak kaliyor.")

    return {"mechanical": m, "inference": i, "meaning": a}


# --- Senaryo D ---

def run_scenario_d():
    scenario = scenario_d_evolution()
    print_header(scenario["name"])
    print(f"  {scenario['description']}")

    engine = RuleEngine()
    query_info = scenario["query_after_each_book"]
    snapshots = []

    for book_idx, book in enumerate(scenario["books"]):
        print_subheader(f"{book['name']}")

        for s, r, o in book["rules"]:
            rule = Rule(s, r, o)
            engine.ingest(rule)

        # Her kitaptan sonra sorgu
        conclusions = engine.query(query_info["question"], query_info["terms"])

        # Teknoloji ile ilgili kurallarin confidence snapshot'i
        tech_rules = [r for r in engine.state if r.subject == "teknoloji"]
        snapshot = {
            "book": book["name"],
            "tech_rules": [(str(r), r.confidence, r.mass) for r in tech_rules],
            "total_rules": len(engine.state),
            "conclusions_count": len(conclusions) if conclusions else 0,
            "conclusions": conclusions,
        }
        snapshots.append(snapshot)

        print(f"  Teknoloji kurallari ({len(tech_rules)}):")
        for r in tech_rules:
            print(f"    {r}")
        print(f"  Toplam kural: {len(engine.state)}")
        print(f"  Cikarim sayisi: {snapshot['conclusions_count']}")

    # Print taxonomy state at end
    print_subheader("Taxonomy Durumu (Son)")
    print_taxonomy_state(engine)

    # Degerlendirme
    print_subheader("Degerlendirme")

    # Katman 1: Mekanik — confidence evriliyor mu?
    first_confidences = [r[1] for r in snapshots[0]["tech_rules"]] if snapshots[0]["tech_rules"] else []
    last_confidences = [r[1] for r in snapshots[-1]["tech_rules"]] if snapshots[-1]["tech_rules"] else []
    confidence_changed = first_confidences != last_confidences or len(first_confidences) != len(last_confidences)

    any_confidence_below_1 = any(
        conf < 1.0
        for snap in snapshots
        for _, conf, _ in snap["tech_rules"]
    )

    if confidence_changed and any_confidence_below_1:
        m = evaluate_layer("Mekanik Dogruluk", "PASS",
            "Confidence skorlari evrildi ve forget gate tetiklendi.")
    elif confidence_changed:
        m = evaluate_layer("Mekanik Dogruluk", "PARTIAL",
            "Kural sayisi degisti ama forget gate hic tetiklenmedi.")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "FAIL",
            "Confidence skorlari hic degismedi.")

    # Katman 2: Cikarim — trend dogru mu?
    def sentiment_score(conclusions):
        if not conclusions:
            return 0
        positive_words = {"olumlu", "faydali", "iyi", "gerekli", "hayat kurtarir", "umut verici"}
        negative_words = {"zararli", "olumsuz", "tehlikeli", "yikici", "kotu"}
        pos = 0
        neg = 0
        for c in conclusions:
            text = str(c.get("rule", "")) + c.get("chain", "")
            for w in positive_words:
                if w in text:
                    pos += c["confidence"]
            for w in negative_words:
                if w in text:
                    neg += c["confidence"]
        return pos - neg

    sentiments = [sentiment_score(s["conclusions"]) for s in snapshots]
    print(f"\n  Sentiment trend: {[f'{s:.2f}' for s in sentiments]}")

    early_positive = all(s > 0 for s in sentiments[:3]) if len(sentiments) >= 3 else False
    mid_shift = any(s <= 0 for s in sentiments[3:6]) if len(sentiments) >= 6 else False

    if early_positive and mid_shift:
        i = evaluate_layer("Cikarim Kalitesi", "PASS",
            "Trend dogru: ilk kitaplar olumlu, ortalar olumsuz/karisik.")
    elif early_positive or mid_shift:
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            "Kismi trend: ya basi ya ortasi dogru ama ikisi birden degil.")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL",
            "Anlamsiz trend. Sistem kitaplara duyarsiz.")

    # Katman 3: Anlam — v3: confidence non-mechanical + mass > 1?
    confidence_pattern_mechanical = True
    any_mass_above_1 = False
    mechanical_values = {1.0, 0.3, 0.09, 0.027, 0.0081}

    for snap in snapshots:
        for rule_str, conf, mass in snap["tech_rules"]:
            if mass > 1:
                any_mass_above_1 = True
            # Check if confidence is NOT a simple power of 0.3
            is_mechanical = False
            for mv in mechanical_values:
                if abs(conf - mv) < 0.001:
                    is_mechanical = True
                    break
            if not is_mechanical and conf != round(conf, 1):
                confidence_pattern_mechanical = False

    # v3: With support-aware gates and mass, values should differ from mechanical 0.3
    # Also check for non-trivial confidence values
    non_trivial_confidences = set()
    for snap in snapshots:
        for _, conf, _ in snap["tech_rules"]:
            non_trivial_confidences.add(round(conf, 4))

    has_non_mechanical = len(non_trivial_confidences - mechanical_values - {1.0}) > 0

    if has_non_mechanical and any_mass_above_1:
        a = evaluate_layer("Anlam Testi", "PASS",
            f"Confidence desenleri mekanik degil (mass > 1 var, {len(non_trivial_confidences)} farkli deger). "
            f"Support-aware gates gercek ogrenme sagliyor.")
    elif has_non_mechanical or any_mass_above_1:
        detail = "mass > 1 var" if any_mass_above_1 else "non-mechanical confidence var"
        a = evaluate_layer("Anlam Testi", "PARTIAL",
            f"Kismi iyilesme: {detail}. Tam ogrenme icin ikisi de gerekli.")
    elif not confidence_pattern_mechanical:
        a = evaluate_layer("Anlam Testi", "PARTIAL",
            "Confidence desenleri mekanik 0.3 carpanindan farkli — bir miktar ogrenme olabilir.")
    else:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Confidence desenleri tamamen mekanik. Sayac tutuyor, ogrenmiyoruz.")

    return {"mechanical": m, "inference": i, "meaning": a}


# --- Senaryo E ---

def run_scenario_e():
    scenario = scenario_e_stress()
    print_header(scenario["name"])
    print(f"  {scenario['description']}")

    engine = RuleEngine()

    # Kural yukleme performansi
    print_subheader("Kural Yukleme (1000 kural)")
    start = time.time()
    for s, r, o in scenario["rules"]:
        engine.ingest(Rule(s, r, o))
    ingest_time = time.time() - start
    print(f"  Yukleme suresi: {ingest_time:.3f} saniye")
    print(f"  State'teki kural sayisi: {len(engine.state)} (bazi kurallar forget gate ile silinmis olabilir)")

    # Taxonomy state summary
    print_subheader("Taxonomy Ozeti")
    all_clusters = engine.taxonomy.get_all_clusters()
    multi_clusters = engine.taxonomy.get_multi_member_clusters()
    print(f"  Toplam cluster: {len(all_clusters)}")
    print(f"  Multi-member cluster: {len(multi_clusters)}")
    for cid, members in sorted(multi_clusters.items(), key=lambda x: -len(x[1]))[:5]:
        print(f"    Cluster {cid} ({len(members)} uye): {', '.join(sorted(members))}")

    # Sorgu performansi
    print_subheader("Sorgu Performansi")
    query_times = []
    query_results = []

    for q in scenario["queries"]:
        start = time.time()
        conclusions = engine.query(q["question"], q["terms"])
        elapsed = time.time() - start
        query_times.append(elapsed)
        result_count = len(conclusions) if conclusions else 0
        query_results.append(result_count)
        print(f"  [{elapsed:.4f}s] {q['question']}: {result_count} sonuc")

    avg_query_time = sum(query_times) / len(query_times)
    max_query_time = max(query_times)
    print(f"\n  Ortalama sorgu suresi: {avg_query_time:.4f}s")
    print(f"  Maksimum sorgu suresi: {max_query_time:.4f}s")

    # Noise analizi
    nonexistent_idx = next(i for i, q in enumerate(scenario["queries"]) if "olmayan" in q["question"])
    noise_from_nonexistent = query_results[nonexistent_idx]

    # Degerlendirme
    print_subheader("Degerlendirme")

    # Katman 1: Mekanik
    if ingest_time < 5.0 and avg_query_time < 1.0:
        m = evaluate_layer("Mekanik Dogruluk", "PASS",
            f"Performans kabul edilebilir. Yukleme: {ingest_time:.3f}s, Ort. sorgu: {avg_query_time:.4f}s")
    elif ingest_time < 30.0 and avg_query_time < 5.0:
        m = evaluate_layer("Mekanik Dogruluk", "PARTIAL",
            f"Yavas ama calisiyor. Yukleme: {ingest_time:.3f}s, Ort. sorgu: {avg_query_time:.4f}s")
    else:
        m = evaluate_layer("Mekanik Dogruluk", "FAIL",
            f"Cok yavas. Yukleme: {ingest_time:.3f}s, Ort. sorgu: {avg_query_time:.4f}s")

    # Katman 2: Cikarim — noise
    max_results = max(query_results)
    if noise_from_nonexistent == 0 and max_results < 100:
        i = evaluate_layer("Cikarim Kalitesi", "PASS",
            f"Noise dusuk. Var olmayan terim 0 sonuc dondu. Max sonuc: {max_results}")
    elif noise_from_nonexistent == 0:
        i = evaluate_layer("Cikarim Kalitesi", "PARTIAL",
            f"Var olmayan terim filtrelendi ama diger sorgular cok sonuc donduruyor (max: {max_results}). Noise yuksek.")
    else:
        i = evaluate_layer("Cikarim Kalitesi", "FAIL",
            f"Var olmayan terim bile {noise_from_nonexistent} sonuc donduruyor. Filtreleme cok zayif.")

    # Katman 3: Anlam — v3: meaningful clusters formed?
    multi_member_count = len(multi_clusters)
    max_cluster_size = max((len(m) for m in multi_clusters.values()), default=0)

    if multi_member_count >= 3 and max_cluster_size >= 3:
        a = evaluate_layer("Anlam Testi", "PASS",
            f"Anlamli cluster'lar olusturuldu: {multi_member_count} multi-member cluster, "
            f"en buyuk cluster {max_cluster_size} uye. Taxonomy calisarak entity'leri gruplayabiliyor.")
    elif multi_member_count >= 3:
        a = evaluate_layer("Anlam Testi", "PARTIAL",
            f"{multi_member_count} multi-member cluster olusturuldu (en buyuk: {max_cluster_size} uye). "
            f"Taxonomy calisiyor ama cluster'lar kucuk.")
    elif multi_member_count >= 1:
        a = evaluate_layer("Anlam Testi", "PARTIAL",
            f"Sadece {multi_member_count} multi-member cluster. Taxonomy basliyor ama yeterli degil.")
    else:
        a = evaluate_layer("Anlam Testi", "FAIL",
            "Hicbir anlamli cluster olusturulamadi. Taxonomy etkisiz.")

    return {"mechanical": m, "inference": i, "meaning": a}


# --- Ana rapor ---

def run_all():
    print("\n" + "#" * 70)
    print("#  CHAINOFMEANING v3 OTOPSI RAPORU")
    print("#  Auto-taxonomy, smart gates, rule mass motoru")
    print("#  Motor hicbir sekilde degistirilmeden test ediliyor.")
    print("#" * 70)

    results = {}
    results["A"] = run_scenario_a()
    results["B"] = run_scenario_b()
    results["C"] = run_scenario_c()
    results["D"] = run_scenario_d()
    results["E"] = run_scenario_e()

    # Ozet tablosu
    print_header("OZET TABLOSU")
    print(f"\n  {'Senaryo':<45} {'Mekanik':<12} {'Cikarim':<12} {'Anlam':<12}")
    print("  " + "-" * 81)

    names = {
        "A": "Celiski Yonetimi",
        "B": "Derin Zincirleme (4 adim)",
        "C": "Hiyerarsi / Kalitim",
        "D": "Zaman Icinde Evrilme",
        "E": "Stres Testi (1000 kural)",
    }

    for key in ["A", "B", "C", "D", "E"]:
        r = results[key]
        print(f"  {names[key]:<45} {r['mechanical']:<12} {r['inference']:<12} {r['meaning']:<12}")

    # Genel sonuc
    all_ratings = []
    for r in results.values():
        all_ratings.extend(r.values())

    pass_count = all_ratings.count("PASS")
    partial_count = all_ratings.count("PARTIAL")
    fail_count = all_ratings.count("FAIL")

    print(f"\n  Toplam: {pass_count} PASS, {partial_count} PARTIAL, {fail_count} FAIL")
    print(f"  (15 degerlendirme uzerinden)")

    # v1 vs v2 vs v3 karsilastirma tablosu
    print_header("v1 vs v2 vs v3 KARSILASTIRMA")

    # v1 results (from autopsy-report.txt: 7 PASS, 4 PARTIAL, 4 FAIL)
    v1_results = {
        "A": {"mechanical": "PASS",    "inference": "PASS",    "meaning": "PARTIAL"},
        "B": {"mechanical": "PASS",    "inference": "PARTIAL", "meaning": "FAIL"},
        "C": {"mechanical": "PASS",    "inference": "PARTIAL", "meaning": "FAIL"},
        "D": {"mechanical": "PASS",    "inference": "PARTIAL", "meaning": "FAIL"},
        "E": {"mechanical": "PASS",    "inference": "PASS",    "meaning": "FAIL"},
    }

    # v2 results (from autopsy-v2-report.txt: 10 PASS, 3 PARTIAL, 2 FAIL)
    v2_results = {
        "A": {"mechanical": "PASS",    "inference": "PASS",    "meaning": "PARTIAL"},
        "B": {"mechanical": "PASS",    "inference": "PASS",    "meaning": "PASS"},
        "C": {"mechanical": "PASS",    "inference": "PASS",    "meaning": "PASS"},
        "D": {"mechanical": "PASS",    "inference": "PARTIAL", "meaning": "FAIL"},
        "E": {"mechanical": "PASS",    "inference": "PARTIAL", "meaning": "FAIL"},
    }

    print(f"\n  {'Senaryo':<25} {'Katman':<12} {'v1':<10} {'v2':<10} {'v3':<10} {'Degisim':<15}")
    print("  " + "-" * 82)

    for key in ["A", "B", "C", "D", "E"]:
        for layer_idx, layer in enumerate(["mechanical", "inference", "meaning"]):
            layer_tr = {"mechanical": "Mekanik", "inference": "Cikarim", "meaning": "Anlam"}[layer]
            v1 = v1_results[key][layer]
            v2 = v2_results[key][layer]
            v3 = results[key][layer]

            # Determine change direction
            score = {"FAIL": 0, "PARTIAL": 1, "PASS": 2}
            if score[v3] > score[v2]:
                change = "IYILESTI"
            elif score[v3] < score[v2]:
                change = "GERILEDI"
            else:
                change = "ayni"

            name = names[key] if layer_idx == 0 else ""
            print(f"  {name:<25} {layer_tr:<12} {v1:<10} {v2:<10} {v3:<10} {change:<15}")
        print("  " + "-" * 82)

    # v1/v2/v3 totals
    v1_all = [v for r in v1_results.values() for v in r.values()]
    v2_all = [v for r in v2_results.values() for v in r.values()]
    v3_all = all_ratings

    print(f"\n  {'Motor':<15} {'PASS':<10} {'PARTIAL':<10} {'FAIL':<10}")
    print("  " + "-" * 45)
    print(f"  {'v1':<15} {v1_all.count('PASS'):<10} {v1_all.count('PARTIAL'):<10} {v1_all.count('FAIL'):<10}")
    print(f"  {'v2':<15} {v2_all.count('PASS'):<10} {v2_all.count('PARTIAL'):<10} {v2_all.count('FAIL'):<10}")
    print(f"  {'v3':<15} {v3_all.count('PASS'):<10} {v3_all.count('PARTIAL'):<10} {v3_all.count('FAIL'):<10}")

    # Improvement summary
    v2_pass = v2_all.count("PASS")
    v3_pass = v3_all.count("PASS")
    v2_fail = v2_all.count("FAIL")
    v3_fail = v3_all.count("FAIL")

    print(f"\n  v2 -> v3 degisim: PASS {v2_pass} -> {v3_pass} ({'+' if v3_pass >= v2_pass else ''}{v3_pass - v2_pass}), "
          f"FAIL {v2_fail} -> {v3_fail} ({'+' if v3_fail >= v2_fail else ''}{v3_fail - v2_fail})")

    print("\n" + "=" * 70)
    print("  OTOPSI TAMAMLANDI")
    print("=" * 70)

    return results


if __name__ == "__main__":
    run_all()
