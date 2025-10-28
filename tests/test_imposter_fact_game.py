import random

import pytest

import imposter_fact_game as ifg


def test_generate_round_has_single_imposter():
    setup = ifg.generate_round(5, rng=random.Random(1))
    imposter_count = sum(a.is_imposter for a in setup.assignments)
    assert imposter_count == 1
    assert setup.assignments[setup.imposter_index].is_imposter


def test_generate_round_assigns_known_facts():
    rng = random.Random(5)
    setup = ifg.generate_round(6, rng=rng)
    topic_prompts = set(ifg.FACT_SETS[setup.topic])
    for idx, assignment in enumerate(setup.assignments):
        if assignment.is_imposter:
            continue
        assert assignment.prompt in topic_prompts, f"player {idx} got unknown prompt"


def test_generate_round_requires_three_players():
    with pytest.raises(ValueError):
        ifg.generate_round(2)


def test_sample_facts_reuses_pool_when_needed():
    rng = random.Random(7)
    facts = ("one", "two", "three")
    # Request more facts than available to ensure the helper repeats entries
    sampled = ifg._sample_facts(facts, 5, rng)
    assert len(sampled) == 5
    assert set(facts).issubset(sampled)
