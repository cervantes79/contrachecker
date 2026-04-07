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
    """DB olustur ve kurallari yaz."""
    # Eski DB varsa sil
    for ext in ["", "-wal", "-shm"]:
        p = DB_PATH + ext
        if os.path.exists(p):
            os.remove(p)

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


def main():
    force = "--force" in sys.argv

    if not force and check_existing():
        store = RuleStore(DB_PATH)
        count = store.count()
        store.close()
        print(f"DB zaten var: {DB_PATH}")
        print(f"  {count:,} kural mevcut. Yeniden olusturmak icin: --force")
        return

    print(f"Bilgi tabani olusturuluyor: {DB_PATH}")
    print()

    print("[1/2] Kurallar uretiliyor...")
    t = time.time()
    rules = generate_all_rules()
    print(f"\n  Toplam: {len(rules):,} kural ({time.time()-t:.1f}s)")

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
