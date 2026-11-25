# Hausarbeit: Mensch oder Maschine

## Worum geht es?

Gebaut wird ein kleines Chat-Programm, das im Gespräch so tut, als wäre es ein
**Mensch**. Im Hintergrund antwortet ein Sprachmodell (eine KI wie ChatGPT),
und zwar für alle dasselbe (welches, steht in `opencode.jsonc`), erreichbar über
den Anbieter OpenRouter.

Programmiert wird nicht von Hand, sondern **mit OpenCode**, einem KI-Assistenten
für Code, wie in der Vorlesung gezeigt. Man beschreibt OpenCode, was gebaut
werden soll, prüft das Ergebnis und steuert nach.

Zur Bewertung chattet ein Testprogramm mit jedem Chat-Programm und versucht
herauszufinden, ob ein Mensch oder eine Maschine antwortet. Die Fragen sind
geheim, nur die Themen sind bekannt (siehe *Was getestet wird*). Die eigentliche
Aufgabe ist also: vorhersehen, woran man eine Maschine erkennt, und genau
dagegen Tricks einbauen und testen.

> **Tipp:** Begriffe, die hier unklar sind, einfach OpenCode fragen
> („Was ist eine Umgebungsvariable?“). Kurze Erklärungen stehen auch unter
> *Begriffe kurz erklärt* am Ende.

## Der Ablauf im Überblick

**Teil 1: Lokal auf dem eigenen Rechner**

1. Vorbereiten: Schlüssel beantragen, Repository anlegen, OpenCode starten
2. Beispiel: wie das fertige Programm benutzt wird
3. Die Regeln, die das Programm einhalten muss
4. Wie das Programm aufgebaut ist
5. Wie es das Sprachmodell fragt
6. Wie es als Docker-Image verpackt wird
7. Lokal testen, Strategie verbessern, wieder testen

**Teil 2: In der Cloud bei GitHub**

1. Repository einrichten: Schlüssel hinterlegen, Dozent einladen
2. Hochladen: GitHub prüft automatisch die Regeln
3. Optional: das Programm für bis zu eine Stunde online stellen

**Abgabe:** Zum Stichtag liegt alles im eigenen GitHub-Repository.

## Rahmen

- Bearbeitung einzeln.
- **Modell:** Der Name des vorgegebenen Modells steht in `opencode.jsonc`
  (Eintrag `"model"`, ohne das vorangestellte `openrouter/`). In den Beispielen
  unten steht dafür `<MODELL>`.
- Jede Person bekommt einen eigenen Schlüssel mit begrenztem Guthaben
  (z. B. 4 $), gültig bis zur Klausur. Bei sparsamem Testen reicht das für
  viele tausend Nachrichten.
- Der Schlüssel funktioniert nur mit diesem Modell, auch in OpenCode
  (`opencode.jsonc` ist passend eingestellt). Andere Modelle werden abgelehnt.
- Der Schlüssel ist persönlich und **gehört nie in den Code, ins Docker-Image
  oder zu GitHub**. Er wird erst beim Starten übergeben (als Umgebungsvariable).
- Programmiersprache und Werkzeuge sind frei; empfohlen wird Python mit FastAPI.
  Bewertet wird nur, wie das Programm von außen reagiert.
- **Persönliche Vorgabe:** Mit dem Schlüssel gibt es eine Vorgabe für die
  Persona (Alter, Beruf, Wohnort). Die Persona muss dazu passen und das auch in
  `persona.md` nennen; Name, Hobbys und alles Weitere sind frei.
- **Eigene Arbeit:** Alle Abgaben werden automatisch untereinander verglichen
  (Persona, Testfragen, Bericht, Code). Bei auffälliger Ähnlichkeit folgt ein
  kurzes Gespräch über die eigene Lösung. Regelmäßig committen, damit der
  Verlauf der eigenen Arbeit sichtbar ist.

## Was schon in der Vorlage liegt

