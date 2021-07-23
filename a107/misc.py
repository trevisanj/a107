"""Miscellanea of miscellanea"""


__all__ = ["random_name", "cowsay_what"]


import random


_forenames = ["Solomon", "John", "Loretta", "Stephen", "Harry", "Nancy", "Tracy", "Maggie", "Lafanda", "Napoleon", "Joe",
        "Ana", "Olivia", "Lucia", "Julien", "June", "Ada", "Blaise", "Platypus", "R2D2", "Obi-Wan",
        "Yoda", "Lancelot", "Shaun", "C3PO", "Luke", "George", "Martin", "Elvira", "Galileo", "Elizabeth",
        "Genie", "Mark", "Karl", "Henry-David", "Ludmilla", "Darth", "Bayden", "Plamen", "Margareth", "Javier",
        "Pouria", "Klen", "Lydiane", "Charlotte", "Edna", "Ricardo", "Francis", "Jemma", "Valon", "Imran", "Sian",
        "Hayat", "Taghreed", "Orla", "Michael", "Lourdes", "Weiyi", "Thomas", "Willian", "Miguel", "Rui",
        "Abdullah", "Angus", "Malcolm", "Donald", "Mickey", "Polona", "Rashmi", "Xiaowei", "Sasha", "Luciano",
        "Avinash", "Anthony", "Karen", "Matthew", "Tatiana", "Mariana", "Antonio", "Hamilton", "Pauderney",
        "BB-8", "Damian", "Rui", "Nicolas", "Viola", "Soledad", "Aspa", "Mirjam", "Micaela", "Yamilla", "Angelica",
        "Chocolate"]
_surnames = ["Northupp", "Kanobi", "de Morgan", "de Vries", "van Halen", "McFly", "Wallace", "McLeod", "Skywalker", "Smith",
       "Silva", "da Silva", "Sexy", "Coupat", "Coupable", "Byron", "Lovelace", "Pascal", "Kareninski", "Dynamite",
       "Souza", "Ha", "Balboa", "Durden", "V.", "Li", "Manco", "Kelly", "Torquato", "Sampaio", "Bittencourt", "Parisi",
       "Oliveira", "Crap", "Coppercup", "Motherfucker", "Firehead", "Martin", "Papanicolau", "Galilei", "Stuart",
       "Bitch", "King", "Cleese", "Thoreau", "Twain", "Marx", "Yankovicz", "Vader", "Prado", "Teixeira", "Oliveira",
       "Nogueira", "Pereira", "Sant'anna", "Kerns", "Patel", "Ahmadzai", "Riding", "Llabjani", "Maus",
       "Liger", "Byrne", "Wood", "Angelov", "Andreu", "Sadeghi", "Gajjar", "Kara", "Wolstenholme", "Alghaith",
       "Young", "Scott", "Luz", "Copic", "Pucihar", "Zhou", "Dutta", "Baruah", "Singh", "Sauro", "do Nascimento",
       "Lee", "Trevisan", "Travisani", "Pereira", "Nandwani", "Moura", "Senna", ]
_prefixes = ["Dr.", "Prof.", "Sir", "Ven."]
_suffixes = ["The 3rd", "Jr.", "Sobrinho", "Neto", "VIII", "XVI", "I", "II", "III", "IV"]
_PROB_PREF = 0.1
_PROB_SUFF = 0.1


def random_name(num_surnames=2):
    """
    Returns a random person name

    Arguments:
      num_surnames -- number of surnames
    """
    a = []

    # Prefix
    if random.random() < _PROB_PREF:
        a.append(_prefixes[random.randint(0, len(_prefixes) - 1)])

    # Forename
    a.append(_forenames[random.randint(0, len(_forenames) - 1)])

    # Surnames
    for i in range(num_surnames):
        a.append(_surnames[random.randint(0, len(_surnames) - 1)])

    # Suffix
    if random.random() < _PROB_SUFF:
        a.append(_suffixes[random.randint(0, len(_suffixes) - 1)])

    return " ".join(a)


_moo = ["please kill me", "mooooooooooo", "got some eyelashes?", "go fuck yourself", "what are you looking at?",
"you piece of shit", "I just farted", "I fucked your mother", "you are a loser", "did you kill yourself already?",
"I hate you", "dig a hole and bury yourself", "I like to fuck cats in the ass"]
def cowsay_what():
    """Returns something that would be appropriate for a cow to say."""
    return random.choice(_moo)
