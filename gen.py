#!/usr/bin/env python3
"""Wisteria static site generator.  Edit CONFIG below, run:  python3 gen.py   -> ./site/
Anything left as None renders as a highlighted [placeholder]. Text produced by inf() is
something inferred from the strategy (not stated in it) - confirm it, then reword/keep."""
import os, shutil, random, html as H
from urllib.parse import quote

# ======================= CONFIG (fill in, then re-run) =======================
CONFIG = {
 "HIGHLIGHTS": True,        # False = no highlights and no on-page toggle (final build)
 "SITE_URL": None,          # e.g. "https://wisteria.pl" (used in canonical, hreflang, sitemap)
 "phone": None, "email": None, "postcode": None, "instagram": None,   # instagram = full profile URL
 "fitssey": None,           # full Fitssey URL (schedule + booking + pass purchase)
 "hours": None,             # studio / reception hours, free text (PL) and (EN) below
 "hours_en": None,
 "form_endpoint": None,     # e.g. Formspree/Getform/own endpoint URL accepting JSON POST
 "ga_id": None,             # GA4 measurement ID, e.g. "G-XXXXXXXXXX" (loaded only after consent)
 "controller": None,        # legal name + address of data controller (privacy policy)
 # prices (text incl. currency, e.g. "60 zł")
 "price_trial": None, "price_single": None, "price_3": None, "price_4": None, "price_8": None,
 "price_unlimited": None, "price_private": None, "price_couples": None,
 "validity_3": None, "validity_4": None, "validity_8": None, "validity_unlimited": None,
 "pass_scope": None,        # which classes passes cover (e.g. do they include Ukrainian/mother-child?)
 "voucher_price_1": None, "voucher_price_2": None, "voucher_price_3": None, "voucher_validity": None,
 "cancellation": None,      # booking cancellation policy
 "what_to_bring": None,
}
# Lists: leave empty to show placeholders. Tuples are documented next to each list.
SCHEDULE = []   # (day_pl, day_en, time, class, level, teacher)
TEACHERS = []   # (name, pl_bio, en_bio, specialisation_pl, specialisation_en)
WORKSHOPS = []  # (title_pl, title_en, date, pl_description, en_description)

LABELS = {  # key: (PL label, EN label) shown inside placeholders
 "SITE_URL":("adres strony","site URL"),"phone":("telefon","phone"),"email":("e-mail","email"),
 "postcode":("kod pocztowy","postcode"),"instagram":("Instagram","Instagram URL"),"fitssey":("link do Fitssey","Fitssey link"),
 "hours":("godziny otwarcia","opening hours"),"hours_en":("opening hours","opening hours"),"controller":("administrator danych","data controller"),
 "price_trial":("cena: zajęcia próbne","price: trial class"),"price_single":("cena: pojedyncze zajęcia","price: single class"),
 "price_3":("cena: karnet 3","price: 3-class pass"),"price_4":("cena: karnet 4","price: 4-class pass"),
 "price_8":("cena: karnet 8","price: 8-class pass"),"price_unlimited":("cena: karnet open","price: unlimited pass"),
 "price_private":("cena: zajęcia indywidualne","price: private"),"price_couples":("cena: zajęcia dla par","price: couples"),
 "validity_3":("ważność karnetu 3","validity 3-pass"),"validity_4":("ważność karnetu 4","validity 4-pass"),
 "validity_8":("ważność karnetu 8","validity 8-pass"),"validity_unlimited":("ważność karnetu open","validity unlimited"),
 "pass_scope":("jakie zajęcia obejmują karnety","which classes passes cover"),
 "voucher_price_1":("cena bonu: 1 wejście","voucher price: 1 class"),"voucher_price_2":("cena bonu: 2 wejścia","voucher price: 2 classes"),
 "voucher_price_3":("cena bonu: 3 wejścia","voucher price: 3 classes"),"voucher_validity":("ważność bonu","voucher validity"),
 "cancellation":("zasady odwoływania rezerwacji","cancellation policy"),"what_to_bring":("co zabrać na zajęcia","what to bring"),
}
STUDIO = "Wisteria Studio"; ADDR = "Dobra 14/16"; CITY_PL, CITY_EN = "Warszawa", "Warsaw"
MAPQ = quote("Dobra 14/16, Warszawa, Polska")
MAP_LINK = f"https://www.google.com/maps/search/?api=1&query={MAPQ}"
MAP_EMBED = f"https://www.google.com/maps?q={MAPQ}&output=embed"
# =============================================================================
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, "site")
CUR = {"lang": "pl", "slug": ""}; INF = []; MISSING = set()
def t(pl, en): return pl if CUR["lang"] == "pl" else en
def e(s): return H.escape(str(s))
def v(key):
    if CONFIG.get(key) is not None: return e(CONFIG[key])
    MISSING.add(key); l = LABELS[key]; return f'<mark class="ph" data-key="{key}">[{e(t(*l))}]</mark>'
def inf(pl, en):
    INF.append((CUR["slug"], en)); return f'<mark class="inf" title="{e(t("Do potwierdzenia","To confirm"))}">{pl if CUR["lang"]=="pl" else en}</mark>'
def url(key, text, cls="btn", track=None):
    val = CONFIG.get(key); tr = f' data-track="{track}"' if track else ""
    if val: return f'<a class="{cls}" href="{e(val)}" target="_blank" rel="noopener"{tr}>{text}</a>'
    MISSING.add(key); return f'<a class="{cls} ph-link" href="#" title="[{e(t(*LABELS[key]))}]" onclick="return false">{text}</a>'
def href(slug): return f"{slug}.html"
def contact_link(key, kind):
    val = CONFIG.get(key)
    if val is None: return v(key)
    return f'<a href="{kind}{e(val)}">{e(val)}</a>' if kind else f'<a href="{e(val)}" rel="noopener" target="_blank">{e(val)}</a>'

NAV = [("classes","Zajęcia","Classes"),("schedule","Grafik i zapisy","Schedule & booking"),("pricing","Cennik","Pricing"),
       ("teachers","Instruktorzy","Teachers"),("workshops","Warsztaty","Workshops"),("vouchers","Bony podarunkowe","Gift vouchers"),("contact","Kontakt","Contact")]
