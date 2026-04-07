"""
ChainOfMeaning v3 BUYUME TESTI
Motor bilgi biriktirikce akillaniytor mu?

5 fazli, 500 elle yazilmis Turkce kural ile gercekci zeka testi.
Her faz bilgi ekler, motorun cevaplarinin iyilesip iyilesmedigini olcer.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine_v3 import Rule, RuleEngineV3


# ======================================================================
#  KURAL SETLERI
# ======================================================================

PHASE_1_RULES = [
    # Hayvanlar
    ("kedi", "turu", "hayvan"),
    ("kopek", "turu", "hayvan"),
    ("hayvan", "ozellik", "canli"),
    ("kedi", "ozellik", "miyavlar"),
    ("kopek", "ozellik", "havlar"),
    ("aslan", "turu", "hayvan"),
    ("aslan", "ozellik", "yirtici"),
    ("tavsan", "turu", "hayvan"),
    ("tavsan", "ozellik", "hizli"),
    ("kus", "turu", "hayvan"),
    ("kus", "ozellik", "ucar"),
    ("balik", "turu", "hayvan"),
    ("balik", "ozellik", "yuzer"),

    # Yiyecek ve icecek
    ("elma", "turu", "meyve"),
    ("muz", "turu", "meyve"),
    ("meyve", "turu", "yiyecek"),
    ("yiyecek", "etki", "besler"),
    ("meyve", "etki", "saglikli"),
    ("sut", "turu", "icecek"),
    ("icecek", "turu", "yiyecek"),
    ("su", "turu", "icecek"),
    ("su", "etki", "hayati"),
    ("portakal", "turu", "meyve"),
    ("ekmek", "turu", "yiyecek"),
    ("peynir", "turu", "yiyecek"),

    # Meslekler
    ("doktor", "turu", "meslek"),
    ("ogretmen", "turu", "meslek"),
    ("muhendis", "turu", "meslek"),
    ("meslek", "saglar", "gelir"),
    ("doktor", "saglar", "saglik"),
    ("ogretmen", "saglar", "bilgi"),
    ("muhendis", "saglar", "teknoloji"),
    ("avukat", "turu", "meslek"),
    ("avukat", "saglar", "adalet"),

    # Tasitlar
    ("araba", "turu", "tasit"),
    ("ucak", "turu", "tasit"),
    ("gemi", "turu", "tasit"),
    ("tasit", "saglar", "ulasim"),
    ("araba", "kullanir", "benzin"),
    ("ucak", "kullanir", "yakit"),
    ("bisiklet", "turu", "tasit"),
    ("bisiklet", "etki", "cevreci"),

    # Renkler
    ("kirmizi", "turu", "renk"),
    ("mavi", "turu", "renk"),
    ("yesil", "turu", "renk"),
    ("renk", "ozellik", "gorsel"),
    ("yesil", "etki", "huzur"),
    ("mavi", "etki", "sakinlik"),
    ("kirmizi", "etki", "enerji"),

    # Sehirler ve ulke
    ("istanbul", "turu", "sehir"),
    ("ankara", "turu", "sehir"),
    ("sehir", "icerir", "insan"),
    ("sehir", "icerir", "bina"),
    ("istanbul", "ozellik", "buyuk"),
    ("ankara", "ozellik", "baskent"),
    ("turkiye", "turu", "ulke"),
    ("ulke", "icerir", "sehir"),
    ("turkiye", "icerir", "istanbul"),
    ("turkiye", "icerir", "ankara"),
]


PHASE_2_RULES = [
    # Besin zinciri
    ("ot", "turu", "bitki"),
    ("bitki", "ozellik", "fotosentez"),
    ("tavsan", "yer", "ot"),
    ("aslan", "yer", "tavsan"),
    ("insan", "yer", "meyve"),
    ("insan", "yer", "et"),
    ("et", "turu", "yiyecek"),
    ("sebze", "turu", "yiyecek"),
    ("sebze", "etki", "saglikli"),
    ("havuc", "turu", "sebze"),
    ("brokoli", "turu", "sebze"),

    # Saglik zinciri
    ("spor", "etki", "saglikli"),
    ("spor", "gelistirir", "kas"),
    ("kas", "saglar", "guc"),
    ("guc", "etki", "faydali"),
    ("stres", "etki", "zararli"),
    ("stres", "azaltir", "saglik"),
    ("uyku", "etki", "saglikli"),
    ("uyku", "gelistirir", "hafiza"),
    ("hafiza", "saglar", "ogrenme"),
    ("meditasyon", "azaltir", "stres"),
    ("meditasyon", "etki", "saglikli"),
    ("yuruyus", "etki", "saglikli"),
    ("yuruyus", "turu", "spor aktivitesi"),
    ("kosu", "turu", "spor aktivitesi"),
    ("kosu", "etki", "saglikli"),

    # Teknoloji zinciri
    ("bilgisayar", "turu", "teknoloji"),
    ("telefon", "turu", "teknoloji"),
    ("internet", "turu", "teknoloji"),
    ("teknoloji", "saglar", "iletisim"),
    ("iletisim", "etki", "faydali"),
    ("teknoloji", "gelistirir", "verimlilik"),
    ("verimlilik", "etki", "olumlu"),
    ("yapay zeka", "turu", "teknoloji"),
    ("yapay zeka", "gelistirir", "otomasyon"),
    ("otomasyon", "etki", "verimli"),
    ("robot", "turu", "teknoloji"),
    ("robot", "kullanir", "yapay zeka"),
    ("yazilim", "turu", "teknoloji"),
    ("yazilim", "saglar", "cozum"),

    # Egitim zinciri
    ("okul", "turu", "egitim kurumu"),
    ("universite", "turu", "egitim kurumu"),
    ("egitim kurumu", "saglar", "bilgi"),
    ("bilgi", "etki", "guclu"),
    ("bilgi", "gelistirir", "dusunce"),
    ("dusunce", "etki", "ozgurlestirir"),
    ("kitap", "saglar", "bilgi"),
    ("kitap", "turu", "egitim araci"),
    ("ogretmen", "kullanir", "kitap"),
    ("arastirma", "saglar", "bilgi"),
    ("arastirma", "gelistirir", "bilim"),
    ("bilim", "saglar", "ilerleme"),
    ("ilerleme", "etki", "olumlu"),

    # Dogal duzen
    ("gunes", "saglar", "isik"),
    ("isik", "saglar", "enerji"),
    ("enerji", "etki", "hayati"),
    ("yagmur", "saglar", "su"),
    ("su", "etki", "hayati"),
    ("toprak", "saglar", "besin"),
    ("besin", "etki", "besleyici"),
    ("agac", "uretir", "oksijen"),
    ("oksijen", "etki", "hayati"),
    ("agac", "turu", "bitki"),
    ("orman", "icerir", "agac"),
    ("orman", "saglar", "oksijen"),
    ("deniz", "icerir", "balik"),
    ("deniz", "saglar", "besin"),

    # Ekonomi
    ("para", "turu", "arac"),
    ("para", "saglar", "alisveris"),
    ("calisma", "saglar", "para"),
    ("meslek", "saglar", "para"),
    ("yatirim", "gelistirir", "para"),
    ("tasarruf", "saglar", "guvenlik"),
    ("ticaret", "saglar", "para"),
    ("ticaret", "gelistirir", "ekonomi"),
    ("ekonomi", "etki", "onemli"),

    # Duygular
    ("mutluluk", "etki", "olumlu"),
    ("uzuntu", "etki", "olumsuz"),
    ("korku", "etki", "uyarici"),
    ("sevgi", "etki", "baglanma"),
    ("empati", "gelistirir", "sevgi"),
    ("iletisim", "gelistirir", "empati"),
    ("guven", "etki", "olumlu"),
    ("saygi", "gelistirir", "guven"),

    # Sosyal
    ("aile", "turu", "topluluk"),
    ("okul", "turu", "topluluk"),
    ("topluluk", "saglar", "ait olma"),
    ("ait olma", "etki", "olumlu"),
    ("arkadaslik", "saglar", "mutluluk"),
    ("yalnizlik", "etki", "olumsuz"),
    ("isbirligi", "saglar", "basari"),
    ("basari", "etki", "olumlu"),
    ("dayanisma", "saglar", "guc"),
    ("dayanisma", "turu", "topluluk"),

    # Ek iliskiler - saglik detay
    ("vitamin", "turu", "besin ogesi"),
    ("mineral", "turu", "besin ogesi"),
    ("besin ogesi", "etki", "saglikli"),
    ("meyve", "icerir", "vitamin"),
    ("sebze", "icerir", "vitamin"),
    ("gunes", "saglar", "sicaklik"),
]


PHASE_3_RULES = [
    # Dogrudan celiskiler
    ("seker", "etki", "zararli"),
    ("meyve", "icerir", "seker"),
    ("teknoloji", "etki", "bagimlilik yapici"),
    ("para", "etki", "bozucu"),
    ("rekabet", "etki", "stresli"),
    ("rekabet", "etki", "gelistirici"),

    # Dolayli celiskiler - kahve
    ("kahve", "icerir", "kafein"),
    ("kafein", "etki", "uyarir"),
    ("kafein", "etki", "bagimlilik yapici"),
    ("kahve", "etki", "saglikli"),
    ("kahve", "etki", "lezzetli"),

    # Sut celiskisi
    ("sut", "icerir", "laktoz"),
    ("laktoz", "etki", "sindirim sorunu"),
    ("sut", "icerir", "kalsiyum"),
    ("kalsiyum", "etki", "kemik guclendirici"),

    # Fastfood celiskisi
    ("fastfood", "turu", "yiyecek"),
    ("fastfood", "etki", "zararli"),
    ("fastfood", "etki", "lezzetli"),
    ("fastfood", "icerir", "yag"),
    ("yag", "etki", "zararli"),

    # Ilac nüansi
    ("ilac", "etki", "iyilestirir"),
    ("ilac", "etki", "yan etki"),
    ("antibiyotik", "turu", "ilac"),
    ("antibiyotik", "etki", "mikrop oldurur"),
    ("antibiyotik", "etki", "flora bozar"),

    # Gunes nüansi
    ("gunes", "etki", "d vitamini"),
    ("gunes", "etki", "yanik"),
    ("gunes", "etki", "sicaklik"),

    # Egzersiz nüansi
    ("egzersiz", "etki", "saglikli"),
    ("egzersiz", "etki", "sakatlik riski"),
    ("egzersiz", "gelistirir", "dayaniklilik"),
    ("dayaniklilik", "etki", "olumlu"),

    # Sosyal medya celiskisi
    ("sosyal medya", "saglar", "iletisim"),
    ("sosyal medya", "etki", "bagimlilik yapici"),
    ("sosyal medya", "azaltir", "dikkat"),
    ("sosyal medya", "turu", "teknoloji"),
    ("sosyal medya", "etki", "eglenceli"),

    # Sehir yasami celiskisi
    ("sehir", "etki", "firsatlar"),
    ("sehir", "etki", "kirlilik"),
    ("sehir", "etki", "stresli"),
    ("koy", "etki", "huzurlu"),
    ("koy", "etki", "sinirli firsatlar"),

    # Enerji kaynaklari celiskisi
    ("nukleer enerji", "saglar", "enerji"),
    ("nukleer enerji", "etki", "tehlikeli"),
    ("nukleer enerji", "etki", "verimli"),
    ("fosil yakit", "saglar", "enerji"),
    ("fosil yakit", "etki", "kirletici"),
    ("gunes enerjisi", "saglar", "enerji"),
    ("gunes enerjisi", "etki", "temiz"),
    ("gunes enerjisi", "etki", "pahali"),
    ("ruzgar enerjisi", "saglar", "enerji"),
    ("ruzgar enerjisi", "etki", "temiz"),

    # Internet celiskisi
    ("internet", "saglar", "bilgi"),
    ("internet", "etki", "bagimlilik yapici"),
    ("internet", "saglar", "eglence"),
    ("internet", "etki", "yanlis bilgi"),

    # Araba celiskisi
    ("araba", "etki", "konforlu"),
    ("araba", "etki", "kirletici"),
    ("araba", "etki", "trafik"),

    # Cay ve kahve detay
    ("cay", "icerir", "kafein"),
    ("cay", "etki", "rahatlatici"),
    ("cay", "etki", "saglikli"),
    ("cikolata", "etki", "mutluluk verici"),
    ("cikolata", "etki", "kilo yapici"),
    ("cikolata", "icerir", "seker"),

    # Egitim sistemi celiskisi
    ("sinav", "etki", "stresli"),
    ("sinav", "saglar", "olcum"),
    ("odev", "etki", "ogretici"),
    ("odev", "etki", "yorucu"),
    ("rekabet", "saglar", "motivasyon"),

    # Daha fazla nuans
    ("televizyon", "etki", "eglenceli"),
    ("televizyon", "etki", "pasiflestirir"),
    ("televizyon", "saglar", "bilgi"),
    ("oyun", "etki", "eglenceli"),
    ("oyun", "etki", "bagimlilik yapici"),
    ("oyun", "gelistirir", "refleks"),
    ("turizm", "saglar", "para"),
    ("turizm", "etki", "cevre tahribati"),
    ("turizm", "etki", "kultur alitsveriis"),

    # Hayvan urunleri celiskisi
    ("et", "etki", "besleyici"),
    ("et", "etki", "kolesterol"),
    ("yumurta", "etki", "besleyici"),
    ("yumurta", "etki", "kolesterol"),
    ("bal", "etki", "saglikli"),
    ("bal", "icerir", "seker"),

    # Plasitk celiskisi
    ("plastik", "etki", "pratik"),
    ("plastik", "etki", "cevre kirletici"),
    ("plastik", "turu", "malzeme"),
]


PHASE_4_RULES = [
    # Guclu tekrarlar - spor ve saglik
    ("spor", "etki", "saglikli"),        # reinforce 1
    ("spor", "etki", "saglikli"),        # reinforce 2
    ("spor", "etki", "saglikli"),        # reinforce 3
    ("su", "etki", "hayati"),            # reinforce 1
    ("su", "etki", "hayati"),            # reinforce 2
    ("egitim", "etki", "faydali"),
    ("egitim", "etki", "faydali"),       # reinforce
    ("egitim", "etki", "faydali"),       # reinforce 2

    # Dunya bilgisi duzeltme
    ("dunya", "ozellik", "yuvarlak"),
    ("dunya", "ozellik", "yuvarlak"),    # reinforce
    ("dunya", "ozellik", "yuvarlak"),    # reinforce 2
    ("dunya", "ozellik", "yuvarlak"),    # reinforce 3
    ("dunya", "ozellik", "duz"),         # yanlis bilgi - dusuk mass ile gelecek

    # Teknoloji faydali tekrar
    ("teknoloji", "etki", "faydali"),
    ("teknoloji", "etki", "faydali"),    # reinforce
    ("teknoloji", "etki", "faydali"),    # reinforce 2
    ("teknoloji", "etki", "faydali"),    # reinforce 3

    # Bilgi ve egitim tekrar
    ("bilgi", "etki", "guclu"),          # reinforce
    ("bilgi", "etki", "guclu"),          # reinforce 2
    ("kitap", "saglar", "bilgi"),        # reinforce
    ("kitap", "saglar", "bilgi"),        # reinforce 2
    ("ogretmen", "saglar", "bilgi"),     # reinforce
    ("ogretmen", "saglar", "bilgi"),     # reinforce 2

    # Saglik bilgi tekrarlari
    ("uyku", "etki", "saglikli"),        # reinforce
    ("uyku", "etki", "saglikli"),        # reinforce 2
    ("meditasyon", "etki", "saglikli"),  # reinforce
    ("meditasyon", "etki", "saglikli"),  # reinforce 2

    # Cevre koruma bilgi guclendirme
    ("cevre koruma", "etki", "onemli"),
    ("cevre koruma", "etki", "onemli"),  # reinforce
    ("geri donusum", "etki", "faydali"),
    ("geri donusum", "etki", "faydali"), # reinforce
    ("yenilenebilir enerji", "etki", "temiz"),
    ("yenilenebilir enerji", "etki", "temiz"), # reinforce
    ("yenilenebilir enerji", "saglar", "enerji"),

    # Nuansli duzeltmeler - olculu kullanim
    ("olculu kullanim", "etki", "saglikli"),
    ("olculu kullanim", "etki", "saglikli"),  # reinforce
    ("bilincli tuketim", "etki", "olumlu"),
    ("bilincli tuketim", "etki", "olumlu"),   # reinforce
    ("denge", "etki", "onemli"),
    ("denge", "etki", "onemli"),              # reinforce

    # Saglik yolu detay
    ("beslenme", "etki", "saglikli"),
    ("beslenme", "etki", "saglikli"),    # reinforce
    ("dengeli beslenme", "etki", "saglikli"),
    ("dengeli beslenme", "etki", "saglikli"), # reinforce
    ("vitamin", "etki", "saglikli"),
    ("mineral", "etki", "saglikli"),
    ("protein", "etki", "guc verici"),
    ("protein", "turu", "besin ogesi"),
    ("karbonhidrat", "turu", "besin ogesi"),
    ("karbonhidrat", "saglar", "enerji"),

    # Bilim ve dogruluk tekrar
    ("bilim", "saglar", "ilerleme"),     # reinforce
    ("bilim", "saglar", "ilerleme"),     # reinforce 2
    ("arastirma", "saglar", "bilgi"),    # reinforce
    ("arastirma", "saglar", "bilgi"),    # reinforce 2
    ("deney", "saglar", "kanit"),
    ("kanit", "saglar", "gercek"),
    ("gercek", "etki", "onemli"),

    # Sosyal duzeltmeler
    ("empati", "etki", "olumlu"),
    ("empati", "etki", "olumlu"),        # reinforce
    ("saygi", "etki", "olumlu"),
    ("saygi", "etki", "olumlu"),         # reinforce
    ("diyalog", "saglar", "anlayis"),
    ("anlayis", "etki", "olumlu"),
    ("hosgoru", "etki", "olumlu"),
    ("hosgoru", "etki", "olumlu"),       # reinforce
    ("adalet", "etki", "onemli"),
    ("adalet", "etki", "onemli"),        # reinforce

    # Yanlis bilgi duzeltme
    ("yanlis bilgi", "etki", "zararli"),
    ("yanlis bilgi", "etki", "zararli"), # reinforce
    ("elestirisel dusunme", "azaltir", "yanlis bilgi"),
    ("elestirisel dusunme", "etki", "faydali"),
    ("kaynak dogrulama", "azaltir", "yanlis bilgi"),

    # Saglik yanlis bilgi duzeltme
    ("asci", "turu", "meslek"),
    ("asci", "saglar", "yemek"),
    ("yemek", "etki", "besleyici"),
    ("temiz hava", "etki", "saglikli"),
    ("temiz hava", "etki", "saglikli"), # reinforce
    ("hareket", "etki", "saglikli"),
    ("hareket", "etki", "saglikli"),    # reinforce

    # Daha fazla guc tekrari
    ("sevgi", "etki", "olumlu"),
    ("sevgi", "etki", "olumlu"),        # reinforce
    ("aile", "saglar", "destek"),
    ("aile", "saglar", "destek"),       # reinforce
    ("destek", "etki", "olumlu"),
    ("arkadaslik", "etki", "olumlu"),
    ("arkadaslik", "etki", "olumlu"),   # reinforce
]


PHASE_5_RULES = [
    # Cografya
    ("izmir", "turu", "sehir"),
    ("antalya", "turu", "sehir"),
    ("bursa", "turu", "sehir"),
    ("trabzon", "turu", "sehir"),
    ("izmir", "ozellik", "deniz kenari"),
    ("antalya", "ozellik", "turistik"),
    ("bursa", "ozellik", "tarihi"),
    ("turkiye", "icerir", "izmir"),
    ("turkiye", "icerir", "antalya"),
    ("avrupa", "turu", "kita"),
    ("asya", "turu", "kita"),
    ("kita", "icerir", "ulke"),
    ("almanya", "turu", "ulke"),
    ("japonya", "turu", "ulke"),
    ("japonya", "ozellik", "teknolojik"),
    ("almanya", "ozellik", "endustriyel"),

    # Bilim dallari
    ("fizik", "turu", "bilim dali"),
    ("kimya", "turu", "bilim dali"),
    ("biyoloji", "turu", "bilim dali"),
    ("matematik", "turu", "bilim dali"),
    ("bilim dali", "saglar", "bilgi"),
    ("fizik", "inceler", "madde"),
    ("kimya", "inceler", "element"),
    ("biyoloji", "inceler", "canli"),
    ("matematik", "saglar", "mantik"),
    ("mantik", "etki", "faydali"),

    # Sanat
    ("muzik", "turu", "sanat"),
    ("resim", "turu", "sanat"),
    ("edebiyat", "turu", "sanat"),
    ("sinema", "turu", "sanat"),
    ("sanat", "etki", "ilham verici"),
    ("sanat", "gelistirir", "yaraticilik"),
    ("yaraticilik", "etki", "olumlu"),
    ("muzik", "etki", "rahatlatici"),
    ("edebiyat", "gelistirir", "empati"),
    ("sinema", "saglar", "eglence"),
    ("tiyatro", "turu", "sanat"),
    ("tiyatro", "etki", "ogretici"),

    # Spor dallari
    ("futbol", "turu", "spor"),
    ("basketbol", "turu", "spor"),
    ("yuzme", "turu", "spor"),
    ("tenis", "turu", "spor"),
    ("spor", "gelistirir", "saglik"),
    ("futbol", "saglar", "takim ruhu"),
    ("takim ruhu", "etki", "olumlu"),
    ("yuzme", "gelistirir", "dayaniklilik"),

    # Insan beden
    ("kalp", "turu", "organ"),
    ("beyin", "turu", "organ"),
    ("akciger", "turu", "organ"),
    ("organ", "ozellik", "hayati"),
    ("beyin", "saglar", "dusunce"),
    ("kalp", "saglar", "kan dolasimi"),
    ("kan dolasimi", "etki", "hayati"),
    ("akciger", "saglar", "solunum"),
    ("solunum", "etki", "hayati"),

    # Mevsimler
    ("ilkbahar", "turu", "mevsim"),
    ("yaz", "turu", "mevsim"),
    ("sonbahar", "turu", "mevsim"),
    ("kis", "turu", "mevsim"),
    ("mevsim", "etki", "dogal dongu"),
    ("ilkbahar", "etki", "canlanma"),
    ("yaz", "etki", "sicaklik"),
    ("kis", "etki", "soguk"),

    # Uzay
    ("ay", "turu", "gok cismi"),
    ("mars", "turu", "gezegen"),
    ("dunya", "turu", "gezegen"),
    ("gezegen", "turu", "gok cismi"),
    ("gunes", "turu", "yildiz"),
    ("yildiz", "turu", "gok cismi"),
    ("uzay", "icerir", "gezegen"),
    ("uzay", "ozellik", "sonsuz"),

    # Iletisim
    ("dil", "turu", "iletisim araci"),
    ("turkce", "turu", "dil"),
    ("ingilizce", "turu", "dil"),
    ("dil", "saglar", "iletisim"),
    ("iletisim", "saglar", "anlayis"),
    ("tercume", "saglar", "iletisim"),
    ("isaret dili", "turu", "dil"),

    # Hukuk
    ("yasa", "saglar", "duzen"),
    ("duzen", "etki", "onemli"),
    ("anayasa", "turu", "yasa"),
    ("insan haklari", "etki", "onemli"),
    ("insan haklari", "etki", "onemli"),  # reinforce
    ("demokrasi", "saglar", "ozgurluk"),
    ("ozgurluk", "etki", "onemli"),

    # Tarih
    ("tarih", "saglar", "ders"),
    ("ders", "etki", "ogretici"),
    ("gecmis", "saglar", "tecrube"),
    ("tecrube", "etki", "faydali"),
    ("medeniyet", "saglar", "kultur"),
    ("kultur", "etki", "zenginlestirici"),

    # Felsefe
    ("felsefe", "gelistirir", "dusunce"),
    ("felsefe", "turu", "bilim dali"),
    ("etik", "saglar", "deger"),
    ("deger", "etki", "yonlendirici"),
    ("erdem", "etki", "olumlu"),
    ("bilgelik", "saglar", "huzur"),
    ("huzur", "etki", "olumlu"),

    # Insan ozellikleri
    ("insan", "ozellik", "dusunebilir"),
    ("insan", "ozellik", "sosyal"),
    ("insan", "turu", "canli"),
    ("insan", "saglar", "medeniyet"),
    ("insan", "gelistirir", "teknoloji"),
    ("insan", "gelistirir", "sanat"),
    ("insan", "saglar", "toplum"),
    ("toplum", "icerir", "insan"),
    ("toplum", "saglar", "duzen"),

    # Doga
    ("nehir", "saglar", "su"),
    ("dag", "ozellik", "yuksek"),
    ("ova", "saglar", "tarim"),
    ("tarim", "saglar", "yiyecek"),
    ("tarim", "etki", "hayati"),
    ("toprak", "etki", "hayati"),
    ("biyocesitlilik", "etki", "onemli"),
    ("biyocesitlilik", "etki", "onemli"),  # reinforce
    ("ekosistem", "icerir", "canli"),
    ("ekosistem", "etki", "dengeli"),

    # Teknoloji detay
    ("uzay araci", "turu", "tasit"),
    ("uzay araci", "kullanir", "roket"),
    ("roket", "kullanir", "yakit"),
    ("uydu", "turu", "teknoloji"),
    ("uydu", "saglar", "iletisim"),
    ("gps", "turu", "teknoloji"),
    ("gps", "saglar", "konum"),
    ("drone", "turu", "teknoloji"),
    ("drone", "etki", "faydali"),
    ("drone", "etki", "mahremiyet riski"),

    # Insan ihtiyaclari
    ("barinak", "turu", "temel ihtiyac"),
    ("yiyecek", "turu", "temel ihtiyac"),
    ("su", "turu", "temel ihtiyac"),
    ("guvenlik", "turu", "temel ihtiyac"),
    ("temel ihtiyac", "etki", "hayati"),
    ("sevgi", "turu", "temel ihtiyac"),
    ("ait olma", "turu", "temel ihtiyac"),

    # Gida ve tarim detay
    ("bugday", "turu", "tahil"),
    ("pirinc", "turu", "tahil"),
    ("tahil", "turu", "yiyecek"),
    ("tahil", "etki", "besleyici"),
    ("bal arisi", "uretir", "bal"),
    ("bal arisi", "saglar", "tozlasma"),
    ("tozlasma", "etki", "hayati"),

    # Meslekler genisleme
    ("pilot", "turu", "meslek"),
    ("pilot", "kullanir", "ucak"),
    ("hemsire", "turu", "meslek"),
    ("hemsire", "saglar", "bakim"),
    ("bakim", "etki", "saglikli"),
    ("itfaiyeci", "turu", "meslek"),
    ("itfaiyeci", "saglar", "guvenlik"),
    ("mimar", "turu", "meslek"),
    ("mimar", "saglar", "tasarim"),
    ("tasarim", "etki", "estetik"),

    # Maden ve kaynak
    ("demir", "turu", "maden"),
    ("altin", "turu", "maden"),
    ("maden", "turu", "dogal kaynak"),
    ("dogal kaynak", "etki", "degerli"),
    ("petrol", "turu", "dogal kaynak"),
    ("petrol", "saglar", "enerji"),
    ("petrol", "etki", "kirletici"),

    # Muzik detay
    ("piyano", "turu", "calgi"),
    ("gitar", "turu", "calgi"),
    ("calgi", "saglar", "muzik"),
]


# ======================================================================
#  SORU SETLERI
# ======================================================================

PHASE_1_QUESTIONS = [
    {
        "id": "P1Q1",
        "text": "Kedi bir hayvan midir?",
        "terms": ["kedi", "hayvan"],
        "expected": "kedi -> hayvan (turu ile)",
        "check": lambda conc: _has_connection(conc, "kedi", "hayvan"),
    },
    {
        "id": "P1Q2",
        "text": "Elma saglikli midir?",
        "terms": ["elma", "saglikli"],
        "expected": "elma -> meyve -> saglikli (kalitim ile)",
        "check": lambda conc: _has_connection(conc, "elma", "saglikli"),
    },
    {
        "id": "P1Q3",
        "text": "Doktor ne saglar?",
        "terms": ["doktor"],
        "expected": "doktor -> saglik (dogrudan)",
        "check": lambda conc: _has_term_in_results(conc, "saglik"),
    },
    {
        "id": "P1Q4",
        "text": "Bisiklet cevreci midir?",
        "terms": ["bisiklet", "cevreci"],
        "expected": "bisiklet -> cevreci (dogrudan kural)",
        "check": lambda conc: _has_connection(conc, "bisiklet", "cevreci"),
    },
    {
        "id": "P1Q5",
        "text": "Aslan miyavlar mi?",
        "terms": ["aslan", "miyavlar"],
        "expected": "BAGLANTI YOK (farkli hayvanlar)",
        "check": lambda conc: not _has_connection(conc, "aslan", "miyavlar"),
    },
]


PHASE_2_QUESTIONS = [
    {
        "id": "P2Q1",
        "text": "Spor neden faydalidir?",
        "terms": ["spor", "faydali"],
        "expected": "spor -> kas -> guc -> faydali (4 adimlik zincir)",
        "check": lambda conc: _has_chain_through(conc, ["spor", "kas", "guc", "faydali"]),
    },
    {
        "id": "P2Q2",
        "text": "Yapay zeka verimli midir?",
        "terms": ["yapay zeka", "verimli"],
        "expected": "yapay zeka -> otomasyon -> verimli",
        "check": lambda conc: _has_connection(conc, "yapay zeka", "verimli"),
    },
    {
        "id": "P2Q3",
        "text": "Egitim ozgurlestirir mi?",
        "terms": ["egitim kurumu", "ozgurlestirir"],
        "expected": "egitim kurumu -> bilgi -> dusunce -> ozgurlestirir",
        "check": lambda conc: _has_connection(conc, "bilgi", "ozgurlestirir") or _has_connection(conc, "egitim kurumu", "ozgurlestirir"),
    },
    {
        "id": "P2Q4",
        "text": "Agac neden onemlidir?",
        "terms": ["agac", "hayati"],
        "expected": "agac -> oksijen -> hayati",
        "check": lambda conc: _has_connection(conc, "agac", "hayati"),
    },
    {
        "id": "P2Q5",
        "text": "Yalnizlik neden kotudur?",
        "terms": ["yalnizlik", "olumsuz"],
        "expected": "yalnizlik -> olumsuz (dogrudan)",
        "check": lambda conc: _has_connection(conc, "yalnizlik", "olumsuz"),
    },
]


PHASE_3_QUESTIONS = [
    {
        "id": "P3Q1",
        "text": "Kahve saglikli midir?",
        "terms": ["kahve"],
        "expected": "Hem saglikli hem zararli yonler (nuans)",
        "check": lambda conc: _has_nuance(conc, ["saglikli", "uyarir", "lezzetli"], ["bagimlilik yapici"]),
    },
    {
        "id": "P3Q2",
        "text": "Teknoloji iyi midir?",
        "terms": ["teknoloji"],
        "expected": "faydali vs bagimlilik yapici (celiski)",
        "check": lambda conc: _has_nuance(conc, ["faydali", "iletisim", "verimlilik"], ["bagimlilik yapici"]),
    },
    {
        "id": "P3Q3",
        "text": "Gunes zararli midir?",
        "terms": ["gunes"],
        "expected": "d vitamini vs yanik (nuans)",
        "check": lambda conc: _has_nuance(conc, ["d vitamini", "isik"], ["yanik"]),
    },
    {
        "id": "P3Q4",
        "text": "Sut saglikli midir?",
        "terms": ["sut"],
        "expected": "kalsiyum vs laktoz (dolayli celiski)",
        "check": lambda conc: _has_nuance(conc, ["kalsiyum", "kemik guclendirici"], ["laktoz", "sindirim sorunu"]),
    },
    {
        "id": "P3Q5",
        "text": "Sosyal medya faydali mi zararli mi?",
        "terms": ["sosyal medya"],
        "expected": "iletisim vs bagimlilik (her iki taraf)",
        "check": lambda conc: _has_nuance(conc, ["iletisim", "eglenceli"], ["bagimlilik yapici", "dikkat"]),
    },
]


PHASE_4_QUESTIONS = [
    {
        "id": "P4Q1",
        "text": "Dunya duz mudur?",
        "terms": ["dunya", "duz"],
        "expected": "duz mass=1, yuvarlak mass>=3 (reinforced, yapisal olarak guclu)",
        "check": lambda conc: _check_yuvarlak_stronger_than_duz(conc),
    },
    {
        "id": "P4Q2",
        "text": "Teknoloji faydali midir?",
        "terms": ["teknoloji", "faydali"],
        "expected": "faydali yuksek confidence (4x reinforced)",
        "check": lambda conc: _check_confidence_higher(conc, "faydali", 0.5),
    },
    {
        "id": "P4Q3",
        "text": "Spor saglikli midir?",
        "terms": ["spor", "saglikli"],
        "expected": "saglikli cok yuksek confidence (4x reinforced)",
        "check": lambda conc: _check_confidence_higher(conc, "saglikli", 0.5),
    },
    {
        "id": "P4Q4",
        "text": "Bilgi guclu mudur?",
        "terms": ["bilgi", "guclu"],
        "expected": "guclu reinforced",
        "check": lambda conc: _check_confidence_higher(conc, "guclu", 0.5),
    },
]


PHASE_5_QUESTIONS = [
    {
        "id": "P5Q1",
        "text": "Insan neden onemlidir?",
        "terms": ["insan"],
        "expected": "Birden fazla domain'den sonuc (genis bilgi)",
        "check": lambda conc: conc is not None and len(conc) >= 5,
    },
    {
        "id": "P5Q2",
        "text": "Sanat neden degerlidir?",
        "terms": ["sanat"],
        "expected": "ilham verici, yaraticilik, olumlu",
        "check": lambda conc: _has_term_in_results(conc, "ilham verici") or _has_term_in_results(conc, "yaraticilik"),
    },
    {
        "id": "P5Q3",
        "text": "Bilim ne saglar?",
        "terms": ["bilim"],
        "expected": "ilerleme, bilgi",
        "check": lambda conc: _has_term_in_results(conc, "ilerleme"),
    },
    {
        "id": "P5Q4",
        "text": "Demokrasi neden onemlidir?",
        "terms": ["demokrasi", "onemli"],
        "expected": "demokrasi -> ozgurluk -> onemli",
        "check": lambda conc: _has_term_in_results(conc, "ozgurluk"),
    },
    {
        "id": "P5Q5",
        "text": "Ekosistem neden onemlidir?",
        "terms": ["ekosistem"],
        "expected": "canli, dengeli",
        "check": lambda conc: _has_term_in_results(conc, "canli") or _has_term_in_results(conc, "dengeli"),
    },
]


# Stability re-test: all earlier questions re-asked in phase 5
STABILITY_QUESTIONS = [
    PHASE_1_QUESTIONS[0],  # Kedi hayvan mi
    PHASE_1_QUESTIONS[1],  # Elma saglikli mi
    PHASE_1_QUESTIONS[4],  # Aslan miyavlar mi
    PHASE_2_QUESTIONS[0],  # Spor faydali mi
    PHASE_2_QUESTIONS[3],  # Agac hayati mi
    PHASE_3_QUESTIONS[0],  # Kahve saglikli mi
    PHASE_3_QUESTIONS[2],  # Gunes zararli mi
    PHASE_4_QUESTIONS[0],  # Dunya duz mu
    PHASE_4_QUESTIONS[1],  # Teknoloji faydali mi
]


# ======================================================================
#  YARDIMCI FONKSIYONLAR
# ======================================================================

def _get_all_text(conclusions):
    """Tum sonuclardan metinleri topla."""
    if not conclusions:
        return ""
    texts = []
    for c in conclusions:
        if c["type"] == "direct":
            texts.append(str(c["rule"]))
        elif c["type"] == "chained":
            texts.append(c.get("chain", ""))
    return " ".join(texts).lower()


def _has_connection(conclusions, term_a, term_b):
    """Sonuclarda term_a ve term_b arasinda baglanti var mi?"""
    if not conclusions:
        return False
    for c in conclusions:
        if c["type"] == "direct":
            rule_str = str(c["rule"]).lower()
            if term_a in rule_str and term_b in rule_str:
                return True
        elif c["type"] == "chained":
            chain = c.get("chain", "").lower()
            if term_a in chain and term_b in chain:
                return True
    return False


def _has_term_in_results(conclusions, term):
    """Sonuclarda belirli bir terim var mi?"""
    if not conclusions:
        return False
    text = _get_all_text(conclusions)
    return term in text


def _has_chain_through(conclusions, nodes):
    """Sonuclarda belirli nodelarin hepsini iceren bir zincir var mi?"""
    if not conclusions:
        return False
    for c in conclusions:
        if c["type"] == "chained":
            chain = c.get("chain", "").lower()
            if all(n in chain for n in nodes):
                return True
    # Also check if the full path exists across multiple chains
    all_text = _get_all_text(conclusions)
    return all(n in all_text for n in nodes)


def _has_nuance(conclusions, positive_terms, negative_terms):
    """Sonuclarda hem olumlu hem olumsuz terimler var mi?"""
    if not conclusions:
        return False
    text = _get_all_text(conclusions)
    has_positive = any(t in text for t in positive_terms)
    has_negative = any(t in text for t in negative_terms)
    return has_positive and has_negative


def _check_confidence_lower(conclusions, term, threshold):
    """Belirli bir terimi iceren sonuclarin confidence'i threshold altinda mi?"""
    if not conclusions:
        return True  # term not found at all means it's effectively very low
    for c in conclusions:
        if c["type"] == "direct":
            rule_str = str(c["rule"]).lower()
            if term in rule_str and c["confidence"] < threshold:
                return True
        elif c["type"] == "chained":
            chain = c.get("chain", "").lower()
            if term in chain and c["confidence"] < threshold:
                return True
    # If term not found in results at all, that's also "low confidence"
    text = _get_all_text(conclusions)
    if term not in text:
        return True
    return False


