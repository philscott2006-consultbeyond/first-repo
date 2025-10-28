"""Word association party game centred on real and improvised prompts.

This module implements a social deduction game inspired by "The Imposter".
Each round all players but one receive a humorous, real-world fact or playful
challenge that is linked to a shared topic.  The remaining player is the
imposter: they must invent a convincing story on the fly and bluff their way
through the group discussion.  The same generation logic powers the browser
version provided in ``imposter_fact_game.html``.

Running the module directly starts an interactive command-line experience that
walks players through a full round.  The :func:`generate_round` function drives
the assignment logic and is intentionally reusable for tests or for integrating
the game into a different interface.
"""

from __future__ import annotations

import argparse
import random
import textwrap
from dataclasses import dataclass
from typing import Iterable, List, Sequence


# A curated selection of topics and their related prompts.  Keep this in sync
# with the ``FACT_SETS`` constant in ``imposter_fact_game.js`` so the browser
# host and CLI host share the same material.
FACT_SETS: dict[str, tuple[str, ...]] = {
    "space": (
        "A day on Venus is longer than an entire Venusian year because the planet"
        " rotates incredibly slowly.",
        "If you could fly a plane straight up, it would only take a little over an"
        " hour to reach outer space.",
        "Neutron stars are so dense that a teaspoon of material from one would"
        " weigh billions of tonnes.",
        "Footprints left on the moon could last for millions of years because the"
        " moon has no atmosphere or weather.",
    ),
    "animals": (
        "Octopuses have three hearts and blue blood that relies on copper instead"
        " of iron to carry oxygen.",
        "Cows form best friends and experience measurable stress when they are"
        " separated from them.",
        "Capybaras are so chill that in Japan some hot springs let them bathe with"
        " human visitors every winter.",
        "Male seahorses go through labor and give birth to hundreds of babies at"
        " once.",
    ),
    "food": (
        "Honey never spoils; archaeologists have found jars in ancient tombs that"
        " are still perfectly edible.",
        "Ketchup was sold as medicine in the 1830s and was marketed as a cure for"
        " indigestion.",
        "Bananas are berries, botanically speaking, while strawberries are not.",
        "Worcestershire sauce is fermented with anchovies that dissolve almost"
        " completely during the process.",
    ),
    "history": (
        "Napoleon was once attacked by a horde of rabbits during a planned hunting"
        " expedition gone wrong.",
        "In 1976, Los Angeles tried to paint its famous Hollywood sign yellow and"
        " red for the bicentennial celebrations.",
        "Oxford University is older than the Aztec Empire by at least two centuries.",
        "The shortest war in history ended after about 38 minutes between Britain"
        " and Zanzibar in 1896.",
    ),
    "tech": (
        "The very first webcam pointed at a coffee pot at Cambridge so researchers"
        " could check if it was empty without walking over.",
        "USB was intentionally designed so you can try to plug it in up to three"
        " times before it actually fits.",
        "NASA's Apollo guidance computers had less processing power than a modern"
        " pocket calculator.",
        "The first alarm clock could only ring at 4 a.m.; the inventor was a man"
        " who had to wake up early for work.",
    ),
    "tongue_twisters": (
        "Recite 'Unique New York' five times fast without stumbling.",
        "Say 'red leather, yellow leather' six times with perfect clarity.",
        "Deliver 'She sells seashells by the seashore' while keeping eye contact"
        " with the group.",
        "Three times quickly, say 'Irish wristwatch' without laughing at"
        " yourself.",
    ),
    "try_not_to_laugh": (
        "Tell the group your most ridiculous childhood snack combination with a"
        " perfectly straight face.",
        "Read this groaner without breaking: 'I used to be a baker, but I couldn't"
        " make enough dough.'",
        "Stare down the player to your left and say, 'Serious scientists"
        " seriously study silly string,' without cracking up.",
        "Share the silliest animal fact you know, but act like it's a Nobel Prize"
        " discovery.",
    ),
}


