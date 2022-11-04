# batcalls_db



## Getting started

Requirements:
```
$ pip install -r requirements.txt
```

Erstellen der Datenbank oder Hinzufügen zu bestehender Datenbank:

1. CSV Datei für Zuordnung von dateinames zu species erstellen z.B.:
```csv
Filename,species,echolocation
01 Constant Frequency Tone.wav,skip,echolocation
02 Frequency Modulated Sweep (Slow) Slow FM.wav,skip,echolocation
03 Frequency Modulated Sweep (Fast) Fast FM.wav,skip,echolocation
04 Frequency Modulated Sweep Ending At Near Constant Frequency Fm-Cf.wav,skip,echolocation
05 Noctule 1.wav,Nyctalusnoctula,echolocation
06 Noctule 2.wav,Nyctalusnoctula,echolocation
```
2. Config Datei config/config.yaml anpassen. Genaue dokumentation in config/default.py

3. run.py ausführen.
