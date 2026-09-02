# CSI 1 - Présentation de suivi de thèse

Présentation web du premier Comité de suivi individuel de Luc Perroquin.

Le projet reprend la direction artistique du Portfolio académique tout en l'adaptant à un usage de présentation : grandes cartes, ombres souples, palette vert profond et crème, titres serif, mode sombre et options d'accessibilité.

## Contenu

La présentation a été réorganisée pour éviter la répétition entre les diapositives et créer un fil narratif continu :

1. construction de la question scientifique ;
2. programme expérimental et résultats déjà acquis ;
3. infrastructure commune qui rend les études possibles ;
4. développement doctoral, priorités et questions au comité.

Les détails techniques sont déplacés dans des annexes afin de conserver un oral fluide sans perdre l'information.

## Utilisation

Ouvrir simplement `index.html` dans un navigateur moderne.

Deux modes sont disponibles :

- **Mode diapo** : une slide plein écran à la fois.
- **Mode scroll** : lecture continue comme une page web.

La présentation fonctionne sans dépendance externe et sans installation.

## Navigation

- `←` / `→` ou espace : slide précédente / suivante
- `Home` / `End` : début / fin
- `M` : basculer diapo / scroll
- `O` : vue d'ensemble
- `N` : notes orateur
- `F` : plein écran
- `C` : personnalisation
- balayage horizontal sur écran tactile : navigation entre slides

Un sommaire, une recherche de slide, une barre de progression et un chronomètre sont intégrés.

## Personnalisation

Les préférences sont sauvegardées localement dans le navigateur :

- thème clair, sombre ou système ;
- palette Portfolio, bleu, cassis ou ocre ;
- taille du texte ;
- contraste élevé ;
- police très lisible ;
- réduction des animations ;
- inclusion ou non des annexes dans le mode diapo.

## Structure technique

Le site repose volontairement sur un seul fichier applicatif :

- `index.html` : HTML, CSS, contenu de la présentation et JavaScript ;
- `README.md` : documentation ;
- `.gitignore` : fichiers locaux à exclure.

Les slides sont définies dans le tableau JavaScript `slides` à la fin de `index.html`. Chaque entrée contient notamment :

- `section`
- `kicker`
- `title`
- `lead`
- `content`
- `notes`
- `appendix` pour les annexes facultatives

Cette structure permet d'ajouter, retirer ou réordonner une slide sans toucher au moteur de présentation.

## GitHub Pages

Le dépôt peut être publié directement avec GitHub Pages en utilisant la branche `main` et la racine du dépôt comme source.

Une fois Pages activé dans les paramètres du dépôt, l'URL attendue est :

`https://lucper01.github.io/CSI-1/`

## Données scientifiques

Le contenu distingue explicitement les résultats préliminaires, les études en cours et les perspectives. Les paramètres ou résultats non verrouillés ne sont pas présentés comme définitifs.

## Licence

Aucune licence n'est ajoutée automatiquement à ce dépôt. Ajouter une licence séparément si nécessaire.