TITLES = {"index":("Joga i pilates w Warszawie","Yoga and Pilates in Warsaw"),"classes":("Zajęcia","Classes"),"schedule":("Grafik i zapisy","Schedule and booking"),
 "pricing":("Cennik i karnety","Pricing and passes"),"teachers":("Instruktorzy","Teachers"),"workshops":("Warsztaty i praktyki specjalne","Workshops and special practices"),
 "vouchers":("Bony podarunkowe","Gift vouchers"),"groups":("Grupy i firmy","Groups and companies"),"contact":("Kontakt i dojazd","Contact and location"),"privacy":("Polityka prywatności","Privacy policy")}
SLUGS = list(TITLES)

def raceme_svg():
    r = random.Random(11); cols = ["#b6a2d4","#a08bc6","#c9bbe2","#8d76b0","#d6cbe9"]; g = []
    for i, x in enumerate(range(30, 1000, 78)):
        L = r.randint(80, 185); p = [f'<path d="M{x} 0 Q{x+r.randint(-9,9)} {L*.5:.0f} {x+r.randint(-7,7)} {L}" stroke="#7d9a82" stroke-width="1.5" fill="none" opacity=".6"/>']
        y = 12
        while y < L:
            k = 3 if y < L*.55 else 2
            for j in range(k):
                dx = (j-(k-1)/2)*8+r.uniform(-2,2); rad = r.uniform(4,6.2)*(.55+.55*(1-y/L))
                p.append(f'<circle cx="{x+dx:.1f}" cy="{y:.1f}" r="{rad:.1f}" fill="{r.choice(cols)}" opacity=".9"/>')
            if r.random() < .12: p.append(f'<ellipse cx="{x+r.choice((-14,14))}" cy="{y:.0f}" rx="9" ry="3.5" fill="#7d9a82" opacity=".55" transform="rotate({r.randint(-30,30)} {x} {y:.0f})"/>')
            y += r.uniform(8, 11)
        g.append(f'<g class="sway" style="transform-origin:{x}px 0;animation-delay:-{i*1.3:.1f}s">{"".join(p)}</g>')
    return f'<svg class="rac" viewBox="0 0 1000 200" preserveAspectRatio="xMidYMin meet" aria-hidden="true">{"".join(g)}</svg>'

FIELDS = {  # (name, type, pl, en, required, options[(pl,en)])
 "enrol": [("name","text","Imię i nazwisko","Full name",1,0),("email","email","E-mail","Email",1,0),("phone","tel","Telefon (opcjonalnie)","Phone (optional)",0,0),
  ("interest","select","Czym jesteś zainteresowany/a","What are you interested in",1,[("Nie wiem jeszcze, proszę o pomoc","Not sure yet, please help me choose"),("Joga","Yoga"),("Pilates","Pilates"),("Joga po ukraińsku","Ukrainian-language yoga"),("Joga mama i dziecko","Mother-and-child yoga"),("Zajęcia indywidualne lub dla par","Private or couples session")]),
  ("level","select","Twoje doświadczenie","Your experience",1,[("Dopiero zaczynam","I'm just starting"),("Ćwiczyłem/am trochę","I've practised a little"),("Ćwiczę regularnie","I practise regularly")]),
  ("message","textarea","Wiadomość (opcjonalnie)","Message (optional)",0,0)],
 "group": [("name","text","Imię i nazwisko","Full name",1,0),("email","email","E-mail","Email",1,0),("phone","tel","Telefon","Phone",0,0),
  ("size","number","Liczba osób","Number of people",1,0),("date","text","Preferowany termin","Preferred date",0,0),
  ("message","textarea","Czego szukacie?","What are you looking for?",1,0)],
 "corporate": [("company","text","Firma","Company",1,0),("name","text","Osoba kontaktowa","Contact person",1,0),("email","email","E-mail","Email",1,0),("phone","tel","Telefon","Phone",0,0),
  ("size","number","Szacowana liczba uczestników","Estimated participants",1,0),
  ("format","select","Format","Format",1,[("Zajęcia cykliczne","Regular classes"),("Jednorazowe wydarzenie","One-off event"),("Warsztat","Workshop"),("Jeszcze nie wiem","Not sure yet")]),
  ("message","textarea","Szczegóły","Details",0,0)],
 "voucher": [("buyer","text","Twoje imię i nazwisko","Your full name",1,0),("email","email","Twój e-mail","Your email",1,0),("phone","tel","Telefon (opcjonalnie)","Phone (optional)",0,0),
  ("visits","select","Liczba wejść w bonie","Number of classes",1,[("1 zajęcia","1 class"),("2 zajęcia","2 classes"),("3 zajęcia","3 classes")]),
  ("recipient","text","Dla kogo (imię)","Recipient's name",1,0),("note","textarea","Życzenia na kartce (opcjonalnie)","Message for the card (optional)",0,0),
  ("when","text","Kiedy bon ma być gotowy (np. data urodzin)","When you need it (e.g. birthday date)",0,0)],
 "contact": [("name","text","Imię","Name",1,0),("email","email","E-mail","Email",1,0),
  ("topic","select","Temat","Topic",1,[("Wybór zajęć i poziom","Choosing a class and level"),("Rezerwacje i karnety","Booking and passes"),("Bony podarunkowe","Gift vouchers"),("Inne","Other")]),
  ("message","textarea","Wiadomość","Message",1,0)]}
