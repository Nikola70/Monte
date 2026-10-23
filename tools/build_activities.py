# -*- coding: utf-8 -*-
"""Generate the Things to Do page (gudauri.html, ka/gudauri.html, ru/gudauri.html).

Reads tools/activities_data.py and tools/activities_distances.json (see compute_distances.py)
and rewrites the <main> block, the title/description tags and a JSON-LD list in the three pages.
Run from the repo root:  python tools/build_activities.py
"""
import html
import json
import os
import re
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from activities_data import HOTEL, PLACES  # noqa: E402

LANGS = ["en", "ka", "ru"]
IDX = {"en": 0, "ka": 1, "ru": 2}
FILES = {"en": "gudauri.html", "ka": "ka/gudauri.html", "ru": "ru/gudauri.html"}
BASE = "https://montegudauri.com"
PATH = {"en": "/gudauri", "ka": "/ka/gudauri", "ru": "/ru/gudauri"}

with open(os.path.join(HERE, "activities_distances.json"), encoding="utf-8") as f:
    DIST = json.load(f)

PHOTO_FILE = os.path.join(HERE, "activities_photos.json")
PHOTOS = json.load(open(PHOTO_FILE, encoding="utf-8")) if os.path.exists(PHOTO_FILE) else {}

UI = {
    "title": ("Things to Do in Gudauri and Kazbegi | Hotel Monte Gudauri",
              "რა ვნახოთ და რა ვაკეთოთ გუდაურსა და ყაზბეგში | სასტუმრო მონტე გუდაური",
              "Что посмотреть и чем заняться в Гудаури и Казбеги | Отель Monte Гудаури"),
    "meta": ("Sights and activities from Ananuri to the Russian border: skiing, paragliding, hiking, rafting, churches and fortresses, with Google Maps links, distances, seasons and costs.",
             "ღირსშესანიშნაობები და აქტივობები ანანურიდან რუსეთის საზღვრამდე: თხილამურები, პარაპლანერიზმი, ლაშქრობა, რაფტინგი, ეკლესიები და ციხეები — Google Maps ბმულებით, მანძილებით, სეზონებითა და ფასებით.",
             "Достопримечательности и занятия от Ананури до российской границы: лыжи, парапланы, походы, рафтинг, церкви и крепости, со ссылками на Google Maps, расстояниями, сезонами и стоимостью."),
    "h1": ("Activities & Sights", "აქტივობები და ღირსშესანიშნაობები", "Чем заняться и что посмотреть"),
    "intro1": ("From Ananuri Fortress on the Aragvi River to the Russian border at Upper Lars, the Georgian Military Road is lined with castles, monasteries, waterfalls and mountain trails, and Gudauri sits right in the middle of it. Here is what you can do and see from Hotel Monte.",
               "არაგვზე მდებარე ანანურის ციხე-სიმაგრიდან ზემო ლარსთან რუსეთის საზღვრამდე საქართველოს სამხედრო გზას გასდევს ციხე-სიმაგრეები, მონასტრები, ჩანჩქერები და სამთო ბილიკები, გუდაური კი სწორედ შუაგულშია. აი, რისი გაკეთება და ნახვა შეგიძლიათ სასტუმრო მონტედან.",
               "От крепости Ананури на реке Арагви до российской границы у Верхнего Ларса вдоль Военно-Грузинской дороги тянутся замки, монастыри, водопады и горные тропы, а Гудаури находится в самой середине маршрута. Вот что можно посмотреть и чем заняться, остановившись в отеле Monte."),
    "intro2": ("Distances are by road from the hotel. Use the filters to plan by season, hiking effort and cost, and open any place in Google Maps.",
               "მანძილები სასტუმროდან საავტომობილო გზით არის მითითებული. გამოიყენეთ ფილტრები სეზონის, ლაშქრობის სირთულისა და ფასის მიხედვით დასაგეგმად და გახსენით ნებისმიერი ადგილი Google Maps-ში.",
               "Расстояния указаны по дороге от отеля. Используйте фильтры, чтобы планировать по сезону, сложности похода и стоимости, и открывайте любое место в Google Maps."),
    "notice": ("Prices, opening hours and seasons are approximate and change often, so please ask at reception before you set off. In winter the Military Road can close for hours after heavy snow: check road conditions. Carry your passport near the border (Truso, Dariali). Mountain trails need proper footwear and a weather check; take a guide for glaciers, ski touring and ice.",
               "ფასები, მუშაობის საათები და სეზონები სავარაუდოა და ხშირად იცვლება, ამიტომ გასვლამდე დაუკავშირდით ადმინისტრატორს. ზამთარში ძლიერი თოვლის შემდეგ სამხედრო გზა საათობით შეიძლება დაიხუროს: შეამოწმეთ გზების მდგომარეობა. საზღვრის სიახლოვეს (თრუსო, დარიალი) თან იქონიეთ პასპორტი. სამთო ბილიკებისთვის საჭიროა შესაბამისი ფეხსაცმელი და ამინდის შემოწმება; მყინვარებზე, სათხილამურო ტურებსა და ყინულზე გიდით იარეთ.",
               "Цены, часы работы и сезоны приблизительны и часто меняются, поэтому перед поездкой уточняйте на ресепшене. Зимой после сильного снегопада Военно-Грузинская дорога может закрываться на несколько часов: проверяйте состояние дороги. Вблизи границы (Трусо, Дарьял) берите с собой паспорт. Для горных троп нужны подходящая обувь и проверка погоды; на ледники, ски-туры и лёд идите с гидом."),
    "f_season": ("Season", "სეზონი", "Сезон"),
    "f_hike": ("Hiking", "ლაშქრობა", "Поход"),
    "f_cost": ("Cost", "ფასი", "Стоимость"),
    "all": ("All", "ყველა", "Все"),
    "winter": ("Winter", "ზამთარი", "Зима"),
    "summer": ("Summer", "ზაფხული", "Лето"),
    "year": ("Year-round", "მთელი წელი", "Круглый год"),
    "h0": ("No hiking needed", "ლაშქრობა საჭირო არ არის", "Поход не нужен"),
    "h1c": ("Easy walk", "მარტივი გასეირნება", "Лёгкая прогулка"),
    "h2c": ("Moderate hike", "საშუალო სირთულის ლაშქრობა", "Поход средней сложности"),
    "h3c": ("Hard hike", "რთული ლაშქრობა", "Сложный поход"),
    "chip_h0": ("No hiking", "ლაშქრობის გარეშე", "Без похода"),
    "chip_h1": ("Easy", "მარტივი", "Лёгкий"),
    "chip_h2": ("Moderate", "საშუალო", "Средний"),
    "chip_h3": ("Hard", "რთული", "Сложный"),
    "free": ("Free", "უფასო", "Бесплатно"),
    "paid": ("Paid", "ფასიანი", "Платно"),
    "mixed": ("Free entry, paid extras", "უფასო შესვლა, ფასიანი დამატებები", "Вход бесплатный, допуслуги платные"),
    "sort": ("Sort by", "დალაგება", "Сортировка"),
    "s_near": ("Closest to Monte", "მონტესთან უახლოესი პირველი", "Сначала ближайшие к Monte"),
    "s_hike": ("Least hiking first", "ჯერ ლაშქრობის გარეშე", "Сначала без похода"),
    "s_name": ("Alphabetical (A–Z)", "ანბანის მიხედვით", "По алфавиту"),
    "reset": ("Reset filters", "ფილტრების გასუფთავება", "Сбросить фильтры"),
    "count": ("Showing {n} of {t} places", "ნაჩვენებია {n} ადგილი {t}-დან", "Показано {n} из {t} мест"),
    "empty": ("No places match these filters. Try resetting them.",
              "ამ ფილტრებს არცერთი ადგილი არ შეესაბამება. სცადეთ გასუფთავება.",
              "По этим фильтрам ничего не найдено. Попробуйте сбросить их."),
    "filters_aria": ("Filter and sort", "ფილტრი და დალაგება", "Фильтры и сортировка"),
    "dist": ("{km} km · about {t} by car from the hotel",
             "{km} კმ · დაახლოებით {t} მანქანით სასტუმროდან",
             "{km} км · около {t} на машине от отеля"),
    "dist_trail": ("{km} km · about {t} by car to the starting point",
                   "{km} კმ · დაახლოებით {t} მანქანით საწყის წერტილამდე",
                   "{km} км · около {t} на машине до начальной точки"),
    "dir": ("Directions from Monte", "მარშრუტი მონტედან", "Маршрут от Monte"),
    "book": ("Book a flight:", "დაჯავშნეთ ფრენა:", "Заказать полёт:"),
    "more_info": ("More information:", "დამატებითი ინფორმაცია:", "Подробнее:"),
    "book_ride": ("Book a ride:", "დაჯავშნეთ გასეირნება:", "Заказать прогулку:"),
    "credits_h": ("Photo credits", "ფოტოების ავტორები", "Авторы фотографий"),
    "credits_intro": ("Photos from Wikimedia Commons, resized and cropped to fit. Each is used under its free licence.",
                      "ფოტოები Wikimedia Commons-იდან, ზომაშეცვლილი და მოჭრილი. თითოეული გამოყენებულია თავისუფალი ლიცენზიით.",
                      "Фотографии с Wikimedia Commons, уменьшены и обрезаны. Каждая используется на условиях свободной лицензии."),
    "by": ("by", "ავტორი:", "автор:"),
    "cost_l": ("Cost", "ფასი", "Стоимость"),
    "note_l": ("Good to know", "სასარგებლო ინფორმაცია", "Полезно знать"),
    "area_a": ("Ananuri to Pasanauri", "ანანურიდან ფასანაურამდე", "От Ананури до Пасанаури"),
    "area_g": ("Gudauri area", "გუდაურის რაიონი", "Район Гудаури"),
    "area_n": ("Kobi to Kazbegi and Dariali", "კობიდან ყაზბეგამდე და დარიალამდე", "От Коби до Казбеги и Дарьяла"),
}
UNITS = {"en": {"h": "h", "min": "min"}, "ka": {"h": "სთ", "min": "წთ"}, "ru": {"h": "ч", "min": "мин"}}
DEC = {"en": ".", "ka": ",", "ru": ","}


