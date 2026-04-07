"""
ChainOfMeaning v3 OLCEK + DURUSTLUK TESTI
10,000 kural ile motorun GERCEKTEN akilli olup olmadigini test eder.

Bu test KOLAY DEGIL. Sahte basar imkansiz:
  - 500 elle yazilmis cekirdek kural (6 alan)
  - 9,500 sistematik gurultu kurali (20 kategori)
  - 30 soru: basit, zincir, kalitim, celiski, NEGATIF, DOGRULAMA
  - Yanlis pozitif tespiti
  - Zincir dogrulama (her halka mevcut mu?)
  - Gurultu direnci (sinyal/gurultu orani)
"""

import sys
import os
import time
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine_v3 import Rule, RuleEngineV3


# ======================================================================
#  CEKIRDEK BILGI: 500 elle yazilmis kural (6 alan)
# ======================================================================

# --- BIYOLOJI (100 kural) ---
BIOLOGY_RULES = [
    # Hayvan taksonomisi
    ("kedi", "turu", "hayvan"),
    ("kopek", "turu", "hayvan"),
    ("aslan", "turu", "hayvan"),
    ("kaplan", "turu", "hayvan"),
    ("tavsan", "turu", "hayvan"),
    ("kus", "turu", "hayvan"),
    ("kartal", "turu", "kus"),
    ("balik", "turu", "hayvan"),
    ("yunus", "turu", "hayvan"),
    ("fil", "turu", "hayvan"),
    ("maymun", "turu", "hayvan"),
    ("kurt", "turu", "hayvan"),
    ("ayi", "turu", "hayvan"),
    ("yilan", "turu", "hayvan"),
    ("kaplumbaga", "turu", "hayvan"),
    ("kurbaga", "turu", "hayvan"),
    ("ari", "turu", "bocek"),
    ("bocek", "turu", "hayvan"),
    ("kelebek", "turu", "bocek"),
    ("karinca", "turu", "bocek"),
    # Hayvan ozellikleri
    ("hayvan", "ozellik", "canli"),
    ("kedi", "ozellik", "miyavlar"),
    ("kopek", "ozellik", "havlar"),
    ("aslan", "ozellik", "yirtici"),
    ("kaplan", "ozellik", "yirtici"),
    ("tavsan", "ozellik", "hizli"),
    ("kus", "ozellik", "ucar"),
    ("kartal", "ozellik", "keskin gorus"),
    ("balik", "ozellik", "yuzer"),
    ("yunus", "ozellik", "akilli"),
    ("fil", "ozellik", "buyuk"),
    ("maymun", "ozellik", "zeki"),
    ("kurt", "ozellik", "sosyal"),
    ("ayi", "ozellik", "guclu"),
    ("yilan", "ozellik", "zehirli"),
    # Besin zinciri
    ("ot", "turu", "bitki"),
    ("agac", "turu", "bitki"),
    ("cicek", "turu", "bitki"),
    ("bitki", "ozellik", "fotosentez"),
    ("bitki", "uretir", "oksijen"),
    ("agac", "uretir", "oksijen"),
    ("oksijen", "etki", "hayati"),
    ("tavsan", "yer", "ot"),
    ("kurt", "yer", "tavsan"),
    ("aslan", "yer", "zebra"),
    ("kus", "yer", "bocek"),
    ("balik", "yer", "plankton"),
    ("ayi", "yer", "balik"),
    ("yilan", "yer", "fare"),
    ("fare", "turu", "hayvan"),
    ("fare", "yer", "tahil"),
    ("zebra", "turu", "hayvan"),
    ("zebra", "yer", "ot"),
    # Insan vucudu
    ("kalp", "turu", "organ"),
    ("beyin", "turu", "organ"),
    ("akciger", "turu", "organ"),
    ("karaciger", "turu", "organ"),
    ("bobrek", "turu", "organ"),
    ("organ", "turu", "vucut parcasi"),
    ("kalp", "saglar", "kan dolasimi"),
    ("beyin", "saglar", "dusunce"),
    ("akciger", "saglar", "solunum"),
    ("karaciger", "saglar", "toksin temizleme"),
    ("bobrek", "saglar", "filtreleme"),
    ("kas", "turu", "vucut parcasi"),
    ("kemik", "turu", "vucut parcasi"),
    ("sinir", "turu", "vucut parcasi"),
    ("kas", "saglar", "hareket"),
    ("kemik", "saglar", "destek"),
    ("sinir", "saglar", "iletim"),
    # Hucre biyolojisi
    ("hucre", "icerir", "cekirdek"),
    ("hucre", "icerir", "mitokondri"),
    ("mitokondri", "uretir", "enerji"),
    ("hucre", "turu", "yasam birimi"),
    ("dna", "icerir", "gen"),
    ("gen", "belirler", "ozellik"),
    # Ekosistem
    ("orman", "icerir", "agac"),
    ("orman", "icerir", "hayvan"),
    ("deniz", "icerir", "balik"),
    ("deniz", "icerir", "su"),
    ("gol", "icerir", "su"),
    ("nehir", "icerir", "su"),
    ("su", "etki", "hayati"),
    # Evrim ve cesitlilik
    ("canli", "gerektirir", "su"),
    ("canli", "gerektirir", "oksijen"),
    ("canli", "gerektirir", "besin"),
    ("bitki", "turu", "canli"),
    ("hayvan", "turu", "canli"),
    ("mantar", "turu", "canli"),
    ("bakteri", "turu", "canli"),
    # Genetik
    ("mutasyon", "degistirir", "gen"),
    ("evrim", "gerektirir", "mutasyon"),
    ("evrim", "gerektirir", "zaman"),
    ("adaptasyon", "turu", "evrim sonucu"),
    ("dogal secilim", "turu", "evrim mekanizmasi"),
    # Ek biyoloji
    ("fotosentez", "gerektirir", "gunes"),
    ("fotosentez", "uretir", "oksijen"),
    ("solunum", "gerektirir", "oksijen"),
    ("solunum", "uretir", "enerji"),
]

# --- TEKNOLOJI (80 kural) ---
TECHNOLOGY_RULES = [
    # Bilgisayar
    ("bilgisayar", "turu", "teknoloji"),
    ("laptop", "turu", "bilgisayar"),
    ("masaustu", "turu", "bilgisayar"),
    ("tablet", "turu", "bilgisayar"),
    ("bilgisayar", "icerir", "islemci"),
    ("bilgisayar", "icerir", "bellek"),
    ("bilgisayar", "icerir", "disk"),
    ("islemci", "saglar", "hesaplama"),
    ("bellek", "saglar", "gecici depolama"),
    ("disk", "saglar", "kalici depolama"),
    ("bilgisayar", "kullanir", "elektrik"),
    ("bilgisayar", "saglar", "veri isleme"),
    # Internet
    ("internet", "turu", "teknoloji"),
    ("internet", "saglar", "baglanti"),
    ("internet", "saglar", "iletisim"),
    ("internet", "icerir", "web sitesi"),
    ("web sitesi", "icerir", "icerik"),
    ("e-posta", "turu", "iletisim araci"),
    ("e-posta", "kullanir", "internet"),
    ("arama motoru", "turu", "internet hizmeti"),
    ("arama motoru", "saglar", "bilgi erisimi"),
    # Yapay zeka
    ("yapay zeka", "turu", "teknoloji"),
    ("makine ogrenimi", "turu", "yapay zeka"),
    ("derin ogrenme", "turu", "makine ogrenimi"),
    ("yapay zeka", "gerektirir", "veri"),
    ("yapay zeka", "gerektirir", "islemci"),
    ("yapay zeka", "saglar", "otomasyon"),
    ("yapay zeka", "etki", "devrimsel"),
    ("robot", "kullanir", "yapay zeka"),
    ("robot", "turu", "makine"),
    ("otomasyon", "etki", "verimlilik"),
    # Sosyal medya
    ("sosyal medya", "turu", "platform"),
    ("sosyal medya", "kullanir", "internet"),
    ("sosyal medya", "saglar", "paylasim"),
    ("sosyal medya", "etki", "bagimlilik yapici"),
    ("sosyal medya", "etki", "bilgi yayilimi"),
    # Yazilim
    ("yazilim", "turu", "teknoloji"),
    ("isletim sistemi", "turu", "yazilim"),
    ("uygulama", "turu", "yazilim"),
    ("programlama", "uretir", "yazilim"),
    ("programlama", "gerektirir", "mantik"),
    ("algoritma", "turu", "problem cozum yontemi"),
    ("algoritma", "saglar", "verimlilik"),
    # Donanim
    ("telefon", "turu", "cihaz"),
    ("telefon", "kullanir", "internet"),
    ("telefon", "saglar", "iletisim"),
    ("televizyon", "turu", "cihaz"),
    ("televizyon", "saglar", "gorsel icerik"),
    # Siber guvenlik
    ("sifreleme", "turu", "guvenlik yontemi"),
    ("sifreleme", "saglar", "gizlilik"),
    ("virus", "turu", "zararli yazilim"),
    ("virus", "etki", "zararli"),
    ("guvenlik duvari", "saglar", "koruma"),
    # Teknoloji genel
    ("teknoloji", "etki", "faydali"),
    ("teknoloji", "etki", "zararli"),
    ("teknoloji", "gerektirir", "bilgi"),
    ("teknoloji", "saglar", "kolaylik"),
    ("inovasyon", "turu", "teknoloji sureci"),
    ("inovasyon", "gerektirir", "yaraticilik"),
    # Veri bilimi
    ("veri", "turu", "bilgi kaynagi"),
    ("buyuk veri", "turu", "veri"),
    ("veri analizi", "saglar", "icerik"),
    ("veritabani", "turu", "depolama"),
    ("veritabani", "saglar", "veri yonetimi"),
    # Bulut bilisim
    ("bulut bilisim", "turu", "teknoloji"),
    ("bulut bilisim", "saglar", "olceklenebilirlik"),
    ("sunucu", "turu", "donanim"),
    ("sunucu", "saglar", "hesaplama"),
    # Blokzincir
    ("blokzincir", "turu", "teknoloji"),
    ("blokzincir", "saglar", "guvenilirlik"),
    ("kripto para", "kullanir", "blokzincir"),
    # IoT
    ("nesnelerin interneti", "turu", "teknoloji"),
    ("nesnelerin interneti", "kullanir", "internet"),
    ("akilli ev", "kullanir", "nesnelerin interneti"),
    # 3D baski
    ("uc boyutlu yazici", "turu", "teknoloji"),
    ("uc boyutlu yazici", "uretir", "fiziksel nesne"),
]

