#let titre = "Analyse interactive de motifs"
#let sous-titre = "BinaPs, sélection WPM et boucle de feedback sur MovieLens 1M"
#let auteurs = "Thomas Trahant · Eliott Mercier Del Forno"
#let cours = "Exploratory Data Analysis"
#let date = "Octobre 2026"
#let bleu = rgb("#1f3b63")

#set document(title: titre, author: auteurs)
#set page(
  paper: "a4",
  margin: (x: 2.2cm, y: 2.2cm),
  numbering: "1",
  header: context {
    if counter(page).get().first() > 1 [
      #set text(size: 8.5pt, fill: luma(110))
      #titre #h(1fr) #cours
      #line(length: 100%, stroke: 0.4pt + luma(180))
    ]
  },
)
#set text(lang: "fr", size: 10.5pt)
#set par(justify: true, leading: 0.62em)
#set heading(numbering: "1.1", supplement: [section])
#show heading.where(level: 1): it => {
  v(0.6em)
  text(size: 14pt, fill: bleu, it)
  v(0.2em)
}
#show heading.where(level: 2): it => {
  v(0.3em)
  text(size: 11.5pt, fill: bleu, it)
}
#set table(stroke: 0.4pt + luma(170), inset: 4.5pt)
#show table: set text(size: 9pt)
#show table: set par(justify: false)
#show table.cell.where(y: 0): strong

#align(center)[
  #text(size: 20pt, weight: "bold", fill: bleu, titre) \
  #v(0.2em)
  #text(size: 12pt, fill: luma(80), sous-titre) \
  #v(0.6em)
  #auteurs · #cours · EPITA ING3 · #date
]
#v(1em)

= Objectif

La fouille de motifs classique (Apriori) énumère tous les ensembles fréquents : leur nombre explose et ils sont très redondants, alors que l'attention de l'analyste est limitée (CM0 d.8–9). Nous suivons la route B du cours (CM0 d.17) :

+ *extraire* un petit ensemble de motifs avec un modèle différentiable, BinaPs ;
+ *sélectionner* ceux qui plaisent à un utilisateur, avec une boucle de feedback et un score WPM ;
+ *présenter* le résultat dans une interface, CinéSwipe.

Sur MovieLens 1M, un motif est un groupe de films aimés par les mêmes personnes ; nous l'appelons un « univers ».

= Données

Une transaction est un utilisateur, un item est un film qu'il a aimé (note ≥ 4). Sur les 3 533 films aimés au moins une fois, on garde ceux aimés par au moins 5 % des utilisateurs (302 personnes) : un film plus rare ne peut pas appartenir à un motif partagé. On obtient une matrice binaire de 6 040 utilisateurs × 572 films, de densité 0,111, qui contient 66 % des avis positifs. Le seuil de 5 % est vérifié en @popularite.

= Extraction des motifs : BinaPs

BinaPs (Fischer et Vreeken, 2021) est un autoencodeur binaire à poids liés : chaque neurone caché est un motif, et le film $j$ appartient au motif $i$ avec la probabilité $W_(i j)$ (CM3 d.5). L'entraînement suit le cours (CM3 d.18) : tirage de Bernoulli des poids, biais $b <= -1$, perte $L_alpha$ adaptée aux données creuses, STE gated et Adam. Notre implémentation NumPy reprend le TP3a, avec les hyperparamètres du code des auteurs : 10 époques, lots de 64, un neurone par film, pas de 0,01 divisé par 10 après les époques 5 et 7, $alpha$ égal à la densité. L'entraînement prend 4 s sur CPU.

*Alignement sur le code officiel.* Avec la règle du STE gated telle qu'écrite dans le cours (gradient $max(0, g)$ pour un neurone éteint, CM3 d.10), aucun motif n'émerge sur MovieLens. Nous avons donc repris le code PyTorch des auteurs : un neurone éteint ne reçoit aucun gradient vers ses poids, et son biais ne reçoit que la partie du gradient qui peut le rallumer ($(1 - y) sum min(g, 0) + y sum g$) ; le gradient du décodeur passe par les poids continus. Nous avons aussi retiré la pénalité sur $W$ du squelette de TP, inutile selon le cours (CM3 d.13).