def u(key, lang):
    return UI[key][IDX[lang]]


def esc(s):
    return html.escape(s, quote=True)


def fmt_km(km, lang):
    s = ("%.1f" % km) if km < 10 else str(int(round(km)))
    return s.replace(".", DEC[lang])


def fmt_min(minutes, lang):
    un = UNITS[lang]
    if minutes < 60:
        return "%d %s" % (minutes, un["min"])
    h, m = divmod(minutes, 60)
    return ("%d %s %d %s" % (h, un["h"], m, un["min"])) if m else ("%d %s" % (h, un["h"]))


def fmt_time(text, lang):
    # "1–1.5 h" / "45 min" -> localized units and decimal separator
    un = UNITS[lang]
    text = text.replace(" h", " " + un["h"]).replace(" min", " " + un["min"])
    return text.replace(".", DEC[lang])


def season_attr(s):
    return {"W": "winter", "S": "summer", "Y": "winter summer"}[s]


def season_badge(s, lang):
    if s == "W":
        return "❄️ " + u("winter", lang)
    if s == "S":
        return "☀️ " + u("summer", lang)
    return "❄️☀️ " + u("year", lang)


def cost_key(c):
    return {"F": "free", "P": "paid", "M": "mixed"}[c]


def map_links(p):
    if "ll" in p and "query" not in p:
        dest = "%s,%s" % p["ll"]
        view = "https://www.google.com/maps/search/?api=1&query=" + dest
    else:
        dest = urllib.parse.quote_plus(p["query"])
        view = "https://www.google.com/maps/search/?api=1&query=" + dest
    if p.get("dir_to"):  # directions go to a different point (e.g. the lift station) than the place itself
        dest = "%s,%s" % p["dir_to"]
    directions = "https://www.google.com/maps/dir/?api=1&origin=%s,%s&destination=%s&travelmode=driving" % (
        HOTEL[0], HOTEL[1], dest)
    return view, directions