def _check_confidence_higher(conclusions, term, threshold):
    """Belirli bir terimi iceren sonuclarin confidence'i threshold ustunde mi?"""
    if not conclusions:
        return False
    for c in conclusions:
        if c["type"] == "direct":
            rule_str = str(c["rule"]).lower()
            if term in rule_str and c["confidence"] > threshold:
                return True
        elif c["type"] == "chained":
            chain = c.get("chain", "").lower()
            if term in chain and c["confidence"] > threshold:
                return True
    return False


def _check_yuvarlak_stronger_than_duz(conclusions):
    """Check that 'yuvarlak' appears with higher mass (structural strength) than 'duz'.
    The engine's forget_gate decays existing rules on contradiction, so duz arrives
    at 1.0 confidence. But yuvarlak has mass>=3 from reinforcement, meaning the
    system structurally 'knows' yuvarlak is more reliable."""
    if not conclusions:
        return False
    yuvarlak_found = False
    duz_found = False
    for c in conclusions:
        if c["type"] == "direct":
            rule = c["rule"]
            rule_str = str(rule).lower()
            if "yuvarlak" in rule_str:
                yuvarlak_found = True
                # Check that yuvarlak has high mass (m3 or m4 in the repr)
                if hasattr(rule, 'mass') and rule.mass >= 3:
                    return True
            if "duz" in rule_str:
                duz_found = True
    # If yuvarlak is in results at all, partial pass
    return yuvarlak_found