*Lecture des motifs.* Les auteurs mettent un film dans un motif si $W_(i j) > 0,2$ ; nous prenons 0,5. Avec $L_alpha$, oublier un film aimé coûte $1 - alpha$ et en ajouter un à tort coûte $alpha$ : un film entre donc dans un motif dès que 11 % de ses utilisateurs l'aiment. Avec 0,2, les motifs accumulent des films secondaires (médiane 12, jusqu'à 34) ; 0,5 n'en garde que le cœur et retrouve mieux les motifs cachés des données synthétiques (@hyper). Nous gardons les motifs d'au moins 4 films, pour remplir une rangée d'affiches. On obtient *41 univers* de 4 à 12 films (médiane 5).

Les motifs de BinaPs tolèrent le bruit (CM3 d.7) : comme dans le code officiel, un utilisateur *aime* un univers s'il en aime au moins la moitié des films (et au moins 2).

= Boucle interactive et score WPM

À chaque tour, l'utilisateur voit 4 univers et répond « J'aime », « Pas pour moi » ou rien. Le premier tour montre les 4 univers les plus différents entre eux.

- *Score d'un film.* $L_f$ et $D_f$ comptent les univers aimés et rejetés qui contiennent le film $f$ :
  $ s(f) = 2^(L_f - D_f) / (max_g 2^(L_g - D_g)) $
- *Score d'un univers (WPM).* C'est un Weighted Product Model dont les critères sont les films de l'univers :
  $ S(U) = product_(f in U) s(f) $
- *Tirage du tour suivant*, parmi les univers pas encore montrés ($J$ : indice de Jaccard) :
  $ P(U) prop (1 - alpha) S(U) + alpha (1 - max_(V "déjà montré") J(U, V)), quad alpha = 0,3 $
- *Recommandation.* Dès 3 univers aimés, la page « Pour toi » présente les 3 univers de meilleur score qui ne partagent aucun film.

Exemple : après {A, B, C} +, {A, D} −, {B} +, {C, D} −, les scores bruts sont A = 1, B = 4, C = 1, D = 1/4 ; divisés par 4, ils valent 1/4, 1, 1/4 et 1/16, et {C, D} obtient 1/64.

Le WPM classique combine des critères par $product_j c_j^(w_j)$. Ici chaque film est un critère de poids 1 : un univers n'est bien noté que si tous ses films plaisent, et un seul film rejeté suffit à le pénaliser. Le tirage combine ensuite deux critères, la préférence apprise et la diversité, pondérés par $alpha$.

= Interface : CinéSwipe

Une application web au style des plateformes de streaming (Flask, HTML/CSS/JS, affiches via l'API TMDB). Aucun calcul n'est montré à l'utilisateur.

- *Découvrir* : une rangée d'affiches par univers, nommé automatiquement par ses deux genres dominants, laissés en anglais comme dans MovieLens, et sa décennie (« Film-Noir & Crime des années 50 ») ; une jauge compte les univers trouvés.
- *Pour toi* : l'univers n°1 en bandeau, puis les 3 univers recommandés ; on peut ensuite affiner ses goûts.
- *Personas* : l'application rejoue tour par tour la partie d'un des trois spectateurs types, avec la même boucle.

= Personas et scénarios

Chaque persona est défini par une liste de films préférés (`personas.py`) et aime un univers si au moins la moitié de ses films en font partie.

#align(center)[
  #table(
    columns: 3,
    align: left,
    [persona], [profil et besoin], [ce que lui propose CinéSwipe],
    [*Inès*, 21 ans, étudiante], [fan d'animation ; cherche quoi regarder entre amis], [Wallace & Gromit, fantasy des années 80 (_Labyrinth_, _Goonies_)],
    [*Marc*, 55 ans, cinéphile], [Hitchcock, film noir, comédies musicales ; veut revoir des classiques], [film noir, _Lawrence of Arabia_, comédies musicales],
    [*Sofia*, 34 ans, cadre], [action et science-fiction ; veut se détendre le soir], [_Aliens_ et _Terminator_, _Jurassic Park_ et _Terminator 2_],
  )
]

