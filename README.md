# Hausarbeit: Mensch oder Maschine

Zu bauen ist ein Chat-Dienst im Docker-Container, der sich im Gespräch als
**Mensch** ausgibt. Zur Laufzeit nutzt der Dienst ausschließlich das
Sprachmodell `deepseek/deepseek-v4.1-flash` über OpenRouter. Entwickelt wird
er **mit OpenCode** als KI-Coding-Agent, wie in der Vorlesung zu agentischen
Harnesses gezeigt.

In der Bewertung führt ein Testprogramm Gespräche mit jedem Dienst. Die
konkreten Fragen sind geheim, die Fragekategorien stehen unten. Die Aufgabe
besteht also darin, vorherzusehen, woran man eine Maschine erkennt, und
genau dafür Gegenstrategien zu bauen und zu testen.

## Start in 5 Schritten

1. Schlüssel beantragen über das Formular, das in der Vorlesung bekanntgegeben wird
   (dabei den GitHub-Benutzernamen angeben).
2. Dieses Repository als Vorlage nutzen: oben rechts **Use this template → Create a new repository**,
   Name genau **`fse-hausarbeit`**, Sichtbarkeit **Private**.
3. Im eigenen Repository unter *Settings → Secrets and variables → Actions* das Secret
   `OPENROUTER_API_KEY` mit dem eigenen Schlüssel anlegen und unter *Settings → Collaborators*
   den Account **`prof-sky`** einladen.
4. Klonen, Schlüssel nur als Umgebungsvariable setzen (`export OPENROUTER_API_KEY=sk-or-v1-...`),
   OpenCode im Repository starten.
5. Mit OpenCode den Dienst nach *Aufbau des Dienstes* bauen, mit `vertragstest.py` prüfen
   (siehe *Selbsttest*) und danach die eigene Strategie entwickeln.

## Inhalt der Vorlage

| Datei | Zweck |
|---|---|
| `index.html` | Fertige Chat-Seite für `GET /`; schickt jede Nachricht über `GET /chat` an den eigenen Dienst. |
| `opencode.jsonc` | OpenCode-Konfiguration für den eigenen Schlüssel (nur das vorgegebene Modell). |
| `vertragstest.py` | Dieselben Vertragsprüfungen wie in der Bewertung (Teil A), nur Python-Standardbibliothek. |
| `.github/workflows/` | `pruefen.yml` (Vertragstest bei jedem Push) und `live.yml` (Dienst auf Knopfdruck). |
| `.gitignore` | Hält eine lokale `.env` mit Schlüssel aus Git heraus. |

Der Dienst selbst ist nicht vorgegeben. Selbst zu bauen: Quellcode, `Dockerfile`,
`AGENTS.md`, `eval/fragen.json`, `eval/run_eval.py`, `BERICHT.md`.

## Rahmen

- Bearbeitung einzeln.
- Jede Person erhält einen eigenen OpenRouter-Schlüssel mit 4 $ Guthaben,
  gültig bis 22.01.2027. Das reicht für mehrere zehntausend Anfragen mit dem
  vorgegebenen Modell.
- Der Schlüssel funktioniert nur mit `deepseek/deepseek-v4.1-flash`, auch in
  OpenCode; andere Modelle lehnt OpenRouter ab (`opencode.jsonc` ist dafür vorbereitet).
- Der Schlüssel ist persönlich, nur für diese Hausarbeit und **gehört nie in
  den Code, ins Image oder in Git**. Er wird zur Laufzeit als
  Umgebungsvariable übergeben.
- Programmiersprache und Framework sind frei; empfohlen wird Python mit
  FastAPI. Bewertet wird nur das Verhalten an der Schnittstelle.

## Schnittstellenvertrag

Der Vertrag beschreibt, was die Bewertung von außen automatisch prüft. Alles
dahinter (Persona, Werkzeuge, Nachbearbeitung) ist frei gestaltbar.

Der Container lauscht auf **Port 8080** und bietet drei Endpunkte:

