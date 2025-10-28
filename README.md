# Fact Imposter Party Game

This repository now centres on a social deduction experience where every
player, except for a single imposter, receives a surprising-but-true trivia
fact or a light-hearted challenge prompt. The imposter must improvise and bluff
their way through the discussion.

## Play in your browser

Open ``imposter_fact_game.html`` in any modern desktop or mobile browser. The
page contains everything you need to host a round:

- Choose how many players are involved (three or more) and optionally list
  their names for personalised briefings.
- Let the page pick a random topic, or select one manually.
- Pass a single device around the table so each person can press and hold to
  reveal their secret briefing in turn.
- Once everyone is briefed, dive into the debate and try to spot the imposter.

The interface is optimised for passing a phone or tablet around the group, with
clear prompts that remind you whose turn it is, how many players have been
briefed, and optional mini-challenges such as tongue twisters or try-not-to-
laugh dares to mix up the energy.

## Command-line host (optional)

Prefer a minimal setup or want reproducible assignments for remote play? Run
``imposter_fact_game.py`` directly:

```bash
python imposter_fact_game.py 5
```

Use ``--seed`` to recreate a round with the same assignments.

## Running tests

Install the dependencies and execute ``pytest`` to verify the round generation
logic that both the browser and command-line experiences rely on:

```bash
pip install pytest
pytest
```
