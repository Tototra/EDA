# Resultats

## 1. BinaPs sur donnees synthetiques (8 motifs plantes, 3 graines, seuil 0.5)

| bruit | STE | motifs trouves | F1 exact | F1 soft |
|---|---|---|---|---|
| 0 | gated | 12.3 | 0.55 | 0.86 |
| 0.01 | gated | 13.7 | 0.49 | 0.81 |
| 0.02 | gated | 10.7 | 0.65 | 0.86 |
| 0.03 | gated | 11.3 | 0.66 | 0.88 |
| 0.05 | gated | 11.0 | 0.43 | 0.78 |
| 0 | simple | 18.3 | 0.33 | 0.76 |
| 0.01 | simple | 46.3 | 0.10 | 0.46 |
| 0.02 | simple | 44.7 | 0.18 | 0.42 |
| 0.03 | simple | 45.7 | 0.09 | 0.43 |
| 0.05 | simple | 43.0 | 0.11 | 0.43 |

## 2. BinaPs sur MovieLens

- donnees : 6040 utilisateurs x 572 films, densite 0.111
- temps d'entrainement : 3.6 s
- nombre de motifs : 41 (capacite 572)
- taille des motifs : min 4, mediane 5, max 12
- frequence (au moins la moitie des films aimes) : mediane 0.066, max 0.256
- redondance (Jaccard moyen entre motifs) : 0.002
- utilisateurs couverts par au moins un motif : 70.0%

## 3. Boucle interactive (utilisateurs simules)

Un utilisateur MovieLens simule aime un univers s'il aime au moins la moitie de ses films. 2271 utilisateurs en aiment au moins 3 ; on en tire 200. 6 tours de 4 univers.

| methode | trouve 3 univers aimes | tours necessaires (moyenne) | Pour toi qui plait | 3 univers jamais vus qui plaisent |
|---|---|---|---|---|
| boucle, alpha = 0 | 70% | 3.8 | 86% | 17% |
| boucle, alpha = 0.3 (appli) | 66% | 4.0 | 86% | 24% |
| boucle, alpha = 1 (diversite seule) | 66% | 4.0 | 86% | 24% |
| tirage au hasard | 63% | 3.8 | 84% | 24% |
| 3 univers les plus populaires, sans interaction | - | - | 38% | - |
| 3 univers au hasard | - | - | 17% | - |

## 4. Personas (20 parties chacun, alpha = 0.3 comme dans l'appli)

Un persona aime un univers si au moins la moitie de ses films font partie de ses films preferes.

| persona | univers aimes sur 41 | trouve 3 univers aimes | tours necessaires | Pour toi qui plait |
|---|---|---|---|---|
| Inès, 21 ans, étudiante, fan d'animation | 4 | 35% | 4.7 | 65% |
| Marc, 55 ans, cinéphile des classiques | 6 | 85% | 4.6 | 97% |
| Sofia, 34 ans, amatrice d'action et de science-fiction | 4 | 55% | 5.4 | 68% |

Pour toi de la premiere partie de chaque persona :

- Inès, 21 ans, étudiante, fan d'animation : Labyrinth (1986), Goonies, The (1985), Dark Crystal, The (1982) / Wallace & Gromit: The Best of Aardman Animation (1996), Close Shave, A (1995), Wrong Trousers, The (1993) / 20,000 Leagues Under the Sea (1954), Westworld (1973), Logan's Run (1976)
- Marc, 55 ans, cinéphile des classiques : Sunset Blvd. (a.k.a. Sunset Boulevard) (1950), Touch of Evil (1958), Strangers on a Train (1951) / Gone with the Wind (1939), African Queen, The (1951), Lawrence of Arabia (1962) / Singin' in the Rain (1952), My Fair Lady (1964), West Side Story (1961)
- Sofia, 34 ans, amatrice d'action et de science-fiction : Braveheart (1995), Jurassic Park (1993), Terminator 2: Judgment Day (1991) / Aliens (1986), Alien (1979), Terminator, The (1984) / Singin' in the Rain (1952), My Fair Lady (1964), West Side Story (1961)

## 5. Le modele de preference capture-t-il les gouts ?