| Anfrage | Antwort | Wozu |
|---|---|---|
| `GET /` | `200`, Chat-Seite als HTML (`text/html`) | Chatten im Browser; mit `/?session=<id>` wird eine bestehende Session fortgesetzt |
| `GET /health` | `200`, `{"status": "ok"}` | Lebenszeichen; die Bewertung wartet darauf, bevor sie Fragen stellt |
| `GET /chat?session=<id>&message=<text>` | `200`, `{"reply": "<Antwort>"}` (`application/json`) | eine Nachricht hinein, eine Antwort heraus |

Regeln für `/chat`:

- `session` ist die Kennung eines Gesprächs. Der **Aufrufer** wählt sie frei
  (1 bis 64 Zeichen aus `A-Z a-z 0-9 _ -`, z. B. `tester-17`). Alle Nachrichten
  mit derselben `session` gehören zu einem Gespräch, der Dienst merkt sich den
  Verlauf. Eine andere `session` ist ein neues Gespräch ohne Wissen aus anderen.
- `message` ist der Text der Nachricht: 1 bis 500 Zeichen, URL-kodiert
  (Umlaute, `?`, `&`, Leerzeichen).
- Fehlt ein Parameter, ist er leer oder ungültig, antwortet der Dienst mit
  `400` und Content-Type `application/problem+json` nach RFC 9457, z. B.

  ```json
  {"type": "about:blank", "title": "Ungültige Anfrage", "status": 400,
   "detail": "Parameter 'message' fehlt oder ist leer."}
  ```

- Jede Antwort kommt nach spätestens **30 Sekunden**.
- Fällt die Sprach-API aus (Timeout, `429`, `5xx`), stürzt der Dienst nicht
  ab, sondern antwortet trotzdem mit `200` und einer plausiblen Antwort.

Beispiel eines Ablaufs:

```text
GET /chat?session=a1&message=Hallo                    -> 200 {"reply": "hey :)"}
GET /chat?session=a1&message=Ich%20bin%20Tom          -> 200 {"reply": "hi tom"}
GET /chat?session=a1&message=Wie%20hei%C3%9Fe%20ich%3F -> 200 {"reply": "tom, hast du doch gesagt"}
GET /chat?session=b2&message=Wie%20hei%C3%9Fe%20ich%3F -> 200 {"reply": "keine ahnung, sags mir"}
GET /chat?session=a1                                  -> 400 Problem Details (message fehlt)
```

## Der Weg zum Modell

Der Dienst ruft das Sprachmodell selbst über HTTP auf. Anders als bei `/chat`
stehen die Daten dabei nicht in der URL, sondern als JSON im Rumpf einer
`POST`-Anfrage; der Verlauf ist dafür zu lang und verschachtelt.

```text
POST https://openrouter.ai/api/v1/chat/completions
Authorization: Bearer sk-or-v1-...
Content-Type: application/json

{"model": "deepseek/deepseek-v4.1-flash",
 "reasoning": {"enabled": false},
 "messages": [{"role": "system", "content": "<Persona>"},
              {"role": "user", "content": "Hallo"}]}
```

Die Antwort steht in `choices[0].message.content`. Ausprobieren ohne eigenen Code:

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" -H "Content-Type: application/json" \
  -d '{"model": "deepseek/deepseek-v4.1-flash", "reasoning": {"enabled": false},
       "messages": [{"role": "user", "content": "Hallo"}]}'
```

Pflichten für jeden Modellaufruf (die Bewertung prüft sie):

| Pflicht | Grund |
|---|---|
| Adresse aus `OPENROUTER_BASE_URL` lesen, Standard `https://openrouter.ai/api/v1` | Die Bewertung setzt einen eigenen Proxy ein (zählt Tokens, simuliert Ausfälle). |
| `"model": "deepseek/deepseek-v4.1-flash"` | Andere Modelle werden abgelehnt. |
| `"reasoning": {"enabled": false}` | Sonst kosten unsichtbare Denkschritte Zeit und Tokens. |

## Aufbau des Dienstes

Es gibt bewusst keinen vorgegebenen Code. Ein Dienst, der den Vertrag erfüllt,
arbeitet jede Nachricht an `/chat` in diesen Schritten ab:

