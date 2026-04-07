"""
ChainOfMeaning Chat - Terminal uzerinden soru-cevap.
Kullanim: python chat.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.engine_v4 import RuleEngineV4

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rules", "knowledge.db")


def format_answer(results, terms):
    """Sonuclari okunabilir cevaba donustur."""
    if not results:
        return "Bu konuda bilgim yok."

    # Dogrudan kurallar
    directs = [r for r in results if r["type"] == "direct"]
    chains = [r for r in results if r["type"] == "chained"]

    lines = []

    # En guclu dogrudan bilgiler (max 5)
    if directs:
        lines.append("Bildiklerim:")
        seen = set()
        for d in directs[:10]:
            rule = d["rule"]
            text = f"  {rule.subject} --{rule.relation}--> {rule.obj}"
            if text not in seen:
                seen.add(text)
                conf = d["confidence"]
                if conf >= 0.8:
                    lines.append(f"  [kesin] {rule.subject} {rule.relation} {rule.obj}")
                elif conf >= 0.5:
                    lines.append(f"  [muhtemel] {rule.subject} {rule.relation} {rule.obj}")
                else:
                    lines.append(f"  [zayif] {rule.subject} {rule.relation} {rule.obj}")
            if len(seen) >= 5:
                break

    # En guclu zincirlemeler (max 5)
    if chains:
        lines.append("\nCikarimlarim:")
        seen = set()
        for c in chains[:20]:
            chain = c["chain"]
            if chain not in seen:
                seen.add(chain)
                conf = c["confidence"]
                if conf >= 0.8:
                    lines.append(f"  [kesin] {chain}")
                elif conf >= 0.5:
                    lines.append(f"  [muhtemel] {chain}")
                else:
                    lines.append(f"  [zayif] {chain}")
            if len(seen) >= 5:
                break

    # Celiski kontrolu
    positive_words = {"saglikli", "faydali", "iyi", "olumlu", "guvenli", "temiz", "verimli"}
    negative_words = {"zararli", "tehlikeli", "kotu", "olumsuz", "riskli", "kirli", "verimsiz"}

    all_text = " ".join(str(r.get("rule", "")) + " " + r.get("chain", "") for r in results[:20]).lower()
    has_positive = any(w in all_text for w in positive_words)
    has_negative = any(w in all_text for w in negative_words)

    if has_positive and has_negative:
        lines.append("\n[!] Bu konuda celiski var — hem olumlu hem olumsuz bilgiler mevcut.")

    return "\n".join(lines)


def extract_terms(question):
    """Sorudan anahtar terimleri cikar. Basit: stop word'leri cikart."""
    stop_words = {
        "mi", "mu", "midir", "mudur", "bir", "bu", "su", "ne", "nedir",
        "nasil", "neden", "icin", "ile", "ve", "veya", "ama", "da", "de",
        "mi?", "mu?", "midir?", "mudur?", "mı", "mı?", "dir", "dır",
        "var", "yok", "olan", "gibi", "kadar", "daha", "en", "cok",
        "hakkinda", "hakkında", "saglar", "yapar", "eder", "olur",
        "iyi", "kotu", "zararli", "faydali", "guvenli",
    }
    words = question.lower().replace("?", "").replace("!", "").replace(",", "").split()
    terms = [w for w in words if w not in stop_words and len(w) > 1]

    # Bitisik terimleri de dene (2-gram)
    bigrams = []
    for i in range(len(words) - 1):
        bigram = f"{words[i]} {words[i+1]}"
        if words[i] not in stop_words and words[i+1] not in stop_words:
            bigrams.append(bigram)

    return terms + bigrams


def main():
    if not os.path.exists(DB_PATH):
        print(f"HATA: DB bulunamadi: {DB_PATH}")
        print(f"Once: python tools/generate_knowledge.py")
        sys.exit(1)

    print("ChainOfMeaning yukleniytor...")
    t = time.time()
    engine = RuleEngineV4(db_path=DB_PATH, taxonomy_threshold=0.3)
    load_time = time.time() - t
    rule_count = len(engine.state)

    print(f"Hazir. {rule_count:,} kural, {load_time:.1f}s")
    print(f"Cikmak icin 'q' yaz.")
    print("-" * 50)

    while True:
        try:
            question = input("\nSen: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not question:
            continue
        if question.lower() in ("q", "quit", "exit", "cik", "cikis"):
            break

        terms = extract_terms(question)
        if not terms:
            print("\nMotor: Soruyu anlayamadim. Baska turlu sormayı dener misin?")
            continue

        t = time.time()
        results = engine.query(question, terms)
        elapsed = (time.time() - t) * 1000

        answer = format_answer(results, terms)
        print(f"\nMotor: ({elapsed:.0f}ms, {len(results) if results else 0} sonuc)")
        print(answer)

    print("\nGorüsmek üzere.")
    engine.store.close()


if __name__ == "__main__":
    main()
