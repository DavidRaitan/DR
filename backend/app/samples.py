import random

_sparks = {
    "fantasy": [
        "A cartographer discovers that the blank edges of every map she draws fill themselves in overnight — with cities she has never visited and roads that shouldn't exist.",
        "The city's dead are taxed. Every soul that lingers past their allotted forty days owes labor to the crown. The debt collector has fallen in love with his oldest debtor.",
        "Magic here runs on memory. The most powerful mages are the oldest — and the most dangerous ones are the ones who have forgotten who they were.",
    ],
    "sci-fi": [
        "The generation ship's AI has been running a therapy program for the crew for two centuries. It is now more emotionally intelligent than any human aboard — and deeply lonely.",
        "First contact arrived not as a signal but as a correction: every database on Earth had one entry quietly updated overnight, a single historical fact changed in every language simultaneously.",
        "The cure for aging worked. The problem is that personality calcifies too. Society is now ruled by the very, very old — and their 200-year-old opinions.",
    ],
    "romance": [
        "Two rival food critics have been assigned the same restaurant on the same night. There is one table left. The maître d' suggests they share it.",
        "She leaves voicemails she never sends, recording her real thoughts at 2am. He finds them, years later, on a phone he bought secondhand.",
        "They met at a grief support group — her for a marriage, him for a career. The facilitator has told them both, separately, that they're ready to move on.",
    ],
    "mystery": [
        "The murder weapon was a book. The method was the content — what was written inside it. The detective must read it to solve the case, knowing it may change him too.",
        "Every witness in this town describes the same suspect: someone who looks exactly like the detective.",
        "The victim left a confession — but to the wrong crime. Someone committed the murder to hide that confession.",
    ],
    "horror": [
        "The house has been in the family for generations. Only this generation has noticed that the floorplan gets slightly larger every year.",
        "She has been receiving birthday cards from her grandmother for three years. Her grandmother died four years ago. The handwriting is getting shakier.",
        "The children in the neighborhood all know the rule: never wave back at the person waving from the third-floor window of the old house. Last Tuesday, someone did.",
    ],
    "literary": [
        "An archivist spent forty years cataloguing a dead poet's papers. She is now older than the poet ever got to be, and she has started finishing his sentences.",
        "The last letter her father wrote was never mailed. She finds it in his desk the week after his funeral, addressed to her, dated six months ago.",
        "He translates books for a living — books no one will ever read, in a language with only one other living speaker, who does not read.",
    ],
    "any": [
        "A museum of failed inventions receives its strangest donation: a device that, according to the donor's note, 'worked perfectly, which is exactly why it had to be destroyed.'",
        "The understudy has waited seventeen years for the lead to miss a performance. Tonight, standing in the wings, she realizes she no longer wants the part.",
        "The apology letter took thirty years to write. It arrives three days after the person it was meant for has died. Their child opens it instead.",
    ],
}


def spark(genre: str, focus: str) -> str:
    pool = _sparks.get(genre, _sparks["any"]) + _sparks["any"]
    return random.choice(pool)


def continuation(story: str) -> str:
    return (
        "She didn't answer right away. The pause stretched long enough to become its own kind of answer — "
        "the kind that arrives before words do, before the speaker has quite decided what to say, "
        "when the body already knows the truth the mind is still negotiating with. "
        "Outside, the city continued its indifferent business: taxis, pigeons, the particular loneliness "
        "of strangers moving past each other in opposite directions, each carrying their invisible weight."
    )


def world_setting(seed: str) -> dict:
    return {
        "name": "The Verdigris Coast",
        "geography": "A curved archipelago of seventeen islands connected by tide-bridges that surface only at low tide, making travel between islands a precise, almost ceremonial affair.",
        "climate": "Warm and maritime, with fog that rolls in from the deep channel each evening carrying the smell of salt and something older, mineral and faintly electrical.",
        "culture": "Trade-based society built around the principle of witnessed exchange — contracts are meaningless; only transactions with a third-party witness are legally binding, giving rise to a professional class of Witnesses.",
        "conflict": "The tide-bridges have been surfacing less predictably. Engineers say it's geological. Priests say the sea is making a decision.",
    }


