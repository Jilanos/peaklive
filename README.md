# PeakLive

**Acquérir, décoder et comprendre les données CAN dans un même espace de travail.**

PeakLive réunit les courbes, les trames et les mesures pour suivre un essai en
direct ou analyser un enregistrement. Chargez vos DBC, choisissez les signaux
utiles et comparez leurs évolutions sur un axe temporel commun.

Application de bureau pour **Windows 10/11 x64**, interface **français / anglais**,
fonctionnement **entièrement local**, sans compte ni service cloud.
L'acquisition utilise les interfaces **PEAK PCAN** ; un adaptateur simulé permet
d'explorer l'application sans matériel.

![Courant moteur, vitesse et tension haute : trois courbes synchronisées avec mesures A/B](docs/images/graphs.png)

*Extrait de démonstration entre 370 et 530 s, avec les curseurs à 400 et 480 s.
Les valeurs décodées sont conservées ; les identifiants et octets bruts sont
masqués dans les captures.*

## De la vue d'ensemble au détail

Gardez les signaux, les courbes et la trace côte à côte, ou donnez toute la place
à la vue qui vous intéresse. Les panneaux se replient et se redimensionnent ;
le profil mémorise votre disposition.

![Vue combinée avec sélection de signaux, courbes et trace aux informations sensibles masquées](docs/images/workspace.png)

| Vue | Pour quoi faire ? |
| --- | --- |
| **Combiné / Combo** | Rapprocher les courbes, les trames et le rapport. |
| **Graphiques / Graphs** | Comparer les signaux et mesurer un intervalle. |
| **Trace** | Filtrer les trames et examiner leur décodage. |
| **Rapport / Report** | Consulter les volumes, la couverture DBC et les anomalies. |

## Voir et mesurer les signaux

Chargez une ou plusieurs bases **DBC**, recherchez les signaux, ajoutez-les aux
favoris et choisissez ceux à afficher. Chaque courbe conserve son unité et son
axe vertical ; toutes partagent le même axe temporel.

- **Navigation** : zoom, déplacement, ajustement X + Y ou Y seulement.
- **Suivi du direct** : durée complète ou fenêtre glissante. La navigation
  manuelle suspend le suivi pour garder la zone examinée.
- **Curseurs A/B** : valeurs aux deux instants, différences et durée commune.
- **Mesures sur l'intervalle** : nombre d'échantillons, minimum, maximum,
  moyenne, écart-type et RMS ; distribution pour les valeurs énumérées.
- **Historique sur disque** : consultation au-delà des points conservés en
  mémoire, avec chargement selon la fenêtre visible.

Le menu **DBC** permet d'activer, désactiver ou retirer une base et de choisir
la définition à utiliser lorsque plusieurs bases décrivent le même identifiant.

## Relier une observation aux trames

La trace chronologique rassemble les trames et les événements. Filtrez par
identifiant, message, signal, direction, statut de décodage ou période, puis
sélectionnez une ligne pour ouvrir l'inspecteur. Les colonnes sont configurables
et les informations peuvent être copiées.

![Trace et inspecteur avec identifiants, messages, empreinte DBC et octets bruts masqués](docs/images/trace.png)

*Les mentions « Masqué » sont appliquées uniquement aux visuels de cette
documentation. Dans l'application, l'inspecteur affiche les informations
complètes du fichier chargé. Les filtres d'affichage ne filtrent jamais
l'enregistrement.*

## Acquérir et enregistrer

PeakLive reçoit un canal **Classic CAN** à 125, 250, 500 ou 1 000 kbit/s.
Le contrôleur peut fonctionner en mode normal ou en écoute passive selon
l'adaptateur. Les commandes de démarrage et d'arrêt sont explicites ; restaurer
un profil ne démarre jamais le bus.

L'état de connexion, les erreurs et la finalisation restent visibles. La
réception, l'écriture et la présentation utilisent des traitements séparés.

![Configuration d'un enregistrement ASC avec dossier et nom d'essai génériques](docs/images/recording.png)

L'enregistrement **ASC (Vector)** ou **TRC texte (PCAN-View)** se configure par
profil : dossier, modèle de nom, texte d'essai et prochaine itération. Un aperçu
montre le nom produit, par exemple :

```text
{date}_{time}_{profile}_{text}_{iteration:03d}_{segment:03d}.asc
```

La numérotation évite d'écraser une capture. La rotation en segments, les seuils
d'espace disque et les marqueurs de fichier partiel accompagnent les sessions
longues ou interrompues. Les événements sont conservés dans un fichier associé.

## Relire, synthétiser et exporter

Ouvrez une capture **ASC** ou une variante prise en charge de **TRC texte**,
chargez les DBC et retrouvez les mêmes outils de visualisation et de mesure.
Le chargement s'effectue en arrière-plan avec une progression.