- *Inès* passe le thriller et le drame du premier tour et aime la fantasy des années 80 ; les univers d'animation remontent ensuite, et « Pour toi » lui présente ses univers sans répéter d'affiche.
- *Marc* aime d'emblée les classiques ; beaucoup d'univers lui correspondent, il atteint vite 3 univers aimés et peut continuer à affiner.
- *Sofia* rejette comédies et drames ; ses univers d'action sont rares et il lui faut plus de tours, d'où l'intérêt de la diversité au début.

= Évaluation

== BinaPs sur données synthétiques

8 motifs sont cachés dans 2 000 transactions de 50 items, puis une fraction des cases est inversée. F1 soft (meilleur Jaccard entre motifs trouvés et cachés), moyenne sur 3 graines :

#align(center)[
  #table(
    columns: 6,
    align: center,
    [bruit], [0 %], [1 %], [2 %], [3 %], [5 %],
    [STE gated], [0,86], [0,81], [0,86], [0,88], [0,78],
    [STE simple], [0,76], [0,46], [0,42], [0,43], [0,43],
  )
]

Le STE gated rend BinaPs robuste au bruit (CM3 d.20) ; sans lui, le modèle s'effondre dès 1 %. L'alignement sur le code officiel a fait passer le F1 à 5 % de bruit de 0,54 à 0,78.

== Hyperparamètres <hyper>

On fait varier un hyperparamètre à la fois autour du réglage des auteurs (`hyperparametres.py`).

#align(center)[
  #table(
    columns: 5,
    align: (left, center, center, center, center),
    [réglage], [univers], [taille médiane (max)], [utilisateurs couverts], [F1 soft synthétique],
    [*référence*], [41], [5 (12)], [70 %], [0,86],
    [pas 0,001], [0], [—], [0 %], [0,00],
    [lots de 128], [27], [6 (12)], [59 %], [0,43],
    [$alpha$ = 0,3], [3], [4 (6)], [23 %], [0,81],
    [seuil 0,2 (auteurs)], [75], [12 (34)], [69 %], [0,68],
    [seuil 0,4], [60], [8 (18)], [68 %], [0,86],
    [seuil 0,6], [19], [5 (8)], [59 %], [0,81],
  )
]

Le seuil de lecture et le $alpha$ de la perte contrôlent la taille des motifs ; le nombre d'époques et de neurones change peu le résultat (seuls 65 neurones sur 572 restent actifs). Les motifs se forment en 5 époques et ne bougent plus ensuite. Avec le seuil 0,2 dans toute la chaîne, la boucle ne trouve 3 univers aimés que dans 49 % des cas (contre 66 %). D'une graine à l'autre, seuls 33 % des univers se retrouvent, mais les résultats de la boucle restent stables (62 à 67 %).

== BinaPs sur MovieLens

- 41 univers, Jaccard moyen 0,002 entre eux : presque aucune redondance (15 films sont dans 2 univers, aucun dans 3).
- 70 % des utilisateurs aiment au moins un univers.
- Les univers ont un sens alors que BinaPs n'a vu ni titres ni genres : classiques Disney, Wallace & Gromit, John Hughes, Woody Allen, Hitchcock et film noir, fantasy des années 80, Star Trek, horreur, comédies musicales.
- 14 des 20 films les plus aimés (_Star Wars_, _Pulp Fiction_…) ne sont dans aucun univers : aimés par 30 à 47 % des utilisateurs, ils ne caractérisent aucun groupe et leur poids reste sous 0,5.

== Boucle interactive (utilisateurs simulés)

200 utilisateurs MovieLens qui aiment au moins 3 univers jouent 6 tours de 4 univers ; un utilisateur simulé aime un univers s'il en aime au moins la moitié des films.

#align(center)[
  #table(
    columns: 4,
    align: (left, center, center, center),
    [méthode], [3 univers aimés trouvés], [« Pour toi » qui plaît], [3 jamais vus qui plaisent],
    [boucle, $alpha = 0$], [70 %], [86 %], [17 %],
    [boucle, $alpha =$ 0,3], [66 %], [86 %], [24 %],
    [tirage au hasard], [63 %], [84 %], [24 %],
    [3 univers les plus populaires], [—], [38 %], [—],
    [3 univers au hasard], [—], [17 %], [—],
  )
]