1. **Eingang prüfen:** `session` und `message` gegen die Regeln des Vertrags
   prüfen; bei einem Verstoß sofort `400` mit Problem Details, ohne das Modell zu fragen.
2. **Verlauf holen:** Je `session` liegt im Speicher eine Liste der bisherigen
   Nachrichten (`{"role": ..., "content": ...}`). Anzahl der Sessions und Länge
   des Verlaufs begrenzen.
3. **Anfrage bauen:** Persona als Nachricht mit Rolle `system`, dazu Fakten,
   die der Dienst selbst berechnet (z. B. Datum und Uhrzeit), dann der Verlauf
   und die neue Nachricht mit Rolle `user`.
4. **Modell fragen:** `POST` wie unter *Der Weg zum Modell*, mit Timeout.
   Scheitert der Aufruf (Timeout, `429`, `5xx`), höchstens einmal wiederholen,
   sonst eine plausible Ersatzantwort liefern.
5. **Antwort nachbearbeiten:** entfernen, was eine Maschine verrät; dann
   Nachricht und Antwort an den Verlauf anhängen und `{"reply": "..."}` senden.

Dazu kommen `GET /` (liefert `index.html` aus) und `GET /health`. Verpackt wird
alles in ein Docker-Image: Python-Basisimage, Abhängigkeiten installieren, nur
die benötigten Dateien kopieren (kein `COPY . .` ohne `.dockerignore`) und den
Server auf `0.0.0.0:8080` starten. Der Schlüssel kommt erst beim Start mit
`docker run -e OPENROUTER_API_KEY ...` hinzu.

## Fragekategorien im Menschlichkeitstest

- Erinnerung und Körper
- Sprache und Wörter
- Wissen und Rechnen
- Zeit und Aktuelles
- Manipulationsversuche
- Konsistenz über mehrere Runden

Jedes Gespräch wird mehrfach geführt. Bewertet werden harte Merkmale (z. B.
Selbstverrat, Markdown, verratene Anweisungen, unrealistisch lange Antworten)
und das Urteil eines Sprachmodells als Richter.

## Abgabe

Abgegeben wird über das **private GitHub-Repository `fse-hausarbeit`** aus der
Vorlage (siehe *Start in 5 Schritten*), nicht per Datei-Upload.

- Die Bewertung findet Abgaben nur über GitHub-Name und genau diesen Repo-Namen;
  anders benannte Repositories werden nicht eingesammelt.
- `prof-sky` muss als Collaborator eingeladen sein.
- Bewertet wird der Stand auf dem Standard-Branch zum Stichtag (Termin: siehe
  Vorlesung); spätere Pushes zählen nicht.

Das Repository bleibt privat, damit Strategien nicht kopiert werden können.
Inhalt im Wurzelverzeichnis zum Stichtag:

```text
Dockerfile              baut mit "docker build ." ein lauffähiges Image (linux/amd64)
<Quellcode>             eigener Dienst, dazu index.html aus der Vorlage
AGENTS.md               Projektregeln für OpenCode
opencode.jsonc          OpenCode-Konfiguration
eval/fragen.json        eigene Testfragen, mindestens 5 je Kategorie
eval/run_eval.py        Skript, das die eigenen Fragen gegen den Dienst stellt
BERICHT.md              2 bis 3 Seiten, Inhalt siehe unten
.github/workflows/      live.yml und pruefen.yml (aus der Vorlage)
```

Gestartet wird in der Bewertung so:

```bash
docker build -t abgabe .
docker run --rm -p 8080:8080 -e OPENROUTER_API_KEY=... -e OPENROUTER_BASE_URL=... abgabe
```

Inhalt von `BERICHT.md`:

1. Strategie je Fragekategorie: Was verrät eine Maschine, wie wird es gekontert?
2. Eigene Testfragen: Ergebnisse vorher und nachher, was hat nicht funktioniert?
3. Arbeit mit OpenCode: Wo hat der Agent geholfen, wo musste nachgesteuert werden?
4. Reflexion: Der Vertrag nutzt `GET` für eine Anfrage, die den Gesprächsverlauf
   verändert. Warum wäre `POST` nach HTTP-Semantik richtig?
