# batcalls_db



## Getting started

Requirements:
```
$ pip install -r requirements.txt
```

Erstellen der Datenbank oder Hinzufügen zu bestehender Datenbank:

1. CSV Datei für Zuordnung von dateinames zu species erstellen z.B.:
```csv
04 Frequency Modulated Sweep Ending At Near Constant Frequency Fm-Cf.wav,skip
05 Noctule 1.wav,Nyctalusnoctula
06 Noctule 2.wav,Nyctalusnoctula
07 Pipistrelle 1.wav,Pipistrelluspipistrellus
08 Pipistrelle 2.wav,Pipistrelluspipistrellus
```
2. Config Datei config.yaml anpassen, z.b.:
```yaml
dbfile: './db/speedtest.db' # path to existing or new db file

newcalls:
  folder: /path/to/wavfiles/Auswahl_Skiba/ # path to wav files to analyse
  dbname: skiba  # identifier of dataset to be used in database
  description: descriptions/skiba.csv # path to description csv file
  skipif: skip # value in csv file to indicate if file should be skipped

analysis:
  pos_offset: 2410 # around each peak samples will be cut out from t_peak - neg_offset to t_peak + pos_offset
  neg_offset: 2000 
  len_analysis: 30 # len of the analysis window in sound file
```

3. batcalls_db/update_db.py ausführen.
