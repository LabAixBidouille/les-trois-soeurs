#!/usr/bin/env python3
"""Construit index.html à partir de source/texte.md.

Le moteur Harlowe (repris au départ du site de La Lune de Rambo, puis de Violette et Patate) est
conservé tel quel dans index.html : seules les pages et la feuille de style du livre sont régénérées.

Usage, depuis la racine du dépôt : python3 source/construire_site.py
"""
import html
import re
import uuid
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
TEXTE = RACINE / "source" / "texte.md"
SORTIE = RACINE / "index.html"
NOINDEX = '<meta name="robots" content="noindex, nofollow, noarchive">'
# Favicon : la patte de loup étoilée dessinée par Manon
FAVICON = ('<link rel="icon" type="image/png" sizes="48x48" href="images/favicon-48.png">'
           '<link rel="icon" type="image/png" sizes="180x180" href="images/favicon.png">'
           '<link rel="apple-touch-icon" href="images/favicon.png">')

TITRE = "Les trois sœurs"
AUTRICES = "Agathe et Alyssa"

# Résumé écrit par Manon le 03/11/2026
SYNOPSIS = (
    "Abandonnées bébés au cœur d’une forêt, Rose, Rosi et Sofia ont grandi sans se connaître, chacune "
    "dans un pays différent. Toutes trois possèdent des dons étranges… et font le même rêve peuplé de "
    "loups.\n\n"
    "Un soir, une carte mystérieuse les réunit. Les trois filles se lancent alors sur les traces de leur "
    "passé, jusqu’à une maison oubliée à l’orée des bois. Mais un homme à la bague en forme de loup "
    "semble lui aussi les chercher…\n\n"
    "Qui sont-elles vraiment ? Que s’est-il passé la nuit de leur disparition ? Lance le dé et découvre "
    "leur histoire !"
)

# Texte écrit par Manon le 03/11/2026, modèle commun aux livres de l'atelier : seuls les noms changent
CONTEXTE = [
    "En octobre 2026, le L.A.B a animé l’atelier « La quête du curry, une histoire dont tu es le héros » "
    "dans les bibliothèques Méjanes d’Aix-en-Provence. Les enfants ont été accompagnés dans la création "
    "d’un récit complet, depuis l’invention des personnages jusqu’à la construction d’une intrigue "
    "reliant les différentes étapes de leur aventure.",
    "Nous leur avons proposé d’introduire une part de hasard dans leur récit. Le résultat d’un lancer de "
    "dé pouvait modifier le déroulement de certains passages et conduire le lecteur vers un chapitre ou "
    "un autre.",
    "Les enfants ont ainsi exploré, sans écran, des notions liées à la pensée computationnelle, une "
    "manière de décomposer un problème et d’organiser les étapes pour le résoudre. Ils ont formulé des "
    "règles de type « si… alors… », créé des embranchements et réfléchi à la façon dont les chemins se "
    "rejoignent pour former une histoire cohérente.",
    f"{AUTRICES} ont choisi d’inventer un mystère. Un défi pour une histoire à embranchements, puisque "
    "les indices doivent garder leur sens et la révélation fonctionner, quel que soit le chemin emprunté.",
    "L’atelier ne durant que deux heures, nous tenions à offrir à chaque enfant un livre complet "
    "pour illustrer leur travail et les rendre fiers de leurs productions. Le L.A.B a donc "
    "prolongé et mis en forme leur récit à l’aide d’outils numériques (l’intelligence "
    "artificielle a notamment permis d’aboutir à une histoire achevée et à un ensemble de visuels "
    "correspondant à leurs descriptions mais uniformes tout au long de la lecture).\n\n<b>À son "
    "origine, il y a avant tout les idées, les personnages et les dessins d’Agathe et "
    "d’Alyssa.</b>",
]
# Les mots d'Agathe sur sa fiche récit, à peine remis au propre
CITATION = ("Les loups se rappellent et ils ne bougent pas. Elles parlent aux loups, qui leur disent "
            "qu'ils étaient gentils et qu'ils les protégeaient d'un homme qui les cherchait.")

