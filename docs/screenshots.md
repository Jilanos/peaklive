# Captures du README

Les images de `docs/images/` sont des captures des widgets Qt de PeakLive,
rendues hors écran avec le thème de l'application. Elles utilisent un extrait
réel, sans génération de valeurs synthétiques ni retouche des courbes.

## Données utilisées

- Acquisition : `demo_capture_010_001.asc`.
- Intervalle inclusif : **370 à 530 secondes**, dans le repère de l'acquisition.
- Trames CAN dans l'intervalle : **28 482**.
- Curseur A : **400 s** ; curseur B : **480 s**.
- DBC : `demo_motor.dbc`, `demo_dashboard.dbc`, `DCDC_generic_DB.dbc`.

| Signal DBC | Titre de présentation | Unité | Échantillons dans l'extrait |
| --- | --- | --- | --- |
| `Edrv_Act_1.Edrv_iAct` | Courant moteur | A | 1 526 |
| `Ecran1.Vitesse` | Vitesse | km/h | 1 532 |
| `DCDC_ELEC_VALUE.DCDC_UHV` | Tension batterie | V | 1 556 |

Le signal désigné comme `DCDC_Elec_Value_UHV` dans la demande est nommé
`DCDC_ELEC_VALUE.DCDC_UHV` dans le DBC fourni. Les alias français sont appliqués
uniquement aux titres des courbes, au récapitulatif des signaux et à la table de
mesures pendant la génération. Les identités des signaux, les unités, les valeurs
et les fichiers DBC restent inchangés. L'explorateur et l'inspecteur montrent les
noms DBC originaux. Ce dispositif documentaire n'ajoute pas une fonction de
renommage au produit.

La capture Report résume uniquement cet extrait, avec ces trois DBC : sa
couverture de décodage ne décrit pas le roulage complet avec toutes les bases.
La capture Recording montre le dialogue de configuration ; aucune acquisition
matérielle n'est démarrée pour produire les images.

## Reproduction

Depuis la racine du dépôt, après `uv sync --all-extras` :

```bash
QT_QPA_PLATFORM=offscreen uv run python scripts/capture_readme.py \
  /chemin/vers/demo_capture_010_001.asc \
  /chemin/vers/dbc
```

Les arguments désignent le fichier ASC et le dossier contenant les trois DBC.
Utiliser `--output /chemin/vers/images` pour changer le dossier de sortie.
Les données privées doivent être disponibles localement ; elles ne sont pas
distribuées avec le dépôt.

Le script utilise un profil temporaire et l'adaptateur simulé sans connexion.
Il charge les DBC, transmet les trames de l'extrait au traitement de l'application,
ordonne l'extrait chronologiquement sans changer ses horodatages ni ses valeurs,
attend la persistance, conserve l'origine temporelle du fichier et capture cinq
vues : courbes, espace combiné, trace et inspecteur, rapport, enregistrement.
Il vérifie la présence des trois signaux, la fenêtre 370–530 s et l'existence de
mesures dans l'intervalle A/B. Les décomptes et les correspondances de signaux
sont imprimés en fin d'exécution pour vérifier la provenance.

Le rendu repose sur les interfaces internes de PeakLive : ce script doit être
adapté si les widgets ou les contrôleurs évoluent. Les décorations et polices
peuvent varier entre Linux et Windows.