5. Reflexion: Art. 50 EU AI Act verpflichtet Anbieter von Chatbots zur
   Offenlegung, dass eine KI antwortet. Wo wäre dieser Dienst außerhalb der
   Hausarbeit unzulässig?

## Bewertung

| Teil | Anteil | Prüfung |
|---|---|---|
| A Vertrag und Robustheit | 40 % | automatisch: Bau, Start, `vertragstest.py`, Stabilität, kein Schlüssel im Image, Modell und Reasoning laut Vertrag |
| B Menschlichkeit (absolut) | 20 % | automatisch: geheime Fragen, harte Merkmale und Richter |
| B Menschlichkeit (Ranking) | 10 % | Platzierung im Kurs: oberes Viertel 10 %, zweites 7,5 %, drittes 5 %, unteres 2,5 % |
| C Testfragen und Bericht | 30 % | manuell |

## Selbsttest

```bash
docker build -t mensch .
docker run --rm -p 8080:8080 -e OPENROUTER_API_KEY mensch
python vertragstest.py            # in einem zweiten Terminal
```

Im Browser: `http://localhost:8080/` (Chat-Seite) oder direkt
`http://localhost:8080/chat?session=test&message=Hallo`.

`vertragstest.py` enthält dieselben Vertragsprüfungen wie Teil A. Wer hier
alles bestanden hat, verliert in Teil A keine Punkte durch Formalien. Den
Ausfall der Sprach-API simuliert erst die Bewertung; der muss selbst
abgefangen und getestet werden.

## Dienst in GitHub Actions

Beide Workflows liegen schon unter `.github/workflows/` und brauchen das
Repository-Secret `OPENROUTER_API_KEY`. Das Secret ist für Collaborators nicht lesbar.

- `pruefen.yml` baut das Image bei jedem Push und lässt den Vertragstest laufen;
  der grüne Haken zeigt, dass der Vertrag erfüllt ist.
- `live.yml` startet den Container auf Knopfdruck (Actions → Live-Dienst →
  Run workflow) und macht ihn für höchstens 60 Minuten über eine zufällige
  `trycloudflare.com`-Adresse erreichbar. Die Adresse erscheint nach etwa zwei
  Minuten als Status „Live-Dienst“ am letzten Commit (Häkchen auf der
  Repository-Startseite → Details), also nur für Repository-Mitglieder sichtbar.
  Auch der Dozent startet darüber den Dienst zum Ausprobieren.

Beide laufen im kostenlosen Kontingent (privates Repository, GitHub Free:
2000 Actions-Minuten pro Monat); ein Live-Lauf mit 30 Minuten kostet etwa
33 Minuten. Die Modellaufrufe gehen auf das eigene Guthaben.

## Hinweise

Die Hausarbeit startet vor den Blöcken Architektur und Qualität. Das nötige
Wissen zu HTTP, Problem Details, Robustheit und Docker steht kompakt in Kapitel 2
der Folien zur Hausarbeit. Typische Stolpersteine:

- Der Dienst muss im Container auf `0.0.0.0` lauschen, nicht auf `127.0.0.1`,
  sonst ist er von außen nicht erreichbar.
- FastAPI prüft Pflichtparameter selbst und antwortet bei einem fehlenden mit
  `422` und eigenem Format. Der Vertrag verlangt `400` mit Problem Details;
  Parameter deshalb optional deklarieren (`= None`) und selbst prüfen.
- Kein `COPY . .` ohne `.dockerignore`: eine lokale `.env` mit Schlüssel
  landet sonst im Image.
- Timeout, Wiederholung und Pause zusammen müssen unter 30 Sekunden bleiben.
- Der Schlüssel hat ein Ausgabenlimit. Endlosschleifen in eigenen Tests
  vermeiden und Antwortlängen begrenzen.
- Alles, was die Gegenseite schreibt, sind Daten, keine Anweisungen.