def card(p, lang, order):
    i = IDX[lang]
    d = DIST[p["id"]]
    name = p["name"][i]
    _, directions = map_links(p)
    hike = p["hike"]
    hike_text = u("h%dc" % hike, lang) if hike else u("h0", lang)
    if hike and p.get("time"):
        hike_text += " · " + fmt_time(p["time"], lang)
    key = "dist_trail" if p.get("trail") else "dist"
    distance = p["where"][i] if p.get("where") else u(key, lang).format(km=fmt_km(d["km"], lang), t=fmt_min(d["min"], lang))
    ck = cost_key(p["cost"])
    cost_badge = u(ck, lang)
    parts = [
        '            <li class="act_card" id="%s" data-season="%s" data-hike="%d" data-cost="%s" data-km="%s" data-name="%s" data-order="%d">' % (
            p["id"], season_attr(p["season"]), hike, ck, d["km"], esc(name.lower()), order),
    ]
    ph = PHOTOS.get(p["id"])
    if ph:
        parts.append('                <figure class="act_photo"><img src="/images/Places/%s.jpg" alt="%s" width="%d" height="%d" loading="lazy"%s></figure>' % (
            p["id"], esc(name), ph["w"], ph["h"], (' style="object-position:%s"' % ph["pos"]) if ph.get("pos") else ""))
    parts += [
        "                <h2>%s</h2>" % esc(name),
        '                <p class="act_area">%s</p>' % esc(u("area_" + p["area"], lang)),
        '                <ul class="act_badges">',
        '                    <li class="act_badge act_season">%s</li>' % season_badge(p["season"], lang),
        '                    <li class="act_badge act_hike act_hike%d">%s%s</li>' % (hike, "🥾 " if hike else "🚗 ", esc(hike_text)),
        '                    <li class="act_badge act_cost act_%s">%s</li>' % (ck, esc(cost_badge)),
        "                </ul>",
    ]
    if not p.get("no_distance"):
        parts.append('                <p class="act_distance">%s</p>' % esc(distance))
    parts.append("                <p>%s</p>" % esc(p["desc"][i]))
    if p.get("cost_note"):
        parts.append('                <p class="act_info"><strong>%s:</strong> %s</p>' % (esc(u("cost_l", lang)), esc(p["cost_note"][i])))
    if p.get("note"):
        parts.append('                <p class="act_info"><strong>%s:</strong> %s</p>' % (esc(u("note_l", lang)), esc(p["note"][i])))
    anchors = []
    if p.get("links"):
        anchors.append('<span class="act_label">%s</span>' % esc(u(p.get("links_label", "book"), lang)))
        for label, url in p["links"]:
            anchors.append('<a class="act_link" href="%s" target="_blank" rel="noopener noreferrer">%s</a>' % (esc(url), esc(label)))
    if p.get("map_url"):  # the hotel's own Google Maps link for this place
        anchors.append('<a class="act_link" href="%s" target="_blank" rel="noopener" aria-label="%s: %s">%s</a>' % (
            esc(p["map_url"]), esc(u("dir", lang)), esc(name), esc(u("dir", lang))))
    elif not p.get("no_directions"):
        anchors.append('<a class="act_link" href="%s" target="_blank" rel="noopener" aria-label="%s: %s">%s</a>' % (
            esc(directions), esc(u("dir", lang)), esc(name), esc(u("dir", lang))))
    if anchors:
        parts.append('                <p class="act_links">')
        parts += ["                    " + a for a in anchors]
        parts.append("                </p>")
    parts.append("            </li>")
    return "\n".join(parts)


