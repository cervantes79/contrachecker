"""
Bilgi tabanini BIR KERE olusturur: rules/knowledge.db
Sadece DB yoksa veya --force ile calistirildiginda uretir.
Varsa dokunmaz.

Kullanim:
  python tools/generate_knowledge.py          # DB yoksa olustur
  python tools/generate_knowledge.py --force  # Sifirdan olustur
"""

import sys
import os
import time

# Project root'u path'e ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage import RuleStore

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rules", "knowledge.db")


def check_existing():
    """DB varsa ve doluysa True don."""
    if not os.path.exists(DB_PATH):
        return False
    try:
        store = RuleStore(DB_PATH)
        count = store.count()
        store.close()
        return count > 0
    except Exception:
        return False


def generate_all_rules():
    """Tum domainlerden kurallar uret. Her kural (subject, relation, obj, confidence, mass, source) tuple."""
    # million_test.py'deki generator'lari import et
    from tests.million_test import (
        generate_ai_tech, generate_health, generate_climate,
        generate_economy, generate_education, generate_society,
        generate_science, generate_culture, generate_sports,
        generate_daily_life, generate_transportation, generate_energy,
        generate_law, generate_media, generate_food, generate_security,
        generate_space, generate_maritime, generate_agriculture,
        generate_architecture, generate_cross_domain_links,
    )

    generators = [
        ("yapay_zeka_teknoloji", generate_ai_tech),
        ("saglik_tip", generate_health),
        ("iklim_cevre", generate_climate),
        ("ekonomi_finans", generate_economy),
        ("egitim_gelisim", generate_education),
        ("toplum_siyaset", generate_society),
        ("bilim", generate_science),
        ("kultur_sanat", generate_culture),
        ("spor", generate_sports),
        ("gunluk_yasam", generate_daily_life),
        ("ulasim", generate_transportation),
        ("enerji", generate_energy),
        ("hukuk", generate_law),
        ("medya", generate_media),
        ("gida", generate_food),
        ("guvenlik", generate_security),
        ("uzay", generate_space),
        ("denizcilik", generate_maritime),
        ("tarim", generate_agriculture),
        ("mimari", generate_architecture),
    ]

    all_rules = []
    for domain_key, gen_func in generators:
        domain_rules = gen_func()
        # 6-tuple: (subject, relation, obj, confidence, mass, source)
        full_rules = [(s, r, o, 1.0, 1, domain_key) for s, r, o in domain_rules]
        print(f"  {domain_key}: {len(full_rules):,} kural")
        all_rules.extend(full_rules)

    cross_links = generate_cross_domain_links()
    cross_full = [(s, r, o, 1.0, 1, "cross_domain") for s, r, o in cross_links]
    all_rules.extend(cross_full)
    print(f"  cross_domain: {len(cross_full)} kural")

    return all_rules


def create_db(rules):
    """DB'ye kural ekle. Mevcut DB varsa ustune ekler, SILMEZ."""
    store = RuleStore(DB_PATH)

    # Batch insert
    batch_size = 50000
    total = len(rules)
    for i in range(0, total, batch_size):
        batch = rules[i:i + batch_size]
        normalized = [(s.lower(), r.lower(), o.lower(), c, m, src) for s, r, o, c, m, src in batch]
        store.bulk_insert_full(normalized)
        print(f"  {min(i + batch_size, total):,}/{total:,} yazildi")

    # Dogrula
    count = store.count()
    store.close()
    return count


def scale_rules(base_rules, multiplier):
    """Mevcut kurallari varyasyonlarla cogalt.
    Her kural icin nitelikli versiyonlar uretir.
    Ornek: (yapay zeka, etki, verimli) -> (yapay zeka sistemi, etki, verimli), vb.
    """
    if multiplier <= 1:
        return base_rules

    import random
    random.seed(42)

    scaled = list(base_rules)
    prefixes = ["ileri", "temel", "modern", "geleneksel", "yeni", "eski",
                 "dijital", "analog", "yerel", "global"]
    suffixes = ["sistemi", "alani", "sureci", "yontemi", "uygulamasi",
                "modeli", "analizi", "stratejisi", "politikasi", "cercevesi"]

    existing = set((s, r, o) for s, r, o, *_ in base_rules)

    for mult in range(1, multiplier):
        for s, r, o, c, m, src in base_rules:
            # Varyasyon 1: prefix + subject
            prefix = prefixes[mult % len(prefixes)]
            new_s = f"{prefix} {s}"
            triple = (new_s, r, o)
            if triple not in existing:
                existing.add(triple)
                scaled.append((new_s, r, o, c, m, src))

            # Varyasyon 2: subject + suffix
            suffix = suffixes[mult % len(suffixes)]
            new_s2 = f"{s} {suffix}"
            triple2 = (new_s2, r, o)
            if triple2 not in existing:
                existing.add(triple2)
                scaled.append((new_s2, r, o, c, m, src))

            if len(scaled) >= len(base_rules) * multiplier:
                return scaled

    return scaled


def main():
    force = "--force" in sys.argv
    # Scale: python tools/generate_knowledge.py --scale 10
    scale = 1
    for i, arg in enumerate(sys.argv):
        if arg == "--scale" and i + 1 < len(sys.argv):
            scale = int(sys.argv[i + 1])

    if not force and check_existing():
        store = RuleStore(DB_PATH)
        count = store.count()
        store.close()
        print(f"DB zaten var: {DB_PATH}")
        print(f"  {count:,} kural mevcut. Yeniden olusturmak icin: --force")
        return

    print(f"Bilgi tabani olusturuluyor: {DB_PATH}")
    if scale > 1:
        print(f"  Scale: {scale}x (hedef ~{scale}M kural)")
    print()

    print("[1/2] Kurallar uretiliyor...")
    t = time.time()
    rules = generate_all_rules()
    print(f"\n  Base: {len(rules):,} kural ({time.time()-t:.1f}s)")

    if scale > 1:
        print(f"\n  {scale}x scale uygulaniytor...")
        t2 = time.time()
        rules = scale_rules(rules, scale)
        print(f"  Scale sonrasi: {len(rules):,} kural ({time.time()-t2:.1f}s)")

    print(f"  Toplam: {len(rules):,} kural")

    print("\n[2/2] SQLite'a yaziliyor...")
    t = time.time()
    count = create_db(rules)
    elapsed = time.time() - t

    db_size = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"\n  Yazilan: {count:,} kural")
    print(f"  DB boyutu: {db_size:.1f} MB")
    print(f"  Sure: {elapsed:.1f}s")
    print(f"\n  TAMAM: {DB_PATH}")


if __name__ == "__main__":
    main()
