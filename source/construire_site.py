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
# Favicon provisoire : l'empreinte de loup et les trois étoiles des cartes
FAVICON = ('<link rel="icon" type="image/png" sizes="48x48" href="images/favicon-48.png">'
           '<link rel="icon" type="image/png" sizes="180x180" href="images/favicon.png">'
           '<link rel="apple-touch-icon" href="images/favicon.png">')

TITRE = "Les trois sœurs"
AUTRICES = "Agathe et Alyssa"

# Résumé provisoire, à remplacer par celui de Manon
SYNOPSIS = (
    "Une nuit sans lune, dans une forêt où personne n'ose s'aventurer, trois bébés encerclés par "
    "les loups disparaissent sans laisser de trace.\n\n"
    "Quatorze ans plus tard, à New York, en Italie et en Espagne, trois filles parlent aux animaux, "
    "font pousser des fleurs ou entendent les pensées, sans savoir d'où leur viennent ces dons. "
    "Une carte marquée d'une empreinte de loup va les réunir. Mais sur la route qui les ramène vers "
    "la forêt, un homme à la bague étrange ne cesse de croiser leur chemin…"
)

CONTEXTE = [
    "En octobre 2026, pendant les vacances d'automne, le L.A.B a animé l'atelier « Le livre dont tu "
    "es le héros » dans le réseau des bibliothèques Méjanes d'Aix-en-Provence. Des enfants y ont "
    "inventé une histoire qui change selon les choix du lecteur, en l'écrivant situation par "
    "situation sur des fiches où chaque lancer de dé renvoie vers une autre situation. L'atelier est "
    "issu du projet européen Robots Meet Arts : derrière le récit, il s'agit de découvrir sans écran "
    "les notions qui structurent un programme informatique. Chaque lancer de dé est une condition, "
    "qui décide de la suite de l'histoire. Chaque choix ouvre un embranchement, et un chemin qui "
    "ramène à une situation déjà écrite forme une boucle.",
    "Écrire une telle histoire demande un travail créatif considérable. Il faut inventer un "
    "personnage et une quête, mais aussi penser l'histoire comme un réseau : prévoir à chaque étape "
    "plusieurs suites possibles, numéroter les situations, s'assurer que chaque chemin mène quelque "
    "part, et faire tenir tous ces fils ensemble sans perdre le sens du récit.",
    "Agathe et Alyssa ont relevé ce défi à deux. Elles ont imaginé trois sœurs abandonnées bébés "
    "dans une forêt, qui se téléportent chacune dans un pays différent quand les loups approchent : "
    "Rose à New York, Rosi en Italie et Sofia en Espagne. C'est à elles que l'on doit leurs dons, "
    "parler aux animaux, faire pousser des fleurs, voler ou lire dans les pensées, la rencontre où "
    "Sofia entend les pensées de ses sœurs, le laboratoire où un ordinateur révèle d'où elles "
    "viennent, le voleur qui tire sur un homme que Rose soigne, l'évasion et l'incendie de la route, "
    "et ces loups qui ne venaient pas dévorer les bébés, mais les protéger d'un homme qui les "
    "cherchait.",
    "Pour leur histoire, Agathe et Alyssa ont choisi le mystère. Avec //Les trois sœurs//, elles "
    "vous présentent un récit où chaque épreuve apporte un indice, et où l'on ne découvre qu'à la "
    "fin qui est vraiment le voleur croisé sur la route.",
    "Pour offrir à chaque enfant un livre achevé, dont il ou elle puisse être fier ou fière et avec "
    "lequel continuer à jouer, le L.A.B a prolongé chaque histoire à partir des idées de celles et "
    "ceux qui l'ont imaginée, puis l'a mise en forme, en s'aidant d'outils numériques, dont "
    "l'intelligence artificielle. Ce travail ne retire rien à celui des enfants : il s'appuie "
    "entièrement sur la créativité, l'imaginaire et les récits de celles et ceux qui ont participé "
    "à l'atelier.",
]

