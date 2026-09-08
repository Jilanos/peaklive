# Test véhicule CAN actif en 10 minutes

Le scénario `scripts/vehicle-test-10m.ps1` est prévu pour un véhicule
immobilisé, un bus Classic CAN actif et un adaptateur PCAN connu. Il impose une
durée maximale de 600 secondes, vérifie d'abord l'identité et le SHA-256 du
binaire CI, et utilise un dossier `PEAKLIVE_DATA_DIR` isolé.

Préparer le test sans démarrer l'application :

```powershell
.\scripts\vehicle-test-10m.ps1 -Mode plan -Bitrate 500
```

Exécuter le parcours supervisé :

```powershell
.\scripts\vehicle-test-10m.ps1 -Mode interactive -Bitrate 500
```

Le test est strictement en réception passive et n'envoie aucune trame. Le
véhicule doit être sécurisé, sans conduite pendant le test, avec une batterie
et un espace disque suffisants. Interrompre immédiatement si la tension,
la température, la sécurité du véhicule ou la connexion USB devient douteuse.

| Temps | Étape | Preuve attendue |
| --- | --- | --- |
| 0:00–0:30 | Hash, Windows, sécurité, bitrate | `environment.txt` |
| 0:30–1:30 | Connexion passive | état Running, canal, bitrate |
| 1:30–3:30 | Capture trafic | compteurs, erreurs, chemin ASC |
| 3:30–4:30 | Stop | état Stopped/degraded, ASC + sidecar |
| 4:30–6:30 | Replay | ordre et volume plausibles |
| 6:30–8:00 | DBC/signal/graph | signal, unité, statut de décodage |
| 8:00–9:00 | CSV/Parquet | fichiers lisibles, sentinel inchangé |
| 9:00–10:00 | Fermeture/preuves | captures, logs, `summary.json` |

Chaque étape demande `Pass`, `Fail` ou `NotRun`. Une absence de trafic, un
adaptateur absent ou une étape non terminée reste `NotRun`; elle ne devient pas
un succès. Conserver le dossier affiché par le runner et transmettre
`summary.json`, `report.md`, `peaklive-metrics.jsonl`, les logs, captures, et les
fichiers `.partial`. Le fichier de métriques ne contient que l'état et des
compteurs agrégés (aucun ID, payload, signal ou contenu DBC).
