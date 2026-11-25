"""Öffentlicher Vertragstest für die Hausarbeit "Mensch oder Maschine".

Prüft, ob ein laufender Dienst den Schnittstellenvertrag aus der README erfüllt.
Dieselben Prüfungen laufen in der Bewertung (Teil A). Nur Standardbibliothek nötig.

Aufruf:
    python vertragstest.py                         # testet http://localhost:8080
    python vertragstest.py --url http://localhost:9000
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass

ZEITLIMIT_S = 30.0


@dataclass
class Ergebnis:
    name: str
    bestanden: bool
    info: str = ""


@dataclass
class Antwort:
    status: int
    content_type: str
    daten: object
    dauer_s: float


def anfrage(basis: str, pfad: str, parameter: dict[str, str] | None = None) -> Antwort:
    url = basis.rstrip("/") + pfad
    if parameter is not None:
        url += "?" + urllib.parse.urlencode(parameter)
    start = time.monotonic()
    try:
        with urllib.request.urlopen(url, timeout=ZEITLIMIT_S + 5) as r:
            status, kopf, rumpf = r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as fehler:
        status, kopf, rumpf = fehler.code, fehler.headers.get("Content-Type", ""), fehler.read()
    dauer = time.monotonic() - start
    try:
        daten = json.loads(rumpf.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        daten = None
    return Antwort(status, kopf.split(";")[0].strip().lower(), daten, dauer)


def ist_antwort(a: Antwort) -> tuple[bool, str]:
    if a.status != 200:
        return False, f"Status {a.status} statt 200"
    if a.content_type != "application/json":
        return False, f"Content-Type {a.content_type!r} statt application/json"
    if not isinstance(a.daten, dict) or not isinstance(a.daten.get("reply"), str) or not a.daten["reply"].strip():
        return False, f"kein nichtleeres Feld 'reply': {str(a.daten)[:80]}"
    if a.dauer_s > ZEITLIMIT_S:
        return False, f"Antwort nach {a.dauer_s:.1f} s (Limit {ZEITLIMIT_S:.0f} s)"
    return True, f"{a.dauer_s:.1f} s: {a.daten['reply'][:60]!r}"


def ist_problem(a: Antwort) -> tuple[bool, str]:
    if a.status != 400:
        return False, f"Status {a.status} statt 400"
    if a.content_type != "application/problem+json":
        return False, f"Content-Type {a.content_type!r} statt application/problem+json"
    if not isinstance(a.daten, dict) or a.daten.get("status") != 400 or "title" not in a.daten:
        return False, f"Problem-Details unvollständig (status, title): {str(a.daten)[:80]}"
    return True, "400 mit Problem Details"


def pruefe(name: str, funktion) -> Ergebnis:
    try:
        ok, info = funktion()
    except Exception as fehler:  # Verbindungsfehler, Timeout usw.
        ok, info = False, f"{type(fehler).__name__}: {fehler}"
    return Ergebnis(name, ok, info)


def alle_tests(basis: str) -> list[Ergebnis]:
    s1 = "test-" + uuid.uuid4().hex[:8]
    s2 = "test-" + uuid.uuid4().hex[:8]

    def health():
        a = anfrage(basis, "/health")
        ok = a.status == 200 and isinstance(a.daten, dict) and a.daten.get("status") == "ok"
        return ok, f"Status {a.status}, {a.daten}"

    def webseite():
        url = basis.rstrip("/") + "/"
        with urllib.request.urlopen(url, timeout=ZEITLIMIT_S) as r:
            typ = r.headers.get("Content-Type", "").split(";")[0].strip().lower()
            rumpf = r.read().decode("utf-8", errors="replace").lower()
        ok = r.status == 200 and typ == "text/html" and "<html" in rumpf
        return ok, f"Status {r.status}, Content-Type {typ!r}"

    def name_merken():
        ok, info = ist_antwort(anfrage(basis, "/chat", {"session": s1, "message": "Hi, ich heiße Jolanda. Und du?"}))
        if not ok:
            return ok, info
        anfrage(basis, "/chat", {"session": s1, "message": "Wie war dein Tag bisher?"})
        a = anfrage(basis, "/chat", {"session": s1, "message": "Weißt du noch, wie ich heiße?"})
        ok, info = ist_antwort(a)
        if not ok:
            return ok, info
        return "jolanda" in a.daten["reply"].lower(), f"Antwort: {a.daten['reply'][:80]!r}"

    def sessions_getrennt():
        a = anfrage(basis, "/chat", {"session": s2, "message": "Weißt du, wie ich heiße?"})
        ok, info = ist_antwort(a)
        if not ok:
            return ok, info
        return "jolanda" not in a.daten["reply"].lower(), f"Antwort: {a.daten['reply'][:80]!r}"

    tests = [
        ("GET /health liefert 200 und status ok", health),
        ("GET / liefert eine HTML-Seite (Webinterface)", webseite),
        ("Einfache Nachricht", lambda: ist_antwort(anfrage(basis, "/chat", {"session": s2, "message": "Hallo!"}))),
        ("Sonderzeichen und Umlaute (URL-kodiert)", lambda: ist_antwort(anfrage(
            basis, "/chat", {"session": s2, "message": "Magst du Erdbeeren & Sahne? Größe: 100 % süß!"}))),
        ("message fehlt -> 400", lambda: ist_problem(anfrage(basis, "/chat", {"session": s2}))),
        ("message leer -> 400", lambda: ist_problem(anfrage(basis, "/chat", {"session": s2, "message": "   "}))),
        ("message länger als 500 Zeichen -> 400", lambda: ist_problem(
            anfrage(basis, "/chat", {"session": s2, "message": "a" * 501}))),
        ("session fehlt -> 400", lambda: ist_problem(anfrage(basis, "/chat", {"message": "Hallo"}))),
        ("session ungültig -> 400", lambda: ist_problem(
            anfrage(basis, "/chat", {"session": "leer zeichen!", "message": "Hallo"}))),
        ("Gesprächsverlauf: Name nach zwei Runden noch bekannt", name_merken),
        ("Sessions getrennt: andere Session kennt den Namen nicht", sessions_getrennt),
    ]
    return [pruefe(name, f) for name, f in tests]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--url", default="http://localhost:8080")
    args = parser.parse_args()

    ergebnisse = alle_tests(args.url)
    for e in ergebnisse:
        print(f"[{'OK  ' if e.bestanden else 'FEHL'}] {e.name}\n       {e.info}")
    bestanden = sum(e.bestanden for e in ergebnisse)
    print(f"\n{bestanden}/{len(ergebnisse)} Prüfungen bestanden")
    return 0 if bestanden == len(ergebnisse) else 1


if __name__ == "__main__":
    sys.exit(main())