CSS = """
@font-face { font-family: "IM Fell English"; font-style: normal; font-weight: 400; font-display: swap; src: url("fonts/IMFellEnglish.woff2") format("woff2"); }
@font-face { font-family: "IM Fell English"; font-style: italic; font-weight: 400; font-display: swap; src: url("fonts/IMFellEnglish-italique.woff2") format("woff2"); }
@font-face { font-family: "Lora"; font-style: normal; font-weight: 400 700; font-display: swap; src: url("fonts/Lora.woff2") format("woff2"); }
@font-face { font-family: "Lora"; font-style: italic; font-weight: 400 700; font-display: swap; src: url("fonts/Lora-italique.woff2") format("woff2"); }

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
  font-family: "Lora", Georgia, serif;
  font-size: 1.02em;
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
.illustration img {
  display: block;
  width: 100%;
  max-height: 85vh;
  object-fit: contain;
  border-radius: 10px;
  box-shadow: 0 6px 24px rgba(19, 28, 51, 0.25);
}
/* Tant qu'un chapitre n'a pas d'illustration, son texte reste en une colonne centrée */
.page:not(:has(.cote)) { grid-template-columns: minmax(0, 44em); justify-content: center; }
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
  grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr);
  gap: 3em;
  align-items: center;
}
.garde-image { text-align: right; }
.garde-image img {
  display: inline-block;
  max-width: 100%;
  max-height: 64vh;
  height: auto;
  border-radius: 10px;
  box-shadow: 0 6px 24px rgba(19, 28, 51, 0.3);
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
  font-size: 1.3em;
  color: var(--gris);
}
.garde .grand-titre {
  font-family: "IM Fell English", Georgia, serif;
  font-size: clamp(2.4em, 8vh, 4.6em);
  line-height: 1;
  color: var(--nuit);
  margin: 0.15em 0 0.15em;
}
.garde .nom-auteur {
  font-family: "IM Fell English", Georgia, serif;
  font-style: italic;
  font-size: clamp(1.3em, 3.6vh, 1.8em);
  color: var(--or-fonce);
}
.garde .synopsis {
  margin: 0 auto;
  max-width: 34em;
  font-size: 1.05em;
  line-height: 1.65;
}
/* Commencer : en gras, entre deux fioritures dorées terminées par une étoile, sans cadre de bouton ;
   au survol, le texte prend une lueur dorée */
.garde .commencer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.9em;
}
.garde .commencer::before, .garde .commencer::after {
  content: "";
  flex: 0 1 7.5em;
  height: 1.2em;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 20' preserveAspectRatio='none'%3E%3Cpath d='M14 10 C40 10 52 4 70 7 C86 10 96 14 118 10' fill='none' stroke='%23d99a2b' stroke-width='1.4' stroke-linecap='round'/%3E%3Cpath d='M7 3 l1.7 4.3 4.3 .4-3.3 2.9 1 4.3L7 12.6l-3.7 2.3 1-4.3L1 7.7l4.3-.4z' fill='%23d99a2b'/%3E%3C/svg%3E") no-repeat center / 100% 100%;
}
.garde .commencer::after { transform: scaleX(-1); }
.garde .commencer tw-link, .garde .commencer .enchantment-link {
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
.garde .commencer tw-link:hover, .garde .commencer .enchantment-link:hover {
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

/* Séparateur : l'empreinte de loup et les trois étoiles des cartes, entre deux traits */
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
  width: 3.4em;
  height: 1.9em;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 68 38'%3E%3Cg fill='%231d2b4f'%3E%3Cellipse cx='34' cy='27' rx='7.5' ry='6.5'/%3E%3Cellipse cx='25.5' cy='17' rx='2.8' ry='3.8' transform='rotate(-20 25.5 17)'/%3E%3Cellipse cx='31' cy='12.5' rx='2.8' ry='3.9'/%3E%3Cellipse cx='37' cy='12.5' rx='2.8' ry='3.9'/%3E%3Cellipse cx='42.5' cy='17' rx='2.8' ry='3.8' transform='rotate(20 42.5 17)'/%3E%3C/g%3E%3Cg fill='%23d99a2b'%3E%3Cpath d='M9 15 l1.6 3.4 3.7.4-2.8 2.5.8 3.6L9 23l-3.3 1.9.8-3.6-2.8-2.5 3.7-.4z'/%3E%3Cpath d='M34 0 l1.3 2.7 3 .3-2.2 2 .6 2.9L34 6.4l-2.7 1.5.6-2.9-2.2-2 3-.3z'/%3E%3Cpath d='M59 15 l1.6 3.4 3.7.4-2.8 2.5.8 3.6L59 23l-3.3 1.9.8-3.6-2.8-2.5 3.7-.4z'/%3E%3C/g%3E%3C/svg%3E") no-repeat center / contain;
}
.garde .separateur { margin: 0; }

/* Bouton de renvoi, quand il n'y a qu'une suite possible : la même étiquette que Commencer, en plus petit */
.elan {
  align-items: center;
  margin-top: 2.2em;
}
/* plus spécifique que les liens de choix, qui sont en gras et soulignés */
.choix.elan tw-link, .choix.elan .enchantment-link { font-size: 1.15em; font-weight: 400; border-bottom: 1px solid var(--or); }

/* Dé à lancer sur le site : à droite du bloc consigne et choix, face blanche, contour bleu nuit,
   points dorés ; il montre une face au repos et ne choisit jamais à la place du lecteur */
.de {
  display: flex;
  align-items: center;
  gap: 1.6em;
}
.de-texte { flex: 1; min-width: 0; }
/* Flèche tracée à la main qui montre le dé */
.fleche-de { flex: none; width: 3.2em; height: auto; margin-right: -0.6em; transform: translateY(-0.4em); }
/* Le résultat s'affiche sous le dé sans compter dans la hauteur : le dé reste fixe,
   exactement au milieu du bloc consigne et choix */
.lancer {
  flex: none;
  position: relative;
  display: flex;
}
.de-virtuel {
  width: 4.6em;
  height: 4.6em;
  padding: 0.5em;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: repeat(3, 1fr);
  background: #ffffff;
  border: 3px solid var(--nuit);
  border-radius: 0.8em;
  box-shadow: 0 4px 0 var(--or);
  cursor: pointer;
  transform: rotate(-5deg);
  transition: transform 0.15s ease;
}
.de-virtuel:hover { transform: rotate(5deg); }
.de-virtuel.roule { animation: roule 0.3s linear infinite; }
@keyframes roule {
  0% { transform: rotate(0deg) translateY(0); }
  50% { transform: rotate(180deg) translateY(-3px); }
  100% { transform: rotate(360deg) translateY(0); }
}
.de-virtuel i {
  width: 0.8em;
  height: 0.8em;
  border-radius: 50%;
  background: var(--or);
  place-self: center;
  visibility: hidden;
}
/* Avant le premier lancer : un point d'interrogation, centré comme les points */
.de-virtuel { position: relative; }
.de-virtuel[data-face="0"]::after {
  content: "?";
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: "IM Fell English", Georgia, serif;
  font-size: 2.8em;
  line-height: 1;
  color: var(--or);
}
.de-virtuel[data-face="1"] i:nth-child(5),
.de-virtuel[data-face="2"] i:is(:nth-child(1), :nth-child(9)),
.de-virtuel[data-face="3"] i:is(:nth-child(1), :nth-child(5), :nth-child(9)),
.de-virtuel[data-face="4"] i:is(:nth-child(1), :nth-child(3), :nth-child(7), :nth-child(9)),
.de-virtuel[data-face="5"] i:is(:nth-child(1), :nth-child(3), :nth-child(5), :nth-child(7), :nth-child(9)),
.de-virtuel[data-face="6"] i:is(:nth-child(1), :nth-child(3), :nth-child(4), :nth-child(6), :nth-child(7), :nth-child(9)) {
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
  font-size: 1.1em;
  color: var(--gris);
  text-align: center;
}
@media (max-width: 600px) {
  .de { gap: 0.6em; }
  .fleche-de { width: 2.2em; }
  .de-virtuel { width: 3.6em; height: 3.6em; padding: 0.4em; }
  .de-virtuel i { width: 0.6em; height: 0.6em; }
  .de-virtuel[data-face="0"]::after { font-size: 2.1em; }
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

.couverture-arbre { margin-top: 1.4em; }

/* Page de l'arbre : le texte à gauche, l'arbre très vertical à droite */
.arbre {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 2.4fr);
  gap: 3.5em;
  align-items: start;
}
.arbre-texte {
  position: sticky;
  top: 2em;
}
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
  height: auto;
}
@media (max-width: 800px) {
  .arbre { grid-template-columns: minmax(0, 1fr); gap: 1.5em; }
  .arbre-texte { position: static; }
}

/* Page de contexte : le texte à gauche, les fiches des autrices à droite */
.contexte {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
  gap: 3em;
  align-items: start;
}
.visuels {
  margin-top: 4em;
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 1em;
}
.visuels .pleine, .visuels .legende { grid-column: 1 / -1; }
.visuels img {
  display: block;
  width: 100%;
  height: auto;
  border-radius: 6px;
  box-shadow: 0 2px 10px rgba(34, 38, 58, 0.15);
}
.visuels img:nth-child(2) { transform: rotate(-1.5deg); }
.visuels img:nth-child(3) { transform: rotate(1.5deg); }
.legende {
  display: block;
  font-family: "IM Fell English", Georgia, serif;
  font-style: italic;
  font-size: 1.15em;
  color: var(--gris);
  text-align: center;
}
@media (max-width: 800px) {
  .contexte { grid-template-columns: minmax(0, 1fr); gap: 1em; }
  .visuels { margin-top: 0; }
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
    '<svg class="fleche-de" viewBox="0 0 60 40" aria-hidden="true"><g fill="none" stroke="#d99a2b" '
    'stroke-width="3" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M4 30 C16 34 34 30 48 16"/><path d="M38 14 L49 15 L47 26"/></g></svg>'
    '<div class="lancer"><button class="de-virtuel" type="button" data-face="0" '
    'aria-label="Lancer le dé">' + "<i></i>" * 9 + '</button>'
    '<span class="resultat" aria-live="polite"></span></div>'
)

# Script commun à toutes les pages : fait rouler le dé puis affiche la face tirée, sans choisir
SCRIPT_DE = """
document.addEventListener('click', function (evenement) {
  var de = evenement.target.closest('.de-virtuel');
  if (!de || de.classList.contains('roule')) return;
  var resultat = de.parentNode.querySelector('.resultat');
  var face = 1 + Math.floor(Math.random() * 6);
  var etapes = 0;
  de.classList.add('roule');
  resultat.textContent = '';
  var minuterie = setInterval(function () {
    de.setAttribute('data-face', 1 + Math.floor(Math.random() * 6));
    etapes += 1;
    if (etapes >= 8) {
      clearInterval(minuterie);
      de.setAttribute('data-face', face);
      de.classList.remove('roule');
      resultat.textContent = 'Le dé affiche ' + face + '.';
    }
  }, 75);
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
            # Sur le site, on lance le dé en cliquant dessus : la consigne le dit, une flèche le montre
            consigne = consigne.replace("Lance le dé", "Clique sur le dé", 1)
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
    image = f"images/chapitres/{illustration(ch['nom'])}.jpg"
    cote = ""
    if (RACINE / image).exists():
        cote = f'<div class="cote"><div class="illustration"><img src="{image}" alt="{ch["titre"]}"></div></div>'
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
        'alt="Rose, les mains lumineuses, dans la forêt au crépuscule, entre un chat et un pigeon"></div>'
        f'<div class="garde-texte"><div class="synopsis">{SYNOPSIS}</div>{SEPARATEUR}'
        f'<div class="commencer">{lien("Commencer l'histoire", "Prologue")}</div>'
        f'<div class="secondaires">{lien("Comment est née cette histoire", "Comment est née cette histoire")} '
        f'{lien("L\'arbre de l\'histoire", "L\'arbre de l\'histoire")}</div>'
        "</div></div></div>"
    )


def passage_contexte():
    return (
        '<div class="contexte"><div class="contexte-texte"><span class="lien-retour">[[Couverture->Page de garde]]</span>\n<h1>Comment est née cette histoire</h1>'
        + "\n\n".join(CONTEXTE)
        + f'\n\n<span class="credits">Une histoire d\'{AUTRICES}. Réalisation du livre : L.A.B, '
        "Laboratoire d'Aix-périmentation et de Bidouille.</span>\n\n"
        + f'<div class="secondaires">{lien("Commencer le livre", "Prologue")}</div></div>'
        + '<div class="visuels">'
        '<img class="pleine" src="images/fiches/fiche_recit.jpg" alt="La fiche récit remplie par Agathe">'
        '<img src="images/fiches/fiche_personnage_sofia.jpg" alt="La fiche personnage de Sofia, par Agathe">'
        '<img src="images/fiches/fiche_personnage_rose.jpg" alt="La fiche personnage de Rose, par Alyssa">'
        '<span class="legende">Les fiches remplies par Agathe et Alyssa pendant l\'atelier</span></div>\n</div>'
    )


def passage_arbre():
    return (
        f'<div class="arbre"><div class="arbre-texte"><h1>{TITRE}</h1>'
        f'<span class="arbre-sous-titre">Tous les chemins de l\'histoire imaginée par {AUTRICES}</span>'
        '<div class="intro-arbre">Un arbre de décision est un schéma qui montre toutes les suites possibles '
        "d'une histoire, ou d'un programme informatique. Chaque case est une étape, ici un chapitre, et chaque "
        "flèche part d'une condition : le résultat du dé, ou ce que le lecteur a déjà lu. En suivant les "
        "flèches, on vérifie qu'aucun chemin ne mène nulle part : c'est grâce à cet outil que chaque parcours "
        f"de //{TITRE}// conduit bien à la fin. Les trois épreuves de la route forment une boucle : on en sort "
        "seulement quand on les a toutes vécues.</div>"
        f'<div class="lien-retour couverture-arbre">{lien("Couverture", "Page de garde")}</div></div>'
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