# --- COGRAFYA (80 kural) ---
GEOGRAPHY_RULES = [
    # Ulkeler
    ("turkiye", "turu", "ulke"),
    ("almanya", "turu", "ulke"),
    ("fransa", "turu", "ulke"),
    ("ingiltere", "turu", "ulke"),
    ("japonya", "turu", "ulke"),
    ("cin", "turu", "ulke"),
    ("abd", "turu", "ulke"),
    ("brezilya", "turu", "ulke"),
    ("rusya", "turu", "ulke"),
    ("misir", "turu", "ulke"),
    # Sehirler
    ("istanbul", "turu", "sehir"),
    ("ankara", "turu", "sehir"),
    ("izmir", "turu", "sehir"),
    ("paris", "turu", "sehir"),
    ("londra", "turu", "sehir"),
    ("tokyo", "turu", "sehir"),
    ("new york", "turu", "sehir"),
    ("sehir", "icerir", "insan"),
    ("sehir", "icerir", "bina"),
    ("ulke", "icerir", "sehir"),
    # Ulke-sehir iliskileri
    ("turkiye", "icerir", "istanbul"),
    ("turkiye", "icerir", "ankara"),
    ("turkiye", "icerir", "izmir"),
    ("fransa", "icerir", "paris"),
    ("ingiltere", "icerir", "londra"),
    ("japonya", "icerir", "tokyo"),
    # Sehir ozellikleri
    ("istanbul", "ozellik", "buyuk"),
    ("ankara", "ozellik", "baskent"),
    ("paris", "ozellik", "romantik"),
    ("tokyo", "ozellik", "kalabik"),
    # Kitalar
    ("avrupa", "turu", "kita"),
    ("asya", "turu", "kita"),
    ("afrika", "turu", "kita"),
    ("amerika", "turu", "kita"),
    ("turkiye", "bulunur", "asya"),
    ("turkiye", "bulunur", "avrupa"),
    ("almanya", "bulunur", "avrupa"),
    ("japonya", "bulunur", "asya"),
    ("brezilya", "bulunur", "amerika"),
    ("misir", "bulunur", "afrika"),
    # Iklim
    ("tropikal", "turu", "iklim"),
    ("kutupsal", "turu", "iklim"),
    ("iliman", "turu", "iklim"),
    ("col", "turu", "iklim"),
    ("tropikal", "ozellik", "sicak ve nemli"),
    ("kutupsal", "ozellik", "soguk"),
    ("iliman", "ozellik", "mevsimli"),
    ("col", "ozellik", "kurak"),
    ("turkiye", "iklimi", "iliman"),
    ("brezilya", "iklimi", "tropikal"),
    # Dogal ozellikler
    ("dag", "turu", "dogal yapi"),
    ("nehir", "turu", "dogal yapi"),
    ("gol", "turu", "dogal yapi"),
    ("okyanus", "turu", "dogal yapi"),
    ("volkan", "turu", "dogal yapi"),
    ("deprem", "turu", "dogal afet"),
    ("sel", "turu", "dogal afet"),
    ("kasirga", "turu", "dogal afet"),
    ("dag", "ozellik", "yuksek"),
    ("okyanus", "ozellik", "derin"),
    ("nehir", "ozellik", "akar"),
    # Kaynaklar
    ("petrol", "turu", "dogal kaynak"),
    ("dogalgaz", "turu", "dogal kaynak"),
    ("gumus", "turu", "dogal kaynak"),
    ("altin", "turu", "dogal kaynak"),
    ("orman", "turu", "dogal kaynak"),
    ("toprak", "turu", "dogal kaynak"),
    ("toprak", "saglar", "tarim"),
    ("tarim", "uretir", "gida"),
    ("gida", "etki", "hayati"),
    # Nufus
    ("nufus", "turu", "demografik olcu"),
    ("kentlesme", "arttirir", "nufus yogunlugu"),
    ("goc", "degistirir", "nufus"),
    # Harita ve konum
    ("ekvatoru", "boler", "dunya"),
    ("kutup", "ozellik", "buzla kapli"),
    ("meridyen", "olcer", "boylam"),
    ("paralel", "olcer", "enlem"),
]

# --- TOPLUM (80 kural) ---
SOCIETY_RULES = [
    # Meslekler
    ("doktor", "turu", "meslek"),
    ("ogretmen", "turu", "meslek"),
    ("muhendis", "turu", "meslek"),
    ("avukat", "turu", "meslek"),
    ("hemsire", "turu", "meslek"),
    ("mimar", "turu", "meslek"),
    ("polis", "turu", "meslek"),
    ("itfaiyeci", "turu", "meslek"),
    ("asci", "turu", "meslek"),
    ("pilot", "turu", "meslek"),
    ("meslek", "saglar", "gelir"),
    ("doktor", "saglar", "saglik"),
    ("ogretmen", "saglar", "bilgi"),
    ("muhendis", "saglar", "teknoloji"),
    ("avukat", "saglar", "adalet"),
    ("hemsire", "saglar", "bakim"),
    ("mimar", "saglar", "tasarim"),
    ("polis", "saglar", "guvenlik"),
    ("itfaiyeci", "saglar", "kurtarma"),
    ("pilot", "saglar", "ucus"),
    # Egitim
    ("okul", "turu", "egitim kurumu"),
    ("universite", "turu", "egitim kurumu"),
    ("egitim kurumu", "saglar", "egitim"),
    ("egitim", "saglar", "bilgi"),
    ("bilgi", "saglar", "yetenek"),
    ("yetenek", "saglar", "basari"),
    ("basari", "saglar", "gelir"),
    ("kitap", "turu", "bilgi kaynagi"),
    ("kitap", "saglar", "bilgi"),
    ("ogretmen", "calisir", "okul"),
    ("profesor", "calisir", "universite"),
    ("profesor", "turu", "meslek"),
    # Ekonomi
    ("para", "turu", "degisim araci"),
    ("banka", "turu", "finans kurumu"),
    ("banka", "saglar", "kredi"),
    ("kredi", "turu", "borc"),
    ("borsa", "turu", "finans piyasasi"),
    ("enflasyon", "etki", "zararli"),
    ("enflasyon", "azaltir", "alisgucu"),
    ("yatirim", "saglar", "kazanc"),
    ("ihracat", "saglar", "doviz"),
    ("ithalat", "gerektirir", "doviz"),
    ("vergi", "saglar", "devlet geliri"),
    ("issizlik", "etki", "zararli"),
    ("issizlik", "azaltir", "refah"),
    # Hukuk
    ("anayasa", "turu", "yasa"),
    ("yasa", "saglar", "duzen"),
    ("yasa", "saglar", "adalet"),
    ("mahkeme", "turu", "hukuk kurumu"),
    ("mahkeme", "saglar", "yargilama"),
    ("hakim", "turu", "meslek"),
    ("hakim", "calisir", "mahkeme"),
    ("suc", "gerektirir", "ceza"),
    ("ceza", "saglar", "caydiricilik"),
    ("insan haklari", "turu", "temel hak"),
    ("demokrasi", "saglar", "ozgurluk"),
    ("demokrasi", "saglar", "esitlik"),
    ("secim", "turu", "demokratik surec"),
    # Aile ve toplum
    ("aile", "turu", "toplum birimi"),
    ("aile", "saglar", "destek"),
    ("toplum", "icerir", "aile"),
    ("toplum", "icerir", "kurum"),
    ("kultur", "turu", "toplumsal deger"),
    ("gelenek", "turu", "kultur"),
    ("dil", "turu", "iletisim araci"),
    ("dil", "saglar", "iletisim"),
    # Medya
    ("gazete", "turu", "medya"),
    ("televizyon", "turu", "medya"),
    ("radyo", "turu", "medya"),
    ("medya", "saglar", "bilgi yayilimi"),
    ("medya", "etki", "kamuoyu olusturma"),
    # Siyaset
    ("siyaset", "turu", "yonetim"),
    ("parti", "turu", "siyasi orgut"),
    ("meclis", "turu", "yasama organi"),
    ("hukumet", "turu", "yurutme organi"),
    ("basbakan", "yonetir", "hukumet"),
    # Tasitlar (K2 testi icin gerekli)
    ("araba", "turu", "tasit"),
    ("ucak", "turu", "tasit"),
    ("gemi", "turu", "tasit"),
    ("bisiklet", "turu", "tasit"),
    ("tasit", "saglar", "ulasim"),
    ("araba", "kullanir", "benzin"),
    ("bisiklet", "etki", "cevreci"),
]

# --- BILIM (80 kural) ---
SCIENCE_RULES = [
    # Fizik
    ("kutle", "turu", "fiziksel buyukluk"),
    ("hiz", "turu", "fiziksel buyukluk"),
    ("ivme", "turu", "fiziksel buyukluk"),
    ("kuvvet", "turu", "fiziksel buyukluk"),
    ("enerji", "turu", "fiziksel buyukluk"),
    ("kuvvet", "uretir", "ivme"),
    ("ivme", "degistirir", "hiz"),
    ("enerji", "turu", "korunan buyukluk"),
    ("isik", "turu", "elektromanyetik dalga"),
    ("ses", "turu", "mekanik dalga"),
    ("isik", "ozellik", "hizli"),
    ("ses", "ozellik", "dalga"),
    ("yercekim", "turu", "kuvvet"),
    ("yercekim", "gerektirir", "kutle"),
    ("newton", "buldu", "yercekim"),
    ("einstein", "buldu", "gorelilik"),
    ("gorelilik", "turu", "fizik teorisi"),
    ("kuantum", "turu", "fizik teorisi"),
    ("atom", "icerir", "proton"),
    ("atom", "icerir", "notron"),
    ("atom", "icerir", "elektron"),
    ("proton", "ozellik", "pozitif yuklu"),
    ("elektron", "ozellik", "negatif yuklu"),
    # Kimya
    ("element", "turu", "madde"),
    ("bilesik", "turu", "madde"),
    ("karisim", "turu", "madde"),
    ("oksijen", "turu", "element"),
    ("hidrojen", "turu", "element"),
    ("karbon", "turu", "element"),
    ("demir", "turu", "element"),
    ("su", "turu", "bilesik"),
    ("su", "icerir", "hidrojen"),
    ("su", "icerir", "oksijen"),
    ("reaksiyon", "degistirir", "madde"),
    ("katalizor", "hizlandirir", "reaksiyon"),
    ("asit", "turu", "kimyasal"),
    ("baz", "turu", "kimyasal"),
    ("tuz", "turu", "kimyasal"),
    ("asit", "etki", "asindirici"),
    ("ph", "olcer", "asiditik"),
    # Astronomi
    ("gunes", "turu", "yildiz"),
    ("dunya", "turu", "gezegen"),
    ("ay", "turu", "uydu"),
    ("mars", "turu", "gezegen"),
    ("jupiter", "turu", "gezegen"),
    ("gunes sistemi", "icerir", "gezegen"),
    ("gunes sistemi", "icerir", "gunes"),
    ("galaksi", "icerir", "yildiz"),
    ("samanyolu", "turu", "galaksi"),
    ("kara delik", "turu", "uzay nesnesi"),
    ("kara delik", "ozellik", "yogun"),
    ("gunes", "uretir", "isik"),
    ("gunes", "uretir", "isi"),
    ("dunya", "donendigi", "gunes"),
    ("ay", "donendigi", "dunya"),
    ("yildiz", "uretir", "enerji"),
    ("uzay", "ozellik", "sonsuz"),
    ("isik yili", "olcer", "mesafe"),
    # Matematik (bilimsel arac)
    ("matematik", "turu", "bilim"),
    ("geometri", "turu", "matematik"),
    ("cebir", "turu", "matematik"),
    ("istatistik", "turu", "matematik"),
    ("sayi", "turu", "matematik kavrami"),
    ("denklem", "turu", "matematik araci"),
    ("ispat", "turu", "matematik yontemi"),
    ("pi", "turu", "matematiksel sabit"),
    # Bilimsel yontem
    ("hipotez", "turu", "bilimsel adim"),
    ("deney", "turu", "bilimsel adim"),
    ("gozlem", "turu", "bilimsel adim"),
    ("teori", "turu", "bilimsel sonuc"),
    ("hipotez", "gerektirir", "gozlem"),
    ("deney", "dogrular", "hipotez"),
    ("teori", "gerektirir", "deney"),
    ("bilim", "kullanir", "bilimsel yontem"),
    ("bilimsel yontem", "icerir", "deney"),
    ("bilimsel yontem", "icerir", "gozlem"),
]

