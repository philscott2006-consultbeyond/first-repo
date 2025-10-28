const FACT_SETS = {
  space: [
    "A day on Venus is longer than an entire Venusian year because the planet rotates incredibly slowly.",
    "If you could fly a plane straight up, it would only take a little over an hour to reach outer space.",
    "Neutron stars are so dense that a teaspoon of material from one would weigh billions of tonnes.",
    "Footprints left on the moon could last for millions of years because the moon has no atmosphere or weather.",
  ],
  animals: [
    "Octopuses have three hearts and blue blood that relies on copper instead of iron to carry oxygen.",
    "Cows form best friends and experience measurable stress when they are separated from them.",
    "Capybaras are so chill that in Japan some hot springs let them bathe with human visitors every winter.",
    "Male seahorses go through labor and give birth to hundreds of babies at once.",
  ],
  food: [
    "Honey never spoils; archaeologists have found jars in ancient tombs that are still perfectly edible.",
    "Ketchup was sold as medicine in the 1830s and was marketed as a cure for indigestion.",
    "Bananas are berries, botanically speaking, while strawberries are not.",
    "Worcestershire sauce is fermented with anchovies that dissolve almost completely during the process.",
  ],
  history: [
    "Napoleon was once attacked by a horde of rabbits during a planned hunting expedition gone wrong.",
    "In 1976, Los Angeles tried to paint its famous Hollywood sign yellow and red for the bicentennial celebrations.",
    "Oxford University is older than the Aztec Empire by at least two centuries.",
    "The shortest war in history ended after about 38 minutes between Britain and Zanzibar in 1896.",
  ],
  tech: [
    "The very first webcam pointed at a coffee pot at Cambridge so researchers could check if it was empty without walking over.",
    "USB was intentionally designed so you can try to plug it in up to three times before it actually fits.",
    "NASA's Apollo guidance computers had less processing power than a modern pocket calculator.",
    "The first alarm clock could only ring at 4 a.m.; the inventor was a man who had to wake up early for work.",
  ],
};

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

function sampleFacts(facts, count) {
  if (count <= 0) {
    return [];
  }

  if (facts.length >= count) {
    const candidates = shuffle([...facts]);
    return candidates.slice(0, count);
  }

  const pool = shuffle([...facts]);
  while (pool.length < count) {
    pool.push(facts[Math.floor(Math.random() * facts.length)]);
  }
  return pool.slice(0, count);
}

function titleCase(topic) {
  return topic
    .split(" ")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function createRound(numPlayers, topicChoice) {
  const topics = Object.keys(FACT_SETS);
  const topic = topicChoice === "random"
    ? topics[Math.floor(Math.random() * topics.length)]
    : topicChoice;

  if (!FACT_SETS[topic]) {
    throw new Error("Unknown topic");
  }

  const imposterIndex = Math.floor(Math.random() * numPlayers);
  const facts = sampleFacts(FACT_SETS[topic], Math.max(0, numPlayers - 1));

  const assignments = [];
  let factIndex = 0;
  for (let i = 0; i < numPlayers; i += 1) {
    if (i === imposterIndex) {
      assignments.push({ isImposter: true });
    } else {
      assignments.push({ isImposter: false, fact: facts[factIndex] });
      factIndex += 1;
    }
  }

  return { topic, imposterIndex, assignments };
}

function setupTopicOptions() {
  const topicSelect = document.getElementById("topic-choice");
  const fragment = document.createDocumentFragment();
  Object.keys(FACT_SETS)
    .sort()
    .forEach((topic) => {
      const option = document.createElement("option");
      option.value = topic;
      option.textContent = titleCase(topic);
      fragment.appendChild(option);
    });
  topicSelect.appendChild(fragment);
}

function main() {
  const form = document.getElementById("setup-form");
  const playerInput = document.getElementById("player-count");
  const topicSelect = document.getElementById("topic-choice");
  const roundArea = document.getElementById("round-area");
  const topicPill = document.getElementById("topic-pill");
  const messageText = document.getElementById("message-text");
  const revealButton = document.getElementById("reveal-button");
  const hideButton = document.getElementById("hide-button");
  const resetButton = document.getElementById("reset-button");
  const progressNote = document.getElementById("progress-note");

  let currentRound = null;
  let currentIndex = 0;

  function updateRevealButtonLabel() {
    revealButton.textContent = `Reveal for Player ${currentIndex + 1}`;
  }

  function showPromptForCurrentPlayer() {
    messageText.textContent = `Pass the device to Player ${currentIndex + 1} and tap “Reveal” when they're ready.`;
    updateRevealButtonLabel();
    revealButton.hidden = false;
    hideButton.hidden = true;
    progressNote.textContent = `${currentIndex} / ${currentRound.assignments.length} players briefed`;
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const numPlayers = Number.parseInt(playerInput.value, 10);
    if (!Number.isFinite(numPlayers) || numPlayers < 3) {
      alert("The game needs at least three players.");
      playerInput.focus();
      return;
    }

    currentRound = createRound(numPlayers, topicSelect.value);
    currentIndex = 0;

    topicPill.textContent = `Secret topic: ${titleCase(currentRound.topic)}`;
    topicPill.hidden = false;
    roundArea.classList.add("active");
    resetButton.hidden = false;
    progressNote.textContent = "0 / " + currentRound.assignments.length + " players briefed";

    showPromptForCurrentPlayer();
  });

  revealButton.addEventListener("click", () => {
    if (!currentRound) {
      return;
    }

    const assignment = currentRound.assignments[currentIndex];
    if (assignment.isImposter) {
      messageText.textContent = "You drew the imposter card! Listen carefully to everyone else's facts, then bluff with your own fabricated story.";
    } else {
      messageText.textContent = `Secret topic: ${titleCase(currentRound.topic)}. Read this true fact aloud when it's your turn: ${assignment.fact}`;
    }
    revealButton.hidden = true;
    hideButton.hidden = false;
  });

  hideButton.addEventListener("click", () => {
    if (!currentRound) {
      return;
    }

    currentIndex += 1;
    const totalPlayers = currentRound.assignments.length;
    if (currentIndex >= totalPlayers) {
      messageText.textContent = "Everyone has their intel. Start the conversation and see if the imposter can stay hidden!";
      hideButton.hidden = true;
      revealButton.hidden = true;
      progressNote.textContent = `${totalPlayers} / ${totalPlayers} players briefed`;
      return;
    }

    progressNote.textContent = `${currentIndex} / ${totalPlayers} players briefed`;
    showPromptForCurrentPlayer();
  });

  resetButton.addEventListener("click", () => {
    currentRound = null;
    currentIndex = 0;
    roundArea.classList.remove("active");
    topicPill.hidden = true;
    revealButton.hidden = true;
    hideButton.hidden = true;
    resetButton.hidden = true;
    progressNote.textContent = "";
    messageText.textContent = "Choose your player count, then press “Start new round” to begin.";
  });
}

setupTopicOptions();
window.addEventListener("DOMContentLoaded", main);