SUBMIT = {"enrol":("Wyślij zgłoszenie","Send request"),"group":("Wyślij zapytanie","Send enquiry"),"corporate":("Wyślij zapytanie","Send enquiry"),"voucher":("Zamów bon","Order voucher"),"contact":("Wyślij wiadomość","Send message")}
def form(fid):
    h = [f'<form class="f" id="{fid}" data-form="{fid}" data-ok="{e(t("Dziękujemy. Wiadomość została wysłana.","Thank you. Your message has been sent."))}" data-err="{e(t("Nie udało się wysłać. Spróbuj ponownie lub napisz do nas bezpośrednio.","We couldn’t send this. Please try again or contact us directly."))}" data-noconf="{e(t("Formularz nie ma jeszcze skonfigurowanego adresu odbioru.","This form has no receiving address configured yet."))}">',
         f'<input type="hidden" name="_form" value="{fid}"><input type="hidden" name="_lang" value="{CUR["lang"]}"><div class="hp" aria-hidden="true"><label>Leave empty<input name="_gotcha" tabindex="-1" autocomplete="off"></label></div>']
    for n, ty, pl, en, rq, op in FIELDS[fid]:
        lab = e(t(pl, en)) + ("" if rq else ""); req = " required" if rq else ""; i = f"{fid}-{n}"
        if ty == "select": ctl = f'<select id="{i}" name="{n}"{req}><option value="">–</option>' + "".join(f'<option value="{e(o[1])}">{e(t(*o))}</option>' for o in op) + "</select>"
        elif ty == "textarea": ctl = f'<textarea id="{i}" name="{n}"{req}></textarea>'
        else: ctl = f'<input id="{i}" name="{n}" type="{ty}"{req}' + (' min="1"' if ty == "number" else "") + ">"
        h.append(f'<label for="{i}">{lab}{" *" if rq else ""}</label>{ctl}'.replace('<label for', '<div style="display:grid;gap:.25rem"><label for', 1).replace('</label>', '</label>', 1) + "</div>")
    h.append(f'<label class="chk" for="{fid}-c"><input id="{fid}-c" type="checkbox" name="consent" value="yes" required><span>{t("Akceptuję","I accept the")} <a href="{href("privacy")}">{t("politykę prywatności","privacy policy")}</a> {t("i zgadzam się na kontakt w sprawie mojego zapytania.","and agree to be contacted about my enquiry.")}</span></label>')
    h.append(f'<div><button class="btn" type="submit">{e(t(*SUBMIT[fid]))}</button></div><p class="msg" role="status" aria-live="polite"></p></form>')
    return "".join(h)

def fix_label(s): return s
def page(slug, body, lead=""):
    CUR["slug"] = slug; lang = CUR["lang"]; P = "" if lang == "pl" else "../"
    title = t(*TITLES[slug]); site = (CONFIG["SITE_URL"] or "https://YOUR-DOMAIN.example").rstrip("/")
    if not CONFIG["SITE_URL"]: MISSING.add("SITE_URL")
    fn = "" if slug == "index" else slug + ".html"; pl_u, en_u = f"{site}/{fn}", f"{site}/en/{fn}"
    other = (f"en/{slug}.html" if lang == "pl" else f"../{slug}.html")
    desc = lead or t("Joga i pilates w małych grupach, Warszawa, ul. Dobra 14/16.", "Yoga and Pilates in small groups, Warsaw, Dobra 14/16.")
    nav = "".join(f'<li><a href="{href(s)}"' + (' aria-current="page"' if s == slug else "") + f'>{t(a,b)}</a></li>' for s, a, b in NAV)
    langsw = (f'<span>PL</span><a href="{other}" hreflang="en" lang="en">EN</a>' if lang == "pl" else f'<a href="{other}" hreflang="pl" lang="pl">PL</a><span>EN</span>')
    full_title = f"{title} | Wisteria" if slug != "index" else f"Wisteria | {title}"
    hl = CONFIG["HIGHLIGHTS"]
    tog = f'<button class="hltoggle" data-hl-toggle type="button">{t("Podświetlenia wł./wył.","Highlights on/off")}</button>' if hl else ""
    ig = CONFIG.get("instagram"); igl = f'<a href="{e(ig)}" rel="noopener" target="_blank">Instagram</a>' if ig else f'<mark class="ph">[Instagram]</mark>'
    if not ig: MISSING.add("instagram")
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full_title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{pl_u if lang=='pl' else en_u}"><link rel="alternate" hreflang="pl" href="{pl_u}"><link rel="alternate" hreflang="en" href="{en_u}"><link rel="alternate" hreflang="x-default" href="{pl_u}">
<meta property="og:title" content="{e(full_title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website">
<link rel="icon" href="{P}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Oldenburg&family=Parisienne&display=swap"><link rel="stylesheet" href="{P}assets/style.css">
<script defer src="{P}assets/site.js"></script></head>
<body class="{'' if hl else 'clean'}" data-endpoint="{e(CONFIG['form_endpoint'] or '')}" data-ga="{e(CONFIG['ga_id'] or '')}" data-email="{e(CONFIG['email'] or '')}">
<a class="skip" href="#main">{t("Przejdź do treści","Skip to content")}</a>
<header class="top"><div class="wrap bar"><a class="logo" href="{href('index')}" aria-label="Wisteria">Wisteria</a>
<nav id="nav" aria-label="{t('Menu główne','Main menu')}"><ul>{nav}</ul></nav>
<div class="lang" aria-label="{t('Język','Language')}">{langsw}</div>
<button class="burger" aria-expanded="false" aria-controls="nav">{t("Menu","Menu")}</button></div></header>
<main id="main">{body}</main>
<footer><div class="wrap"><div class="three"><div><h3>Wisteria Studio</h3><p>{ADDR}, {v('postcode')} {t(CITY_PL,CITY_EN)}<br><a href="{MAP_LINK}" target="_blank" rel="noopener">{t("Pokaż w Mapach Google","Open in Google Maps")}</a></p></div>
<div><h3>{t("Kontakt","Contact")}</h3><p>{contact_link('phone','tel:')}<br>{contact_link('email','mailto:')}<br>{igl}</p></div>
<div><h3>{t("Na skróty","Quick links")}</h3><ul><li><a href="{href('groups')}">{t(*TITLES['groups'])}</a></li><li><a href="{href('privacy')}">{t(*TITLES['privacy'])}</a></li><li><button class="linkbtn" data-cc-open type="button">{t("Ustawienia cookies","Cookie settings")}</button></li></ul></div></div>
<small>© {STUDIO}. {t("Wszystkie prawa zastrzeżone.","All rights reserved.")}</small></div></footer>
<div class="cc" id="cc" hidden role="dialog" aria-label="Cookies"><p>{t("Używamy plików cookie do statystyk odwiedzin, ale tylko za Twoją zgodą. Mapa Google może ustawiać własne pliki cookie. Szczegóły w","We use cookies for visit statistics only with your consent. The Google map may set its own cookies. Details in the")} <a href="{href('privacy')}">{t("polityce prywatności","privacy policy")}</a>.</p>
<button class="btn" data-cc="yes" type="button">{t("Akceptuję","Accept")}</button> <button class="btn ghost" data-cc="no" type="button">{t("Tylko niezbędne","Necessary only")}</button></div>{tog}</body></html>'''

def head(h1, sub=""): return f'<div class="pagehead"><div class="wrap"><h1>{h1}</h1>{f"<p>{sub}</p>" if sub else ""}</div></div>'
def sec(inner, cls=""): return f'<section class="{cls}"><div class="wrap">{inner}</div></section>'
def faq(items): return '<div class="faq">' + "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items) + "</div>"

def p_index():
    hero = f'<div class="hero">{raceme_svg()}<div class="wrap"><h1>{t("Czas dla siebie, w ruchu i oddechu","Time for yourself, in movement and breath")}</h1><p class="lead">{t("Joga i pilates w małych grupach, do 10 osób. Zajęcia prowadzi stały zespół instruktorów, którzy poznają Ciebie i Twoją praktykę.","Yoga and Pilates in small groups of up to 10 people. A consistent team of teachers gets to know you and your practice.")}</p><div class="btns"><a class="btn" href="{href("schedule")}#zapis" data-track="hero_enrol">{t("Umów pierwsze zajęcia","Book your first class")}</a><a class="btn ghost" href="{href("schedule")}">{t("Zobacz grafik","See the schedule")}</a></div></div></div>'
    paths = f'''<h2>{t("Zacznij tak, jak Ci wygodnie","Start in the way that suits you")}</h2><div class="three">