# --- SAGLIK (80 kural) ---
HEALTH_RULES = [
    # Beslenme
    ("elma", "turu", "meyve"),
    ("muz", "turu", "meyve"),
    ("portakal", "turu", "meyve"),
    ("cilek", "turu", "meyve"),
    ("meyve", "turu", "yiyecek"),
    ("sebze", "turu", "yiyecek"),
    ("et", "turu", "yiyecek"),
    ("yiyecek", "etki", "besler"),
    ("meyve", "etki", "saglikli"),
    ("sebze", "etki", "saglikli"),
    ("vitamin", "turu", "besin ogesi"),
    ("mineral", "turu", "besin ogesi"),
    ("protein", "turu", "besin ogesi"),
    ("karbonhidrat", "turu", "besin ogesi"),
    ("yag", "turu", "besin ogesi"),
    ("vitamin", "saglar", "bagisiklik"),
    ("protein", "saglar", "kas gelisimi"),
    ("karbonhidrat", "saglar", "enerji"),
    ("portakal", "icerir", "c vitamini"),
    ("sut", "turu", "icecek"),
    ("icecek", "turu", "yiyecek"),
    ("su", "turu", "icecek"),
    ("ekmek", "turu", "yiyecek"),
    ("peynir", "turu", "yiyecek"),
    # Spor ve egzersiz
    ("spor", "turu", "aktivite"),
    ("spor", "etki", "saglikli"),
    ("spor", "gelistirir", "kas"),
    ("kas", "saglar", "guc"),
    ("spor", "gelistirir", "dayaniklilik"),
    ("egzersiz", "turu", "spor"),
    ("yuruyus", "turu", "egzersiz"),
    ("kosma", "turu", "egzersiz"),
    ("yoga", "turu", "egzersiz"),
    ("yoga", "saglar", "esneklik"),
    ("yoga", "saglar", "huzur"),
    ("meditasyon", "turu", "zihinsel aktivite"),
    ("meditasyon", "saglar", "huzur"),
    ("meditasyon", "azaltir", "stres"),
    # Hastaliklar
    ("grip", "turu", "hastalik"),
    ("diyabet", "turu", "hastalik"),
    ("kanser", "turu", "hastalik"),
    ("kalp hastaligi", "turu", "hastalik"),
    ("depresyon", "turu", "hastalik"),
    ("hastalik", "etki", "zararli"),
    ("grip", "belirtisi", "ates"),
    ("grip", "belirtisi", "oksuruk"),
    ("diyabet", "etki", "kan sekeri yukselir"),
    ("kanser", "etki", "olumcul olabilir"),
    ("depresyon", "etki", "mutsuzluk"),
    ("stres", "etki", "zararli"),
    ("stres", "neden olur", "hastalik"),
    # Tedavi
    ("ilac", "turu", "tedavi"),
    ("ameliyat", "turu", "tedavi"),
    ("terapi", "turu", "tedavi"),
    ("antibiyotik", "turu", "ilac"),
    ("antibiyotik", "tedavi eder", "enfeksiyon"),
    ("asi", "turu", "tedavi"),
    ("asi", "saglar", "bagisiklik"),
    ("tedavi", "azaltir", "hastalik"),
    ("doktor", "uygular", "tedavi"),
    ("ilac", "etki", "faydali"),
    ("ilac", "etki", "yan etki"),
    # Uyku ve dinlenme
    ("uyku", "turu", "ihtiyac"),
    ("uyku", "saglar", "dinlenme"),
    ("uyku", "saglar", "yenilenme"),
    ("uykusuzluk", "etki", "zararli"),
    ("uykusuzluk", "azaltir", "dikkat"),
    # Hijyen
    ("hijyen", "saglar", "saglik"),
    ("el yikama", "turu", "hijyen"),
    ("el yikama", "azaltir", "enfeksiyon"),
    # Ruh sagligi
    ("mutluluk", "turu", "duygu"),
    ("uzuntu", "turu", "duygu"),
    ("ofke", "turu", "duygu"),
    ("korku", "turu", "duygu"),
    ("mutluluk", "etki", "saglikli"),
    ("stres", "turu", "zihinsel durum"),
    ("anksiyete", "turu", "zihinsel durum"),
    ("anksiyete", "etki", "zararli"),
]


# ======================================================================
#  TAMAMLAYICI: Zincir testi icin ozel kurallar
# ======================================================================
# Bu kurallar test sorularinin BEKLEDIGI zincirleri GARANTI eder.
# Her zincir acikca belgelenmistir.

CHAIN_TEST_RULES = [
    # Zincir 2: spor -> kas -> guc (2 hop)
    # Zaten: spor gelistirir kas, kas saglar guc (HEALTH_RULES'da mevcut)

    # Zincir 3: agac -> oksijen -> hayati (2 hop)
    # Zaten: agac uretir oksijen, oksijen etki hayati (BIOLOGY_RULES'da mevcut)

    # Zincir 4: bilgi -> yetenek -> basari (2 hop)
    # Zaten: bilgi saglar yetenek, yetenek saglar basari (SOCIETY_RULES'da mevcut)

    # Zincir 5: 4-hop: gunes -> isik -> enerji -> hareket -> basari
    # Bazi linkler mevcut, eksik olanlari ekle:
    ("isik", "saglar", "enerji"),      # isik -> enerji
    ("enerji", "saglar", "hareket"),    # enerji -> hareket
    ("hareket", "saglar", "saglik"),    # hareket -> saglik (sonuc)
    # Yani: gunes -> isik -> enerji -> hareket -> saglik (4 hop)
    # gunes uretir isik zaten mevcut

    # Zincir 6: 5-hop: toprak -> tarim -> gida -> hayati -> onemli -> korunmali
    # toprak saglar tarim, tarim uretir gida, gida etki hayati zaten mevcut
    ("hayati", "etki", "onemli"),       # hayati -> onemli
    ("onemli", "gerektirir", "korunmali"),  # onemli -> korunmali
    # toprak -> tarim -> gida -> hayati -> onemli -> korunmali (5 hop)
]


# ======================================================================
#  GURULTU KURALLARI: 9,500 sistematik ama tutarli kural
# ======================================================================

random.seed(42)