CSS = """
@font-face { font-family: "IM Fell English"; font-style: normal; font-weight: 400; font-display: swap; src: url("fonts/IMFellEnglish.woff2") format("woff2"); }
@font-face { font-family: "IM Fell English"; font-style: italic; font-weight: 400; font-display: swap; src: url("fonts/IMFellEnglish-italique.woff2") format("woff2"); }
@font-face { font-family: "EB Garamond"; font-style: normal; font-weight: 400 800; font-display: swap; src: url("fonts/EBGaramond.woff2") format("woff2"); }
@font-face { font-family: "EB Garamond"; font-style: italic; font-weight: 400 800; font-display: swap; src: url("fonts/EBGaramond-italique.woff2") format("woff2"); }

/* Couleurs : le bleu violacé du ciel de nuit, l'or des mains qui brillent */
:root {
  --nuit: #1d2b4f;
  --nuit-fonce: #131c33;
  --or-fonce: #a8740f;
  --foret: #2f4b3c;
  --or: #d99a2b;
  --or-clair: #f7e3b0;
  --rouille: #b9441c;
  --couchant: #e98a4b;
  --encre: #22263a;
  --gris: #5d6475;
  --papier: #ffffff;
}
html, body, tw-story {
  background-color: var(--papier);
  color: var(--encre);
}
tw-story {
  /* Garamond, de la même famille de livres anciens que la police des titres ; un peu plus grand,
     car ses lettres sont plus petites que celles de Lora */
  font-family: "EB Garamond", Georgia, serif;
  font-size: 1.2em;
  line-height: 1.75;
  padding: 4em 1.25em 4em;
}
tw-passage {
  max-width: 1180px;
  margin: 0 auto;
}

/* Pages de lecture : le texte à gauche, l'illustration à droite */
.page {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  gap: 2.5em;
  align-items: start;
}
.cote {
  position: sticky;
  top: 1.5em;
  margin-top: 2.5em;
}
.illustration { display: flex; flex-direction: column; }
.halo { display: block; }
.illustration img {
  display: block;
  width: 100%;
  max-height: 85vh;
  object-fit: contain;
  border-radius: 10px;
  box-shadow: 0 6px 24px rgba(19, 28, 51, 0.25);
}
.illustration .halo + .halo { margin-top: 1.2em; }
/* Tant qu'un chapitre n'a pas d'illustration, son texte reste en une colonne centrée */
.page:not(:has(.cote)) { grid-template-columns: minmax(0, 38em); justify-content: center; }
@media (max-width: 800px) {
  .page { grid-template-columns: minmax(0, 1fr); gap: 1.2em; }
  /* Sur téléphone : l'illustration au-dessus du texte */
  .cote { position: static; order: -1; margin-top: 0; }
}
tw-sidebar { display: none; }
/* Harlowe met « overflow: hidden » sur tw-story, ce qui empêche la colonne de droite de rester
   visible au défilement ; « clip » coupe pareil sans créer de zone de défilement */
tw-story { overflow: clip; }

/* Titres de chapitre : le numéro en italique doré, le titre en caractères de vieux livre */
.chapitre {
  font-size: 1em;
  font-weight: 400;
  margin: 0 0 1.1em;
  line-height: 1.1;
}
.chapitre .numero {
  display: block;
  font-family: "IM Fell English", Georgia, serif;
  font-style: italic;
  font-size: 1.3em;
  color: var(--or-fonce);
  letter-spacing: 0.04em;
  margin-bottom: 0.2em;
}
.chapitre .titre {
  display: block;
  font-family: "IM Fell English", Georgia, serif;
  font-weight: 400;
  font-size: 2.4em;
  color: var(--nuit);
}

/* Page de garde */
/* La couverture tient dans l'écran : marges réduites et tailles qui suivent la hauteur de l'écran */
tw-story:has(.garde) { padding-top: 1em; padding-bottom: 1em; }
.garde {
  min-height: calc(100vh - 2.2em);
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: clamp(0.8em, 3vh, 2em);
}
.garde-entete {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.garde-corps {
  display: grid;
  /* Le triptyque des trois sœurs est en paysage : il prend la plus large des deux colonnes */
  grid-template-columns: minmax(0, 1.1fr) minmax(26em, 1fr);
  gap: 3.5em;
  align-items: center;
  width: 100%;
  max-width: 1120px;
  margin: 0 auto;
}
.garde-image img {
  display: block;
  width: 100%;
  height: auto;
}
.garde-texte {
  display: flex;
  flex-direction: column;
  /* Même écart entre le résumé, le séparateur, le bouton Commencer et les deux petits boutons */
  gap: clamp(1.2em, 3.6vh, 2.1em);
  text-align: center;
}
@media (max-width: 800px) {
  .garde { min-height: 0; }
  .garde-corps { grid-template-columns: minmax(0, 1fr); gap: 1em; }
  .garde-image { text-align: center; }
  .garde-image img { max-height: 70vh; }
}
.garde .surtitre {
  font-family: "IM Fell English", Georgia, serif;
  font-style: italic;
  font-size: 1.05em;
  color: var(--gris);
}
.garde .grand-titre {
  font-family: "IM Fell English", Georgia, serif;
  font-size: clamp(2.4em, 8vh, 4.6em);
  line-height: 0.95;
  letter-spacing: -0.02em;
  color: var(--nuit);
  margin: 0.05em 0 0.05em;
}
.garde .nom-auteur {
  font-family: "IM Fell English", Georgia, serif;
  font-style: italic;
  font-size: clamp(1.3em, 3.6vh, 1.8em);
  color: var(--or-fonce);
}
.garde .synopsis {
  margin: 0 auto;
  max-width: 40em;
  font-size: 1.05em;
  line-height: 1.65;
}
/* Commencer : en gras, entre deux fioritures dorées terminées par une étoile, sans cadre de bouton ;
   au survol, le texte prend une lueur dorée */
.garde .commencer, .contexte .commencer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.9em;
}
.garde .commencer::before, .garde .commencer::after,
.contexte .commencer::before, .contexte .commencer::after {
  content: "";
  flex: 0 1 7.5em;
  height: 1.2em;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 20' preserveAspectRatio='none'%3E%3Cpath d='M24 10 C46 10 56 4 72 7 C86 10 96 14 118 10' fill='none' stroke='%23d99a2b' stroke-width='1.4' stroke-linecap='round'/%3E%3Cpath d='M7 3 l1.7 4.3 4.3 .4-3.3 2.9 1 4.3L7 12.6l-3.7 2.3 1-4.3L1 7.7l4.3-.4z' fill='%23d99a2b'/%3E%3C/svg%3E") no-repeat center / 100% 100%;
}
.garde .commencer::after, .contexte .commencer::after { transform: scaleX(-1); }
.garde .commencer tw-link, .garde .commencer .enchantment-link,
.contexte .commencer tw-link, .contexte .commencer .enchantment-link {
  font-family: "IM Fell English", Georgia, serif;
  font-weight: 700;
  font-size: 1.6em;
  letter-spacing: 0.02em;
  color: var(--nuit);
  border: none;
  background: none;
  white-space: nowrap;
  transition: color 0.25s ease, text-shadow 0.25s ease;
}
.garde .commencer tw-link:hover, .garde .commencer .enchantment-link:hover,
.contexte .commencer tw-link:hover, .contexte .commencer .enchantment-link:hover {
  color: var(--nuit);
  text-shadow: 0 0 12px rgba(217, 154, 43, 0.75);
}

/* Boutons de renvoi : une étiquette de vieux livre, cernée d'un double filet doré, sans aplat ;
   au survol, elle se remplit de nuit et l'or s'allume */
.elan tw-link, .elan .enchantment-link {
  display: inline-block;
  font-family: "IM Fell English", Georgia, serif;
  font-weight: 400;
  font-size: 1.4em;
  letter-spacing: 0.03em;
  color: var(--nuit);
  background-color: transparent;
  border: 1px solid var(--or);
  border-radius: 2px;
  outline: 1px solid var(--or);
  outline-offset: 3px;
  padding: 0.3em 1.3em 0.35em;
  transition: background-color 0.25s ease, color 0.25s ease, box-shadow 0.25s ease;
}
.elan tw-link::before, .elan tw-link::after {
  content: "✦";
  font-size: 0.55em;
  color: var(--or);
  vertical-align: middle;
}
.elan tw-link::before { margin-right: 0.9em; }
.elan tw-link::after { margin-left: 0.9em; }
/* Au survol, le texte passe en blanc : le doré foncé des liens de choix disparaissait sur le bleu.
   « .choix.elan » est plus spécifique que la règle des liens de choix, qui l'emportait */
.choix.elan tw-link:hover, .choix.elan .enchantment-link:hover {
  color: #ffffff;
  background-color: var(--nuit);
  box-shadow: 0 0 16px 3px rgba(217, 154, 43, 0.4);
}
.garde .secondaires {
  margin-top: 4px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.8em 1.4em;
}

/* Petits boutons secondaires */
.secondaires tw-link, .secondaires .enchantment-link {
  display: inline-block;
  font-size: 0.85em;
  color: var(--nuit);
  border: 1.5px solid var(--nuit);
  border-radius: 999px;
  padding: 0.3em 1em;
}
.secondaires tw-link:hover, .secondaires .enchantment-link:hover {
  background-color: var(--nuit);
  color: #ffffff;
}

/* Lien Couverture : discret, en haut à gauche, au-dessus du numéro de chapitre */
.retour {
  margin: 0 auto 1.2em;
  text-align: left;
}
.retour tw-link, .retour .enchantment-link,
.lien-retour tw-link, .lien-retour .enchantment-link {
  font-size: 0.9em;
  font-weight: 600;
  color: var(--gris);
}
.retour tw-link::before, .lien-retour tw-link::before { content: "← "; }
.retour tw-link:hover, .retour .enchantment-link:hover,
.lien-retour tw-link:hover, .lien-retour .enchantment-link:hover { color: var(--or-fonce); }
.contexte .lien-retour { display: block; margin-bottom: 1em; }

/* Le lancer de dé */
.de .consigne {
  display: block;
  font-family: "IM Fell English", Georgia, serif;
  font-style: italic;
  font-size: 1.35em;
  line-height: 1.3;
  color: var(--nuit);
  margin-bottom: 0.5em;
}
/* Choix en liste à puces : une petite étoile dorée devant chaque suite possible */
.choix {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.45em;
}
.choix > *::before {
  content: "✦";
  color: var(--or);
  margin-right: 0.55em;
}
.choix tw-link, .choix .enchantment-link {
  color: var(--nuit);
  font-weight: 700;
  border-bottom: 1.5px solid rgba(29, 43, 79, 0.3);
}
.choix tw-link:hover, .choix .enchantment-link:hover {
  color: var(--or-fonce);
  border-bottom-color: var(--or-fonce);
}
.elan > *::before { content: none; }
.suite {
  margin-top: 0.8em;
}

/* Séparateur : la patte de loup étoilée de Manon, entre deux traits dorés */
.separateur {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.8em;
  margin: 1.6em 0 1.1em;
}
.separateur::before, .separateur::after {
  content: "";
  width: 6em;
  height: 1px;
  background: linear-gradient(to right, transparent, var(--or));
}
.separateur::after { background: linear-gradient(to left, transparent, var(--or)); }
.separateur .embleme {
  /* La patte de loup étoilée dessinée par Manon, qui sert aussi de favicon */
  width: 2.4em;
  height: 2.4em;
  background: url("images/embleme.png") no-repeat center / contain;
}

/* Bouton de renvoi, quand il n'y a qu'une suite possible : la même étiquette que Commencer, en plus petit */
.elan {
  align-items: center;
  margin-top: 2.2em;
}
/* plus spécifique que les liens de choix, qui sont en gras et soulignés */
.choix.elan tw-link, .choix.elan .enchantment-link { font-size: 1.15em; font-weight: 400; border-bottom: 1px solid var(--or); }

/* Sur le site, le dé devient une carte, comme celles que reçoivent les trois sœurs : un dos bleu nuit à
   la patte de loup ; touchée, elle tourne sur elle-même et révèle des points d'or disposés comme sur
   un dé. Elle ne choisit jamais à la place du lecteur */
.de {
  display: flex;
  align-items: center;
  gap: 1.6em;
}
.de-texte { flex: 1; min-width: 0; }
.lancer {
  flex: none;
  position: relative;
  display: flex;
  perspective: 30em;
}
.carte {
  position: relative;
  width: 5em;
  height: 6.8em;
  padding: 0;
  border-radius: 0.55em;
  /* un bouton ne reprend pas la taille du texte : sans cette ligne, la carte restait petite */
  font-size: inherit;
  /* bleu plus clair qu'avant, pour que la patte de loup se détache */
  background: radial-gradient(circle at 50% 38%, #5a6fa8, #3d5287 55%, #2b3c68);
  border: 1px solid var(--or);
  outline: 1px solid var(--or);
  outline-offset: -5px;
  box-shadow: 0 6px 16px rgba(19, 28, 51, 0.28);
  cursor: pointer;
  transition: box-shadow 0.3s ease;
}
.carte:hover { box-shadow: 0 0 22px 4px rgba(217, 154, 43, 0.45); }
.carte.tourne { animation: tourne 0.9s ease-in-out; }
@keyframes tourne { from { transform: rotateY(0); } to { transform: rotateY(1080deg); } }
.carte .dos {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.carte .dos img { width: 64%; filter: drop-shadow(0 0 6px rgba(247, 227, 176, 0.45)); }
.carte .dos::before, .carte .dos::after { content: "✦"; position: absolute; color: var(--or); font-size: 0.6em; }
.carte .dos::before { top: 1em; }
.carte .dos::after { bottom: 1em; }
.carte .devant {
  position: absolute;
  inset: 22% 16%;
  display: none;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
}
.carte.montre .dos { display: none; }
.carte.montre .devant { display: grid; }
.carte .devant i {
  width: 0.85em;
  height: 0.85em;
  border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, #fff6d8 0%, var(--or-clair) 35%, var(--or) 100%);
  box-shadow: 0 0 6px 1px rgba(247, 227, 176, 0.8);
  place-self: center;
  visibility: hidden;
}
.carte[data-face="1"] i:nth-child(5),
.carte[data-face="2"] i:is(:nth-child(1), :nth-child(9)),
.carte[data-face="3"] i:is(:nth-child(1), :nth-child(5), :nth-child(9)),
.carte[data-face="4"] i:is(:nth-child(1), :nth-child(3), :nth-child(7), :nth-child(9)),
.carte[data-face="5"] i:is(:nth-child(1), :nth-child(3), :nth-child(5), :nth-child(7), :nth-child(9)),
.carte[data-face="6"] i:is(:nth-child(1), :nth-child(3), :nth-child(4), :nth-child(6), :nth-child(7), :nth-child(9)) {
  visibility: visible;
}
.resultat {
  position: absolute;
  top: calc(100% + 0.6em);
  left: 50%;
  transform: translateX(-50%);
  white-space: nowrap;
  font-family: "IM Fell English", Georgia, serif;
  font-style: italic;
  font-size: 1.05em;
  color: var(--or-fonce);
  text-align: center;
}
@media (max-width: 600px) {
  .de { gap: 0.8em; }
  .carte { width: 4.4em; height: 6em; }
  .carte .devant i { width: 0.55em; height: 0.55em; }
}

/* Fin */
.fin {
  margin-top: 0.6em;
  text-align: center;
}
.fin .mot-fin {
  display: block;
  font-family: "IM Fell English", Georgia, serif;
  font-size: 2.8em;
  letter-spacing: 0.08em;
  color: var(--nuit);
  margin-bottom: 0.4em;
}

/* Phrase mise en avant dans le texte */
.appel {
  font-family: "IM Fell English", Georgia, serif;
  font-style: italic;
  font-size: 1.4em;
  color: var(--or-fonce);
}

/* Page « Comment est née cette histoire » */
.contexte h1 {
  line-height: 1.1;
  font-family: "IM Fell English", Georgia, serif;
  font-weight: 400;
  font-size: 2.2em;
  color: var(--nuit);
  margin: 0 0 0.6em;
}
.contexte .credits {
  font-size: 0.92em;
  color: var(--gris);
}

.arbre .lien-retour { display: block; font-size: 0.86em; }

/* Page de l'arbre : le titre centré en haut, l'arbre dessous */
.arbre-tete { text-align: center; margin-bottom: 1.5em; }
.arbre h1 {
  font-family: "IM Fell English", Georgia, serif;
  font-weight: 400;
  font-size: 2.5em;
  line-height: 1.1;
  color: var(--nuit);
  margin: 0;
}
.arbre .arbre-sous-titre {
  display: block;
  font-family: "IM Fell English", Georgia, serif;
  font-style: italic;
  font-size: 1.25em;
  color: var(--gris);
  margin: 0.3em 0 1em;
}
.arbre img {
  display: block;
  width: 100%;
  max-width: 760px;
  height: auto;
  margin: 0 auto;
}

/* Page de contexte : les trois sœurs dessinées par les autrices, un texte court au centre, une phrase
   de leur fiche, puis leurs fiches sur une table, en miniatures cliquables */
.contexte {
  font-size: 0.86em;
}
.contexte-tete {
  text-align: center;
}
.portraits {
  display: flex;
  justify-content: center;
  align-items: flex-end;
  gap: 2.2em;
  margin: 0 auto 0.6em;
}
.portraits figure { margin: 0; }
.portraits img { display: block; height: 11em; width: auto; margin: 0 auto; }
.portraits figcaption {
  font-family: "IM Fell English", Georgia, serif;
  font-style: italic;
  font-size: 1.05em;
  color: var(--or-fonce);
  margin-top: 0.3em;
}
.contexte h1 {
  font-size: 2.6em;
  margin: 0.2em 0 0.1em;
}
.contexte-texte {
  max-width: 36em;
  margin: 0 auto;
  text-align: center;
}
.citation {
  max-width: 30em;
  margin: 2em auto;
  padding: 1.1em 0;
  border-top: 1px solid var(--or);
  border-bottom: 1px solid var(--or);
  text-align: center;
  font-family: "IM Fell English", Georgia, serif;
  font-style: italic;
  font-size: 1.35em;
  line-height: 1.45;
  color: var(--nuit);
}
.citation .source {
  display: block;
  margin-top: 0.6em;
  font-family: "EB Garamond", Georgia, serif;
  font-size: 0.68em;
  letter-spacing: 0.04em;
  color: var(--gris);
}
.contexte .credits {
  display: block;
  text-align: center;
  margin-top: 1.6em;
}
/* La table : un papier clair où les fiches sont posées de travers */
.table-fiches {
  margin: 2.8em auto 0;
  max-width: 62em;
  padding: 2em 1.5em 1.6em;
  background: #f6f3ec;
  border-radius: 14px;
  text-align: center;
}
.table-fiches .titre-table {
  display: block;
  font-family: "IM Fell English", Georgia, serif;
  font-style: italic;
  font-size: 1.3em;
  color: var(--nuit);
  margin-bottom: 1.2em;
}
.miniatures {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 2.4em;
}
.miniatures figure { margin: 0; }
.miniatures figcaption {
  margin-top: 0.8em;
  font-size: 0.95em;
  color: var(--gris);
}
.miniature {
  display: block;
  padding: 0;
  border: none;
  background: none;
  cursor: zoom-in;
}
.miniature img {
  display: block;
  height: 16em;
  width: auto;
  border-radius: 3px;
  box-shadow: 0 3px 12px rgba(34, 38, 58, 0.22);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.miniatures figure:nth-child(1) img { transform: rotate(-3deg); }
.miniatures figure:nth-child(2) img { transform: rotate(1deg); }
.miniatures figure:nth-child(3) img { transform: rotate(3deg); }
.miniatures .miniature:hover img { transform: rotate(0) scale(1.05); box-shadow: 0 0 0 2px var(--or), 0 8px 20px rgba(34, 38, 58, 0.28); }
.indication {
  display: block;
  margin-top: 1.2em;
  font-size: 0.9em;
  font-style: italic;
  color: var(--gris);
}
.contexte .commencer { margin-top: 2.2em; }
@media (max-width: 600px) {
  .portraits { gap: 0.8em; }
  .portraits img { height: 7.5em; }
  .miniature img { height: 11em; }
}

/* Fiche ouverte en grand par-dessus la page ; un clic n'importe où la referme */
.agrandi {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2vh 2vw;
  background: rgba(19, 28, 51, 0.82);
  cursor: zoom-out;
}
.agrandi img {
  max-width: 100%;
  max-height: 96vh;
  border-radius: 4px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
}
@media (max-width: 600px) {
  .miniature img { height: 11em; }
}

/* Liens dans le texte */
tw-link, .enchantment-link {
  color: var(--nuit);
  font-weight: 700;
  text-decoration: none;
}
tw-link:hover, .enchantment-link:hover { color: var(--or-fonce); }

@media (max-width: 600px) {
  tw-story { font-size: 0.98em; }
  .garde .grand-titre { font-size: 3em; }
  .chapitre .titre { font-size: 1.9em; }
}

/* Écrans peu hauts : on resserre le résumé et les espacements pour que tout tienne */
@media (max-height: 620px) and (min-width: 801px) {
  tw-story:has(.garde) { padding-top: 0.6em; padding-bottom: 0.6em; }
  .garde { min-height: calc(100vh - 1.4em); gap: 0.6em; }
  .garde .synopsis { font-size: 0.95em; line-height: 1.45; }
  .garde-texte { gap: 0.85em; }
  .garde-image img { max-height: 58vh; }
}
"""