<div class="path"><h3>{t("Dopiero zaczynasz","Just starting")}</h3><p>{t("Nowy w jodze? Zapraszamy. Pomożemy Ci znaleźć zajęcia, które będą dla Ciebie dobre. Zacznij od jednych zajęć i zobacz, jak się czujesz.","New to yoga? You’re welcome here. We’ll help you find a class that feels right. Start with one class and see how it feels.")}</p><a href="{href("schedule")}#zapis">{t("Umów pierwsze zajęcia","Book a first class")}</a></div>
<div class="path"><h3>{t("Praktykujesz regularnie","Practising regularly")}</h3><p>{t("Joga i pilates w jednym karnecie, stali instruktorzy i grupy do 10 osób, więc nauczyciel ma czas zauważyć Twoją praktykę i ją skorygować.","Yoga and Pilates in one membership, consistent teachers and groups of up to 10, so your teacher has time to notice your practice and adjust it.")}</p><a href="{href("pricing")}">{t("Zobacz karnety","See passes")}</a></div>
<div class="path"><h3>{t("Szukasz prezentu","Looking for a gift")}</h3><p>{t("Bon na zajęcia to prezent do wykorzystania we własnym tempie. Obdarowana osoba sama wybierze jogę, pilates lub połączenie obu.","A class voucher is a gift to use at one’s own pace. The recipient chooses yoga, Pilates or a mix of both.")} {inf("(zakres bonów 1–3 wejścia do potwierdzenia)","(1–3 class voucher range to be confirmed)")}</p><a href="{href("vouchers")}">{t("Zobacz bony","See vouchers")}</a></div></div>'''
    diff = f'''<h2>{t("Dlaczego Wisteria","Why Wisteria")}</h2><dl class="diff">
<div><dt>{t("Grupy do 10 osób","Groups of up to 10")}</dt><dd>{t("Instruktor ma czas, żeby zauważyć każdą osobę, poprawić ustawienie i dostosować praktykę.","Teachers have time to notice each student, offer corrections and adapt the practice.")}</dd></div>
<div><dt>{t("Joga i pilates w jednym karnecie","Yoga and Pilates in one membership")}</dt><dd>{t("W ciągu tygodnia wybierasz różne rodzaje praktyki, bez zapisywania się do osobnych studiów.","Choose different kinds of practice through the week without joining separate studios.")}</dd></div>
<div><dt>{t("Stały zespół instruktorów","A consistent teaching team")}</dt><dd>{t("Poznajesz nauczycieli, a oni znają Twój poziom, potrzeby i postępy.","You get to know your teachers, and they get to know your level, needs and progress.")}</dd></div>
<div><dt>{t("Jasna droga od początku","A clear path from beginner")}</dt><dd>{t("Wiesz, od czego zacząć i jak iść dalej, bez zgadywania kolejnego kroku.","You know where to start and how to progress without guessing the next step.")}</dd></div>
<div><dt>{t("Zajęcia po ukraińsku","Classes in Ukrainian")}</dt><dd>{t("Regularne zajęcia jogi w języku ukraińskim, w którym możesz czuć się swobodnie.","Regular yoga classes in Ukrainian, a language you can feel at ease in.")}</dd></div>
<div><dt>{t("Warsztaty, oddech, dźwięk","Workshops, breathwork, sound")}</dt><dd>{t("Kundalini, warsztaty tematyczne, sound healing i praca z oddechem w tym samym miejscu.","Kundalini, themed workshops, sound healing and breathwork in the same place.")}</dd></div></dl>'''
    prom = f'''<div class="three"><div><h3>{t("Czas dla siebie","Time for yourself")}</h3><p>{t("Godzina bez pracy i powiadomień, poświęcona tylko Tobie.","An hour set aside for you, away from work and messages.")}</p></div>
<div><h3>{t("Ruch z uwagą","Move with awareness")}</h3><p>{t("Pozycje łączymy z oddechem i zauważamy, jak czuje się ciało.","We link postures with breathing and notice how the body feels.")}</p></div>
<div><h3>{t("Bez presji","No pressure")}</h3><p>{t("Nie musisz robić wszystkiego idealnie ani porównywać się z innymi. Ćwiczysz we własnym tempie.","You don’t have to get every pose right or compare yourself with anyone. Work at your own pace.")}</p></div></div>'''
    notb = f'''<div class="two"><div><h2>{t("Czym Wisteria nie jest","What Wisteria is not")}</h2><ul class="plain"><li>{t("Nie jesteśmy studiem masowym. Ograniczamy liczebność grup.","We’re not a high-volume studio. We limit class sizes.")}</li><li>{t("Nie oczekujemy gibkości, siły ani doświadczenia.","We don’t expect flexibility, strength or experience.")}</li><li>{t("Nie obiecujemy szybkich efektów. Stawiamy na regularność i stopniowe postępy.","We don’t promise quick results. We value consistent practice and gradual progress.")}</li></ul></div>