@dataclass(frozen=True)
class PlayerAssignment:
    """Information given to a single player for a round."""

    is_imposter: bool
    prompt: str | None

    def display_message(self, topic: str) -> str:
        """Return the text shown to a player during the briefing phase."""

        if self.is_imposter:
            return textwrap.fill(
                "You drew the imposter card! Listen to everyone else's stories,"
                " then invent your own and try to blend in."
            )
        assert self.prompt is not None
        return textwrap.fill(
            f"Secret topic: {topic.title()}. Your prompt when the spotlight is on"
            f" you: {self.prompt}"
        )


@dataclass(frozen=True)
class RoundSetup:
    """Complete configuration for a single round of the game."""

    topic: str
    imposter_index: int
    assignments: tuple[PlayerAssignment, ...]

    def __post_init__(self) -> None:  # pragma: no cover - defensive programming
        if not 0 <= self.imposter_index < len(self.assignments):
            raise ValueError("Imposter index must point at a player assignment")


def _sample_facts(
    facts: Sequence[str],
    count: int,
    rng: random.Random,
) -> List[str]:
    """Return ``count`` facts, sampling without exhausting the source list."""

    if count <= 0:
        return []

    if len(facts) >= count:
        # Sample without replacement when we can provide unique facts.
        return rng.sample(list(facts), count)

    # When we need more facts than are available, provide every fact at least
    # once, then keep drawing with replacement for the remainder.  Shuffling the
    # base set up front keeps the distribution fair.
    pool = list(facts)
    rng.shuffle(pool)
    while len(pool) < count:
        pool.append(rng.choice(facts))
    return pool[:count]


def generate_round(
    num_players: int,
    *,
    rng: random.Random | None = None,
    fact_sets: dict[str, Sequence[str]] | None = None,
) -> RoundSetup:
    """Create the secret assignments for a single round of the game.

    Parameters
    ----------
    num_players:
        How many people are participating in the round.  Must be three or more
        so there is at least one imposter and two truth tellers.
    rng:
        Optional :class:`random.Random` instance used for reproducible tests.
    fact_sets:
        Optional custom fact pool.  Defaults to :data:`FACT_SETS`.
    """

    if num_players < 3:
        raise ValueError("The game needs at least three players")

    rng = rng or random.Random()
    available_facts = fact_sets or FACT_SETS
    topic, facts = rng.choice(tuple(available_facts.items()))

    imposter_index = rng.randrange(num_players)
    prompt_count = num_players - 1
    prompt_pool = _sample_facts(facts, prompt_count, rng)

    assignments: list[PlayerAssignment] = []
    prompt_iter = iter(prompt_pool)
    for idx in range(num_players):
        if idx == imposter_index:
            assignments.append(PlayerAssignment(is_imposter=True, prompt=None))
        else:
            assignments.append(
                PlayerAssignment(is_imposter=False, prompt=next(prompt_iter))
            )

    return RoundSetup(
        topic=topic,
        imposter_index=imposter_index,
        assignments=tuple(assignments),
    )


def run_cli(num_players: int, *, rng_seed: int | None = None) -> None:
    """Run the interactive command-line version of the game."""

    rng = random.Random(rng_seed)
    setup = generate_round(num_players, rng=rng)

    print("\nWelcome to the Fact Imposter!\n")
    print(
        textwrap.fill(
            "Pass the screen around. Each player will secretly read their prompt."
            " Keep a poker face and try to expose the imposter once discussion"
            " begins!\n"
        )
    )

    for player_number, assignment in enumerate(setup.assignments, start=1):
        input(f"Pass to Player {player_number} and press Enter when you're ready...")
        print()
        print(assignment.display_message(setup.topic))
        input("\nHide your prompt and press Enter to continue.")
        print("\n" + "-" * 60 + "\n")

    print(
        textwrap.fill(
            "Everyone has seen their prompt. Discuss, vote on who you think the"
            " imposter is, and then reveal the topic: "
            f"{setup.topic.title()}"
        )
    )


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Play a social deduction game where only one player must fake their"
            " prompt."
        )
    )
    parser.add_argument(
        "players",
        type=int,
        help="Number of players taking part in the round (minimum 3).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for predictable assignments.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv)
    run_cli(args.players, rng_seed=args.seed)


if __name__ == "__main__":  # pragma: no cover - manual usage
    main()