def e(texte):
    return html.escape(texte, quote=True)


def lire_chapitres():
    blocs = re.split(r"^## ", TEXTE.read_text(encoding="utf-8"), flags=re.M)[1:]
    chapitres = []
    for bloc in blocs:
        lignes = bloc.strip().split("\n")
        titre_complet = lignes[0].strip()
        numero, titre = titre_complet.split(". ", 1)
        nom = numero
        paragraphes = [p.strip() for p in "\n".join(lignes[1:]).split("\n\n") if p.strip()]
        chapitres.append({"nom": nom, "numero": numero, "titre": titre, "paragraphes": paragraphes})
    return chapitres


SEPARATEUR = '<div class="separateur"><span class="embleme"></span></div>'


DE_VIRTUEL = (
    '<div class="lancer"><button class="carte" type="button" data-face="0" aria-label="Retourner la carte">'
    '<span class="dos"><img src="images/embleme.png" alt=""></span>'
    '<span class="devant">' + "<i></i>" * 9 + '</span></button>'
    '<span class="resultat" aria-live="polite"></span></div>'
)

# Script commun à toutes les pages : fait rouler le dé puis affiche la face tirée, sans choisir
SCRIPT_DE = """
// La carte tourne sur elle-même ; à mi-tour, elle montre la face tirée. Elle ne choisit pas la suite
document.addEventListener('click', function (evenement) {
  var carte = evenement.target.closest('.carte');
  if (!carte || carte.classList.contains('tourne')) return;
  var resultat = carte.parentNode.querySelector('.resultat');
  var face = 1 + Math.floor(Math.random() * 6);
  resultat.textContent = '';
  carte.classList.add('tourne');
  setTimeout(function () {
    carte.setAttribute('data-face', face);
    carte.classList.add('montre');
  }, 450);
  setTimeout(function () {
    carte.classList.remove('tourne');
    resultat.textContent = 'La carte montre ' + face + '.';
  }, 900);
});

// Page de contexte : une miniature s'ouvre en grand, un clic referme
document.addEventListener('click', function (evenement) {
  var ouvert = document.querySelector('.agrandi');
  if (ouvert) { ouvert.remove(); return; }
  var miniature = evenement.target.closest('.miniature');
  if (!miniature) return;
  var fond = document.createElement('div');
  fond.className = 'agrandi';
  var image = document.createElement('img');
  image.src = miniature.querySelector('img').src;
  image.alt = miniature.querySelector('img').alt;
  fond.appendChild(image);
  document.body.appendChild(fond);
});
document.addEventListener('keydown', function (evenement) {
  var ouvert = document.querySelector('.agrandi');
  if (ouvert && evenement.key === 'Escape') ouvert.remove();
});
"""