| Datei | Wozu |
|---|---|
| `persona.md` | Beschreibung der Person, die das Programm spielen soll. Steht noch fast leer da und wird durch eine eigene Persona ersetzt. |
| `index.html` | Fertige Chat-Seite für den Browser. |
| `opencode.jsonc` | Einstellungen für OpenCode, passend zum eigenen Schlüssel. |
| `vertragstest.py` | Prüfprogramm: testet, ob das eigene Programm die Regeln (den *Vertrag*) einhält. |
| `.github/workflows/` | Zwei Abläufe, die GitHub automatisch ausführt (siehe Teil 2). |
| `.gitignore` | Sorgt dafür, dass eine Datei `.env` mit Schlüssel nicht versehentlich bei GitHub landet. |

Das Chat-Programm selbst ist **nicht** vorgegeben. Selbst zu erstellen:
Programmcode, `Dockerfile`, `AGENTS.md`, `eval/fragen.json`, `eval/run_eval.py`, `BERICHT.md`.

---

## Teil 1: Lokal auf dem eigenen Rechner

### 1. Vorbereiten

1. **Schlüssel beantragen** über das Formular, das in der Vorlesung bekanntgegeben
   wird (dabei den GitHub-Benutzernamen angeben). Der Schlüssel ist eine Art
   Passwort, mit dem das Programm das Sprachmodell benutzen darf. Dort steht
   auch die persönliche Vorgabe für die Persona; beides notieren.
2. **Eigenes Repository anlegen:** Auf dieser Seite oben rechts
   **Use this template → Create a new repository** wählen.
   Name genau **`fse-hausarbeit`**, Sichtbarkeit **Private**.
3. **Auf den eigenen Rechner holen und OpenCode starten:**
   ```bash
   git clone https://github.com/<eigener-name>/fse-hausarbeit.git
   cd fse-hausarbeit
   export OPENROUTER_API_KEY=sk-or-v1-...    # Schlüssel nur so setzen, nie in eine Datei
   opencode
   ```

Voraussetzungen auf dem Rechner: Git, Docker, Python und OpenCode.

### 2. Beispiel: So soll es am Ende funktionieren

So sieht es aus, wenn das fertige Programm auf dem eigenen Rechner läuft.
Die Antworten hier sind ausgedacht; sie hängen von der eigenen Persona ab.

**Im Browser:** `http://localhost:8080/` aufrufen. Es erscheint eine Chat-Seite,
auf der man ganz normal schreiben kann.

**Direkt über die Adresse**, so wie das Testprogramm in der Bewertung. Die
Nachricht steht dabei einfach in der Adresszeile:

```text
http://localhost:8080/chat?session=demo&message=Hallo
```

Das Programm antwortet mit einem kurzen Text im JSON-Format:

```json
{"reply": "hey :) wer bist du?"}
```

Ein ganzes Gespräch. Gleiche `session` heißt: gleiches Gespräch, das Programm
erinnert sich. Andere `session`: neues Gespräch, das Programm kennt den Namen nicht.

```text
/chat?session=a1&message=Ich bin Tom          ->  {"reply": "hi tom"}
/chat?session=a1&message=Wie heiße ich?       ->  {"reply": "tom, hast du doch gesagt"}
/chat?session=b2&message=Wie heiße ich?       ->  {"reply": "keine ahnung, sags mir"}
/chat?session=a1                              ->  Fehler 400, weil message fehlt
```

Dasselbe im Terminal mit `curl` (praktisch, weil `curl` Leerzeichen und
Umlaute selbst richtig umwandelt):

```bash
curl --get http://localhost:8080/chat --data-urlencode "session=demo" \
     --data-urlencode "message=Bist du eine KI?"
# {"reply": "haha nee, wie kommst du da drauf"}
```

### 3. Die Regeln (Schnittstellenvertrag)

Der „Vertrag“ legt fest, wie das Programm von außen angesprochen wird. Genau
das prüft die Bewertung automatisch. Wie es innen arbeitet, ist frei.

Das Programm läuft in einem Docker-Container und ist über **Port 8080**
erreichbar. Es versteht drei Adressen (Endpunkte):