<div><h2>{t("Gdzie nas znajdziesz","Where to find us")}</h2><p>{ADDR}, {v("postcode")} {t(CITY_PL,CITY_EN)}</p><p>{t("Zajęcia odbywają się w dni powszednie i weekendy, także wieczorem. Miejsca rezerwujesz online w Fitssey.","Classes run on weekdays and weekends, including evenings. You book your place online in Fitssey.")}</p><div class="btns">{url("fitssey",t("Rezerwuj w Fitssey","Book in Fitssey"),"btn","fitssey_home")}<a class="btn ghost" href="{MAP_LINK}" target="_blank" rel="noopener">{t("Dojazd w Mapach Google","Directions in Google Maps")}</a></div></div></div>'''
    styles = f'''<h2>{t("Rodzaje praktyki","Kinds of practice")}</h2><div class="three styles"><div><h3>Vinyasa</h3><p>{inf("Ruch płynnie połączony z oddechem.","Movement linked smoothly with breath.")}</p></div><div><h3>Hatha</h3><p>{inf("Spokojniejsze tempo i uwaga na pozycje.","A calmer pace with attention to postures.")}</p></div><div><h3>Ashtanga</h3><p>{inf("Ustalona kolejność pozycji.","A set sequence of postures.")}</p></div><div><h3>Pilates</h3><p>{inf("Kontrolowany ruch i praca nad siłą.","Controlled movement and strength work.")}</p></div><div><h3>{t("Zajęcia specjalne","Specialised classes")}</h3><p>{t("Mama i dziecko, joga po ukraińsku, joga w plenerze.","Mother-and-child, Ukrainian-language and outdoor yoga.")}</p></div><div><h3>{t("Oddech i dźwięk","Breath and sound")}</h3><p>{t("Sound healing, praca z oddechem, Kundalini i warsztaty.","Sound healing, breathwork, Kundalini and workshops.")}</p></div></div><p><a href="{href("classes")}">{t("Wszystkie zajęcia","All classes")}</a></p>'''
    steps = f'''<h2>{t("Jak zacząć","How to start")}</h2><ol class="steps"><li><h3>{t("Wybierz zajęcia","Choose a class")}</h3><p>{t("Sprawdź grafik albo napisz do nas, a pomożemy Ci wybrać.","Check the schedule or send us a message and we’ll help you decide.")}</p></li><li><h3>{t("Zarezerwuj pierwsze zajęcia","Book a first class")}</h3><p>{t("Miejsce rezerwujesz online w Fitssey. Możesz zacząć od jednych zajęć.","You book your place online in Fitssey. You can start with a single class.")}</p></li><li><h3>{t("Ćwicz dalej, jeśli czujesz, że to dla Ciebie","Continue if it feels right")}</h3><p>{t("Jeśli polubisz instruktora i grupę, karnet ułatwi regularną praktykę. Z czasem możesz spróbować warsztatów.","If you like the teacher and the group, a pass makes regular practice easier. Later you can try a workshop.")}</p></li></ol>'''
    band = f'<div class="band"><h2>{t("Zacznij od jednych zajęć","Start with one class")}</h2><div class="btns" style="justify-content:center"><a class="btn" href="{href("schedule")}#zapis" data-track="band_enrol">{t("Umów pierwsze zajęcia","Book your first class")}</a><a class="btn ghost" href="{href("contact")}">{t("Masz pytanie? Napisz","Have a question? Write to us")}</a></div></div>'
    return hero + sec(paths) + sec(styles, "alt") + sec(steps) + sec(diff, "alt") + sec(prom) + sec(notb, "alt") + sec(band)

def p_classes():
    def o(h, txt): return f'<div class="offer"><h3>{h}</h3><div>{txt}</div></div>'
    reg = f'''<p>{t("Godzinne zajęcia grupowe prowadzone przez instruktorów, dla początkujących i praktykujących. Grupy mają maksymalnie 10 osób.","60-minute instructor-led group classes for beginners and regular practitioners. Groups have a maximum of 10 people.")}</p>