def lien(texte, cible):
    return f"[[{texte}->{cible}]]"


def passage_chapitre(ch):
    corps = []
    tirage = any(p.startswith("**Lance le dé") for p in ch["paragraphes"])
    consigne = None
    choix = []
    fin = False
    appel = False
    for p in ch["paragraphes"]:
        if p.startswith("- "):
            for ligne in p.split("\n"):
                texte, cible = ligne[2:].rsplit(" -> ", 1)
                choix.append(lien(texte, f"Chapitre {cible}"))
        elif p == "FIN":
            fin = True
        elif p.startswith("**") and p.endswith("**"):
            interieur = p[2:-2]
            if interieur.startswith("Lance le dé") or interieur.startswith("Te souviens-tu"):
                consigne = interieur
            else:
                corps.append(SEPARATEUR + f'<span class="appel">{interieur}</span>')
                appel = True
        else:
            corps.append(p)

    suite = []
    if not appel:
        suite.append(SEPARATEUR)
    if consigne:
        # Sur les vrais tirages, un dé à lancer à droite du bloc consigne et choix ; il montre la face sans choisir
        lancer = DE_VIRTUEL if tirage else ""
        if tirage:
            # Sur le site, le dé devient une carte à toucher, sans flèche
            consigne = consigne.replace("Lance le dé", "Touche la carte", 1)
        suite.append(f'<div class="de"><div class="de-texte"><span class="consigne">{consigne}</span>'
                     f'<div class="choix">{"".join(choix)}</div></div>{lancer}</div>')
    elif len(choix) == 1:
        # Un renvoi seul, sans lancer de dé, devient un bouton
        suite.append(f'<div class="choix suite elan">{"".join(choix)}</div>')
    elif choix:
        # Les épreuves de la route : le lecteur choisit selon ce qu'il a déjà lu, en liste comme les tirages
        suite.append(f'<div class="choix suite">{"".join(choix)}</div>')
    if fin:
        suite.append('<div class="fin"><span class="mot-fin">FIN</span>'
                     f'<div class="secondaires">{lien("Comment est née cette histoire", "Comment est née cette histoire")}</div></div>')
    texte = ('<div class="texte">'
             f'<h1 class="chapitre"><span class="numero">{ch["numero"]}</span>'
             f'<span class="titre">{ch["titre"]}</span></h1>'
             + "\n\n".join(corps) + "".join(suite) + "</div>")
    # Colonne de droite : l'illustration, qui suit la lecture au défilement
    base = illustration(ch['nom'])
    images = [f"images/chapitres/{base}{suffixe}.jpg" for suffixe in ("", "b")
              if (RACINE / f"images/chapitres/{base}{suffixe}.jpg").exists()]
    cote = ""
    if images:
        cote = ('<div class="cote"><div class="illustration">'
                + "".join(f'<span class="halo"><img src="{i}" alt="{ch["titre"]}"></span>' for i in images)
                + '</div></div>')
    return f'<div class="page">{texte}{cote}</div>'