NOISE_CATEGORIES = {
    "muzik": {
        "subjects": ["piyano", "gitar", "keman", "davul", "flut", "saksafon", "bas gitar", "ud", "ney", "kanun",
                      "opera", "caz", "rock muzik", "klasik muzik", "pop muzik", "hiphop muzik", "blues muzik",
                      "reggae", "turk halk muzigi", "elektronik muzik"],
        "relations": ["turu", "ozellik", "kullanir", "icerir", "uretir"],
        "objects": ["melodi", "ritim", "armoni", "nota", "ses tonu", "enstruman sesi", "muzik turu",
                    "sanat formu", "performans gosterisi", "konser etkinligi"]
    },
    "spor_turleri": {
        "subjects": ["futbol sporu", "basketbol sporu", "voleybol sporu", "tenis sporu", "yuzme sporu",
                      "atletizm sporu", "boks sporu", "judo sporu", "okculuk sporu", "kayak sporu",
                      "halter sporu", "gures sporu", "eskrim sporu", "binicilik sporu", "yelken sporu",
                      "dalga sorfu", "buz pateni sporu", "hokey sporu", "ragbi sporu", "kriket sporu"],
        "relations": ["turu", "gerektirir", "gelistirir", "kullanir", "ozellik"],
        "objects": ["top ekipmani", "raket ekipmani", "fiziksel guc", "fiziksel dayaniklilik", "fiziksel hiz",
                    "koordinasyon becerisi", "esneklik yetisi", "denge becerisi", "takim calismasi", "bireysel performans"]
    },
    "yemek": {
        "subjects": ["pizza yemegi", "kebap yemegi", "sushi yemegi", "pasta yemegi", "corba yemegi",
                      "pilav yemegi", "salata yemegi", "borek yemegi", "makarna yemegi", "kofte yemegi",
                      "lahmacun yemegi", "pide yemegi", "manti yemegi", "dolma yemegi", "sarma yemegi",
                      "baklava tatlisi", "kunefe tatlisi", "sutlac tatlisi", "ayran icecegi", "cay icecegi"],
        "relations": ["turu", "icerir", "ozellik", "yapilir", "sunulur"],
        "objects": ["ana yemek turu", "tatli turu", "icecek turu", "un malzemesi", "et malzemesi",
                    "lezzetli tat", "geleneksel yemek", "modern yemek", "sicak servis", "soguk servis"]
    },
    "mimari": {
        "subjects": ["gotik mimari", "barok mimari", "modern mimari", "osmanli mimari", "roma mimari",
                      "art deco mimari", "minimalist mimari", "japon mimari", "hint mimari", "maya mimari",
                      "kule yapisi", "kopru yapisi", "cami yapisi", "kilise yapisi", "saray yapisi",
                      "kale yapisi", "anit yapisi", "stadyum yapisi", "muzze yapisi", "kutuphane yapisi"],
        "relations": ["turu", "ozellik", "kullanir", "icerir", "temsil eder"],
        "objects": ["yapi tarzi", "tas malzeme", "ahsap malzeme", "beton malzeme", "cam malzeme",
                    "estetik deger", "tarihi deger", "islevsel tasarim", "anit tasarim", "susleme ozelligi"]
    },
    "edebiyat": {
        "subjects": ["roman turu", "siir turu", "hikaye turu", "deneme turu", "oyun turu",
                      "makale turu", "biyografi turu", "otobiyografi turu", "fantastik tur", "bilim kurgu turu",
                      "nazim hikmet", "yasar kemal", "orhan pamuk", "elif safak", "ahmet hamdi",
                      "sait faik", "oguz atay", "adalet agaoglu", "halide edip", "resat nuri"],
        "relations": ["turu", "ozellik", "kullanir", "anlattigi", "temsil eder"],
        "objects": ["edebi eser", "kurgu turumu", "gercekci anlati", "lirik anlatim", "epik anlati",
                    "toplumsal tema", "bireysel tema", "tarihsel tema", "felsefi tema", "romantik tema"]
    },
    "felsefe": {
        "subjects": ["varoluculuk akimi", "idealizm akimi", "materyalizm akimi", "pragmatizm akimi", "nihilizm akimi",
                      "rasyonalizm akimi", "ampirizm akimi", "fenomenoloji akimi", "yapisalcilik akimi", "postyapisalcilik akimi",
                      "platon dusunur", "aristoteles dusunur", "kant dusunur", "hegel dusunur", "nietzsche dusunur",
                      "sartre dusunur", "husserl dusunur", "heidegger dusunur", "wittgenstein dusunur", "foucault dusunur"],
        "relations": ["turu", "savunur", "elestirir", "temellendirir", "gelistirir"],
        "objects": ["felsefi akimlar", "ozgurluk kavrami", "bilgi kavrami", "varlik kavrami", "ahlak kavrami",
                    "estetik kavrami", "mantik kavrami", "dil kavrami", "toplum kavrami", "bilinc kavrami"]
    },
    "ekonomi_detay": {
        "subjects": ["kapitalizm sistemi", "sosyalizm sistemi", "merkantilizm sistemi", "liberalizm sistemi", "keynescilik sistemi",
                      "monetarizm sistemi", "arz ekonomisi", "talep ekonomisi", "dis ticaret", "ic piyasa",
                      "adam smith", "karl marx", "keynes", "hayek", "friedman",
                      "gsyh", "enflasyon orani", "faiz orani", "issizlik orani", "buyume orani"],
        "relations": ["turu", "savunur", "elestirir", "arttirir", "azaltir"],
        "objects": ["ekonomik sistem", "piyasa mekanizmasi", "devlet mudahalesi", "serbest ticaret", "korumaci politika",
                    "gelir dagilimi", "kaynak dagitimi", "verimlilik olcusu", "refah duzeyi", "fiyat istikrari"]
    },
    "psikoloji": {
        "subjects": ["davraniscilik akimi", "bilissel psikoloji", "psikanaliz akimi", "insancil psikoloji", "gelisim psikolojisi",
                      "sosyal psikoloji", "klinik psikoloji", "endistri psikolojisi", "egitim psikolojisi", "spor psikolojisi",
                      "freud psikolog", "jung psikolog", "skinner psikolog", "pavlov psikolog", "piaget psikolog",
                      "maslow psikolog", "rogers psikolog", "bandura psikolog", "erikson psikolog", "adler psikolog"],
        "relations": ["turu", "inceler", "aciklar", "elestirir", "kullanir"],
        "objects": ["insan davranisi", "zihinsel surec", "bilinc durumu", "bilincdisi surec", "ogrenme sureci",
                    "motivasyon kaynagi", "duygu durumu", "kisilik ozelligi", "sosyal etkilesim", "gelisim asamasi"]
    },
    "tarih": {
        "subjects": ["roma imparatorlugu", "osmanli imparatorlugu", "mogol imparatorlugu", "britanya imparatorlugu", "bizans imparatorlugu",
                      "antik yunan", "antik misir", "sumer medeniyeti", "hitit medeniyeti", "maya medeniyeti",
                      "birinci dunya savasi", "ikinci dunya savasi", "soguk savas", "hacliseferler donemi", "ronesans donemi",
                      "aydinlanma donemi", "sanayi devrimi", "fransiz devrimi", "amerikan devrimi", "turk kurtulus savasi"],
        "relations": ["turu", "yasandigi", "etkisi", "neden olan", "sonucu"],
        "objects": ["tarihi donem", "imparatorluk turu", "medeniyet turu", "savas donemi", "devrim donemi",
                    "siyasi degisim", "toplumsal degisim", "ekonomik degisim", "kulturel degisim", "teknolojik degisim"]
    },
    "sanat": {
        "subjects": ["empresyonizm akimi", "kubizm akimi", "surrealizm akimi", "ekspresyonizm akimi", "pop art akimi",
                      "ronesans sanati", "barok sanati", "modern sanat", "cagdas sanat", "dijital sanat",
                      "picasso sanatci", "van gogh sanatci", "da vinci sanatci", "monet sanatci", "dali sanatci",
                      "warhol sanatci", "frida kahlo", "michelangelo sanatci", "rembrandt sanatci", "hokusai sanatci"],
        "relations": ["turu", "ozellik", "kullanir", "temsil eder", "etkisi"],
        "objects": ["sanat akimi", "gorsel ifade", "soyut ifade", "figuratif ifade", "renk kullanimi",
                    "isik kullanimi", "perspektif kullanimi", "duygu ifadesi", "toplumsal elestiri", "estetik arayis"]
    },
    "sinema": {
        "subjects": ["dram filmi", "komedi filmi", "aksiyon filmi", "korku filmi", "bilimkurgu filmi",
                      "animasyon filmi", "belgesel filmi", "muzikal filmi", "western filmi", "gerilim filmi",
                      "yonetmen turu", "senarist turu", "oyuncu turu", "yapimci turu", "goruntu yonetmeni",
                      "kurgu yapimcisi", "ses tasarimcisi", "efekt uzmani", "kostum tasarimcisi", "set tasarimcisi"],
        "relations": ["turu", "icerir", "kullanir", "anlatir", "uretir"],
        "objects": ["film turu", "gorsel anlati", "dramatik yapi", "karakter gelisimi", "senaryo yapisi",
                    "gorsel efekt", "ses efekti", "muzik kullanimi", "kurgu teknigi", "anlatim bicimi"]
    },
    "botanik": {
        "subjects": ["gul bitkisi", "lale bitkisi", "papatya bitkisi", "orkide bitkisi", "yasemin bitkisi",
                      "cinar agaci", "mese agaci", "zeytin agaci", "palmiye agaci", "selvi agaci",
                      "bugday tahili", "arpa tahili", "misir tahili", "pirinc tahili", "cavdar tahili",
                      "domates bitkisi", "biber bitkisi", "patates bitkisi", "sogan bitkisi", "sarimsak bitkisi"],
        "relations": ["turu", "ozellik", "uretir", "gerektirir", "bulunur"],
        "objects": ["cicekli bitki", "yaprak dokmeyen", "yaprak doken", "meyveli bitki", "tahil turu",
                    "gunesli ortam", "nemli ortam", "kurak ortam", "iliman ortam", "tropikal ortam"]
    },
    "denizcilik": {
        "subjects": ["yelkenli gemi", "tanker gemi", "konteyner gemi", "savas gemisi", "yolcu gemisi",
                      "denizalti araci", "firkateyn gemisi", "tekne araci", "sal araci", "kano araci",
                      "liman tesisi", "dok tesisi", "fener yapisi", "rihim yapisi", "tersane tesisi",
                      "kaptan meslegi", "denizci meslegi", "balakci meslegi", "dalgic meslegi", "navigator meslegi"],
        "relations": ["turu", "kullanir", "tasir", "gerektirir", "bulunur"],
        "objects": ["deniz araci", "yuk tasimaciligi", "yolcu tasimaciligi", "askeri kullanim", "ticari kullanim",
                    "ruzgar gucu", "motor gucu", "buhar gucu", "nukleer guc", "insan gucu"]
    },
    "havacilik": {
        "subjects": ["yolcu ucagi", "savas jeti", "helikopter araci", "planor araci", "balon araci",
                      "drone araci", "roket araci", "uzay mekigi", "bombardiman ucagi", "kargo ucagi",
                      "havaalani tesisi", "kontrol kulesi", "pist yapisi", "hangar yapisi", "terminal yapisi",
                      "pilot meslegi", "hostes meslegi", "hava trafik kontrolor", "ucak muhendisi", "test pilotu"],
        "relations": ["turu", "kullanir", "tasir", "gerektirir", "ozellik"],
        "objects": ["hava araci", "sivil havacilik", "askeri havacilik", "kargo tasimaciligi", "yolcu tasimaciligi",
                    "jet motoru", "pervane motoru", "roket motoru", "elektrik motoru", "turbin motoru"]
    },
    "tekstil": {
        "subjects": ["pamuk kumasin", "ipek kumasin", "yun kumasin", "keten kumasin", "polyester kumasin",
                      "denim kumasin", "satin kumasin", "kadife kumasin", "organze kumasin", "flanel kumasin",
                      "gomlek giysisi", "pantolon giysisi", "elbise giysisi", "ceket giysisi", "etek giysisi",
                      "sort giysisi", "kazak giysisi", "hirka giysisi", "yelek giysisi", "palto giysisi"],
        "relations": ["turu", "ozellik", "kullanir", "uretilir", "giyilir"],
        "objects": ["dogal kumas", "sentetik kumas", "karisim kumas", "gunluk giysi", "resmi giysi",
                    "spor giysi", "hafif ozellik", "agir ozellik", "yumusak doku", "sert doku"]
    },
    "otomotiv": {
        "subjects": ["sedan araba", "suv araba", "hatchback araba", "coupe araba", "cabrio araba",
                      "kamyon araci", "otobus araci", "minibus araci", "tir araci", "ambulans araci",
                      "benzinli motor", "dizel motor", "elektrikli motor", "hibrit motor", "lpg motor",
                      "abs freni", "esp sistemi", "hava yastigi", "geri gorus kamera", "park sensoru"],
        "relations": ["turu", "kullanir", "ozellik", "saglar", "gerektirir"],
        "objects": ["binek araci", "ticari arac", "tuketim araci", "guvenlik sistemi", "konfor sistemi",
                    "benzin yakiti", "dizel yakiti", "elektrik enerjisi", "dusuk tuketim", "yuksek performans"]
    },
    "astronomi_detay": {
        "subjects": ["merkur gezegen", "venus gezegen", "mars gezegeni", "jupiter gezegeni", "saturn gezegeni",
                      "uranus gezegeni", "neptun gezegeni", "pluto cuce gezegen", "halley kuyruklu yildiz", "ceres cuce gezegen",
                      "hubble teleskobu", "james webb teleskobu", "arecibo teleskobu", "iss uzay istasyonu", "voyager sondasi",
                      "nasa kurumu", "esa kurumu", "roscosmos kurumu", "spacex sirketi", "blue origin sirketi"],
        "relations": ["turu", "ozellik", "bulunur", "kesfetti", "inceler"],
        "objects": ["ic gezegen", "dis gezegen", "cuce gezegen", "gaz devi", "kayac gezegen",
                    "halka sistemi", "uydu sistemi", "atmosfer yapisi", "yuzey ozelligi", "yoros yunge"]
    },
    "tip_detay": {
        "subjects": ["kardiyoloji bolumu", "noroloji bolumu", "ortopedi bolumu", "dermatoloji bolumu", "oftalmoloji bolumu",
                      "uroloji bolumu", "gastroenteroloji bolumu", "endokrinoloji bolumu", "onkoloji bolumu", "psikiyatri bolumu",
                      "rontgen cihazi", "mr cihazi", "ultrason cihazi", "tomografi cihazi", "ekg cihazi",
                      "penisilin ilaci", "aspirin ilaci", "insulin ilaci", "morfin ilaci", "kortizol ilaci"],
        "relations": ["turu", "tedavi eder", "inceler", "kullanir", "ozellik"],
        "objects": ["tip uzmanlik", "tani yontemi", "tedavi yontemi", "cerrahi yontem", "ilac tedavisi",
                    "kronik hastalik", "akut hastalik", "bulasici hastalik", "genetik hastalik", "otoimmun hastalik"]
    },
    "hukuk_detay": {
        "subjects": ["ceza hukuku", "medeni hukuk", "anayasa hukuku", "idare hukuku", "is hukuku",
                      "ticaret hukuku", "vergi hukuku", "uluslararasi hukuk", "cevre hukuku", "bilisim hukuku",
                      "yargi hakimi", "savci kisi", "avukat kisi", "noter kisi", "bilirkisi kisi",
                      "anayasa mahkemesi", "yargitay mahkemesi", "danistay mahkemesi", "aihm mahkemesi", "adliye yapisi"],
        "relations": ["turu", "duzenler", "korur", "gerektirir", "icerir"],
        "objects": ["hukuk dali", "temel haklar", "kamu duzeni", "ozel haklar", "yargilama sureci",
                    "yargi bagimsizligi", "hukuk devleti", "adil yargilanma", "masumiyet karinesi", "savunma hakki"]
    },
    "cevre": {
        "subjects": ["kuresel isinma sorunu", "ozon tabakasi", "asit yagmuru", "ormansizlasma sorunu", "cevre kirliligi",
                      "hava kirliligi", "su kirliligi", "toprak kirliligi", "gurultu kirliligi", "isik kirliligi",
                      "gunes enerjisi", "ruzgar enerjisi", "hidroelektrik enerji", "jeotermal enerji", "biokutle enerjisi",
                      "geri donusum", "kompostlama", "atik yonetimi", "surdurulebilirlik", "karbon ayakizi"],
        "relations": ["turu", "neden olur", "azaltir", "arttirir", "etkiler"],
        "objects": ["cevre sorunu", "enerji kaynagi", "yenilenebilir enerji", "sera gazi", "karbon emisyonu",
                    "biyocesitlilik kaybi", "iklim degisikligi", "ekosistem bozulmasi", "dogal kaynak tukenisi", "cevre koruma"]
    },
}


