import random

ADJECTIVES = [
    "happy", "lucky", "sunny", "clever", "brave", "calm", "eager", "fancy", "gentle", "jolly",
    "kind", "lively", "merry", "nice", "proud", "silly", "witty", "zesty", "bright", "cool",
    "daring", "epic", "fresh", "grand", "heroic", "infinite", "joyful", "keen", "legendary", "magic"
]

NOUNS = [
    "coder", "builder", "maker", "hacker", "artist", "designer", "writer", "runner", "gamer", "dreamer",
    "explorer", "creator", "solver", "thinker", "doer", "friend", "guide", "hero", "icon", "joker",
    "knight", "leader", "master", "ninja", "pilot", "quest", "ranger", "star", "traveler", "wizard"
]

def generate_friendly_handle() -> str:
    """Generates a random friendly handle like 'happy-coder-123'."""
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    number = random.randint(100, 999)
    return f"{adj}-{noun}-{number}"