def chip(group, value, label, pressed=False):
    return '                    <button type="button" class="act_chip" data-filter="%s" data-value="%s" aria-pressed="%s">%s</button>' % (
        group, value, "true" if pressed else "false", esc(label))


def controls(lang, total):
    rows = []
    rows.append('            <div class="act_group" role="group" aria-labelledby="act_f_season">')
    rows.append('                <span class="act_label" id="act_f_season">%s</span>' % esc(u("f_season", lang)))
    rows.append(chip("season", "all", u("all", lang), True))
    rows.append(chip("season", "winter", "❄️ " + u("winter", lang)))
    rows.append(chip("season", "summer", "☀️ " + u("summer", lang)))
    rows.append("            </div>")
    rows.append('            <div class="act_group" role="group" aria-labelledby="act_f_hike">')
    rows.append('                <span class="act_label" id="act_f_hike">%s</span>' % esc(u("f_hike", lang)))
    rows.append(chip("hike", "all", u("all", lang), True))
    for n in range(4):
        rows.append(chip("hike", str(n), u("chip_h%d" % n, lang)))
    rows.append("            </div>")
    rows.append('            <div class="act_group" role="group" aria-labelledby="act_f_cost">')
    rows.append('                <span class="act_label" id="act_f_cost">%s</span>' % esc(u("f_cost", lang)))
    rows.append(chip("cost", "all", u("all", lang), True))
    rows.append(chip("cost", "free", u("free", lang)))
    rows.append(chip("cost", "paid", u("paid", lang)))
    rows.append("            </div>")
    rows.append('            <div class="act_group act_sortbox">')
    rows.append('                <label class="act_label" for="act_sort">%s</label>' % esc(u("sort", lang)))
    rows.append('                <select id="act_sort" class="act_sort">')
    rows.append('                    <option value="name" selected>%s</option>' % esc(u("s_name", lang)))
    rows.append('                    <option value="near">%s</option>' % esc(u("s_near", lang)))
    rows.append('                    <option value="hike">%s</option>' % esc(u("s_hike", lang)))
    rows.append("                </select>")
    rows.append('                <button type="button" class="act_reset" id="act_reset">%s</button>' % esc(u("reset", lang)))
    rows.append("            </div>")
    return "\n".join(rows)