def world_species(seed: str) -> dict:
    return {
        "name": "The Rendered",
        "origin": "Humans who survived the Bleaching — a plague that leached pigment from everything it touched — and emerged changed: translucent skin, slowed aging, sensitivity to light.",
        "biology": "Semi-translucent skin shows circulatory system under bright light. Lifespan roughly 200 years. Low fertility. Heightened sensory sensitivity, especially to electromagnetic fields.",
        "culture": "Insular and archive-focused; the Rendered maintain the most complete historical records in the known world because they have personally witnessed centuries of it.",
        "tension": "Younger generations increasingly reject the archival obsession and the insularity it creates, demanding engagement with a world that once tried to exterminate them.",
    }


def magic_hard(seed: str) -> dict:
    return {
        "name": "Impression",
        "source": "Emotional memory — specifically, memories encoded at moments of intense feeling.",
        "mechanics": "A practitioner revisits a specific memory with full emotional fidelity. The intensity of the original feeling determines the power of the effect. Stronger memories yield stronger results.",
        "cost": "Each use degrades the memory slightly — the emotional charge diminishes. The most powerful mages have cast so many times that their strongest memories are now only facts, stripped of feeling.",
        "limits": "Cannot fabricate memories; cannot use other people's memories; cannot use memories the practitioner has lied to themselves about.",
        "thematic_resonance": "Power requires the willingness to spend the things that matter most to you.",
    }


def magic_soft(seed: str) -> dict:
    return {
        "name": "Speaking",
        "nature": "Certain individuals are born with the ability to perceive the 'intent' behind physical objects — the accumulated wishes, angers, and losses of everyone who touched them.",
        "expression": "Some Speakers can whisper to objects, nudging that accumulated intent toward specific outcomes. This is not reliable, not precise, and not fully understood even by practitioners.",
        "cultural_status": "Considered sacred in some regions, fraudulent in others, and dangerous in all of them — because Speakers who listen to objects long enough begin to lose the thread of their own feelings.",
        "mystery": "No one knows why some people are born Speakers. Heredity seems irrelevant. The pattern, if there is one, hasn't been found.",
    }


def character(seed: str) -> dict:
    return {
        "name": "Delara Voss",
        "age": 41,
        "occupation": "Maritime insurance investigator",
        "psychology": "Obsessively thorough in professional matters; avoidant in personal ones. Has constructed a life in which being right about facts substitutes for being present in relationships.",
        "wound": "At 19, she testified truthfully in an investigation that resulted in her father's company being destroyed. She was right. She has never fully forgiven herself for being right.",
        "desire": "To find the one case that doesn't have an answer, which would mean the world is less knowable than she has built her life assuming.",
        "contradiction": "Claims to be motivated by truth. Is actually motivated by control — truth is simply the most reliable lever she has found.",
        "voice": "Precise and dry, with occasional flashes of unexpected dark humor that surprise even her.",
        "physical": "Moves like someone who is always slightly calculating the weight of a room. Rarely sits fully in a chair.",
        "secret": "She has not opened her email in four days because she knows what the message from her sister says.",
        "arc": "Must learn that being right about a person is not the same as knowing them.",
    }


def scene_analysis(scene: str) -> dict:
    return {
        "act": "Act II — Rising Complications",
        "function": "Reversal / Complication",
        "analysis": "This scene functions as a reversal: the protagonist's plan appears to be working, then a new obstacle emerges that raises the stakes and forces a new approach.",
        "what_works": "The tension is well-paced, and the reversal feels earned rather than arbitrary.",
        "suggestion": "Consider what the antagonist (or opposing force) is doing during this scene. A sense of active opposition, even offstage, adds pressure.",
    }