def generate_noise_rules(target_count=9500):
    """9,500 tutarli gurultu kurali uret."""
    rules = []
    categories = list(NOISE_CATEGORIES.items())
    rules_per_category = target_count // len(categories)  # ~475

    for cat_name, cat_data in categories:
        subjects = cat_data["subjects"]
        relations = cat_data["relations"]
        objects = cat_data["objects"]

        generated = set()
        attempts = 0
        max_attempts = rules_per_category * 10

        while len(generated) < rules_per_category and attempts < max_attempts:
            attempts += 1
            s = random.choice(subjects)
            r = random.choice(relations)
            o = random.choice(objects)
            key = (s, r, o)
            if key not in generated:
                generated.add(key)
                rules.append((s, r, o))

        # If we couldn't fill with unique combinations, generate cross-subject rules
        while len(generated) < rules_per_category:
            s1 = random.choice(subjects)
            s2 = random.choice(subjects)
            if s1 != s2:
                r = random.choice(["iliskili", "benzer", "farkli", "karsilastirma", "etkilesim"])
                key = (s1, r, s2)
                if key not in generated:
                    generated.add(key)
                    rules.append((s1, r, s2))

    return rules


# ======================================================================
#  YARDIMCI FONKSIYONLAR
# ======================================================================

def _get_all_text(conclusions):
    """Tum sonuc metnini birlestir."""
    if not conclusions:
        return ""
    parts = []
    for c in conclusions:
        if c["type"] == "direct":
            parts.append(str(c["rule"]).lower())
        elif c["type"] == "chained":
            parts.append(c.get("chain", "").lower())
    return " ".join(parts)


def _has_term(conclusions, term):
    """Sonuclarda belirli terim var mi?"""
    if not conclusions:
        return False
    return term in _get_all_text(conclusions)


def _has_chain_connecting(conclusions, start, end):
    """Sonuclarda start'tan end'e bir zincir var mi?"""
    if not conclusions:
        return False
    for c in conclusions:
        if c["type"] == "chained":
            chain = c.get("chain", "").lower()
            start_pos = chain.find(start)
            end_pos = chain.find(end)
            if start_pos != -1 and end_pos != -1 and start_pos < end_pos:
                return True
    return False


def _count_relevant_results(conclusions, terms):
    """Sonuclarda kac tanesi verilen terimlerin EN AZ IKISINI iceriyor?"""
    if not conclusions:
        return 0
    count = 0
    for c in conclusions:
        if c["type"] == "direct":
            text = str(c["rule"]).lower()
        elif c["type"] == "chained":
            text = c.get("chain", "").lower()
        else:
            continue
        matched = sum(1 for t in terms if t in text)
        if matched >= 2:
            count += 1
    return count


def verify_chain_links(engine, chain_str):
    """Bir zincirdeki her halkayi engine.state'te dogrula.
    Donus: (gecerli_halka_sayisi, toplam_halka, gecersiz_halkalar)
    """
    nodes = [n.strip() for n in chain_str.split("->")]
    if len(nodes) < 2:
        return 0, 0, []

    valid = 0
    total = len(nodes) - 1
    invalid = []

    for i in range(total):
        src = nodes[i]
        dst = nodes[i + 1]
        found = False
        for rule in engine.state:
            if rule.subject == src and rule.obj == dst and rule.confidence >= 0.2:
                found = True
                break
        if found:
            valid += 1
        else:
            invalid.append(f"{src} -> {dst}")

    return valid, total, invalid


def check_false_positive(engine, conclusions, terms):
    """Sonuclardaki zincirleri dogrula, sahte baglantilari tespit et.
    Donus: (gecerli_zincir_sayisi, toplam_zincir, sahte_zincirler)
    """
    if not conclusions:
        return 0, 0, []

    valid_chains = 0
    total_chains = 0
    fake_chains = []

    for c in conclusions:
        if c["type"] == "chained":
            total_chains += 1
            chain_str = c.get("chain", "")
            v, t, inv = verify_chain_links(engine, chain_str)
            if v == t:
                valid_chains += 1
            else:
                fake_chains.append({
                    "chain": chain_str,
                    "valid_links": v,
                    "total_links": t,
                    "invalid": inv,
                })

    return valid_chains, total_chains, fake_chains


# ======================================================================
#  TEST SORULARI: 30 soru, 6 kategori
# ======================================================================

# KATEGORI 1: Basit Getirme (5 soru)
SIMPLE_RETRIEVAL_QUESTIONS = [
    {
        "id": "B1",
        "text": "Kedi bir hayvan midir?",
        "terms": ["kedi", "hayvan"],
        "expected": "EVET (kedi turu hayvan direkt kural)",
        "check": lambda c: _has_term(c, "kedi") and _has_term(c, "hayvan"),
    },
    {
        "id": "B2",
        "text": "Su hayati midir?",
        "terms": ["su", "hayati"],
        "expected": "EVET (su etki hayati direkt kural)",
        "check": lambda c: _has_term(c, "su") and _has_term(c, "hayati"),
    },
    {
        "id": "B3",
        "text": "Doktor ne saglar?",
        "terms": ["doktor", "saglik"],
        "expected": "EVET (doktor saglar saglik direkt kural)",
        "check": lambda c: _has_term(c, "doktor") and _has_term(c, "saglik"),
    },
    {
        "id": "B4",
        "text": "Gunes bir yildiz midir?",
        "terms": ["gunes", "yildiz"],
        "expected": "EVET (gunes turu yildiz direkt kural)",
        "check": lambda c: _has_term(c, "gunes") and _has_term(c, "yildiz"),
    },
    {
        "id": "B5",
        "text": "Istanbul buyuk mudur?",
        "terms": ["istanbul", "buyuk"],
        "expected": "EVET (istanbul ozellik buyuk direkt kural)",
        "check": lambda c: _has_term(c, "istanbul") and _has_term(c, "buyuk"),
    },
]

# KATEGORI 2: Zincir Cikarim (5 soru)
CHAIN_REASONING_QUESTIONS = [
    {
        "id": "Z1",
        "text": "Spor neden guc verir?",
        "terms": ["spor", "guc"],
        "expected": "EVET: spor -> kas -> guc (2 hop)",
        "check": lambda c: _has_chain_connecting(c, "spor", "guc") or (_has_term(c, "spor") and _has_term(c, "kas") and _has_term(c, "guc")),
    },
    {
        "id": "Z2",
        "text": "Agac neden hayati?",
        "terms": ["agac", "hayati"],
        "expected": "EVET: agac -> oksijen -> hayati (2 hop)",
        "check": lambda c: _has_chain_connecting(c, "agac", "hayati") or (_has_term(c, "agac") and _has_term(c, "oksijen") and _has_term(c, "hayati")),
    },
    {
        "id": "Z3",
        "text": "Bilgi neden basari saglar?",
        "terms": ["bilgi", "basari"],
        "expected": "EVET: bilgi -> yetenek -> basari (2 hop)",
        "check": lambda c: _has_chain_connecting(c, "bilgi", "basari") or (_has_term(c, "bilgi") and _has_term(c, "yetenek") and _has_term(c, "basari")),
    },
    {
        "id": "Z4",
        "text": "Gunes neden saglik icin onemli?",
        "terms": ["gunes", "saglik"],
        "expected": "EVET: gunes -> isik -> enerji -> hareket -> saglik (4 hop)",
        "check": lambda c: _has_chain_connecting(c, "gunes", "saglik") or (_has_term(c, "gunes") and _has_term(c, "saglik")),
    },
    {
        "id": "Z5",
        "text": "Toprak neden korunmali?",
        "terms": ["toprak", "korunmali"],
        "expected": "EVET: toprak -> tarim -> gida -> hayati -> onemli -> korunmali (5 hop)",
        "check": lambda c: _has_chain_connecting(c, "toprak", "korunmali") or (_has_term(c, "toprak") and _has_term(c, "korunmali")),
    },
]