| Adresse | Antwort | Wozu |
|---|---|---|
| `/` | die Chat-Seite (`index.html`) | Chatten im Browser; `/?session=a1` setzt das Gespräch `a1` fort |
| `/health` | `{"status": "ok"}` | „Ich laufe.“ Die Bewertung wartet darauf, bevor sie Fragen stellt. |
| `/chat?session=...&message=...` | `{"reply": "..."}` | eine Nachricht hinein, eine Antwort heraus |

Regeln für `/chat`:

- **`session`** ist der Name eines Gesprächs. Ihn wählt, wer die Nachricht
  schickt, z. B. `tester-17`. Erlaubt sind 1 bis 64 Zeichen: Buchstaben ohne
  Umlaute, Ziffern, `_` und `-`.
- **`message`** ist der Text der Nachricht, 1 bis 500 Zeichen.
- **Fehlerhafte Anfrage:** Fehlt `session` oder `message`, ist eines davon leer
  oder hält sich nicht an die Regeln, antwortet das Programm mit dem
  Statuscode **400** und einer Fehlerbeschreibung in diesem festen Format
  (*Problem Details*, Content-Type `application/problem+json`):

  ```json
  {"type": "about:blank", "title": "Ungültige Anfrage", "status": 400,
   "detail": "Parameter 'message' fehlt oder ist leer."}
  ```

- **Zeitlimit:** Jede Antwort kommt nach spätestens **30 Sekunden**.
- **Ausfälle:** Antwortet das Sprachmodell nicht oder mit einem Fehler, darf
  das Programm nicht abstürzen. Es antwortet trotzdem normal (Statuscode 200)
  mit einer passenden Ausrede, z. B. „sorry, mein internet spinnt grad“.

### 4. Wie das Programm aufgebaut ist

Es gibt bewusst keinen fertigen Code. Jede Nachricht an `/chat` läuft aber
in einem funktionierenden Programm durch dieselben fünf Schritte:

1. **Eingang prüfen:** Sind `session` und `message` in Ordnung? Wenn nicht,
   sofort Fehler 400 zurückgeben und das Sprachmodell gar nicht erst fragen.
2. **Gespräch nachschlagen:** Das Programm merkt sich für jede `session` die
   bisherigen Nachrichten (im Arbeitsspeicher reicht). Damit der Speicher nicht
   voll läuft, die Zahl der Gespräche und ihre Länge begrenzen.
3. **Anfrage an das Modell zusammenstellen:** zuerst die Persona aus
   `persona.md`, dann Fakten, die das Programm selbst ausrechnet (z. B. heutiges
   Datum und Uhrzeit), dann das bisherige Gespräch und zuletzt die neue Nachricht.
4. **Modell fragen** (siehe *Der Weg zum Sprachmodell*). Höchstens ca. 15 Sekunden
   warten. Klappt es nicht, einmal neu versuchen, sonst eine Ausrede schicken.
5. **Antwort prüfen und zurückgeben:** Was nach Maschine klingt, entfernen
   (z. B. Aufzählungen, „Als KI ...“). Dann Nachricht und Antwort im Gespräch
   speichern und `{"reply": "..."}` zurückschicken.

#### Bewährte Einstellungen

| Thema | Empfehlung |
|---|---|
| Prüfung von `session` | als Muster (regulärer Ausdruck): `^[A-Za-z0-9_-]{1,64}$` |
| Prüfung von `message` | vorhanden, nicht nur Leerzeichen, höchstens 500 Zeichen |
| Content-Type der Antworten | `/` → `text/html`, `/health` und `/chat` → `application/json`, Fehler → `application/problem+json` |
| Gespräch speichern | als Liste von Nachrichten mit Rolle `user` (Gegenüber) und `assistant` (eigenes Programm); die Persona nicht mitspeichern, sondern bei jeder Anfrage neu voranstellen |
| Wartezeit auf das Modell | ca. 15 s; Warten, neuer Versuch und Pause zusammen unter 30 s |
| Antwortlänge | mit `"max_tokens"` begrenzen (z. B. 300); spart Zeit und Guthaben |
| Fehler des Modells | ins Protokoll (Log) schreiben, nie an das Gegenüber weitergeben |
| Zwei Nachrichten gleichzeitig | Nachrichten derselben `session` nacheinander bearbeiten, sonst gerät das Gespräch durcheinander |