![Rapport de l'extrait de démonstration avec identifiants et charges utiles masqués](docs/images/report.png)

Le rapport synthétise le nombre de trames, la cadence, la couverture de décodage,
les bases chargées et les anomalies. Il peut être actualisé et exporté en texte.
Sa couverture dépend des DBC effectivement chargés : le visuel ci-dessus décrit
uniquement l'extrait de démonstration et sa base.

Exportez les signaux décodés en **CSV** ou **Parquet**, pour l'intervalle A/B,
la fenêtre visible ou le tampon conservé. La portée dépend des échantillons
disponibles dans ce tampon ; elle ne représente pas nécessairement tout le
fichier brut ni tout l'historique de navigation.

## Prise en main

### Analyser un fichier

1. Charger les DBC avec `Ctrl+D`, puis la capture avec `Ctrl+O`.
2. Rechercher les signaux et activer leur affichage.
3. Passer en **Graphiques**, ajuster les axes et placer les curseurs A/B.
4. Utiliser **Trace** et **Rapport** pour compléter l'analyse.
5. Exporter les signaux souhaités avec `Ctrl+E`.

### Préparer une acquisition

1. Installer le pilote PEAK et connecter l'interface PCAN.
2. Choisir le canal, le débit et le mode du contrôleur dans **Configuration**.
3. Charger les DBC, sélectionner les signaux et configurer l'enregistrement.
4. Démarrer avec `F5`, arrêter avec `F6` et attendre la fin de la finalisation.

Un profil conserve les réglages du bus, les DBC, les signaux, les favoris, les
filtres et la disposition. **Enregistrer la configuration de mesure sous…**
(`Ctrl+Shift+S`) crée une copie indépendante pour un autre essai.

La langue se choisit dans **Configuration → Langue** : **Français** ou
**English**. Le changement est immédiat et mémorisé indépendamment du profil.
Il conserve la session, les sélections et les valeurs. Les noms issus des DBC
et les données techniques restent ceux de la source.

### Raccourcis utiles

| Raccourci | Action |
| --- | --- |
| `F5` / `F6` | Démarrer / arrêter l'acquisition |
| `Ctrl+D` / `Ctrl+O` | Charger des DBC / ouvrir une capture |
| `Ctrl+E` | Exporter les signaux |
| `Ctrl+Shift+S` | Enregistrer une copie du profil |
| `Ctrl+1` / `Ctrl+2` | Placer le curseur A / B |
| `Ctrl+0` | Ajuster les courbes |
| `Ctrl+F` | Accéder au filtre de trace |
| `Ctrl+B` | Replier / déplier les signaux |
| `F11` | Basculer en plein écran |

## À propos des visuels

Les cinq captures sont rendues avec les **widgets Qt du dépôt**, à partir de
la capture et du DBC de démonstration fournis pour la documentation. Les courbes
ne sont pas redessinées et les valeurs décodées ne sont pas modifiées.

Les identifiants CAN, les charges utiles et le détail des octets sont remplacés
avant la capture. Les noms de messages visibles dans la trace et l'inspecteur,
les empreintes DBC et les références aux fichiers privés sont également cachés
ou remplacés par des libellés génériques. Les titres français des trois courbes
sont des alias documentaires, pas une fonction de renommage du produit.

Les fichiers sources ne sont pas distribués dans le dépôt. Ce masquage porte
sur les informations visibles dans les images ; les courbes, valeurs physiques
et statistiques restent consultables. Le rendu hors écran sous Linux peut
différer légèrement des décorations Windows.

Voir la [procédure de reproduction et de masquage](docs/screenshots.md).

## Développement et exécutable Windows

Prérequis : **Python 3.13+** et [uv](https://docs.astral.sh/uv/).

```bash
uv sync --all-extras
uv run peaklive
uv run ruff check .
uv run pytest
uv build
```

Pour les tests Qt sans écran : `QT_QPA_PLATFORM=offscreen uv run pytest`.
`PEAKLIVE_DATA_DIR` isole les profils et les données de développement ;
`PEAKLIVE_ADAPTER=fake` active l'adaptateur simulé.

Depuis PowerShell, `./scripts/build-windows.ps1` produit `dist/PeakLive.exe`.
Le pilote PEAK s'installe séparément. La pile repose sur **PySide6/Qt**,
**pyqtgraph**, **python-can** et **cantools**, avec un historique SQLite.

Le périmètre actuel est la **réception d'un canal Classic CAN**. Le CAN FD,
le LIN, l'émission de trames, l'acquisition multicanal synchronisée et les
protocoles de diagnostic ne sont pas proposés. La simulation et les tests
logiciels ne remplacent pas une qualification sur le matériel réel.

## Documentation

- [Périmètre produit](docs/product-scope.md) et [architecture](docs/architecture.md)
- [Identité des builds](docs/build-identity.md)
- [Qualification Windows](docs/windows-qualification.md)
- [Vérification bilingue](docs/bilingual-windows-smoke.md)
- [Acceptation matérielle](docs/windows-hardware-acceptance.md)
- [Essai véhicule de dix minutes](docs/vehicle-test-10m.md)
- [Notes de version 0.1.2](docs/release-notes-0.1.2.md)

Les demandes, décisions et validations sont suivies dans `logics/`.
PeakLive est distribué sous [licence Apache 2.0](LICENSE).