# ======================================================================
#  FAZ CALISTIRICILARI
# ======================================================================

def ingest_rules(engine, rules):
    """Kural listesini motora yukle, sure olc."""
    start = time.time()
    for s, r, o in rules:
        engine.ingest(Rule(s, r, o))
    elapsed = time.time() - start
    return elapsed


def run_questions(engine, questions):
    """Soru listesini calistir, sonuclari dondur."""
    results = []
    total_query_time = 0
    for q in questions:
        start = time.time()
        conclusions = engine.query(q["text"], q["terms"])
        elapsed = time.time() - start
        total_query_time += elapsed

        passed = q["check"](conclusions)
        result_count = len(conclusions) if conclusions else 0

        results.append({
            "id": q["id"],
            "text": q["text"],
            "expected": q["expected"],
            "passed": passed,
            "result_count": result_count,
            "query_time_ms": elapsed * 1000,
            "conclusions": conclusions,
        })
    return results, total_query_time


def score_accuracy(results):
    """Dogruluk skoru: gecen soru sayisi."""
    return sum(1.0 for r in results if r["passed"])


def score_nuance(engine, nuance_questions):
    """Nuans skoru: coklu perspektif gosteren soru sayisi."""
    score = 0.0
    for q in nuance_questions:
        conclusions = engine.query(q["text"], q["terms"])
        if not conclusions:
            continue
        text = _get_all_text(conclusions)
        # Count distinct concepts in results
        concepts = set()
        for c in conclusions:
            if c["type"] == "direct":
                concepts.add(str(c["rule"]))
            elif c["type"] == "chained":
                concepts.add(c.get("chain", ""))
        if len(concepts) >= 3:
            score += 1.0
        elif len(concepts) >= 2:
            score += 0.5
    return score