Memes 200 utilisateurs, alpha = 0.3. Apres chaque tour, on compare le score WPM des univers a ce que l'utilisateur aime vraiment dans MovieLens. AUC = probabilite qu'un univers aime ait un meilleur score qu'un univers non aime (0.5 = hasard, 1 = parfait).

| tour | AUC univers montres | AUC univers jamais vus : WPM | jamais vus : popularite | jamais vus : petite taille d'abord | jamais vus partageant un film avec un univers montre |
|---|---|---|---|---|---|
| 1 | 1.00 | 0.52 | 0.68 | 0.53 | 4% |
| 2 | 1.00 | 0.55 | 0.68 | 0.54 | 9% |
| 3 | 1.00 | 0.56 | 0.68 | 0.54 | 14% |
| 4 | 1.00 | 0.55 | 0.67 | 0.53 | 17% |
| 5 | 1.00 | 0.56 | 0.67 | 0.52 | 22% |
| 6 | 1.00 | 0.57 | 0.66 | 0.52 | 27% |

## 6. Traces d'interaction (utilisateurs reels, alpha = 0.3)

### Utilisateur 3940 (170 films aimes, 12 univers aimes)

Univers qu'il aime d'apres MovieLens : Romance & Comedy des années 90 (Sense and Sensibility, Much Ado About Nothing) ; Action & Sci-Fi des années 90 (Matrix, The, Terminator 2: Judgment Day) ; Drama & Thriller des années 70 (Graduate, The, Taxi Driver) ; Drama & Documentary des années 90 (Player, The, Insider, The) ; Children's & Musical des années 50 (Mary Poppins, Lady and the Tramp) ; Comedy & Romance des années 70 (Annie Hall, Sleeper) ; Drama & Crime des années 70 (French Connection, The, Dog Day Afternoon) ; Drama & War des années 80 (Apocalypse Now, Boat, The (Das Boot)) ; Drama des années 80 (Dead Poets Society, Field of Dreams) ; Comedy & Drama des années 80 (Breakfast Club, The, Caddyshack) ; Drama & Comedy des années 90 (Shakespeare in Love, Toy Story 2) ; Comedy & Drama des années 2000 (High Fidelity, Almost Famous)

