# Fossiland

Fossilien aus sechs Erdzeitaltern ausgraben, im Labor präparieren und ein Museum mit 38 Skeletten aufbauen. Auf Deutsch, Englisch, Französisch und Spanisch, für Handy und Tablet.

Dieses Repository macht aus dem Spiel eine Android-App (mit [Capacitor](https://capacitorjs.com)). GitHub baut die App bei jeder Änderung automatisch.

## App aufs Handy bekommen

1. Oben im Repository auf **Releases** gehen (rechts auf der Startseite).
2. Die neueste Version öffnen und die Datei **Fossiland-1.0.x.apk** auf dem Android-Handy herunterladen.
3. Die Datei öffnen. Android fragt einmal, ob Apps aus dieser Quelle installiert werden dürfen: erlauben.

Die Test-APK läuft komplett offline. Spielstände bleiben bei einem Update erhalten.

## Wie der Build funktioniert

Jeder Push auf `main` startet den Workflow **Android-App bauen** (Reiter **Actions**):

| Schritt | Ergebnis |
| --- | --- |
| Spiel nach `www/` bauen (`npm run build:web`) | Spiel, Grafiken und Schriften für die App |
| `npx cap sync android` | Spiel in das Android-Projekt kopiert |
| `./gradlew assembleDebug` | Test-APK, als Release und als Download unter **Actions** |
| `./gradlew bundleRelease` | signiertes Paket (AAB) für den Play Store, nur wenn Schlüssel hinterlegt sind |

Die Versionsnummer steigt automatisch mit jedem Build.

## Spiel ändern

Das Spiel steckt in `src/game.html`, die Grafiken in `src/assets/`. Nach einer Änderung einfach pushen, der Rest passiert automatisch.

Lokal bauen (braucht Node 22, JDK 21 und das Android SDK):

```bash
npm ci
npm run apk   # Ergebnis: android/app/build/outputs/apk/debug/app-debug.apk
```

## Für den Play Store

Google verlangt ein signiertes Paket. Der Schlüssel muss **für immer** aufbewahrt werden, ohne ihn lassen sich keine Updates mehr veröffentlichen (oder Play App Signing nutzen, dann verwaltet Google den eigentlichen Schlüssel).

1. Schlüssel einmalig erzeugen:
   ```bash
   keytool -genkeypair -v -keystore fossiland.jks -alias fossiland -keyalg RSA -keysize 2048 -validity 10000
   ```
2. Unter **Settings → Secrets and variables → Actions** vier Secrets anlegen:
   - `FOSSILAND_KEYSTORE_BASE64`: Inhalt von `base64 -w0 fossiland.jks`
   - `FOSSILAND_KEYSTORE_PASSWORD`: Passwort des Keystores
   - `FOSSILAND_KEY_ALIAS`: `fossiland`
   - `FOSSILAND_KEY_PASSWORD`: Passwort des Schlüssels
3. Beim nächsten Build erscheint unter **Actions** zusätzlich `Fossiland-PlayStore-AAB-…`. Diese Datei lädst du in der Play Console hoch.

Store-Grafiken liegen in `store/` (App-Symbol 512 × 512, Vorstellungsgrafik 1024 × 500).

## Aufbau

| Pfad | Inhalt |
| --- | --- |
| `src/game.html` | das Spiel (eine Datei, HTML/CSS/JavaScript) |
| `src/assets/` | 3D-Grafiken aus Blender (WebP/PNG) |
| `scripts/build-web.mjs` | baut `www/` inklusive Schriften für den Offline-Betrieb |
| `android/` | Android-Projekt (App-ID `com.familienplaner.fossiland`) |
| `store/` | Grafiken für den Play-Store-Eintrag |
| `.github/workflows/android.yml` | automatischer Build |

## Noch offen

- Echte Werbung (AdMob) statt des 5-Sekunden-Platzhalters in `showRewardedAd`
- Benachrichtigungen („Dein Knochen ist fertig präpariert“)
- Spielstand in der Cloud
