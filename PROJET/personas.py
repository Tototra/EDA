import numpy as np

PERSONAS = {
    "Inès, 21 ans, étudiante, fan d'animation": [
        "Cinderella", "Mary Poppins", "Alice in Wonderland", "Lady and the Tramp", "Peter Pan", "Snow White", "Dumbo",
        "Sleeping Beauty", "Close Shave", "Wrong Trousers", "Grand Day Out", "Labyrinth", "Goonies", "Dark Crystal",
        "NeverEnding Story", "Willow", "Toy Story 2", "Bug's Life"],
    "Marc, 55 ans, cinéphile des classiques": [
        "Rear Window", "North by Northwest", "Notorious", "Big Sleep", "Strangers on a Train", "Key Largo",
        "Double Indemnity", "Sunset Blvd", "Touch of Evil", "Third Man", "All About Eve", "Singin' in the Rain",
        "My Fair Lady", "West Side Story", "Philadelphia Story", "It Happened One Night", "To Catch a Thief",
        "His Girl Friday", "Gone with the Wind", "African Queen", "Lawrence of Arabia"],
    "Sofia, 34 ans, amatrice d'action et de science-fiction": [
        "Aliens", "Alien (1979)", "Terminator, The", "Thing, The", "Predator", "Die Hard (1988)", "Highlander",
        "Raiders of the Lost Ark", "Indiana Jones and the Last", "Lethal Weapon 2", "Batman (1989)", "Top Gun",
        "Terminator 2", "Matrix", "Face/Off", "Jurassic Park", "Fifth Element", "Stargate"],
}


def favorites(words, movies):
    return [j for j, t in enumerate(movies.title) if any(w in t for w in words)]


def liked_patterns(words, movies, patterns):
    fav = set(favorites(words, movies))
    return np.array([len(fav & set(F)) >= max(2, len(F) / 2) for F in patterns])