def illustration(nom):
    """Nom du fichier d'illustration : prologue, chapitre-01, chapitre-02…"""
    return "prologue" if nom == "Prologue" else f"chapitre-{int(nom.split()[-1]):02d}"


def passage_garde():
    return (
        # En haut, centrés : surtitre, titre et autrices ; dessous, l'image à gauche et le texte à droite
        '<div class="garde"><div class="garde-entete">'
        '<span class="surtitre">Une histoire dont le lecteur est le héros</span>'
        f'<div class="grand-titre">{TITRE}</div>'
        f'<span class="nom-auteur">{AUTRICES}</span></div>'
        '<div class="garde-corps"><div class="garde-image"><img src="images/couverture.jpg" '
        'alt="Rose à New York, Rosi en Italie et Sofia en Espagne, chacune à sa fenêtre, les mains pleines de lumière"></div>'
        f'<div class="garde-texte"><div class="synopsis">{SYNOPSIS}</div>'
        f'<div class="commencer">{lien("Commencer l'histoire", "Prologue")}</div>'
        f'<div class="secondaires">{lien("Comment est née cette histoire", "Comment est née cette histoire")} '
        f'{lien("L\'arbre de l\'histoire", "L\'arbre de l\'histoire")}</div>'
        "</div></div></div>"
    )