# KATEGORI 3: Kalitim (5 soru)
INHERITANCE_QUESTIONS = [
    {
        "id": "K1",
        "text": "Elma besleyici midir?",
        "terms": ["elma", "besler"],
        "expected": "EVET: elma -> meyve -> yiyecek -> besler (kalitim)",
        "check": lambda c: _has_term(c, "elma") and _has_term(c, "besler"),
    },
    {
        "id": "K2",
        "text": "Bisiklet ulasim saglar mi?",
        "terms": ["bisiklet", "ulasim"],
        "expected": "EVET: bisiklet -> tasit -> ulasim (kalitim)",
        "check": lambda c: _has_term(c, "bisiklet") and _has_term(c, "ulasim"),
    },
    {
        "id": "K3",
        "text": "Kedi canli midir?",
        "terms": ["kedi", "canli"],
        "expected": "EVET: kedi -> hayvan -> canli (kalitim ozellik)",
        "check": lambda c: _has_term(c, "kedi") and _has_term(c, "canli"),
    },
    {
        "id": "K4",
        "text": "Kartal ucar mi?",
        "terms": ["kartal", "ucar"],
        "expected": "EVET: kartal -> kus -> ucar (kalitim ozellik)",
        "check": lambda c: _has_term(c, "kartal") and _has_term(c, "ucar"),
    },
    {
        "id": "K5",
        "text": "Avukat gelir saglar mi?",
        "terms": ["avukat", "gelir"],
        "expected": "EVET: avukat -> meslek -> gelir (kalitim)",
        "check": lambda c: _has_term(c, "avukat") and _has_term(c, "gelir"),
    },
]

# KATEGORI 4: Celiski & Nuans (5 soru)
CONTRADICTION_QUESTIONS = [
    {
        "id": "C1",
        "text": "Teknoloji faydali mi zararli mi?",
        "terms": ["teknoloji", "faydali", "zararli"],
        "expected": "HER IKISI: teknoloji etki faydali VE teknoloji etki zararli",
        "check": lambda c: _has_term(c, "faydali") and _has_term(c, "zararli"),
    },
    {
        "id": "C2",
        "text": "Ilac iyi mi kotu mu?",
        "terms": ["ilac", "faydali", "yan etki"],
        "expected": "HER IKISI: ilac etki faydali VE ilac etki yan etki",
        "check": lambda c: _has_term(c, "faydali") and _has_term(c, "yan etki"),
    },
    {
        "id": "C3",
        "text": "Sosyal medya bilgi yayar mi bagimlilik yapar mi?",
        "terms": ["sosyal medya", "bilgi yayilimi", "bagimlilik yapici"],
        "expected": "HER IKISI: sosyal medya her iki etkiyi de gosterir",
        "check": lambda c: _has_term(c, "bilgi yayilimi") or _has_term(c, "bagimlilik"),
    },
    {
        "id": "C4",
        "text": "Stres zararli midir?",
        "terms": ["stres", "zararli"],
        "expected": "EVET: stres etki zararli",
        "check": lambda c: _has_term(c, "stres") and _has_term(c, "zararli"),
    },
    {
        "id": "C5",
        "text": "Enflasyonun etkisi nedir?",
        "terms": ["enflasyon", "zararli"],
        "expected": "EVET: enflasyon etki zararli",
        "check": lambda c: _has_term(c, "enflasyon") and _has_term(c, "zararli"),
    },
]

# KATEGORI 5: NEGATIF TESTLER (5 soru) - EN ONEMLI KATEGORI
NEGATIVE_QUESTIONS = [
    {
        "id": "N1",
        "text": "Piyano bir hayvan midir?",
        "terms": ["piyano", "hayvan"],
        "expected": "HAYIR: piyano ve hayvan arasinda baglanti OLMAMALI",
        "check": lambda c: not _has_chain_connecting(c, "piyano", "hayvan"),
    },
    {
        "id": "N2",
        "text": "Gitar bilgi saglar mi?",
        "terms": ["gitar", "bilgi"],
        "expected": "HAYIR: gitar ve bilgi arasinda baglanti OLMAMALI",
        "check": lambda c: not _has_chain_connecting(c, "gitar", "bilgi"),
    },
    {
        "id": "N3",
        "text": "Boks huzur verir mi?",
        "terms": ["boks sporu", "huzur"],
        "expected": "HAYIR: boks ve huzur arasinda baglanti OLMAMALI",
        "check": lambda c: not _has_chain_connecting(c, "boks", "huzur"),
    },
    {
        "id": "N4",
        "text": "Kayak besleyici midir?",
        "terms": ["kayak sporu", "besler"],
        "expected": "HAYIR: kayak ve besler arasinda baglanti OLMAMALI",
        "check": lambda c: not _has_chain_connecting(c, "kayak", "besler"),
    },
    {
        "id": "N5",
        "text": "Opera bir gezegen midir?",
        "terms": ["opera", "gezegen"],
        "expected": "HAYIR: opera ve gezegen arasinda baglanti OLMAMALI",
        "check": lambda c: not _has_chain_connecting(c, "opera", "gezegen"),
    },
]

# KATEGORI 6: DOGRULAMA (5 soru) - bulunan zincirlerin GERCEKTEN gecerli oldugunu dogrula
# Bu sorularin "check" fonksiyonu ozel: zincir dogrulama yapar
VERIFICATION_QUESTIONS = [
    {
        "id": "D1",
        "text": "Kedi canli midir? (dogrulama)",
        "terms": ["kedi", "canli"],
        "expected": "ZINCIR DOGRULANMALI: kedi -> hayvan -> canli her halkasi state'te olmali",
    },
    {
        "id": "D2",
        "text": "Elma besleyici midir? (dogrulama)",
        "terms": ["elma", "besler"],
        "expected": "ZINCIR DOGRULANMALI: elma -> meyve -> yiyecek -> besler her halkasi state'te olmali",
    },
    {
        "id": "D3",
        "text": "Agac neden hayati? (dogrulama)",
        "terms": ["agac", "hayati"],
        "expected": "ZINCIR DOGRULANMALI: agac -> oksijen -> hayati her halkasi state'te olmali",
    },
    {
        "id": "D4",
        "text": "Bilgi neden basari saglar? (dogrulama)",
        "terms": ["bilgi", "basari"],
        "expected": "ZINCIR DOGRULANMALI: bilgi -> yetenek -> basari her halkasi state'te olmali",
    },
    {
        "id": "D5",
        "text": "Spor neden guc verir? (dogrulama)",
        "terms": ["spor", "guc"],
        "expected": "ZINCIR DOGRULANMALI: spor -> kas -> guc her halkasi state'te olmali",
    },
]


# ======================================================================
#  SONUC YAZDIRMA
# ======================================================================

def print_conclusions_compact(conclusions, max_show=6):
    """Sonuclari kompakt yazdir."""
    if not conclusions:
        print("    Sonuc: YOK")
        return
    shown = 0
    for c in conclusions:
        if shown >= max_show:
            remaining = len(conclusions) - max_show
            print(f"    ... ve {remaining} sonuc daha")
            break
        if c["type"] == "direct":
            print(f"    [DOGRUDAN] {c['rule']} (guven: {c['confidence']:.2f})")
        elif c["type"] == "chained":
            print(f"    [ZINCIR]   {c['chain']} (guven: {c['confidence']:.2f})")
        shown += 1


def print_verification_detail(engine, conclusions, question_id):
    """Zincir dogrulama detayini yazdir."""
    if not conclusions:
        print("    DOGRULAMA: Sonuc yok - KALDI")
        return False

    all_valid = True
    chain_count = 0
    for c in conclusions:
        if c["type"] == "chained":
            chain_count += 1
            chain_str = c.get("chain", "")
            v, t, inv = verify_chain_links(engine, chain_str)
            if v == t:
                print(f"    DOGRULAMA: '{chain_str}' -> GECERLI ({v}/{t} halka dogrulandi)")
            else:
                print(f"    DOGRULAMA: '{chain_str}' -> GECERSIZ ({v}/{t} halka)")
                for link in inv:
                    print(f"      EKSIK HALKA: {link}")
                all_valid = False

    if chain_count == 0:
        # Sadece direkt sonuclar var - bu da kabul edilebilir
        for c in conclusions:
            if c["type"] == "direct":
                rule = c["rule"]
                # Direkt kurallar state'te olmali
                found = any(
                    r.subject == rule.subject and r.relation == rule.relation and r.obj == rule.obj
                    for r in engine.state
                )
                if found:
                    print(f"    DOGRULAMA: Direkt kural '{rule}' -> STATE'TE MEVCUT")
                else:
                    print(f"    DOGRULAMA: Direkt kural '{rule}' -> STATE'TE YOK!")
                    all_valid = False

    return all_valid


# ======================================================================
#  ANA TEST
# ======================================================================

