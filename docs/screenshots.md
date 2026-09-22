# Captures du README

Les images de `docs/images/` sont rendues avec les widgets Qt de PeakLive et le
thème de l'application, en français. Elles utilisent les fichiers de
démonstration fournis localement : `dummy_data.asc` et `transparent_signals.dbc`.
Ces fichiers ne sont pas ajoutés au dépôt.

## Sélection présentée

L'extrait contient **28 482 trames**, de **370 à 530 secondes** dans le repère
du fichier. Les curseurs A et B sont placés à **400 s** et **480 s**.

| Signal de démonstration | Titre du visuel | Unité | Échantillons |
| --- | --- | --- | --- |
| `Motor_Current` | Courant moteur | A | 1 526 |
| `Vehicle_Speed` | Vitesse | km/h | 1 532 |
| `High_Voltage` | Tension haute | V | 1 556 |

Les alias ne changent ni le décodage ni les valeurs. Ils sont appliqués au rendu
documentaire et ne constituent pas une fonction de renommage dans l'application.
Le rapport décrit uniquement l'extrait et le DBC chargé, pas la capture complète.

## Masquage avant capture

Le script remplace les textes sensibles directement dans les widgets avant
leur export en PNG. Aucun identifiant ni octet brut n'est conservé sous un
flou ou une couche transparente dans l'image finale.

- **Trace** : identifiants CAN, données brutes et noms de messages remplacés
  par « Masqué ».
- **Inspecteur** : identifiant, charge utile, détail des octets, message et
  empreinte DBC remplacés par « Masqué ».
- **Explorateur** : base et groupes de messages nommés génériquement,
  identifiants supprimés des libellés visibles.
- **Rapport** : identifiants, derniers octets et empreintes masqués ; source
  et nom de base génériques. Volumes, cadence et couverture conservés.
- **Enregistrement** : profil, texte d'essai et dossier de destination de
  démonstration, sans chemin utilisateur.

Les valeurs physiques, les courbes, les horodatages et les statistiques restent
visibles. Ce dispositif masque les champs documentés ; il ne transforme pas les
fichiers sources et ne constitue pas un export anonymisé de la session.

## Reproduction

Depuis la racine du dépôt, après `uv sync --all-extras` :

```bash
QT_QPA_PLATFORM=offscreen uv run python scripts/capture_readme.py \
  /chemin/vers/dummy_data.asc \
  /chemin/vers/dossier-dbc
```

Le second argument désigne le dossier contenant `transparent_signals.dbc`.
`--output /chemin/vers/images` permet de changer le dossier de sortie.

Le script utilise un profil et des préférences de langue temporaires. Il
n'ouvre aucune connexion CAN. Les trames sont triées chronologiquement, puis
transmises au traitement de l'application sans changer leurs horodatages ou
leur contenu. Le rendu attend la fin de la persistance et vérifie les trois
signaux, la fenêtre temporelle et les mesures A/B.

Les cinq fichiers produits sont `graphs.png`, `workspace.png`, `trace.png`,
`report.png` et `recording.png`. Les décomptes d'échantillons sont imprimés en
fin d'exécution. Vérifier visuellement chaque image avant publication, notamment
si un panneau ou le format du rapport a évolué.

Le rendu utilise les interfaces internes de PeakLive ; il doit être adapté
lorsque celles-ci changent. Les polices et décorations peuvent différer entre
Linux et Windows.