def miniature(fichier, legende, description):
    return (f'<figure><button class="miniature" type="button" aria-label="Agrandir {description}">'
            f'<img src="images/fiches/{fichier}" alt="{description}"></button>'
            f'<figcaption>{legende}</figcaption></figure>')


def portrait(fichier, nom, autrice):
    return (f'<figure><img src="images/portraits/{fichier}" alt="{nom}, dessinée par {autrice}">'
            f'<figcaption>{nom}</figcaption></figure>')


def passage_contexte():
    return (
        '<div class="contexte"><span class="lien-retour">[[Couverture->Page de garde]]</span>\n'
        '<div class="contexte-tete"><div class="portraits">'
        + portrait("rosi.png", "Rosi", "Agathe ou Alyssa")
        + portrait("sofia.png", "Sofia", "Agathe")
        + portrait("rose.png", "Rose", "Alyssa")
        + f'</div><h1>Comment est née cette histoire</h1>{SEPARATEUR}</div>'
        '<div class="contexte-texte">'
        + f'{CONTEXTE[0]}\n\n'
        + "\n\n".join(CONTEXTE[1:4])
        + f'<div class="citation">« {CITATION} »<span class="source">Agathe, sur sa fiche récit</span></div>'
        + CONTEXTE[4]
        + '</div><div class="table-fiches"><span class="titre-table">Les fiches de l’atelier</span>'
        '<div class="miniatures">'
        + miniature("fiche_recit.jpg", "Le récit", "la fiche récit, par Agathe")
        + miniature("fiche_personnage_rose.jpg", "Une fiche personnage", "la fiche personnage de Rose, par Alyssa")
        + miniature("fiche_situation_1.jpg", "Une fiche à embranchement", "la fiche situation n° 1, avec ses choix au dé")
        + '</div></div>'
        + '<span class="credits">Une histoire d’Agathe et d’Alyssa.\nRéalisation du livre : '
        "Laboratoire d’Aix-périmentation et de Bidouille.</span>"
        + f'<div class="commencer">{lien("Commencer le livre", "Prologue")}</div>\n</div>'
    )