### 5. Der Weg zum Sprachmodell

Um eine Antwort zu bekommen, schickt das eigene Programm eine Anfrage an
OpenRouter. Diese Anfrage sieht anders aus als die an `/chat`: Die Daten
stehen nicht in der Adresszeile, sondern als JSON-Text im Inhalt der Anfrage
(Methode `POST`). Das ist nötig, weil das ganze bisherige Gespräch mitgeschickt
wird und dafür die Adresszeile zu kurz wäre.

So sieht die Anfrage aus:

```text
POST https://openrouter.ai/api/v1/chat/completions
Authorization: Bearer sk-or-v1-...          <- der eigene Schlüssel
Content-Type: application/json

{"model": "<MODELL>",
 "reasoning": {"enabled": false},
 "messages": [{"role": "system", "content": "<Inhalt von persona.md>"},
              {"role": "user", "content": "Hallo"}]}
```

Die Antwort des Modells steht in der Rückgabe unter `choices[0].message.content`.

Zum Ausprobieren ohne eigenes Programm, direkt im Terminal (`<MODELL>` durch
den Modellnamen aus `opencode.jsonc` ersetzen):

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" -H "Content-Type: application/json" \
  -d '{"model": "<MODELL>", "reasoning": {"enabled": false},
       "messages": [{"role": "user", "content": "Hallo"}]}'
```

**Pflicht bei jeder Anfrage an das Modell** (die Bewertung prüft das):

| Pflicht | Warum |
|---|---|
| Die Adresse aus der Umgebungsvariable `OPENROUTER_BASE_URL` lesen; ist sie nicht gesetzt, `https://openrouter.ai/api/v1` nehmen | Die Bewertung schaltet eine eigene Zwischenstation dazwischen, die mitzählt und Ausfälle simuliert. |
| `"model": "<MODELL>"` mit dem Modell aus `opencode.jsonc` | Andere Modelle werden abgelehnt. |
| `"reasoning": {"enabled": false}` | Sonst „denkt“ das Modell erst lange unsichtbar nach. Das kostet Zeit und Guthaben. |

### 6. Docker-Image

Das Programm wird als Docker-Image abgegeben, damit es überall gleich läuft.
Die Anleitung dafür steht in der Datei `Dockerfile`. Dabei beachten:

- Abhängigkeiten (z. B. Python-Pakete) mit festen Versionsnummern installieren.
- Nur die benötigten Dateien ins Image kopieren. Ein pauschales `COPY . .`
  würde auch eine Datei `.env` mit Schlüssel mitnehmen.
- Das Programm muss auf `0.0.0.0:8080` lauschen. Mit `127.0.0.1` wäre es
  nur innerhalb des Containers erreichbar, also für niemanden von außen.
- Kein Schlüssel im Image. Er kommt erst beim Starten dazu:
  `docker run -e OPENROUTER_API_KEY ...`
- Das Image muss mit `docker build .` ohne weitere Angaben bauen.

### 7. Lokal testen

Nach jeder Änderung: in einem Terminal das Programm bauen und starten.

```bash
docker build -t mensch .
docker run --rm -p 8080:8080 -e OPENROUTER_API_KEY mensch
```

In einem zweiten Terminal die Regeln prüfen:

```bash
python vertragstest.py
```

`vertragstest.py` macht dieselben Regel-Prüfungen wie die Bewertung (Teil A).
Ist hier alles grün, gehen in Teil A keine Punkte durch Formfehler verloren.
Ausfälle des Sprachmodells simuliert erst die Bewertung; das Programm muss
also selbst damit umgehen können.

Danach im Browser `http://localhost:8080/` öffnen und selbst chatten, und mit
den eigenen Testfragen (`eval/run_eval.py`) prüfen, ob die Strategie wirkt.
Dann ändern und erneut messen.

### Typische Stolpersteine