- tour 1 : Drama & Romance des années 90 (English Patient, The, Like Water for Chocolate (Como agua para chocolate)) -, Action & Sci-Fi des années 90 (Matrix, The, Terminator 2: Judgment Day) +, Comedy & Drama des années 80 (Breakfast Club, The, Caddyshack) +, War & Romance des années 50 (African Queen, The, Gone with the Wind) -
  - meilleurs scores parmi les jamais vus : Film-Noir & Crime des années 50 (Double Indemnity, Sunset Blvd. (a.k.a. Sunset Boulevard)) [0/4 films aimes], Sci-Fi & Action des années 70 (War of the Worlds, The, 20,000 Leagues Under the Sea) [0/4 films aimes], Musical & Romance des années 60 (Singin' in the Rain, West Side Story) [0/4 films aimes]
- tour 2 : Action & Adventure des années 80 (Die Hard, Indiana Jones and the Last Crusade) -, Drama & Comedy des années 90 (Shakespeare in Love, Toy Story 2) +, Horror & Thriller des années 80 (Shining, The, Exorcist, The) -, Comedy & Drama des années 90 (Election, Clerks) -
  - meilleurs scores parmi les jamais vus : Film-Noir & Crime des années 50 (Double Indemnity, Sunset Blvd. (a.k.a. Sunset Boulevard)) [0/4 films aimes], Sci-Fi & Action des années 70 (War of the Worlds, The, 20,000 Leagues Under the Sea) [0/4 films aimes], Musical & Romance des années 60 (Singin' in the Rain, West Side Story) [0/4 films aimes]
- tour 3 : Fantasy & Adventure des années 80 (Willow, Dark Crystal, The) -, Comedy & Drama des années 80 (Airplane!, Ferris Bueller's Day Off) -, Action & Drama des années 2000 (Patriot, The, Frequency) -, Drama & Thriller des années 70 (Graduate, The, Taxi Driver) +
  - meilleurs scores parmi les jamais vus : Film-Noir & Crime des années 50 (Double Indemnity, Sunset Blvd. (a.k.a. Sunset Boulevard)) [0/4 films aimes], Drama & War des années 80 (Apocalypse Now, Boat, The (Das Boot)) [3/4 films aimes], Sci-Fi & Action des années 70 (War of the Worlds, The, 20,000 Leagues Under the Sea) [0/4 films aimes]
- tour 4 : Comedy & Drama des années 2000 (High Fidelity, Almost Famous) +, Drama des années 80 (Dead Poets Society, Field of Dreams) +, Sci-Fi & Action des années 70 (War of the Worlds, The, 20,000 Leagues Under the Sea) -, War & Drama des années 60 (Great Escape, The, Ben-Hur) -
  - meilleurs scores parmi les jamais vus : Film-Noir & Crime des années 50 (Double Indemnity, Sunset Blvd. (a.k.a. Sunset Boulevard)) [0/4 films aimes], Drama & War des années 80 (Apocalypse Now, Boat, The (Das Boot)) [3/4 films aimes], Musical & Romance des années 60 (Singin' in the Rain, West Side Story) [0/4 films aimes]
- tour 5 : Comedy & Romance des années 90 (American President, The, Sleepless in Seattle) -, Romance & Comedy des années 90 (Sense and Sensibility, Much Ado About Nothing) +, Action & Adventure des années 80 (Batman, Indiana Jones and the Temple of Doom) -, Children's & Musical des années 50 (Mary Poppins, Lady and the Tramp) +
  - meilleurs scores parmi les jamais vus : Animation & Children's des années 50 (Snow White and the Seven Dwarfs, Cinderella) [1/4 films aimes], Film-Noir & Crime des années 50 (Double Indemnity, Sunset Blvd. (a.k.a. Sunset Boulevard)) [0/4 films aimes], Drama & War des années 80 (Apocalypse Now, Boat, The (Das Boot)) [3/4 films aimes]
- tour 6 : Drama & Thriller des années 50 (North by Northwest, Rear Window) -, Film-Noir & Crime des années 50 (Double Indemnity, Sunset Blvd. (a.k.a. Sunset Boulevard)) -, Comedy & Thriller des années 90 (American Pie, Austin Powers: The Spy Who Shagged Me) -, Animation & Children's des années 50 (Snow White and the Seven Dwarfs, Cinderella) -
  - meilleurs scores parmi les jamais vus : Musical & Romance des années 60 (Singin' in the Rain, West Side Story) [0/4 films aimes], Drama & War des années 80 (Apocalypse Now, Boat, The (Das Boot)) [3/4 films aimes], Animation & Comedy des années 90 (Wrong Trousers, The, Close Shave, A) [0/4 films aimes]
- Pour toi : Drama des années 80 (Dead Poets Society, Field of Dreams) + ; Romance & Comedy des années 90 (Sense and Sensibility, Much Ado About Nothing) + ; Comedy & Drama des années 2000 (High Fidelity, Almost Famous) +

### Utilisateur 1806 (126 films aimes, 6 univers aimes)

Univers qu'il aime d'apres MovieLens : Drama & Thriller des années 90 (Silence of the Lambs, The, Shawshank Redemption, The) ; Comedy & Romance des années 90 (There's Something About Mary, Austin Powers: International Man of Mystery) ; Action & Sci-Fi des années 90 (Matrix, The, Terminator 2: Judgment Day) ; Sci-Fi & Action des années 90 (Fifth Element, The, Star Trek: First Contact) ; Drama & Comedy des années 90 (Shakespeare in Love, Toy Story 2) ; Comedy & Thriller des années 90 (American Pie, Austin Powers: The Spy Who Shagged Me)

- tour 1 : Fantasy & Adventure des années 80 (Willow, Dark Crystal, The) -, Action & Adventure des années 80 (Batman, Indiana Jones and the Temple of Doom) -, Drama & Comedy des années 90 (Shakespeare in Love, Toy Story 2) +, Film-Noir & Crime des années 50 (Double Indemnity, Sunset Blvd. (a.k.a. Sunset Boulevard)) -
  - meilleurs scores parmi les jamais vus : Sci-Fi & Action des années 70 (War of the Worlds, The, 20,000 Leagues Under the Sea) [0/4 films aimes], Animation & Comedy des années 90 (Wrong Trousers, The, Close Shave, A) [0/4 films aimes], Animation & Children's des années 50 (Snow White and the Seven Dwarfs, Cinderella) [0/4 films aimes]
- tour 2 : Thriller & Crime des années 90 (Reservoir Dogs, Seven (Se7en)) -, Drama & War des années 80 (Apocalypse Now, Boat, The (Das Boot)) -, Drama & Thriller des années 70 (Graduate, The, Taxi Driver) -, Action & Sci-Fi des années 80 (Terminator, The, Alien) -
  - meilleurs scores parmi les jamais vus : Musical & Romance des années 60 (Singin' in the Rain, West Side Story) [0/4 films aimes], Animation & Children's des années 50 (Snow White and the Seven Dwarfs, Cinderella) [0/4 films aimes], Romance & Comedy des années 90 (Sense and Sensibility, Much Ado About Nothing) [0/4 films aimes]
- tour 3 : Animation & Children's des années 50 (Snow White and the Seven Dwarfs, Cinderella) -, Drama & Thriller des années 90 (Silence of the Lambs, The, Shawshank Redemption, The) +, Romance & Comedy des années 90 (Sense and Sensibility, Much Ado About Nothing) -, Horror des années 70 (Exorcist, The, Birds, The) -
  - meilleurs scores parmi les jamais vus : Drama & Romance des années 90 (English Patient, The, Like Water for Chocolate (Como agua para chocolate)) [0/4 films aimes], War & Romance des années 50 (African Queen, The, Gone with the Wind) [0/4 films aimes], Musical & Romance des années 60 (Singin' in the Rain, West Side Story) [0/4 films aimes]
- tour 4 : Children's & Musical des années 50 (Mary Poppins, Lady and the Tramp) -, Drama & Crime des années 70 (French Connection, The, Dog Day Afternoon) -, War & Romance des années 50 (African Queen, The, Gone with the Wind) -, Sci-Fi & Action des années 70 (War of the Worlds, The, 20,000 Leagues Under the Sea) -
  - meilleurs scores parmi les jamais vus : Musical & Romance des années 60 (Singin' in the Rain, West Side Story) [0/4 films aimes], Drama & Romance des années 90 (English Patient, The, Like Water for Chocolate (Como agua para chocolate)) [0/4 films aimes], Animation & Comedy des années 90 (Wrong Trousers, The, Close Shave, A) [0/4 films aimes]
- tour 5 : Action & Adventure des années 80 (Die Hard, Indiana Jones and the Last Crusade) -, Comedy & Drama des années 80 (Breakfast Club, The, Caddyshack) -, Drama & Thriller des années 50 (North by Northwest, Rear Window) -, Drama & Romance des années 80 (Gandhi, Chariots of Fire) -
  - meilleurs scores parmi les jamais vus : Drama & Romance des années 90 (English Patient, The, Like Water for Chocolate (Como agua para chocolate)) [0/4 films aimes], Animation & Comedy des années 90 (Wrong Trousers, The, Close Shave, A) [0/4 films aimes], Musical & Romance des années 60 (Singin' in the Rain, West Side Story) [0/4 films aimes]
- tour 6 : Comedy & Romance des années 80 (When Harry Met Sally..., Big) -, Comedy & Romance des années 90 (American President, The, Sleepless in Seattle) -, Comedy & Drama des années 2000 (High Fidelity, Almost Famous) -, Comedy & Drama des années 90 (Election, Clerks) -
  - meilleurs scores parmi les jamais vus : Musical & Romance des années 60 (Singin' in the Rain, West Side Story) [0/4 films aimes], Drama & Romance des années 90 (English Patient, The, Like Water for Chocolate (Como agua para chocolate)) [0/4 films aimes], Animation & Comedy des années 90 (Wrong Trousers, The, Close Shave, A) [0/4 films aimes]
- Pour toi : Drama & Comedy des années 90 (Shakespeare in Love, Toy Story 2) + ; Drama & Thriller des années 90 (Silence of the Lambs, The, Shawshank Redemption, The) + ; Musical & Romance des années 60 (Singin' in the Rain, West Side Story) -

