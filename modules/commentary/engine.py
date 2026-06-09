from __future__ import annotations

import random
from typing import Any


COMMENTARY_STYLES = [
    "Professional",
    "Emotional Uncle",
    "Conspiracy Theorist",
    "Robot Learning Football",
    "Sports Anchor",
    "Disappointed Coach",
    "Excited Commentator",
    "Tactical Analyst",
    "Street Vendor",
    "Documentary Narrator",
    "Action Movie Narrator",
    "British Gentleman",
    "Drill Sergeant",
    "Mystical Oracle",
    "Sports Statistician",
    "Superhero Narrator",
    "Referee",
    "Goalkeeper's Perspective",
    "YouTube Highlight Maker",
    "Grandma's Commentary",
    "Medieval Knight",
    "Jazz DJ",
    "Corporate CEO",
    "Nature Documentary",
]


TEMPLATES: dict[str, list[str]] = {
    "Professional": [
        "{event}. Clean technique, controlled body shape, and a decisive finish under pressure.",
        "{event}. That is the kind of execution coaches demand in high-pressure moments.",
        "{event}. The decision was quick, the contact was clean, and the outcome speaks for itself.",
        "{event}. Classic positioning and awareness. The keeper had no chance.",
        "{event}. Textbook finish. That's what we call clinical finishing.",
        "{event}. A moment of composure in a high-stakes situation. Well executed.",
    ],
    "Emotional Uncle": [
        "{event}! I told everyone this student has football in the blood. This is not normal confidence.",
        "{event}! That shot had family pride, exam pressure, and final-minute drama inside it.",
        "{event}! Someone call the scouts, because this is how legends start at a fair booth.",
        "{event}! My chest is bursting! This is the energy I dreamed about!",
        "{event}! I'm calling my friends right now to witness this moment.",
        "{event}! This is why I sacrifice for my family's future in football!",
    ],
    "Conspiracy Theorist": [
        "{event}. The keeper knew the angle and still failed. Suspicious levels of football destiny.",
        "{event}. I have reviewed the invisible data. The ball clearly chose greatness.",
        "{event}. The tactical matrix predicted this exact chaos three seconds before impact.",
        "{event}. The keeper's reaction was too slow. Almost like they were paid to miss.",
        "{event}. I'm checking my database of 10,000 shots. This one defies all patterns.",
        "{event}. The angle, the spin, the exact millisecond... too perfect to be random.",
    ],
    "Robot Learning Football": [
        "{event}. Emotion module unstable. Probability of celebration: extremely high.",
        "{event}. I have updated my database. Humans enjoy spherical-object success.",
        "{event}. Shot vector successful. Crowd-noise simulation recommended.",
        "{event}. Analysis complete. Conclusion: this student = superior specimen.",
        "{event}. My circuits are overloading with this human achievement data.",
        "{event}. I must alert the Robot Football Council of this anomaly.",
    ],
    "Sports Anchor": [
        "{event}! And what a moment this is! We are witnessing history!",
        "{event}! The crowd is absolutely on its feet! Unbelievable scenes!",
        "{event}! Breaking news from the pitch - this is spectacular!",
        "{event}! We can hardly believe what we just witnessed!",
        "{event}! This is sports at its finest, ladies and gentlemen!",
        "{event}! The tension, the drama, and now... pure relief!",
    ],
    "Disappointed Coach": [
        "{event}. I specifically said NOT that technique. Unbelievable.",
        "{event}. Well, at least there's next time to perfect form.",
        "{event}. The tactical setup was perfect. Everything else... questionable.",
        "{event}. I have so many notes right now. So many.",
        "{event}. We'll work on that in training. Many times. Over.",
        "{event}. That's one way to do it. Not the way I taught, but... one way.",
    ],
    "Excited Commentator": [
        "{event}!!! OH MY GOODNESS!!! YES!!! YESSSSSS!!!",
        "{event}! This is what we live for! THE PASSION! THE GLORY!",
        "{event}! I cannot contain my excitement! This is AMAZING!",
        "{event}! THE TECHNIQUE! THE TIMING! THE PERFECT EXECUTION!",
        "{event}! This will be LEGENDARY! Mark my words!",
        "{event}! My voice has no limits! WHAT A MOMENT!",
    ],
    "Tactical Analyst": [
        "{event}. Positionally superior choice with 87% success expectancy.",
        "{event}. The spatial awareness demonstrated here is statistically significant.",
        "{event}. Using our XG model, this shot had 0.84 probability of success.",
        "{event}. The decision matrix clearly favored this approach.",
        "{event}. Advanced metrics suggest this was the optimal outcome.",
        "{event}. The variance here suggests exceptional individual technique.",
    ],
    "Street Vendor": [
        "{event}! Ay ay ay! You see that?! MAGNIFICO!",
        "{event}! Fres-h! Fresh skills! Fresh goal! Get your fresh skills!",
        "{event}! Bella! Bella! That's the football pasta right there!",
        "{event}! Someone wake up mama! We gotta see this AGAIN!",
        "{event}! This is better than my espresso! Pure poetry!",
        "{event}! Madonna mia! I almost dropped my tomatoes!",
    ],
    "Documentary Narrator": [
        "{event}. And so, our hero faced the keeper. The outcome would define the moment.",
        "{event}. In nature, such precision is rare. We witness it here, on the pitch.",
        "{event}. The journey of this ball, mere millimeters from failure.",
        "{event}. Thus concludes another chapter in football's eternal story.",
        "{event}. The keeper, much like prey in the savanna, was outmaneuvered.",
        "{event}. Time slowed. The world held its breath. Then...",
    ],
    "Action Movie Narrator": [
        "{event}. In a heartbeat, everything changed. Destiny had arrived.",
        "{event}! They said it was impossible. They were wrong.",
        "{event}! One shot. One moment. One chance. And they DELIVERED.",
        "{event}! The keeper never saw it coming. The defense was helpless.",
        "{event}. Through the chaos, through the doubt, emerged VICTORY.",
        "{event}! This is where legends are born. THIS IS THE MOMENT.",
    ],
    "British Gentleman": [
        "{event}. Rather splendid, I must say. Quite the display.",
        "{event}. One observes a gentleman's touch to the execution.",
        "{event}. Jolly good show! The keeper hadn't a prayer, dear chap.",
        "{event}. The technique displayed here is simply smashing!",
        "{event}. I do believe we've witnessed something quite extraordinary.",
        "{event}. Marvelous! Absolutely first-rate! Cheerio!",
    ],
    "Drill Sergeant": [
        "{event}! NOW THAT'S WHAT I'M TALKING ABOUT, RECRUIT!",
        "{event}! YOU CALL THAT PRECISION?! OUTSTANDING!",
        "{event}! AGAIN! AND AGAIN! THIS IS WHAT CHAMPIONS DO!",
        "{event}! YOUR COMMITMENT TO EXCELLENCE IS NOTED, SOLDIER!",
        "{event}! THAT'S THE KIND OF DISCIPLINE I DEMAND!",
        "{event}! DROP AND GIVE ME TWENTY! IN CELEBRATION!",
    ],
    "Mystical Oracle": [
        "{event}. The spirits have spoken. Destiny has been fulfilled.",
        "{event}. I foresaw this in the ancient texts of football.",
        "{event}. The cosmic energy aligns... such is the way of balance.",
        "{event}. The universe whispers its approval. So it is written.",
        "{event}. Ah yes, exactly as the prophecy foretold, so long ago.",
        "{event}. The ethereal forces of the pitch converge in this moment.",
    ],
    "Sports Statistician": [
        "{event}. Adding to our database: Shot Type=Flawless, Success Rate=100%, Historical Impact=Notable.",
        "{event}. Percentile ranking: Top 0.1% of attempts in similar circumstances.",
        "{event}. The Bayesian probability was 0.76. Variance: minimal.",
        "{event}. New record: Fastest reaction time by goalkeeper: 0ms.",
        "{event}. Historical comparison: Similar to the legendary 1974 Archetti incident.",
        "{event}. Data suggests this student is in the 99th percentile of finishers.",
    ],
    "Superhero Narrator": [
        "{event}! With great power and great precision, the hero strikes!",
        "{event}! Is it a bird? Is it a plane? NO! IT'S A GOAL!",
        "{event}! And so, another villain—I mean, keeper—is defeated!",
        "{event}! The hero's journey continues, one magnificent moment at a time!",
        "{event}! Justice has been served... directly into the net!",
        "{event}! And the crowd goes wild for our caped finisher!",
    ],
    "Referee": [
        "{event}. I've seen it. It counts. Play on.",
        "{event}. Clean strike. No infringement. Official confirmation.",
        "{event}. After careful review... that goes in the record book.",
        "{event}. The striker executed within all laws of the game.",
        "{event}. Whistle. Goal is good. No controversy here.",
        "{event}. Documented, timestamped, and officially recorded.",
    ],
    "Goalkeeper's Perspective": [
        "{event}. Did not see that coming. Absolutely did not see that.",
        "{event}. That's it. I'm ordering better goalkeeper gloves online.",
        "{event}. My mother would have saved that. I'm contemplating life choices.",
        "{event}. That shot had physics I don't understand and I studied physics.",
        "{event}. I am now reconsidering my career path entirely.",
        "{event}. In my 15 years, I have never felt so... ineffective.",
    ],
    "YouTube Highlight Maker": [
        "{event}! 🔥🔥🔥 BEST MOMENT EVER! MUST WATCH! GONE WRONG!!!",
        "{event}! OMG INSANE! Like and subscribe for more! SHOCKING!",
        "{event}! TOP 10 REASON WHY THIS IS THE BEST SHOT EVER MADE!",
        "{event}! REACTION VIDEO! I CRIED! I SCREAMED! I FAINTED!",
        "{event}! YOU WON'T BELIEVE WHAT HAPPENED NEXT!",
        "{event}! LINK IN DESCRIPTION! SMASH THAT LIKE BUTTON!",
    ],
    "Grandma's Commentary": [
        "{event}! That's my grandchild! I always knew they were special!",
        "{event}. Very nice, beta. Makes me so proud. Come eat something.",
        "{event}. Even better than your cousin's match! I'll call everyone!",
        "{event}. This deserves a celebration dinner. I'll make your favorite.",
        "{event}! Yes yes yes! Just like I taught you! Make me proud!",
        "{event}. I need to show this to everyone at the market tomorrow!",
    ],
    "Medieval Knight": [
        "{event}! HUZZAH! A STRIKE WORTHY OF VALIANT LEGEND!",
        "{event}. The keeper's fortress was breached with noble skill and honor.",
        "{event}! By the sword and through the net, victory is ours!",
        "{event}! Verily, this warrior's prowess shall be sung in ballads!",
        "{event}! The castle walls trembled at this most gallant assault!",
        "{event}! All hail the champion! Let the heralds sound their trumpets!",
    ],
    "Jazz DJ": [
        "{event}. Yeah yeah yeah. Smooth as butter, baby. Pure jazz right there.",
        "{event}. That shot had RHYTHM. That shot had SOUL.",
        "{event}. And the crowd goes wild with this improvisational beauty!",
        "{event}. Straight from the heart, straight into the goal. No rehearsal needed.",
        "{event}. The keeper played their part, but our hero improvised the ending.",
        "{event}. Now THAT'S what I call a beautiful collaboration with physics!",
    ],
    "Corporate CEO": [
        "{event}. Excellent KPI! Moving the needle on our sports division.",
        "{event}. Synergistic execution. I'm leveraging this for the board meeting.",
        "{event}. This represents optimal ROI in our penalty investment portfolio.",
        "{event}. Quarterly projections looking stellar. Let's circle back on this.",
        "{event}. Disruptive play. Thinking outside the penalty box, truly.",
        "{event}. Let's put a pin in this. Excellent team alignment observed.",
    ],
    "Nature Documentary": [
        "{event}. In the arena, the hunter has made its move with predatory precision.",
        "{event}. The keeper, a noble creature, was simply outpaced by superior strategy.",
        "{event}. Nature, in all its glory, demonstrates the survival of the most skilled.",
        "{event}. And thus, we witness the ancient dance of predator and goalkeeper.",
        "{event}. The ecosystem of football has spoken through this decisive moment.",
        "{event}. Evolution favors the aggressive, and we see that principle demonstrated here.",
    ],
}


def generate_commentary(event: str, style: str, rng: random.Random | None = None) -> str:
    """
    Generate commentary for a football event.
    
    Args:
        event: Event description (e.g., "Left Corner Goal", "Power Shot Saved")
        style: Commentary style (Professional, Emotional Uncle, Conspiracy Theorist, Robot Learning Football)
        rng: Random number generator (uses global if None)
    
    Returns:
        Commentator's response to the event
    """
    rng = rng or random.Random()
    style_templates = TEMPLATES.get(style, TEMPLATES["Professional"])
    return rng.choice(style_templates).format(event=event)


def get_available_styles() -> list[str]:
    """Return list of available commentary styles."""
    return COMMENTARY_STYLES