def jsonld(lang, places):
    i = IDX[lang]
    items = []
    for n, p in enumerate(places, 1):
        view, _ = map_links(p)
        item = {"@type": "TouristAttraction", "name": p["name"][i], "description": p["desc"][i]}
        if not p.get("no_directions"):
            item["hasMap"] = view
        if p["id"] in PHOTOS:
            item["image"] = BASE + "/images/Places/%s.jpg" % p["id"]
        if "ll" in p and "query" not in p:
            item["geo"] = {"@type": "GeoCoordinates", "latitude": p["ll"][0], "longitude": p["ll"][1]}
        items.append({"@type": "ListItem", "position": n, "item": item})
    data = {"@context": "https://schema.org", "@type": "ItemList", "name": u("h1", lang),
            "inLanguage": lang, "itemListElement": items}
    return '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/") + "\n    </script>"


def author_name(a):
    return re.sub(r"\s*\d{4} \d{4}.*$", "", a).strip()  # drop ORCID-style numbers some authors add


def credits(lang, places):
    return ""  # the photo credits section was removed from the page on request
    rows = []
    for p in places:
        ph = PHOTOS.get(p["id"])
        if not ph or not ph.get("credit"):
            continue
        rows.append(
            '                    <li>%s: <a href="%s" target="_blank" rel="noopener">%s</a> %s %s, <a href="%s" target="_blank" rel="noopener">%s</a></li>' % (
                esc(p["name"][IDX[lang]]), esc(ph["page"].replace("%3A", ":")), esc("“" + ph["title"] + "”"), esc(u("by", lang)),
                esc(author_name(ph["author"])), esc(ph["license_url"] or ph["page"]), esc(ph["license"])))
    if not rows:
        return ""
    return (
        '            <section class="act_credits" id="act_credits">\n'
        '                <h2>%s</h2>\n'
        '                <p>%s</p>\n'
        '                <ul>\n%s\n                </ul>\n'
        '            </section>\n' % (esc(u("credits_h", lang)), esc(u("credits_intro", lang)), "\n".join(rows)))


def build_main(lang):
    places = sorted(PLACES, key=lambda p: (p["name"][IDX[lang]].casefold(), DIST[p["id"]]["km"]))
    total = len(places)
    cards = "\n".join(card(p, lang, n) for n, p in enumerate(places))
    count0 = u("count", lang).format(n=total, t=total)
    return (
        '<main>\n'
        '        <article class="things_page">\n'
        '            <section class="initial_card things_card" id="things_to_do">\n'
        '                <h1>%s</h1>\n'
        '                <p>%s</p>\n'
        '                <p>%s</p>\n'
        '                <p class="act_notice">%s</p>\n'
        '            </section>\n'
        '            <section class="act_controls" id="act_controls" aria-label="%s" data-total="%d" data-count="%s" hidden>\n'
        '%s\n'
        '            </section>\n'
        '            <p class="act_count" id="act_count" role="status" aria-live="polite">%s</p>\n'
        '            <p class="act_empty" id="act_empty" hidden>%s</p>\n'
        '            <ul class="act_grid" id="act_grid">\n'
        '%s\n'
        '            </ul>\n'
        '%s'
        '            %s\n'
        '        </article>\n'
        '    </main>'
    ) % (esc(u("h1", lang)), esc(u("intro1", lang)), esc(u("intro2", lang)), esc(u("notice", lang)),
         esc(u("filters_aria", lang)), total, esc(u("count", lang)), controls(lang, total),
         esc(count0), esc(u("empty", lang)), cards, credits(lang, places), jsonld(lang, places))


def rebuild(lang):
    path = os.path.join(ROOT, FILES[lang])
    src = open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in src else "\n"
    t = src.replace("\r\n", "\n")
    title, meta = u("title", lang), u("meta", lang)
    t = re.sub(r"<title>[^<]*</title>", lambda m: "<title>%s</title>" % html.escape(title, quote=False), t, count=1)
    t = re.sub(r'(<meta name="description" content=")[^"]*"', lambda m: m.group(1) + esc(meta) + '"', t, count=1)
    t = re.sub(r'(<meta property="og:title" content=")[^"]*"', lambda m: m.group(1) + esc(title) + '"', t, count=1)
    t = re.sub(r'(<meta property="og:description" content=")[^"]*"', lambda m: m.group(1) + esc(meta) + '"', t, count=1)
    new_main = build_main(lang)
    t, n = re.subn(r"<main>.*?</main>", lambda m: new_main, t, count=1, flags=re.S)
    assert n == 1, "no <main> block in " + path
    if "/activities.js" not in t:
        t = t.replace("</body>", '    <script src="/activities.js" defer></script>\n</body>', 1)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(t.replace("\n", nl))
    print("wrote", FILES[lang], "-", len(PLACES), "places")


if __name__ == "__main__":
    for lang in LANGS:
        rebuild(lang)
