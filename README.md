# Denimulator3

Windows-3DS-Emulator auf Basis von **Azahar 2123.3 / Citra**.
Erstes Kompatibilitätsziel: eine lokal vorhandene Pokémon-Y-CXI-Datei,
die in Citra Nightly 2104 funktioniert.

**Stand:** Build-Integration und Anpassungen vorbereitet. Es liegt noch kein
hier validierter Windows-Build vor; Pokémon Y wurde noch nicht getestet.
Die vorhandene Emulation wird aus Quellcode als eigene Anwendung gebaut.

## Windows-Build

1. Installiere [MSYS2](https://www.msys2.org/) und öffne **MSYS2 CLANG64**.
2. Aktualisiere mit `pacman -Syu`. Falls ein Neustart der Shell verlangt wird,
   öffne CLANG64 erneut und führe den Befehl nochmals aus.
3. Installiere die Werkzeuge:

   ```bash
   pacman -S --needed git make \
     mingw-w64-clang-x86_64-toolchain mingw-w64-clang-x86_64-cmake \
     mingw-w64-clang-x86_64-ninja mingw-w64-clang-x86_64-python \
     mingw-w64-clang-x86_64-spirv-tools \
     mingw-w64-clang-x86_64-qt6-base mingw-w64-clang-x86_64-qt6-multimedia \
     mingw-w64-clang-x86_64-qt6-multimedia-wmf \
     mingw-w64-clang-x86_64-qt6-tools mingw-w64-clang-x86_64-qt6-translations
   ```

4. Klone dieses Repository, wechsle hinein und führe aus:

   ```bash
   bash scripts/build-windows.sh
   ```

Der erste Build lädt den festgelegten Emulator-Commit und dessen Submodule.
Plane mehrere GB Speicher und einige Zeit ein. Standardmäßig laufen vier
Compilerprozesse; `BUILD_JOBS=2 bash scripts/build-windows.sh` reduziert den
Speicherbedarf. Das Skript stoppt auch bei fehlgeschlagenen Tests.
Vor erneutem Verpacken ein vorhandenes `dist/Denimulator3-windows-x64`
verschieben; es wird nicht automatisch überschrieben.

Nach erfolgreichem Build liegt das Paket unter `dist/Denimulator3-windows-x64.zip`.
Entpacke den **ganzen Ordner** an einen beschreibbaren Ort und starte
`Denimulator3.exe`; die DLLs werden mitgeliefert.
Alternativ erzeugt der Workflow **Windows build** nach einem Push oder manuell
über GitHub Actions das Artefakt. Dieser Workflow wurde hier noch nicht ausgeführt.

## Pokémon Y testen

1. Starte Denimulator3 und öffne über **File → Load File** deine `.cxi`-Datei.
   Sprache und Steuerung lassen sich in den Emulationseinstellungen ändern.
2. Verwende zunächst native Auflösung (1×) und OpenGL oder Vulkan mit aktuellem
   NVIDIA-Treiber. Teste Titelbild, Spielstart, Bewegung, einen Kampf und Ton.
3. Speichere im Spiel, beende den Emulator und prüfe nach erneutem Start,
   ob der Spielstand geladen werden kann.
4. Bei Fehlern notiere Renderer, Fehlermeldung und den letzten Abschnitt des
   Protokolls. ROM oder Schlüssel müssen nicht hochgeladen werden.

Unter Windows verwendet der Build `%APPDATA%/Denimulator3` für Benutzerdaten.
Ein vorhandener `user`-Ordner neben der EXE aktiviert wie bei Azahar den
portablen Modus. Die Upstream-Migrationsabfrage kann den Import alter
Citra-Daten anbieten; für den ersten unabhängigen Test ablehnen. Vor einem
späteren Import Citra-Spielstände separat sichern. Die Build-Skripte übernehmen
keine bestehenden Spielstände oder Einstellungen.

CXI-Unterstützung stammt vom unveränderten Azahar-NCCH-Loader. Daraus folgt
keine Garantie gleicher Kompatibilität wie Citra 2104. Manche Dateien benötigen
zusätzliche lokal vorhandene Konsolendaten; das Projekt liefert diese nicht mit.

## Entwicklung

`scripts/prepare.py` prüft den exakten Commit und wendet die Änderungen aus
`patches/denimulator3.patch` an. Fremde Änderungen werden nicht überschrieben.
Angepasst werden EXE-Name, Fenstertitel, Über-Dialog und Windows-Datenverzeichnis.
Andere Dialoge und Grafiken können weiterhin Azahar nennen.

Vorbereitungslogik testen: `python -m unittest discover -s tests -v`.
Diese Tests ersetzen weder Windows-Build noch Spieltest.
Lizenz und Herkunft: [THIRD_PARTY.md](THIRD_PARTY.md).