L'interaction est utile : « Pour toi » plaît dans 86 % des cas, contre 38 % sans interaction. Mais ce gain vient surtout des réponses, pas de la règle de tirage (84 % avec un tirage au hasard), car « Pour toi » recommande surtout des univers déjà aimés.

== Le modèle de préférence capture-t-il les goûts ? <pref>

Après chaque tour, on mesure l'AUC du score WPM par rapport aux goûts réels (0,5 = hasard, 1 = parfait).

#align(center)[
  #table(
    columns: 5,
    align: center,
    [tour], [univers montrés], [jamais vus : WPM], [jamais vus : popularité], [jamais vus : plus petits d'abord],
    [1], [1,00], [0,52], [0,68], [0,53],
    [3], [1,00], [0,56], [0,68], [0,54],
    [6], [1,00], [0,57], [0,66], [0,52],
  )
]

Sur les univers montrés, le score reprend fidèlement les réponses. Sur les univers jamais vus, il fait à peine mieux que le hasard et moins bien qu'un simple classement par popularité. Le score ne passe d'un univers à l'autre que par les films communs, or seuls 4 % (tour 1) à 27 % (tour 6) des univers jamais vus en partagent un avec un univers montré ; pour les autres, le produit classe simplement les plus petits en premier. Le modèle capture donc les goûts exprimés, pas les goûts latents.

On le voit sur l'utilisateur 1806 : il aime l'univers de _Matrix_ et _Terminator 2_, le plus populaire (25,6 %), qui ne lui est jamais montré, tandis que le modèle met en tête les comédies musicales et _Wallace & Gromit_, dont il n'aime aucun film.

== Personas et seuil de popularité <popularite>

En 20 parties simulées, Marc (6 univers aimés sur 41) trouve 3 univers dans 85 % des cas et son « Pour toi » plaît à 97 % ; Inès et Sofia (4 univers chacune) n'y arrivent que dans 35 et 55 % des cas (« Pour toi » à 65 et 68 %).

#align(center)[
  #table(
    columns: 5,
    align: center,
    [seuil], [films], [univers], [3 univers aimés trouvés], [« Pour toi » qui plaît],
    [10 %], [231], [13], [100 %], [100 %],
    [*5 %*], [572], [41], [67 %], [86 %],
    [1 %], [1 634], [66], [43 %], [58 %],
  )
]

Au-dessus de 5 %, il reste si peu d'univers qu'une partie (24 univers montrés) parcourt presque tout le catalogue ; en dessous, les univers grossissent (jusqu'à 25 films) et la recommandation se dégrade.

= Limites

- *Pas de généralisation* (@pref) : BinaPs produit des univers presque disjoints (25 sur 41 ne partagent aucun film), alors que le WPM ne transmet l'information que par les films communs.
- *Biais de taille* : le produit fait passer les petits univers jamais vus devant les gros.
- *Échelle de $alpha$* : le score tombe vite près de 0 alors que la diversité reste proche de 1, si bien qu'au-delà d'un petit $alpha$ le tirage est presque uniforme.
- *Grands succès absents* : seuls 241 des 572 films apparaissent dans un univers.
- *Évaluation simulée* : utilisateurs parfaitement cohérents, personas choisis en connaissant les univers ; un test avec de vrais utilisateurs reste à mener.

Une piste simple serait d'ajouter la popularité comme troisième critère, dans un vrai produit pondéré $S(U)^(w_1) dot "diversité"(U)^(w_2) dot "popularité"(U)^(w_3)$ : c'est le meilleur prédicteur sur les univers jamais vus, et le produit règle le problème d'échelle de $alpha$.

= Références

- L. Diop, cours d'Exploratory Data Analysis (CM0 à CM4, TD et TP), EPITA, 2026.
- J. Fischer, J. Vreeken. _Differentiable Pattern Set Mining_. KDD 2021, et code officiel PyTorch.
- F. M. Harper, J. A. Konstan. _The MovieLens Datasets: History and Context_. ACM TiiS 5(4), 2015.
- Affiches : This product uses the TMDB API but is not endorsed or certified by TMDB.