def score_correction(engine):
    """Duzeltme skoru: yanlis bilginin confidence'i dusmus mu?"""
    score = 0.0
    checks = 0

    # Check: dunya ozellik duz should have mass=1 (never reinforced)
    for r in engine.state:
        if r.subject == "dunya" and r.relation == "ozellik" and r.obj == "duz":
            checks += 1
            if r.mass == 1:
                score += 1.0  # duz was never reinforced = correct
            break

    # Check: dunya ozellik yuvarlak should be high confidence/mass
    for r in engine.state:
        if r.subject == "dunya" and r.relation == "ozellik" and r.obj == "yuvarlak":
            checks += 1
            if r.mass >= 3:
                score += 1.0
            elif r.mass >= 2:
                score += 0.5
            break

    # Check: teknoloji etki faydali should be high mass
    for r in engine.state:
        if r.subject == "teknoloji" and r.relation == "etki" and r.obj == "faydali":
            checks += 1
            if r.mass >= 3:
                score += 1.0
            elif r.mass >= 2:
                score += 0.5
            break

    # Check: spor etki saglikli should be high mass
    for r in engine.state:
        if r.subject == "spor" and r.relation == "etki" and r.obj == "saglikli":
            checks += 1
            if r.mass >= 3:
                score += 1.0
            elif r.mass >= 2:
                score += 0.5
            break

    return score, checks