def passage_arbre():
    # Page simple : le titre centré en haut, l'arbre dessous
    return (
        f'<div class="arbre"><span class="lien-retour">{lien("Couverture", "Page de garde")}</span>'
        f'<div class="arbre-tete"><h1>{TITRE}</h1>'
        f'<span class="arbre-sous-titre">Tous les chemins de l\'histoire imaginée par {AUTRICES}</span></div>'
        '<img src="images/arbre.svg" alt="L\'arbre de toutes les branches de l\'histoire"></div>'
    )


def construire():
    modele = SORTIE.read_text(encoding="utf-8")
    debut = modele[: modele.index("<tw-storydata")]
    moteur = modele[modele.index("</tw-storydata>"):]
    if NOINDEX not in debut:
        debut = debut.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + NOINDEX)
    # Icônes : on retire celles qui traînent (héritées d'un autre livre ou d'une construction précédente)
    # puis on remet le favicon du livre
    debut = re.sub(r"<link rel=\"(?:icon|apple-touch-icon)\"[^>]*>", "", debut)
    debut = debut.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + FAVICON)
    debut = re.sub(r"<title>[^<]*</title>", f"<title>{TITRE}</title>", debut)
    lire = re.compile(r"JavaScript (?:needs to be enabled to play|doit être activé pour lire) [^<.]*\.")
    debut = lire.sub(f"JavaScript doit être activé pour lire {TITRE}.", debut)
    moteur = lire.sub(f"JavaScript doit être activé pour lire {TITRE}.", moteur)

    passages = [
        ("Bouton couverture", "header",
         '(unless: (a: "Page de garde", "L\'arbre de l\'histoire", "Comment est née cette histoire") contains (passage:)\'s name)'
         '[<div class="retour">[[Couverture->Page de garde]]</div>]'),
        ("Page de garde", "", passage_garde()),
        ("Comment est née cette histoire", "", passage_contexte()),
        ("L'arbre de l'histoire", "", passage_arbre()),
    ]
    for ch in lire_chapitres():
        passages.append((ch["nom"], "", passage_chapitre(ch)))

    # Espaces insécables de la typographie française : un guillemet ou un deux-points ne se retrouve
    # jamais seul en début de ligne
    insecables = [("« ", "«\u00a0"), (" »", "\u00a0»"), (" :", "\u00a0:"), (" ?", "\u00a0?"),
                  (" !", "\u00a0!"), (" ;", "\u00a0;")]
    for i, (nom, tags, contenu) in enumerate(passages):
        if tags != "header":
            for avant, apres in insecables:
                contenu = contenu.replace(avant, apres)
            passages[i] = (nom, tags, contenu)

    noms = {p[0] for p in passages}
    for nom, _, contenu in passages:
        for cible in re.findall(r"->([^\]]+)\]\]", contenu):
            assert cible in noms, f"Lien cassé dans {nom} : {cible}"

    xml = [f'<tw-storydata name="{e(TITRE)}" startnode="2" creator="Twine" creator-version="2.12.1" '
           f'format="Harlowe" format-version="3.3.9" ifid="{str(uuid.uuid5(uuid.NAMESPACE_URL, TITRE)).upper()}" '
           'options="" tags="" zoom="1" hidden>',
           f'<style role="stylesheet" id="twine-user-stylesheet" type="text/twine-css">{CSS}</style>',
           '<script role="script" id="twine-user-script" type="text/twine-javascript">' + SCRIPT_DE + '</script>']
    for pid, (nom, tags, contenu) in enumerate(passages, start=1):
        xml.append(f'<tw-passagedata pid="{pid}" name="{e(nom)}" tags="{tags}" '
                   f'position="{pid * 150},0" size="100,100">{e(contenu)}</tw-passagedata>')
    SORTIE.write_text(debut + "".join(xml) + moteur, encoding="utf-8")
    print(f"{SORTIE} : {len(passages)} passages")


if __name__ == "__main__":
    construire()