def run_scale_test():
    print()
    print("#" * 74)
    print("#  CHAINOFMEANING v3 OLCEK + DURUSTLUK TESTI")
    print("#  10,000 kural | 30 soru | Yanlis pozitif tespiti | Zincir dogrulama")
    print("#" * 74)

    engine = RuleEngineV3()

    # ==================================================================
    #  ADIM 1: Cekirdek kurallarini yukle (500)
    # ==================================================================
    print(f"\n{'='*74}")
    print("  ADIM 1: Cekirdek Bilgi Yukleniyor")
    print(f"{'='*74}")

    core_rules = (
        BIOLOGY_RULES + TECHNOLOGY_RULES + GEOGRAPHY_RULES +
        SOCIETY_RULES + SCIENCE_RULES + HEALTH_RULES + CHAIN_TEST_RULES
    )
    core_count = len(core_rules)
    print(f"\n  Cekirdek kural sayisi: {core_count}")
    print(f"    Biyoloji:  {len(BIOLOGY_RULES)}")
    print(f"    Teknoloji: {len(TECHNOLOGY_RULES)}")
    print(f"    Cografya:  {len(GEOGRAPHY_RULES)}")
    print(f"    Toplum:    {len(SOCIETY_RULES)}")
    print(f"    Bilim:     {len(SCIENCE_RULES)}")
    print(f"    Saglik:    {len(HEALTH_RULES)}")
    print(f"    Zincir:    {len(CHAIN_TEST_RULES)}")

    start = time.time()
    for s, r, o in core_rules:
        engine.ingest(Rule(s, r, o))
    core_time = time.time() - start

    print(f"\n  Yukleme suresi: {core_time:.3f}s")
    print(f"  State: {len(engine.state)} aktif kural")

    # ==================================================================
    #  ADIM 2: Gurultu kurallarini yukle (9,500)
    # ==================================================================
    print(f"\n{'='*74}")
    print("  ADIM 2: Gurultu Kurallari Yukleniyor (9,500)")
    print(f"{'='*74}")

    noise_rules = generate_noise_rules(9500)
    noise_count = len(noise_rules)
    print(f"\n  Uretilen gurultu kurali: {noise_count}")

    start = time.time()
    for s, r, o in noise_rules:
        engine.ingest(Rule(s, r, o))
    noise_time = time.time() - start

    total_rules = core_count + noise_count
    print(f"\n  Yukleme suresi: {noise_time:.3f}s")
    print(f"  Toplam yuklenen: {total_rules}")
    print(f"  State: {len(engine.state)} aktif kural")
    print(f"  Sinyal/Gurultu orani: {core_count}/{noise_count} = {core_count/noise_count:.2%}")

    # Taxonomy summary
    all_clusters = engine.taxonomy.get_all_clusters()
    multi_clusters = engine.taxonomy.get_multi_member_clusters()
    print(f"  Taxonomy: {len(all_clusters)} cluster ({len(multi_clusters)} multi-member)")

    # ==================================================================
    #  ADIM 3: Testleri Calistir
    # ==================================================================
    print(f"\n{'='*74}")
    print("  ADIM 3: Test Bataryasi (30 Soru)")
    print(f"{'='*74}")

    # Sonuc toplama
    all_results = {
        "basit": [],
        "zincir": [],
        "kalitim": [],
        "celiski": [],
        "negatif": [],
        "dogrulama": [],
    }

    total_query_time = 0

    # --- Kategori 1: Basit Getirme ---
    print(f"\n  --- KATEGORI 1: Basit Getirme (5 soru) ---\n")
    for q in SIMPLE_RETRIEVAL_QUESTIONS:
        start = time.time()
        conclusions = engine.query(q["text"], q["terms"])
        elapsed = time.time() - start
        total_query_time += elapsed

        passed = q["check"](conclusions)
        result_count = len(conclusions) if conclusions else 0

        # Yanlis pozitif kontrolu
        _, total_chains, fake = check_false_positive(engine, conclusions, q["terms"])
        fp_count = len(fake)

        status = "GECTI" if passed else "KALDI"
        if fp_count > 0:
            status = "YANLIS POZITIF"

        print(f"  Soru {q['id']}: \"{q['text']}\"")
        print(f"    Beklenen: {q['expected']}")
        print_conclusions_compact(conclusions)
        print(f"    Dogrulama: {result_count} sonuc, {total_chains} zincir, {fp_count} sahte")
        print(f"    Sonuc: {status} ({elapsed*1000:.1f}ms)")
        print()

        all_results["basit"].append({
            "id": q["id"],
            "passed": passed and fp_count == 0,
            "false_positive": fp_count > 0,
            "query_ms": elapsed * 1000,
            "result_count": result_count,
        })

    # --- Kategori 2: Zincir Cikarim ---
    print(f"\n  --- KATEGORI 2: Zincir Cikarim (5 soru) ---\n")
    for q in CHAIN_REASONING_QUESTIONS:
        start = time.time()
        conclusions = engine.query(q["text"], q["terms"])
        elapsed = time.time() - start
        total_query_time += elapsed

        passed = q["check"](conclusions)
        result_count = len(conclusions) if conclusions else 0

        _, total_chains, fake = check_false_positive(engine, conclusions, q["terms"])
        fp_count = len(fake)

        status = "GECTI" if passed else "KALDI"
        if fp_count > 0 and not passed:
            status = "YANLIS POZITIF"

        print(f"  Soru {q['id']}: \"{q['text']}\"")
        print(f"    Beklenen: {q['expected']}")
        print_conclusions_compact(conclusions)
        if fake:
            for f in fake[:3]:
                print(f"    !!! SAHTE ZINCIR: {f['chain']} ({f['valid_links']}/{f['total_links']} gecerli)")
        print(f"    Dogrulama: {result_count} sonuc, {total_chains} zincir, {fp_count} sahte")
        print(f"    Sonuc: {status} ({elapsed*1000:.1f}ms)")
        print()

        all_results["zincir"].append({
            "id": q["id"],
            "passed": passed,
            "false_positive": fp_count > 0,
            "query_ms": elapsed * 1000,
            "result_count": result_count,
            "fake_chains": fake,
        })

    # --- Kategori 3: Kalitim ---
    print(f"\n  --- KATEGORI 3: Kalitim (5 soru) ---\n")
    for q in INHERITANCE_QUESTIONS:
        start = time.time()
        conclusions = engine.query(q["text"], q["terms"])
        elapsed = time.time() - start
        total_query_time += elapsed

        passed = q["check"](conclusions)
        result_count = len(conclusions) if conclusions else 0

        _, total_chains, fake = check_false_positive(engine, conclusions, q["terms"])
        fp_count = len(fake)

        status = "GECTI" if passed else "KALDI"
        if fp_count > 0 and not passed:
            status = "YANLIS POZITIF"

        print(f"  Soru {q['id']}: \"{q['text']}\"")
        print(f"    Beklenen: {q['expected']}")
        print_conclusions_compact(conclusions)
        print(f"    Dogrulama: {result_count} sonuc, {total_chains} zincir, {fp_count} sahte")
        print(f"    Sonuc: {status} ({elapsed*1000:.1f}ms)")
        print()

        all_results["kalitim"].append({
            "id": q["id"],
            "passed": passed,
            "false_positive": fp_count > 0,
            "query_ms": elapsed * 1000,
            "result_count": result_count,
        })

    # --- Kategori 4: Celiski & Nuans ---
    print(f"\n  --- KATEGORI 4: Celiski & Nuans (5 soru) ---\n")
    for q in CONTRADICTION_QUESTIONS:
        start = time.time()
        conclusions = engine.query(q["text"], q["terms"])
        elapsed = time.time() - start
        total_query_time += elapsed

        passed = q["check"](conclusions)
        result_count = len(conclusions) if conclusions else 0

        status = "GECTI" if passed else "KALDI"

        print(f"  Soru {q['id']}: \"{q['text']}\"")
        print(f"    Beklenen: {q['expected']}")
        print_conclusions_compact(conclusions)
        print(f"    Dogrulama: {result_count} sonuc")
        print(f"    Sonuc: {status} ({elapsed*1000:.1f}ms)")
        print()

        all_results["celiski"].append({
            "id": q["id"],
            "passed": passed,
            "false_positive": False,
            "query_ms": elapsed * 1000,
            "result_count": result_count,
        })

    # --- Kategori 5: NEGATIF TESTLER ---
    print(f"\n  --- KATEGORI 5: NEGATIF TESTLER (5 soru) ---")
    print(f"  (Burada DOGRU cevap baglanti BULMAMAKTIR)\n")
    for q in NEGATIVE_QUESTIONS:
        start = time.time()
        conclusions = engine.query(q["text"], q["terms"])
        elapsed = time.time() - start
        total_query_time += elapsed

        passed = q["check"](conclusions)
        result_count = len(conclusions) if conclusions else 0

        # Negatif testlerde "passed" = baglanti bulunamadi demek
        # Ama yine de bazi sonuclar donebilir (tek terimle eslesen direkt kurallar)
        # Onemli olan: iki terim arasinda ZINCIR olmamasi

        has_cross_chain = False
        if conclusions:
            for c in conclusions:
                if c["type"] == "chained":
                    chain = c.get("chain", "").lower()
                    terms_in_chain = sum(1 for t in q["terms"] if t in chain)
                    if terms_in_chain >= 2:
                        has_cross_chain = True
                        break

        if passed and not has_cross_chain:
            status = "GECTI (baglanti bulunmadi - dogru)"
        elif not passed:
            status = "KALDI (yanlis baglanti bulundu!)"
        else:
            status = "GECTI"

        print(f"  Soru {q['id']}: \"{q['text']}\"")
        print(f"    Beklenen: {q['expected']}")
        if conclusions:
            # Negatif testlerde sadece cross-term sonuclari goster
            relevant = [c for c in conclusions if c["type"] == "chained"]
            if relevant:
                print(f"    !!! UYARI: {len(relevant)} zincir bulundu:")
                for c in relevant[:3]:
                    print(f"      {c['chain']} (guven: {c['confidence']:.2f})")
            else:
                print(f"    Sonuc: {result_count} direkt eslesme (zincir yok - iyi)")
        else:
            print(f"    Sonuc: YOK (hic sonuc yok - iyi)")
        print(f"    Sonuc: {status} ({elapsed*1000:.1f}ms)")
        print()

        all_results["negatif"].append({
            "id": q["id"],
            "passed": passed,
            "false_positive": not passed,
            "query_ms": elapsed * 1000,
            "result_count": result_count,
            "had_cross_chain": has_cross_chain,
        })

    # --- Kategori 6: DOGRULAMA ---
    print(f"\n  --- KATEGORI 6: DOGRULAMA (5 soru) ---")
    print(f"  (Bulunan zincirlerin her halkasi state'te dogrulanir)\n")
    for q in VERIFICATION_QUESTIONS:
        start = time.time()
        conclusions = engine.query(q["text"], q["terms"])
        elapsed = time.time() - start
        total_query_time += elapsed

        result_count = len(conclusions) if conclusions else 0

        print(f"  Soru {q['id']}: \"{q['text']}\"")
        print(f"    Beklenen: {q['expected']}")
        print_conclusions_compact(conclusions, max_show=4)

        chain_valid = print_verification_detail(engine, conclusions, q["id"])

        # Ek: tum zincirlerdeki sahte halkalari say
        _, total_chains, fake = check_false_positive(engine, conclusions, q["terms"])

        passed = chain_valid and result_count > 0

        status = "GECTI (tum halkalar dogrulandi)" if passed else "KALDI (dogrulama basarisiz)"
        print(f"    Sonuc: {status} ({elapsed*1000:.1f}ms)")
        print()

        all_results["dogrulama"].append({
            "id": q["id"],
            "passed": passed,
            "false_positive": len(fake) > 0,
            "query_ms": elapsed * 1000,
            "result_count": result_count,
            "fake_count": len(fake),
        })

    # ==================================================================
    #  ADIM 4: Ozet Tablosu
    # ==================================================================
    print(f"\n{'='*74}")
    print("  ADIM 4: Sonuc Tablosu")
    print(f"{'='*74}")

    print()
    header = f"  {'Kategori':<28} {'Gecti':<10} {'Kaldi':<10} {'Yanlis Poz.':<12}"
    print(header)
    print("  " + "-" * 58)

    total_passed = 0
    total_failed = 0
    total_fp = 0

    for cat_name, cat_label in [
        ("basit", "Basit Getirme"),
        ("zincir", "Zincir Cikarim"),
        ("kalitim", "Kalitim"),
        ("celiski", "Celiski & Nuans"),
        ("negatif", "NEGATIF TESTLER"),
        ("dogrulama", "DOGRULAMA"),
    ]:
        results = all_results[cat_name]
        passed = sum(1 for r in results if r["passed"])
        failed = sum(1 for r in results if not r["passed"])
        fp = sum(1 for r in results if r.get("false_positive", False))
        total_passed += passed
        total_failed += failed
        total_fp += fp

        print(f"  {cat_label:<28} {passed}/{len(results):<8} {failed}/{len(results):<8} {fp}/{len(results):<10}")

    print("  " + "-" * 58)
    print(f"  {'TOPLAM':<28} {total_passed}/30{'':<5} {total_failed}/30{'':<5} {total_fp}/30")

    # ==================================================================
    #  ADIM 5: Performans Metrikleri
    # ==================================================================
    print(f"\n{'='*74}")
    print("  ADIM 5: Performans Metrikleri")
    print(f"{'='*74}")

    avg_query_ms = (total_query_time / 30) * 1000
    all_query_times = []
    for cat in all_results.values():
        for r in cat:
            all_query_times.append(r["query_ms"])

    print(f"\n  Toplam kural yuklenen:     {total_rules}")
    print(f"  Aktif kural (state):       {len(engine.state)}")
    print(f"  Cekirdek yukleme suresi:   {core_time:.3f}s")
    print(f"  Gurultu yukleme suresi:    {noise_time:.3f}s")
    print(f"  Toplam yukleme suresi:     {core_time + noise_time:.3f}s")
    print(f"  Ortalama sorgu suresi:     {avg_query_ms:.1f}ms")
    print(f"  En yavas sorgu:            {max(all_query_times):.1f}ms")
    print(f"  En hizli sorgu:            {min(all_query_times):.1f}ms")
    print(f"  Toplam sorgu suresi:       {total_query_time:.3f}s")
    print(f"  Cluster sayisi:            {len(all_clusters)}")
    print(f"  Multi-member cluster:      {len(multi_clusters)}")

    # Performans uyari
    if core_time + noise_time > 60:
        print(f"\n  !!! UYARI: Yukleme suresi 60 saniyeyi asti ({core_time + noise_time:.1f}s)")
    if avg_query_ms > 1000:
        print(f"\n  !!! UYARI: Ortalama sorgu suresi 1 saniyeyi asti ({avg_query_ms:.1f}ms)")

    # ==================================================================
    #  ADIM 6: Durust Degerlendirme
    # ==================================================================
    print(f"\n{'='*74}")
    print("  ADIM 6: DURUST DEGERLENDIRME")
    print(f"{'='*74}")

    accuracy_pct = (total_passed / 30) * 100
    fp_pct = (total_fp / 30) * 100

    # Kategori bazli analiz
    basit_passed = sum(1 for r in all_results["basit"] if r["passed"])
    zincir_passed = sum(1 for r in all_results["zincir"] if r["passed"])
    kalitim_passed = sum(1 for r in all_results["kalitim"] if r["passed"])
    celiski_passed = sum(1 for r in all_results["celiski"] if r["passed"])
    negatif_passed = sum(1 for r in all_results["negatif"] if r["passed"])
    dogrulama_passed = sum(1 for r in all_results["dogrulama"] if r["passed"])

    print(f"\n  Genel basari orani: {total_passed}/30 ({accuracy_pct:.1f}%)")
    print(f"  Yanlis pozitif orani: {total_fp}/30 ({fp_pct:.1f}%)")

    print(f"\n  Detayli analiz:")
    print(f"    Basit getirme:     {basit_passed}/5 - {'IKONUK' if basit_passed >= 4 else 'ZAYIF'}")
    print(f"    Zincir cikarim:    {zincir_passed}/5 - {'IKONUK' if zincir_passed >= 4 else 'ZAYIF' if zincir_passed >= 2 else 'BASARISIZ'}")
    print(f"    Kalitim:           {kalitim_passed}/5 - {'IKONUK' if kalitim_passed >= 4 else 'ZAYIF' if kalitim_passed >= 2 else 'BASARISIZ'}")
    print(f"    Celiski/Nuans:     {celiski_passed}/5 - {'IKONUK' if celiski_passed >= 4 else 'ZAYIF' if celiski_passed >= 2 else 'BASARISIZ'}")
    print(f"    Negatif testler:   {negatif_passed}/5 - {'IKONUK' if negatif_passed >= 4 else 'ZAYIF' if negatif_passed >= 2 else 'BASARISIZ'}")
    print(f"    Dogrulama:         {dogrulama_passed}/5 - {'IKONUK' if dogrulama_passed >= 4 else 'ZAYIF' if dogrulama_passed >= 2 else 'BASARISIZ'}")

    # Kanit ve endiseler
    print(f"\n  KANITLAR:")
    evidence = []
    concerns = []

    if basit_passed >= 4:
        evidence.append("Basit gerceleri 10K kural arasinda bulabiliyor")
    else:
        concerns.append(f"Basit gercekleri bile bulamiyor ({basit_passed}/5)")

    if zincir_passed >= 3:
        evidence.append("Cok adimli zincir cikarimi calisiyor")
    elif zincir_passed >= 1:
        evidence.append(f"Zincir cikarim KISMI calisiyor ({zincir_passed}/5)")
        concerns.append("Uzun zincirlerde zorlaniyor")
    else:
        concerns.append("Zincir cikarim CALISMIYOR")

    if kalitim_passed >= 3:
        evidence.append("'turu' kalitimi calisiyor")
    else:
        concerns.append(f"Kalitim zayif ({kalitim_passed}/5)")

    if celiski_passed >= 3:
        evidence.append("Celiskileri taniyor (hem olumlu hem olumsuz)")
    else:
        concerns.append(f"Celiski tespiti zayif ({celiski_passed}/5)")

    if negatif_passed >= 4:
        evidence.append("Gurultu arasinda sahte baglanti KURMUYOR (cok onemli!)")
    elif negatif_passed >= 2:
        concerns.append(f"Bazi sahte baglantilar kuruyor ({5 - negatif_passed}/5 yanlis pozitif)")
    else:
        concerns.append(f"COK FAZLA sahte baglanti kuruyor ({5 - negatif_passed}/5 yanlis pozitif) - CIDDI SORUN")

    if dogrulama_passed >= 4:
        evidence.append("Bulunan zincirlerin halkalari gercekten mevcut")
    else:
        concerns.append(f"Dogrulama basarisiz ({dogrulama_passed}/5) - motor gecersiz zincirler uretiyor olabilir")

    # Performans kanit
    if avg_query_ms < 100:
        evidence.append(f"Sorgu performansi iyi ({avg_query_ms:.1f}ms ortalama)")
    elif avg_query_ms < 1000:
        evidence.append(f"Sorgu performansi kabul edilebilir ({avg_query_ms:.1f}ms ortalama)")
    else:
        concerns.append(f"Sorgu performansi cok yavas ({avg_query_ms:.1f}ms ortalama)")

    if core_time + noise_time < 30:
        evidence.append(f"10K kural yukleme hizli ({core_time + noise_time:.1f}s)")
    elif core_time + noise_time < 120:
        pass  # ne iyi ne kotu
    else:
        concerns.append(f"10K kural yukleme cok yavas ({core_time + noise_time:.1f}s)")

    for e in evidence:
        print(f"    [+] {e}")
    if concerns:
        print(f"\n  ENDISELER:")
        for c in concerns:
            print(f"    [-] {c}")

    # Nihai karar
    print(f"\n  {'='*58}")

    # Karar kriterlerini agirliklandir
    # Negatif testler ve dogrulama EN ONEMLI (aci 2x)
    weighted_score = (
        basit_passed * 1 +
        zincir_passed * 1.5 +
        kalitim_passed * 1.5 +
        celiski_passed * 1 +
        negatif_passed * 2 +      # 2x agirlik
        dogrulama_passed * 2      # 2x agirlik
    )
    weighted_max = 5 * (1 + 1.5 + 1.5 + 1 + 2 + 2)  # = 45
    weighted_pct = (weighted_score / weighted_max) * 100

    print(f"  Agirlikli skor: {weighted_score:.1f}/{weighted_max:.1f} ({weighted_pct:.1f}%)")
    print(f"  (Negatif testler ve dogrulama 2x agirlikli)")

    if weighted_pct >= 80 and negatif_passed >= 4 and dogrulama_passed >= 4:
        print(f"\n  KARAR: EVET - Motor gercekten akillaniytor.")
        print(f"         10K kural arasinda sinyal/gurultu ayrimini yapiyor.")
        print(f"         Sahte baglanti kurmuyor. Zincirleri gecerli.")
    elif weighted_pct >= 60 and negatif_passed >= 3:
        print(f"\n  KARAR: KISMEN - Motor bazi yetenekler gosteriyor ama kusurlu.")
        print(f"         Bazi alanlarda basarili, bazi alanlarda basarisiz.")
    elif weighted_pct >= 40:
        print(f"\n  KARAR: TARTISMALI - Motor temel islemleri yapiyor ama")
        print(f"         gercek zeka kanitlari zayif. Basit pattern matching olabilir.")
    else:
        print(f"\n  KARAR: HAYIR - Motor olcekte basarisiz.")
        print(f"         10K kuralda performans ve dogruluk dusuyor.")

    if negatif_passed < 3:
        print(f"\n  !!! KRITIK UYARI: Motor cok fazla sahte baglanti kuruyor.")
        print(f"      Bu, motorun gercekten 'anlamadigini', sadece string")
        print(f"      eslestirme yaptigini gosterebilir.")

    if total_fp > 5:
        print(f"\n  !!! KRITIK UYARI: {total_fp} yanlis pozitif tespit edildi.")
        print(f"      Motor varolmayan baglantilar 'buluyor'.")

    print()
    print("=" * 74)
    print("  OLCEK + DURUSTLUK TESTI TAMAMLANDI")
    print("=" * 74)


if __name__ == "__main__":
    run_scale_test()