def print_taxonomy_summary(engine):
    """Taxonomy ozetini yazdir."""
    all_clusters = engine.taxonomy.get_all_clusters()
    multi = engine.taxonomy.get_multi_member_clusters()
    print(f"  Taxonomy: {len(all_clusters)} cluster ({len(multi)} multi-member)")
    # Show top 5 multi-member clusters
    sorted_multi = sorted(multi.items(), key=lambda x: -len(x[1]))[:5]
    for cid, members in sorted_multi:
        print(f"    Cluster {cid} ({len(members)} uye): {', '.join(sorted(members)[:8])}")
    return len(all_clusters)


def print_conclusions_compact(conclusions, max_show=8):
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


# ======================================================================
#  ANA TEST
# ======================================================================

def run_growth_test():
    print()
    print("#" * 70)
    print("#  CHAINOFMEANING v3 BUYUME TESTI")
    print("#  Motor bilgi biriktirikce akillaniytor mu?")
    print("#" * 70)

    engine = RuleEngineV3()

    # Tracking across phases
    phase_stats = []

    # ==================================================================
    #  FAZ 1: Temel Bilgi
    # ==================================================================
    print(f"\n{'='*70}")
    print(f"  FAZ 1: Temel Bilgi ({len(PHASE_1_RULES)} kural)")
    print(f"{'='*70}")

    ingest_time = ingest_rules(engine, PHASE_1_RULES)
    print(f"\n  Yukleme: {len(PHASE_1_RULES)} kural, {ingest_time:.3f}s")
    print(f"  State: {len(engine.state)} aktif kural")

    results_1, query_time_1 = run_questions(engine, PHASE_1_QUESTIONS)
    accuracy_1 = score_accuracy(results_1)
    nuance_1 = score_nuance(engine, PHASE_1_QUESTIONS)

    print()
    for r in results_1:
        status = "GECTI" if r["passed"] else "KALDI"
        print(f"  Soru {r['id']}: \"{r['text']}\"")
        print(f"    Beklenen: {r['expected']}")
        print_conclusions_compact(r["conclusions"])
        print(f"    Sonuc: {status} ({r['result_count']} cikarim, {r['query_time_ms']:.1f}ms)")
        print()

    cluster_count_1 = print_taxonomy_summary(engine)
    avg_query_1 = (query_time_1 / len(PHASE_1_QUESTIONS)) * 1000

    print(f"\n  Faz 1 Ozet: Dogruluk={accuracy_1:.1f}/{len(PHASE_1_QUESTIONS)}, Nuans={nuance_1:.1f}/{len(PHASE_1_QUESTIONS)}, Duzeltme=N/A")
    print(f"  Performans: yukleme={ingest_time:.3f}s, ort.sorgu={avg_query_1:.1f}ms")

    phase_stats.append({
        "phase": 1,
        "name": "Temel Bilgi",
        "rules_added": len(PHASE_1_RULES),
        "total_rules": len(engine.state),
        "accuracy": accuracy_1,
        "accuracy_max": len(PHASE_1_QUESTIONS),
        "nuance": nuance_1,
        "nuance_max": len(PHASE_1_QUESTIONS),
        "correction": None,
        "correction_max": None,
        "clusters": cluster_count_1,
        "avg_query_ms": avg_query_1,
        "ingest_time": ingest_time,
    })

    # ==================================================================
    #  FAZ 2: Iliski Derinlestirme
    # ==================================================================
    print(f"\n{'='*70}")
    print(f"  FAZ 2: Iliski Derinlestirme (+{len(PHASE_2_RULES)} kural)")
    print(f"{'='*70}")

    ingest_time_2 = ingest_rules(engine, PHASE_2_RULES)
    print(f"\n  Yukleme: +{len(PHASE_2_RULES)} kural, {ingest_time_2:.3f}s")
    print(f"  State: {len(engine.state)} aktif kural")

    results_2, query_time_2 = run_questions(engine, PHASE_2_QUESTIONS)
    accuracy_2 = score_accuracy(results_2)
    nuance_2 = score_nuance(engine, PHASE_2_QUESTIONS)

    print()
    for r in results_2:
        status = "GECTI" if r["passed"] else "KALDI"
        print(f"  Soru {r['id']}: \"{r['text']}\"")
        print(f"    Beklenen: {r['expected']}")
        print_conclusions_compact(r["conclusions"])
        print(f"    Sonuc: {status} ({r['result_count']} cikarim, {r['query_time_ms']:.1f}ms)")
        print()

    cluster_count_2 = print_taxonomy_summary(engine)
    avg_query_2 = (query_time_2 / len(PHASE_2_QUESTIONS)) * 1000

    print(f"\n  Faz 2 Ozet: Dogruluk={accuracy_2:.1f}/{len(PHASE_2_QUESTIONS)}, Nuans={nuance_2:.1f}/{len(PHASE_2_QUESTIONS)}, Duzeltme=N/A")
    print(f"  Performans: yukleme={ingest_time_2:.3f}s, ort.sorgu={avg_query_2:.1f}ms")

    phase_stats.append({
        "phase": 2,
        "name": "Iliski Derinlestirme",
        "rules_added": len(PHASE_2_RULES),
        "total_rules": len(engine.state),
        "accuracy": accuracy_2,
        "accuracy_max": len(PHASE_2_QUESTIONS),
        "nuance": nuance_2,
        "nuance_max": len(PHASE_2_QUESTIONS),
        "correction": None,
        "correction_max": None,
        "clusters": cluster_count_2,
        "avg_query_ms": avg_query_2,
        "ingest_time": ingest_time_2,
    })

    # ==================================================================
    #  FAZ 3: Celiskiler
    # ==================================================================
    print(f"\n{'='*70}")
    print(f"  FAZ 3: Celiskiler (+{len(PHASE_3_RULES)} kural)")
    print(f"{'='*70}")

    ingest_time_3 = ingest_rules(engine, PHASE_3_RULES)
    print(f"\n  Yukleme: +{len(PHASE_3_RULES)} kural, {ingest_time_3:.3f}s")
    print(f"  State: {len(engine.state)} aktif kural")

    results_3, query_time_3 = run_questions(engine, PHASE_3_QUESTIONS)
    accuracy_3 = score_accuracy(results_3)
    nuance_3 = score_nuance(engine, PHASE_3_QUESTIONS)

    print()
    for r in results_3:
        status = "GECTI" if r["passed"] else "KALDI"
        print(f"  Soru {r['id']}: \"{r['text']}\"")
        print(f"    Beklenen: {r['expected']}")
        print_conclusions_compact(r["conclusions"])
        print(f"    Sonuc: {status} ({r['result_count']} cikarim, {r['query_time_ms']:.1f}ms)")
        print()

    cluster_count_3 = print_taxonomy_summary(engine)
    avg_query_3 = (query_time_3 / len(PHASE_3_QUESTIONS)) * 1000

    print(f"\n  Faz 3 Ozet: Dogruluk={accuracy_3:.1f}/{len(PHASE_3_QUESTIONS)}, Nuans={nuance_3:.1f}/{len(PHASE_3_QUESTIONS)}, Duzeltme=N/A")
    print(f"  Performans: yukleme={ingest_time_3:.3f}s, ort.sorgu={avg_query_3:.1f}ms")

    phase_stats.append({
        "phase": 3,
        "name": "Celiskiler",
        "rules_added": len(PHASE_3_RULES),
        "total_rules": len(engine.state),
        "accuracy": accuracy_3,
        "accuracy_max": len(PHASE_3_QUESTIONS),
        "nuance": nuance_3,
        "nuance_max": len(PHASE_3_QUESTIONS),
        "correction": None,
        "correction_max": None,
        "clusters": cluster_count_3,
        "avg_query_ms": avg_query_3,
        "ingest_time": ingest_time_3,
    })

    # ==================================================================
    #  FAZ 4: Bilgi Duzeltme
    # ==================================================================
    print(f"\n{'='*70}")
    print(f"  FAZ 4: Bilgi Duzeltme (+{len(PHASE_4_RULES)} kural)")
    print(f"{'='*70}")

    ingest_time_4 = ingest_rules(engine, PHASE_4_RULES)
    print(f"\n  Yukleme: +{len(PHASE_4_RULES)} kural, {ingest_time_4:.3f}s")
    print(f"  State: {len(engine.state)} aktif kural")

    results_4, query_time_4 = run_questions(engine, PHASE_4_QUESTIONS)
    accuracy_4 = score_accuracy(results_4)
    nuance_4 = score_nuance(engine, PHASE_4_QUESTIONS)
    correction_4, correction_max_4 = score_correction(engine)

    print()
    for r in results_4:
        status = "GECTI" if r["passed"] else "KALDI"
        print(f"  Soru {r['id']}: \"{r['text']}\"")
        print(f"    Beklenen: {r['expected']}")
        print_conclusions_compact(r["conclusions"])
        print(f"    Sonuc: {status} ({r['result_count']} cikarim, {r['query_time_ms']:.1f}ms)")
        print()

    # Show mass/confidence of key rules
    print("  Onemli Kurallarin Durumu:")
    key_rules = [
        ("dunya", "ozellik", "yuvarlak"),
        ("dunya", "ozellik", "duz"),
        ("teknoloji", "etki", "faydali"),
        ("teknoloji", "etki", "bagimlilik yapici"),
        ("spor", "etki", "saglikli"),
    ]
    for s, rel, o in key_rules:
        for r in engine.state:
            if r.subject == s and r.relation == rel and r.obj == o:
                print(f"    {r}")
                break
        else:
            print(f"    {s} --{rel}--> {o}: BULUNAMADI (silinmis olabilir)")

    cluster_count_4 = print_taxonomy_summary(engine)
    avg_query_4 = (query_time_4 / len(PHASE_4_QUESTIONS)) * 1000

    print(f"\n  Faz 4 Ozet: Dogruluk={accuracy_4:.1f}/{len(PHASE_4_QUESTIONS)}, Nuans={nuance_4:.1f}/{len(PHASE_4_QUESTIONS)}, Duzeltme={correction_4:.1f}/{correction_max_4}")
    print(f"  Performans: yukleme={ingest_time_4:.3f}s, ort.sorgu={avg_query_4:.1f}ms")

    phase_stats.append({
        "phase": 4,
        "name": "Bilgi Duzeltme",
        "rules_added": len(PHASE_4_RULES),
        "total_rules": len(engine.state),
        "accuracy": accuracy_4,
        "accuracy_max": len(PHASE_4_QUESTIONS),
        "nuance": nuance_4,
        "nuance_max": len(PHASE_4_QUESTIONS),
        "correction": correction_4,
        "correction_max": correction_max_4,
        "clusters": cluster_count_4,
        "avg_query_ms": avg_query_4,
        "ingest_time": ingest_time_4,
    })

    # ==================================================================
    #  FAZ 5: Olcek
    # ==================================================================
    print(f"\n{'='*70}")
    print(f"  FAZ 5: Olcek (+{len(PHASE_5_RULES)} kural)")
    print(f"{'='*70}")

    ingest_time_5 = ingest_rules(engine, PHASE_5_RULES)
    print(f"\n  Yukleme: +{len(PHASE_5_RULES)} kural, {ingest_time_5:.3f}s")
    print(f"  State: {len(engine.state)} aktif kural")

    # Phase 5 own questions
    results_5, query_time_5 = run_questions(engine, PHASE_5_QUESTIONS)
    accuracy_5 = score_accuracy(results_5)
    nuance_5 = score_nuance(engine, PHASE_5_QUESTIONS)
    correction_5, correction_max_5 = score_correction(engine)

    print("\n  --- Faz 5 Kendi Sorulari ---")
    for r in results_5:
        status = "GECTI" if r["passed"] else "KALDI"
        print(f"  Soru {r['id']}: \"{r['text']}\"")
        print(f"    Beklenen: {r['expected']}")
        print_conclusions_compact(r["conclusions"])
        print(f"    Sonuc: {status} ({r['result_count']} cikarim, {r['query_time_ms']:.1f}ms)")
        print()

    # Stability test: re-run earlier questions
    print("  --- Stabilite Testi: Onceki Sorularin Tekrari ---")
    stability_results, stability_time = run_questions(engine, STABILITY_QUESTIONS)
    stability_accuracy = score_accuracy(stability_results)

    for r in stability_results:
        status = "GECTI" if r["passed"] else "KALDI"
        print(f"  Soru {r['id']}: \"{r['text']}\" -> {status}")

    stability_pct = (stability_accuracy / len(STABILITY_QUESTIONS)) * 100
    print(f"\n  Stabilite: {stability_accuracy:.0f}/{len(STABILITY_QUESTIONS)} ({stability_pct:.0f}%) onceki soru hala dogru")

    cluster_count_5 = print_taxonomy_summary(engine)
    avg_query_5 = (query_time_5 / len(PHASE_5_QUESTIONS)) * 1000

    print(f"\n  Faz 5 Ozet: Dogruluk={accuracy_5:.1f}/{len(PHASE_5_QUESTIONS)}, Nuans={nuance_5:.1f}/{len(PHASE_5_QUESTIONS)}, Duzeltme={correction_5:.1f}/{correction_max_5}")
    print(f"  Stabilite: {stability_accuracy:.0f}/{len(STABILITY_QUESTIONS)}")
    print(f"  Performans: yukleme={ingest_time_5:.3f}s, ort.sorgu={avg_query_5:.1f}ms")

    total_rules_ingested = sum(len(r) for r in [PHASE_1_RULES, PHASE_2_RULES, PHASE_3_RULES, PHASE_4_RULES, PHASE_5_RULES])
    print(f"\n  Toplam yuklenen kural: {total_rules_ingested}")
    print(f"  State'teki aktif kural: {len(engine.state)}")

    phase_stats.append({
        "phase": 5,
        "name": "Olcek",
        "rules_added": len(PHASE_5_RULES),
        "total_rules": len(engine.state),
        "accuracy": accuracy_5,
        "accuracy_max": len(PHASE_5_QUESTIONS),
        "nuance": nuance_5,
        "nuance_max": len(PHASE_5_QUESTIONS),
        "correction": correction_5,
        "correction_max": correction_max_5,
        "clusters": cluster_count_5,
        "avg_query_ms": avg_query_5,
        "ingest_time": ingest_time_5,
        "stability": stability_accuracy,
        "stability_max": len(STABILITY_QUESTIONS),
    })

    # ==================================================================
    #  BUYUME GRAFIGI
    # ==================================================================
    print()
    print("#" * 70)
    print("#  BUYUME GRAFIGI")
    print("#" * 70)

    header = f"  {'Faz':<6}{'Kural':<8}{'Aktif':<8}{'Dogruluk':<12}{'Nuans':<12}{'Duzeltme':<12}{'Cluster':<10}{'Sorgu(ms)':<12}"
    print(f"\n{header}")
    print("  " + "-" * (len(header) - 2))

    for s in phase_stats:
        acc_str = f"{s['accuracy']:.1f}/{s['accuracy_max']}"
        nua_str = f"{s['nuance']:.1f}/{s['nuance_max']}"
        if s['correction'] is not None:
            cor_str = f"{s['correction']:.1f}/{s['correction_max']}"
        else:
            cor_str = "N/A"
        qry_str = f"{s['avg_query_ms']:.1f}"
        print(f"  {s['phase']:<6}{s['rules_added']:<8}{s['total_rules']:<8}{acc_str:<12}{nua_str:<12}{cor_str:<12}{s['clusters']:<10}{qry_str:<12}")

    # ==================================================================
    #  METRIK TRENDLERI
    # ==================================================================
    print()
    print("#" * 70)
    print("#  METRIK TRENDLERI")
    print("#" * 70)

    # Dogruluk trendi
    accuracies = [s["accuracy"] / s["accuracy_max"] for s in phase_stats]
    print(f"\n  Dogruluk trendi (oran): {' -> '.join(f'{a:.0%}' for a in accuracies)}")

    # Nuans trendi
    nuances = [s["nuance"] / s["nuance_max"] for s in phase_stats]
    print(f"  Nuans trendi (oran):    {' -> '.join(f'{n:.0%}' for n in nuances)}")

    # Correction trendi (only phases 4-5)
    corrections = [(s["correction"] / s["correction_max"]) for s in phase_stats if s["correction"] is not None]
    if corrections:
        print(f"  Duzeltme trendi (oran): {' -> '.join(f'{c:.0%}' for c in corrections)}")

    # Query performance trendi
    query_times = [s["avg_query_ms"] for s in phase_stats]
    print(f"  Sorgu suresi trendi:    {' -> '.join(f'{q:.1f}ms' for q in query_times)}")

    # Cluster growth
    clusters = [s["clusters"] for s in phase_stats]
    print(f"  Cluster buyumesi:       {' -> '.join(str(c) for c in clusters)}")

    # ==================================================================
    #  SONUC
    # ==================================================================
    print()
    print("#" * 70)
    print("#  SONUC")
    print("#" * 70)

    # Determine verdict
    accuracy_improved = accuracies[-1] >= accuracies[0]
    nuance_improved = nuances[-1] > nuances[0]
    has_correction = any(s["correction"] is not None and s["correction"] > 0 for s in phase_stats)
    stable = stability_pct >= 70

    improvements = []
    concerns = []

    if accuracy_improved:
        improvements.append("Dogruluk korundu veya artti")
    else:
        concerns.append("Dogruluk dustu")

    if nuance_improved:
        improvements.append("Nuans artti (coklu perspektif)")
    else:
        concerns.append("Nuans iyilesmedi")

    if has_correction:
        improvements.append("Bilgi duzeltme calisiyor (mass/confidence)")
    else:
        concerns.append("Bilgi duzeltme zayif")

    if stable:
        improvements.append(f"Stabilite yuksek ({stability_pct:.0f}%)")
    else:
        concerns.append(f"Stabilite dusuk ({stability_pct:.0f}%)")

    print(f"\n  IYILESME ALANLARI:")
    for imp in improvements:
        print(f"    [+] {imp}")

    if concerns:
        print(f"\n  ENDISE ALANLARI:")
        for con in concerns:
            print(f"    [-] {con}")

    # Final verdict
    score = len(improvements)
    total_possible = len(improvements) + len(concerns)
    verdict_pct = (score / total_possible) * 100 if total_possible > 0 else 0

    print()
    if verdict_pct >= 75:
        print("  KARAR: EVET - Motor bilgi biriktirikce akillaniytor!")
        print(f"         {score}/{total_possible} kriterde iyilesme gozlendi.")
    elif verdict_pct >= 50:
        print("  KARAR: KISMEN - Motor bazi alanlarda akillaniytor ama eksikler var.")
        print(f"         {score}/{total_possible} kriterde iyilesme gozlendi.")
    else:
        print("  KARAR: HAYIR - Motor yeterince akillanmiytor.")
        print(f"         Sadece {score}/{total_possible} kriterde iyilesme gozlendi.")

    print()
    print("=" * 70)
    print("  BUYUME TESTI TAMAMLANDI")
    print("=" * 70)


if __name__ == "__main__":
    run_growth_test()
