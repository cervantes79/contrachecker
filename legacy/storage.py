"""
SQLite-based persistent storage for ChainOfMeaning rules.
Kurallar RAM'de degil, diskte tutulur. Program kapansa bile bilgi korunur.
"""
import sqlite3
import os


class RuleStore:
    def __init__(self, db_path=":memory:"):
        """db_path=":memory:" for RAM-only, or a file path for persistence."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")  # Daha iyi es zamanli performans
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT NOT NULL,
                relation TEXT NOT NULL,
                obj TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                mass INTEGER DEFAULT 1,
                source TEXT DEFAULT 'direct',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_subject ON rules(subject);
            CREATE INDEX IF NOT EXISTS idx_obj ON rules(obj);
            CREATE INDEX IF NOT EXISTS idx_subject_relation ON rules(subject, relation);
            CREATE INDEX IF NOT EXISTS idx_relation ON rules(relation);
            CREATE INDEX IF NOT EXISTS idx_confidence ON rules(confidence);

            CREATE TABLE IF NOT EXISTS taxonomy_profiles (
                entity TEXT NOT NULL,
                relation TEXT NOT NULL,
                obj TEXT NOT NULL,
                PRIMARY KEY (entity, relation, obj)
            );
            CREATE INDEX IF NOT EXISTS idx_taxonomy_entity ON taxonomy_profiles(entity);

            CREATE TABLE IF NOT EXISTS clusters (
                entity TEXT PRIMARY KEY,
                cluster_id INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_cluster_id ON clusters(cluster_id);
        """)
        self.conn.commit()

    # --- Rule CRUD ---

    def insert_rule(self, subject, relation, obj, confidence=1.0, mass=1, source="direct"):
        cursor = self.conn.execute(
            "INSERT INTO rules (subject, relation, obj, confidence, mass, source) VALUES (?, ?, ?, ?, ?, ?)",
            (subject, relation, obj, confidence, mass, source)
        )
        self.conn.commit()
        return cursor.lastrowid

    def find_exact(self, subject, relation, obj):
        """Tam eslesen kurali bul."""
        row = self.conn.execute(
            "SELECT id, subject, relation, obj, confidence, mass, source FROM rules WHERE subject=? AND relation=? AND obj=?",
            (subject, relation, obj)
        ).fetchone()
        return row  # (id, subject, relation, obj, confidence, mass, source) veya None

    def find_by_subject(self, subject, min_confidence=0.2):
        return self.conn.execute(
            "SELECT id, subject, relation, obj, confidence, mass FROM rules WHERE subject=? AND confidence>=?",
            (subject, min_confidence)
        ).fetchall()

    def find_by_obj(self, obj, min_confidence=0.2):
        return self.conn.execute(
            "SELECT id, subject, relation, obj, confidence, mass FROM rules WHERE obj=? AND confidence>=?",
            (obj, min_confidence)
        ).fetchall()

    def find_by_subject_relation(self, subject, relation, min_confidence=0.2):
        return self.conn.execute(
            "SELECT id, subject, relation, obj, confidence, mass FROM rules WHERE subject=? AND relation=? AND confidence>=?",
            (subject, relation, min_confidence)
        ).fetchall()

    def find_contradictions(self, subject, relation, obj):
        """Ayni subject+relation ama farkli obj olan kurallari bul."""
        return self.conn.execute(
            "SELECT id, subject, relation, obj, confidence, mass FROM rules WHERE subject=? AND relation=? AND obj!=? AND confidence>=0.1",
            (subject, relation, obj)
        ).fetchall()

    def update_confidence(self, rule_id, new_confidence):
        self.conn.execute(
            "UPDATE rules SET confidence=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (new_confidence, rule_id)
        )
        self.conn.commit()

    def update_mass(self, rule_id, new_mass):
        self.conn.execute(
            "UPDATE rules SET mass=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (new_mass, rule_id)
        )
        self.conn.commit()

    def reinforce(self, rule_id, confidence_boost=0.2):
        """Kuralın güvenini ve kütlesini artir."""
        self.conn.execute(
            "UPDATE rules SET confidence=MIN(1.0, confidence+?), mass=mass+1, updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (confidence_boost, rule_id)
        )
        self.conn.commit()

    def delete_dead(self, threshold=0.1):
        """Guveni esik altinda olan kurallari sil."""
        deleted = self.conn.execute(
            "DELETE FROM rules WHERE confidence < ?", (threshold,)
        ).rowcount
        self.conn.commit()
        return deleted

    def count(self):
        return self.conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0]

    def count_active(self, min_confidence=0.2):
        return self.conn.execute("SELECT COUNT(*) FROM rules WHERE confidence>=?", (min_confidence,)).fetchone()[0]

    # --- Bulk operations ---

    def bulk_insert(self, rules_list):
        """Cok sayida kurali tek seferde ekle. rules_list = [(subject, relation, obj), ...]"""
        self.conn.executemany(
            "INSERT INTO rules (subject, relation, obj) VALUES (?, ?, ?)",
            rules_list
        )
        self.conn.commit()

    def bulk_insert_full(self, rules_list):
        """Tum alanlarla ekle. rules_list = [(subject, relation, obj, confidence, mass, source), ...]"""
        self.conn.executemany(
            "INSERT INTO rules (subject, relation, obj, confidence, mass, source) VALUES (?, ?, ?, ?, ?, ?)",
            rules_list
        )
        self.conn.commit()

    # --- Taxonomy persistence ---

    def save_profile(self, entity, relation, obj):
        self.conn.execute(
            "INSERT OR IGNORE INTO taxonomy_profiles (entity, relation, obj) VALUES (?, ?, ?)",
            (entity, relation, obj)
        )

    def save_profiles_bulk(self, profiles_list):
        """Toplu profil kaydi. profiles_list = [(entity, relation, obj), ...]"""
        self.conn.executemany(
            "INSERT OR IGNORE INTO taxonomy_profiles (entity, relation, obj) VALUES (?, ?, ?)",
            profiles_list
        )
        self.conn.commit()

    def save_cluster(self, entity, cluster_id):
        self.conn.execute(
            "INSERT OR REPLACE INTO clusters (entity, cluster_id) VALUES (?, ?)",
            (entity, cluster_id)
        )

    def save_clusters_bulk(self, clusters_list):
        """Toplu cluster kaydi. clusters_list = [(entity, cluster_id), ...]"""
        self.conn.executemany(
            "INSERT OR REPLACE INTO clusters (entity, cluster_id) VALUES (?, ?)",
            clusters_list
        )
        self.conn.commit()

    def load_all_rules(self):
        """Aktif kurallari yukle, RAM indeksleri icin."""
        return self.conn.execute(
            "SELECT id, subject, relation, obj, confidence, mass, source FROM rules WHERE confidence >= 0.1"
        ).fetchall()

    def load_all_profiles(self):
        """Tum taxonomy profillerini yukle."""
        return self.conn.execute(
            "SELECT entity, relation, obj FROM taxonomy_profiles"
        ).fetchall()

    def load_all_clusters(self):
        """Tum cluster atamalarini yukle."""
        return self.conn.execute(
            "SELECT entity, cluster_id FROM clusters"
        ).fetchall()

    # --- Istatistikler ---

    def stats(self):
        """Veritabani istatistikleri."""
        total = self.count()
        active = self.count_active()
        subjects = self.conn.execute("SELECT COUNT(DISTINCT subject) FROM rules").fetchone()[0]
        relations = self.conn.execute("SELECT COUNT(DISTINCT relation) FROM rules").fetchone()[0]
        objects = self.conn.execute("SELECT COUNT(DISTINCT obj) FROM rules").fetchone()[0]
        return {
            "total_rules": total,
            "active_rules": active,
            "dead_rules": total - active,
            "unique_subjects": subjects,
            "unique_relations": relations,
            "unique_objects": objects,
        }

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