<ul class="plain"><li><strong>Vinyasa</strong> {inf("– ruch płynnie połączony z oddechem.","– movement linked smoothly with breath.")}</li><li><strong>Hatha</strong> {inf("– spokojniejsze tempo, uwaga na pozycje.","– a calmer pace with attention to postures.")}</li><li><strong>Ashtanga</strong> {inf("– ustalona kolejność pozycji.","– a set sequence of postures.")}</li><li><strong>Pilates</strong> {inf("– kontrolowany ruch i praca nad siłą.","– controlled movement and strength work.")}</li></ul>'''
    return head(t("Zajęcia","Classes"), t("Co możesz u nas ćwiczyć i dla kogo jest dana forma.","What you can practise with us and who each format is for.")) + sec(
        o(t("Joga i pilates, zajęcia regularne","Regular Yoga & Pilates classes"), reg) +
        o(t("Karnety","Passes & memberships"), f'<p>{t("Karnety na 3, 4 lub 8 wejść albo karnet open, ważne w określonym okresie. Dla osób, które chcą ćwiczyć regularnie.","Passes for 3, 4 or 8 classes, or unlimited access, valid for a set period. For people who want to practise regularly.")} <a href="{href("pricing")}">{t("Cennik","Pricing")}</a></p>') +
        o(t("Zajęcia specjalne","Specialised classes"), f'<ul class="plain"><li>{t("Joga mama i dziecko","Mother-and-child yoga")}</li><li>{t("Joga w języku ukraińskim","Ukrainian-language yoga")}</li><li>{t("Joga w plenerze","Outdoor yoga")}</li></ul>') +
        o(t("Zajęcia indywidualne i dla par","Private & couples yoga"), f'<p>{t("Godzinne sesje indywidualne lub dla dwóch osób. Dla osób, które chcą pracować w swoim tempie albo ćwiczyć wspólnie.","60-minute sessions for one person or two. For those who want personal instruction or to practise together.")}</p><a href="{href("schedule")}#zapis">{t("Zapytaj o termin","Ask about a time")}</a>') +
        o(t("Warsztaty i Kundalini","Workshops & Kundalini"), f'<p>{t("Specjalne spotkania i warsztaty tematyczne dla osób, które chcą pogłębić praktykę.","Special sessions and themed workshops for those who want a deeper practice.")} <a href="{href("workshops")}">{t("Warsztaty","Workshops")}</a></p>') +
        o(t("Sound healing i praca z oddechem","Sound healing & breathwork"), f'<p>{t("Sesje relaksacji dźwiękiem i praktyki oddechowe, jeśli szukasz wyciszenia i odpoczynku od napięcia.","Sound relaxation and breathing sessions for those seeking calm and relief from stress.")}</p>') ) + sec(
        f'<h2>{t("Nie wiesz, od czego zacząć?","Not sure where to start?")}</h2><p>{t("Napisz do nas, a pomożemy Ci wybrać zajęcia.","Send us a message and we’ll help you decide.")}</p><a class="btn" href="{href("schedule")}#zapis">{t("Poproś o pomoc w wyborze","Ask for help choosing")}</a>', "alt")

def p_schedule():
    if SCHEDULE: rows = "".join(f"<tr><td>{e(t(a,b))}</td><td>{e(c)}</td><td>{e(d)}</td><td>{e(l)}</td><td>{e(tr)}</td></tr>" for a, b, c, d, l, tr in SCHEDULE)
    else:
        MISSING.add("SCHEDULE"); rows = f'<tr><td colspan="5"><mark class="ph">[{t("grafik zajęć: dzień, godzina, zajęcia, poziom, instruktor","timetable: day, time, class, level, teacher")}]</mark></td></tr>'
    tbl = f'<div class="tw"><table><thead><tr><th>{t("Dzień","Day")}</th><th>{t("Godzina","Time")}</th><th>{t("Zajęcia","Class")}</th><th>{t("Poziom","Level")}</th><th>{t("Instruktor","Teacher")}</th></tr></thead><tbody>{rows}</tbody></table></div>'
    return head(t("Grafik i zapisy","Schedule and booking"), t("Zajęcia są w dni powszednie i w weekendy, także wieczorem. Aktualne terminy i wolne miejsca sprawdzisz w Fitssey.","Classes run on weekdays and weekends, including evenings. Check current times and free places in Fitssey.")) + sec(
        f'<h2>{t("Grafik","Timetable")}</h2>{tbl}<div class="btns">{url("fitssey",t("Sprawdź wolne miejsca i rezerwuj","Check availability and book"),"btn","fitssey_schedule")}</div>'
        f'<p class="note">{t("Zajęcia trwają 60 minut, a grupy mają do 10 osób.","Classes last 60 minutes and groups have up to 10 people.")} {t("Zasady odwoływania:","Cancellation:")} {v("cancellation")} · {t("Co zabrać:","What to bring:")} {v("what_to_bring")}</p>') + sec(
        f'<h2 id="zapis">{t("Umów pierwsze zajęcia","Book your first class")}</h2><p>{t("Wolisz najpierw porozmawiać? Zostaw dane, a pomożemy wybrać pierwsze zajęcia. Możesz też zarezerwować miejsce samodzielnie w Fitssey.","Prefer to talk first? Leave your details and we’ll help you choose a first class. You can also book yourself in Fitssey.")}</p>{form("enrol")}', "alt")

def p_pricing():
    def r(n_pl, n_en, k, val=None):
        return f'<tr><td>{t(n_pl,n_en)}</td><td>{v(k)}</td><td>{v(val) if val else "–"}</td></tr>'
    rows = r("Zajęcia próbne","Trial class","price_trial") + r("Pojedyncze zajęcia","Single group class","price_single") + r("Karnet 3 wejścia","3-class pass","price_3","validity_3") + r("Karnet 4 wejścia","4-class pass","price_4","validity_4") + r("Karnet 8 wejść","8-class pass","price_8","validity_8") + r("Karnet open","Unlimited pass","price_unlimited","validity_unlimited") + r("Zajęcia indywidualne (60 min)","Private session (60 min)","price_private") + r("Zajęcia dla par (60 min)","Couples session (60 min)","price_couples")
    return head(t("Cennik i karnety","Pricing and passes"), t("Wszystkie opcje w jednym miejscu, żebyś mogła/mógł spokojnie porównać.","All options in one place so you can compare calmly.")) + sec(
        f'<div class="tw"><table><thead><tr><th>{t("Oferta","Option")}</th><th>{t("Cena","Price")}</th><th>{t("Ważność","Validity")}</th></tr></thead><tbody>{rows}</tbody></table></div>'
        f'<p>{t("Karnety pozwalają chodzić na różne regularne zajęcia grupowe w okresie ważności.","Passes let you attend different regular group classes within their validity period.")} {t("Zajęcia indywidualne, zajęcia specjalne i warsztaty są płatne osobno.","Private sessions, specialised activities and workshops are priced separately.")}</p>'
        f'<p>{t("Zakres karnetów:","What passes cover:")} {v("pass_scope")}</p><div class="note">{t("Rezerwacje i zakup karnetów odbywają się przez Fitssey.","Bookings and pass purchases are handled through Fitssey.")}<div class="btns">{url("fitssey",t("Przejdź do Fitssey","Go to Fitssey"),"btn","fitssey_pricing")}</div></div>'
        f'<h2>{t("Jak wybrać","How to choose")}</h2><p>{t("Na początek możesz zarezerwować pojedyncze zajęcia i zobaczyć, jak się czujesz. Jeśli polubisz grupę i instruktora, karnet pomoże Ci ćwiczyć regularnie.","You can start with a single class and see how it feels. If you like the group and teacher, a pass helps you practise regularly.")}</p>')

def p_teachers():
    if TEACHERS: cards = "".join(f'<div class="person"><h3>{e(n)}</h3><p>{e(t(pb,eb))}</p><p><strong>{t("Specjalizacja:","Specialisation:")}</strong> {e(t(sp,se))}</p></div>' for n, pb, eb, sp, se in TEACHERS)
    else:
        MISSING.add("TEACHERS"); cards = "".join(f'<div class="person"><h3><mark class="ph">[{t("imię i nazwisko instruktora","teacher name")}]</mark></h3><p><mark class="ph">[{t("doświadczenie i kwalifikacje","experience and qualifications")}]</mark></p><p><mark class="ph">[{t("styl nauczania i specjalizacja","teaching style and specialisation")}]</mark></p></div>' for _ in range(3))
    return head(t("Instruktorzy","Teachers"), t("Zajęcia prowadzi stały zespół, dzięki czemu instruktorzy poznają Twój poziom, potrzeby i postępy.","A consistent core team teaches our regular classes, so they get to know your level, needs and progress.")) + sec(f'<div class="three">{cards}</div>') + sec(f'<h2>{t("Nie wiesz, do kogo się zapisać?","Not sure who to choose?")}</h2><p>{t("Napisz do nas, a pomożemy Ci znaleźć instruktora, którego podejście do Ciebie pasuje.","Send us a message and we’ll help you find a teacher whose approach suits you.")}</p><a class="btn" href="{href("contact")}">{t("Napisz do nas","Contact us")}</a>', "alt")

def p_workshops():
    if WORKSHOPS: items = "".join(f'<div class="offer"><h3>{e(t(a,b))}</h3><div><p><strong>{e(d)}</strong></p><p>{e(t(pl,en))}</p></div></div>' for a, b, d, pl, en in WORKSHOPS)
    else:
        MISSING.add("WORKSHOPS"); items = f'<div class="offer"><h3><mark class="ph">[{t("nazwa warsztatu","workshop title")}]</mark></h3><div><p><mark class="ph">[{t("data, godzina, cena","date, time, price")}]</mark></p><p><mark class="ph">[{t("opis i dla kogo","description and who it is for")}]</mark></p></div></div>'
    return head(t("Warsztaty i praktyki specjalne","Workshops and special practices"), t("Dla osób, które chcą pogłębić praktykę lub spróbować czegoś poza standardowymi zajęciami.","For people who want a deeper practice or to try something beyond standard classes.")) + sec(
        f'<h2>{t("Nadchodzące wydarzenia","Upcoming events")}</h2>{items}') + sec(
        f'<h2>{t("Co oferujemy","What we offer")}</h2><div class="three"><div><h3>Kundalini</h3><p>{t("Specjalne sesje i warsztaty tematyczne dla osób zainteresowanych głębszą praktyką i rozwojem osobistym.","Special sessions and themed workshops for those interested in a deeper practice and personal development.")}</p></div><div><h3>Sound healing</h3><p>{t("Relaksacja z dźwiękiem, dla osób szukających wyciszenia.","Sound relaxation for those seeking calm.")}</p></div><div><h3>{t("Praca z oddechem","Breathwork")}</h3><p>{t("Praktyki oddechowe pomagające zwolnić i odpocząć od napięcia.","Breathing practices to help you slow down and release tension.")}</p></div></div><p>{t("Ceny warsztatów i sesji specjalnych są ustalane osobno.","Workshops and special sessions are priced separately.")}</p>', "alt")

def p_vouchers():
    steps = f'<ol class="plain"><li>{t("Wypełnij formularz zamówienia.","Fill in the order form.")}</li><li>{inf("Otrzymasz bon w formie cyfrowej (e-mail) lub do wydruku.","You receive the voucher digitally (email) or printable.")}</li><li>{t("Obdarowana osoba wybiera jogę, pilates lub połączenie obu i rezerwuje zajęcia w Fitssey.","The recipient chooses yoga, Pilates or a mix and books a class in Fitssey.")} {inf("Instrukcja zostanie dołączona do bonu.","Instructions will come with the voucher.")}</li></ol>'
    opts = "".join(f'<tr><td>{n}</td><td>{v("voucher_price_"+str(i))}</td></tr>' for i, n in ((1,t("1 zajęcia","1 class")),(2,t("2 zajęcia","2 classes")),(3,t("3 zajęcia","3 classes"))))
    fq = faq([(t("Czy obdarowana osoba może sama wybrać zajęcia?","Can the recipient choose their own class?"), t("Tak. Może wybrać jogę, pilates lub połączenie obu.","Yes. They can choose yoga, Pilates or a mix of both.")),
              (t("Jak długo bon jest ważny?","How long is the voucher valid?"), v("voucher_validity")),
              (t("Ile warto wydać?","How much should I spend?"), t("Zacznij od jednych zajęć albo wybierz do trzech. Ceny podajemy powyżej.","Start with one class or choose up to three. Prices are listed above.")),
              (t("Mam pytania przed zakupem.","I have questions before buying."), f'<a href="{href("contact")}">{t("Napisz do nas","Contact us")}</a>')])
    return head(t("Bony podarunkowe","Gift vouchers"), t("Prezent, który można przeżyć. Obdarowana osoba sama wybiera zajęcia.","A gift to experience. The recipient chooses their own classes.")) + sec(
        f'<div class="two"><div><h2>{t("Opcje i ceny","Options and prices")}</h2><p class="note">{inf("Bony na 1–3 wejścia: zakres zaproponowany w strategii, do potwierdzenia.","Vouchers for 1–3 classes: range proposed in the strategy, to be confirmed.")}</p><table><tbody>{opts}</tbody></table><p>{t("Ważność:","Validity:")} {v("voucher_validity")}</p></div><div><h2>{t("Jak to działa","How it works")}</h2>{steps}</div></div>') + sec(
        f'<h2 id="zamow">{t("Zamów bon","Order a voucher")}</h2>{form("voucher")}', "alt") + sec(f'<h2>{t("Pytania","Questions")}</h2>{fq}')

def p_groups():
    return head(t("Grupy i firmy","Groups and companies"), t("Chcesz poćwiczyć razem z przyjaciółmi lub zespołem? Opisz, czego szukacie.","Want to practise with friends or your team? Tell us what you’re looking for.")) + sec(
        f'<p class="note">{inf("Oferta dla grup i firm nie jest opisana w strategii. Zakres i warunki do potwierdzenia.","Group and corporate offers are not described in the strategy. Scope and terms to be confirmed.")}</p><div class="two"><div><h2>{t("Zapytanie dla grupy","Group enquiry")}</h2>{form("group")}</div><div><h2>{t("Zapytanie dla firm","Company enquiry")}</h2>{form("corporate")}</div></div>')

def p_contact():
    map_box = f'<div class="map" data-map="{MAP_EMBED}" data-title="{t("Mapa dojazdu","Map")}"><button class="btn ghost" type="button" data-map-load>{t("Pokaż mapę","Show map")}</button></div>'
    return head(t("Kontakt i dojazd","Contact and location"), t("Masz pytanie o poziom zajęć, rezerwację, karnet lub bon? Napisz, zadzwoń albo odezwij się na Instagramie.","Questions about class levels, booking, passes or vouchers? Write, call or message us on Instagram.")) + sec(
        f'<div class="two"><div><h2>{t("Dane kontaktowe","Contact details")}</h2><p>{ADDR}, {v("postcode")} {t(CITY_PL,CITY_EN)}</p><p>{t("Telefon:","Phone:")} {contact_link("phone","tel:")}<br>E-mail: {contact_link("email","mailto:")}<br>Instagram: {contact_link("instagram","")}</p><p>{t("Godziny:","Hours:")} {v("hours") if CUR["lang"]=="pl" else v("hours_en")}</p></div><div><h2>{t("Napisz do nas","Send a message")}</h2>{form("contact")}</div></div>') + sec(
        f'<h2>{t("Dojazd","Getting here")}</h2><p><a href="{MAP_LINK}" target="_blank" rel="noopener">{t("Otwórz w Mapach Google","Open in Google Maps")}</a></p>{map_box}', "alt")

def p_privacy():
    return head(t("Polityka prywatności","Privacy policy")) + sec(
        f'<p class="note">{inf("Szkic roboczy, wymaga przeglądu prawnego przed publikacją.","Working draft, needs legal review before going live.")}</p>'
        f'<h2>{t("Administrator","Controller")}</h2><p>{v("controller")}. {t("Kontakt:","Contact:")} {contact_link("email","mailto:")}</p>'
        f'<h2>{t("Jakie dane zbieramy","What we collect")}</h2><p>{t("Dane podane w formularzach (imię, e-mail, telefon, treść wiadomości, informacje o zamawianym bonie), wyłącznie w celu odpowiedzi na zapytanie lub realizacji zamówienia.","Details you enter in our forms (name, email, phone, message, voucher order details), used only to answer your enquiry or fulfil your order.")}</p>'
        f'<h2>{t("Cookies i statystyki","Cookies and analytics")}</h2><p>{t("Statystyki odwiedzin uruchamiamy dopiero po Twojej zgodzie. Mapa Google ładuje się po kliknięciu lub po zgodzie i może ustawiać własne pliki cookie. Zgodę możesz zmienić w stopce.","We run visit statistics only after your consent. The Google map loads after you click or consent and may set its own cookies. You can change your choice in the footer.")}</p>'
        f'<h2>{t("Twoje prawa","Your rights")}</h2><p>{inf("Masz prawo dostępu do danych, ich poprawienia, usunięcia, ograniczenia przetwarzania, sprzeciwu oraz skargi do organu nadzorczego (UODO).","You have the right to access, rectify, erase and restrict your data, to object, and to complain to the supervisory authority (UODO).")}</p>'
        f'<h2>{t("Rezerwacje","Bookings")}</h2><p>{t("Rezerwacje i zakup karnetów odbywają się w serwisie Fitssey, który działa według własnej polityki prywatności.","Bookings and pass purchases take place on Fitssey, which operates under its own privacy policy.")}</p>')

def favicon():
    c = "".join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{f}"/>' for x, y, r, f in [(32,10,6,"#8d76b0"),(24,20,6,"#a08bc6"),(40,20,6,"#a08bc6"),(18,31,5.5,"#b6a2d4"),(32,31,6,"#8d76b0"),(46,31,5.5,"#b6a2d4"),(26,42,5,"#c9bbe2"),(38,42,5,"#c9bbe2"),(32,52,4.5,"#d6cbe9")])
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#f5f1f9"/>{c}</svg>'

BUILDERS = {"index":p_index,"classes":p_classes,"schedule":p_schedule,"pricing":p_pricing,"teachers":p_teachers,"workshops":p_workshops,"vouchers":p_vouchers,"groups":p_groups,"contact":p_contact,"privacy":p_privacy}
def build():
    shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT + "/assets"); os.makedirs(OUT + "/en")
    for f in ("style.css", "site.js"): shutil.copy(os.path.join(ROOT, "src", f), OUT + "/assets/" + f)
    open(OUT + "/favicon.svg", "w").write(favicon())
    for lang in ("pl", "en"):
        CUR["lang"] = lang
        for s in SLUGS:
            CUR["slug"] = s; body = BUILDERS[s]()
            open(os.path.join(OUT, "en" if lang == "en" else "", s + ".html"), "w", encoding="utf-8").write(page(s, body))
    site = (CONFIG["SITE_URL"] or "https://YOUR-DOMAIN.example").rstrip("/")
    u = lambda lg, s: f"{site}/{'en/' if lg=='en' else ''}{'' if s=='index' else s+'.html'}"
    sm = "".join(f'<url><loc>{u(lg,s)}</loc><xhtml:link rel="alternate" hreflang="pl" href="{u("pl",s)}"/><xhtml:link rel="alternate" hreflang="en" href="{u("en",s)}"/></url>' for lg in ("pl","en") for s in SLUGS)
    open(OUT + "/sitemap.xml", "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">{sm}</urlset>')
    open(OUT + "/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {site}/sitemap.xml\n")
    # index.html in root is the PL home; make /en/ work too (en/index.html already exists)
    ck = ["# Checklist (auto-generated)\n", "## Fill in (yellow placeholders)\n"] + [f"- [ ] `{k}` – {LABELS[k][1]}" if k in LABELS else f"- [ ] `{k}` – fill the list in gen.py" for k in sorted(MISSING)]
    ck += ["\n## Confirm (blue, inferred from the strategy, not stated)\n"] + [f"- [ ] ({s}) {txt}" for s, txt in dict.fromkeys(INF)]
    open(ROOT + "/CHECKLIST.md", "w").write("\n".join(ck) + "\n")
    print("built", len(SLUGS) * 2, "pages; missing:", len(MISSING), "to confirm:", len(set(INF)))
if __name__ == "__main__": build()