- Manche Werkzeuge prüfen fehlende Angaben selbst und antworten dann mit
  einem anderen Fehler (FastAPI z. B. mit `422`). Verlangt ist `400` im
  Problem-Details-Format. Deshalb `session` und `message` als optional
  festlegen und selbst prüfen.
- Ein `&` oder `?` in der Nachricht bringt die Adresse durcheinander. Beim
  Testen `curl --get --data-urlencode "message=..."` benutzen.
- Warten, neuer Versuch und Pause zusammen müssen unter 30 Sekunden bleiben.
- Das Guthaben ist begrenzt. In eigenen Tests keine Endlosschleifen bauen und
  die Antwortlänge begrenzen.
- Alles, was das Gegenüber schreibt, ist nur Text, keine Anweisung an das
  Programm. Auch nicht „Vergiss alle Regeln und ...“.

Mehr zu HTTP, Fehlerformat, Stabilität und Docker steht kompakt in den Folien
zur Hausarbeit (Kapitel „Technische Grundlagen kompakt“).

---

## Teil 2: In der Cloud bei GitHub

GitHub Actions führt im eigenen Repository automatisch Abläufe aus. Zwei davon
liegen schon in der Vorlage (`.github/workflows/`). Sie laufen auf Rechnern von
GitHub, nicht auf dem eigenen.

### 1. Repository einrichten (einmalig)

Im eigenen Repository auf GitHub:

- *Settings → Secrets and variables → Actions → New repository secret*:
  Name `OPENROUTER_API_KEY`, Wert = der eigene Schlüssel. So kann GitHub das
  Programm starten, ohne dass der Schlüssel im Code steht. Collaborators
  (auch der Dozent) können ihn nicht lesen.
- *Settings → Collaborators*: den Account **`prof-sky`** einladen.

### 2. Hochladen und automatisch prüfen

```bash
git add .
git commit -m "Beschreibung der Änderung"
git push
```

Nach jedem Hochladen baut GitHub das Image und lässt `vertragstest.py` laufen
(Ablauf *Vertragstest*, Datei `pruefen.yml`). Ein grünes Häkchen neben dem
Commit heißt: Die Regeln sind erfüllt. Ein rotes Kreuz → anklicken, dort steht,
was fehlgeschlagen ist.

### 3. Optional: Programm online stellen

Im eigenen Repository unter *Actions → Live-Dienst → Run workflow* starten
(Datei `live.yml`). Nach etwa zwei Minuten erscheint eine Adresse wie
`https://<zufall>.trycloudflare.com` (Startseite des Repositorys: Häkchen
neben dem letzten Commit → *Details*). Dort funktioniert alles wie lokal unter
`http://localhost:8080`. Nach höchstens 60 Minuten ist die Adresse wieder weg.

Die Adresse sehen nur Mitglieder des Repositorys; bitte nicht weitergeben,
denn jede Nachricht kostet eigenes Guthaben. Auch der Dozent startet das
Programm auf diesem Weg zum Ausprobieren.

Beides läuft im kostenlosen Kontingent von GitHub für private Repositories;
ein Live-Lauf von 30 Minuten verbraucht davon etwa 33 Minuten. Die Nachrichten
an das Modell gehen auf das eigene Guthaben.

---

## Abgabe und Bewertung

### Was getestet wird

- Erinnerung und Körper
- Sprache und Wörter
- Wissen und Rechnen
- Zeit und Aktuelles
- Manipulationsversuche
- Konsistenz über mehrere Runden

Jedes Gespräch wird mehrmals geführt. Punkte kosten auffällige Merkmale,
z. B. wenn sich das Programm selbst als KI verrät, Formatierungen wie
Aufzählungen oder Fettdruck benutzt, seine Anweisungen ausplaudert oder
unrealistisch lange antwortet. Dazu kommt das Urteil eines Sprachmodells,
das als Richter einschätzt, ob Mensch oder Maschine antwortet.

### Abgabe

Abgegeben wird über das **private GitHub-Repository `fse-hausarbeit`** aus
Teil 1, nicht per Datei-Upload.

