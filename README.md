# Les trois sœurs

Une histoire dont le lecteur est le héros, imaginée par Agathe et Alyssa pendant l'atelier « Le livre dont tu es le héros » du L.A.B, dans le réseau des bibliothèques Méjanes (Aix-en-Provence), en octobre 2026.

## Modifier le livre

Le texte se trouve dans `source/texte.md`, recopié de la page Notion de référence. Chaque chapitre commence par `## Chapitre n. Titre`, les choix s'écrivent `- texte du lien -> n` et la fin se termine par `FIN`. La couverture, la page « Comment est née cette histoire » et la mise en forme sont dans `source/construire_site.py`. Les illustrations vont dans `images/chapitres/` (`prologue.jpg`, `chapitre-01.jpg`…, en 1200 pixels de large au plus) et la couverture dans `images/couverture.jpg` ; une page sans image s'affiche sur une seule colonne. L'arbre se redessine avec `python3 source/construire_arbre.py`, qui vérifie que ses flèches correspondent aux renvois du texte.

Après une modification, reconstruire la page :

```
python3 source/construire_site.py
```

Réalisation du livre : L.A.B, Laboratoire d'Aix-périmentation et de Bidouille.