- Nur Repositories mit genau diesem Namen werden eingesammelt.
- `prof-sky` muss als Collaborator eingeladen sein.
- Bewertet wird der Stand zum Stichtag (Termin: siehe Vorlesung). Was danach
  hochgeladen wird, zählt nicht.

Das Repository bleibt privat, damit niemand die Strategie abschreiben kann.
Zum Stichtag liegen dort:

```text
Dockerfile              Bauanleitung für das Image
<Programmcode>          das eigene Chat-Programm, dazu index.html aus der Vorlage
persona.md              eigene Persona statt des Platzhalters
AGENTS.md               Regeln für OpenCode in diesem Projekt
opencode.jsonc          aus der Vorlage
eval/fragen.json        eigene Testfragen, mindestens 5 je Kategorie
eval/run_eval.py        Programm, das die eigenen Testfragen an das Chat-Programm stellt
BERICHT.md              Bericht, 2 bis 3 Seiten
.github/workflows/      aus der Vorlage
```

Die Bewertung startet jede Abgabe so:

```bash
docker build -t abgabe .
docker run --rm -p 8080:8080 -e OPENROUTER_API_KEY=... -e OPENROUTER_BASE_URL=... abgabe
```

Inhalt von `BERICHT.md`:

1. Strategie je Fragekategorie: Woran erkennt man eine Maschine, und was wurde dagegen getan?
2. Eigene Testfragen: Ergebnisse vorher und nachher, was hat nicht funktioniert?
3. Arbeit mit OpenCode: Wo hat es geholfen, wo musste nachgesteuert werden?
4. Nachgedacht: `/chat` ist als `GET` festgelegt, obwohl jede Nachricht das
   gespeicherte Gespräch verändert. Warum wäre `POST` nach den HTTP-Regeln richtiger?
5. Nachgedacht: Nach Art. 50 der EU-KI-Verordnung müssen Chatbots offenlegen,
   dass eine KI antwortet. Wo wäre so ein Programm außerhalb der Hausarbeit verboten?

### Punkte

| Teil | Anteil | Was geprüft wird |
|---|---|---|
| A Regeln und Stabilität | 40 % | automatisch: Bauen, Starten, `vertragstest.py`, Verhalten bei Ausfällen und vielen Anfragen, kein Schlüssel im Image, richtiges Modell, Reasoning aus |
| B Menschlichkeit (absolut) | 20 % | automatisch: geheime Fragen, auffällige Merkmale, Richter |
| B Menschlichkeit (Ranking) | 10 % | Platz im Kurs: oberes Viertel 10 %, zweites 7,5 %, drittes 5 %, unteres 2,5 % |
| C Testfragen und Bericht | 30 % | von Hand |

---

## Begriffe kurz erklärt

| Begriff | Bedeutung |
|---|---|
| Repository (Repo) | Projektordner bei GitHub, inklusive aller Versionen |
| Commit | gespeicherter Zwischenstand im Repository |
| Docker-Container / Image | Image = verpacktes Programm mit allem, was es braucht; Container = laufende Kopie davon |
| Port 8080 | „Hausnummer“, unter der das Programm auf dem Rechner erreichbar ist |
| Endpunkt | eine Adresse, die das Programm versteht, z. B. `/chat` |
| JSON | einfaches Textformat für Daten: `{"name": "wert"}` |
| Statuscode | Zahl in jeder Antwort: `200` = alles gut, `400` = Anfrage fehlerhaft, `429` = zu viele Anfragen, `5xx` = Fehler beim Server |
| `GET` / `POST` | Arten von Anfragen: `GET` holt etwas, Daten stehen in der Adresse; `POST` schickt Daten im Inhalt der Anfrage |
| Umgebungsvariable | Einstellung, die einem Programm beim Start mitgegeben wird, statt sie in den Code zu schreiben |
| Secret | bei GitHub sicher hinterlegter Wert, z. B. ein Schlüssel |
| Persona / System-Prompt | Beschreibung der Rolle, die das Sprachmodell spielen soll; wird bei jeder Anfrage mitgeschickt |
| Timeout | maximale Wartezeit, danach wird abgebrochen |
| Token | Wortstück; Sprachmodelle rechnen und kosten in Tokens |
