import random
from typing import Dict, List, Any

# --- Data: Players ---
PLAYERS_WITH_CLUES = [
    {
        "name": "Lionel Messi",
        "clues": [
            "My first professional contract was famously signed on a paper napkin.",
            "I made my senior international debut against Hungary, but was sent off after just 47 seconds.",
            "I won the Golden Boy award in 2005.",
            "I scored my first professional goal against Albacete, assisted by Ronaldinho.",
            "I have scored five goals in a single UEFA Champions League match.",
            "I hold the record for the most European Golden Shoes won.",
            "I hold the record for the most goals in a calendar year (91).",
            "I formed a famous attacking trio known as 'MSN'.",
            "I left my boyhood club in 2021 to join Paris Saint-Germain.",
            "I finally won the FIFA World Cup in 2022, cementing my legacy as 'La Pulga'."
        ]
    },
    {
        "name": "Cristiano Ronaldo",
        "clues": [
            "I was diagnosed with a racing heart condition at age 15 that required surgery.",
            "I became the first player to win all three main PFA and FWA awards in a single English season.",
            "I won the FIFA Puskás Award in its inaugural year (2009).",
            "I am the all-time top goalscorer in the UEFA European Championship.",
            "I am the first player to win five UEFA Champions League titles in the modern era.",
            "I hold the record for the most international goals scored by a male player.",
            "I transferred to Real Madrid for a then-world record fee in 2009.",
            "I have played professionally in Portugal, England, Spain, Italy, and Saudi Arabia.",
            "I famously formed a rivalry with Lionel Messi that defined a generation.",
            "I am famously associated with the number 7 and the 'Siuuu' celebration."
        ]
    },
    {
        "name": "Zinedine Zidane",
        "clues": [
            "I began my professional career at Cannes, where I scored my first goal and received a car from the club president.",
            "I played for Bordeaux, helping them reach the 1996 UEFA Cup Final.",
            "I won the Ballon d'Or in 1998 after a historic international tournament.",
            "I scored two headers in a World Cup final.",
            "I transferred to Real Madrid for a world-record fee of 77.5 million euros in 2001.",
            "I scored one of the most famous volleys in Champions League history in the 2002 final.",
            "My elegant playing style and incredible first touch earned me the nickname 'Zizou'.",
            "I came out of international retirement to lead my country to the 2006 World Cup final.",
            "I famously received a red card for a headbutt in my final professional match.",
            "I later managed Real Madrid to three consecutive Champions League titles."
        ]
    },
    {
        "name": "Diego Maradona",
        "clues": [
            "I made my professional debut at age 15, nutmegging an opponent with my first touch.",
            "I was controversially left out of the 1978 World Cup squad for being too young.",
            "I broke the world record transfer fee twice in my career (moving to Barcelona, then Napoli).",
            "I spent my prime years playing in Serie A, bringing unprecedented success to a southern Italian club.",
            "I was suspended from football for 15 months in 1991 for failing a drug test.",
            "I captained my country to victory in the 1986 World Cup.",
            "I scored the 'Goal of the Century' after dribbling past five players.",
            "In the same match, I scored a highly controversial goal with my hand.",
            "My legendary number 10 shirt was retired by Napoli.",
            "I am considered a footballing god in Argentina, alongside Messi."
        ]
    },
    {
        "name": "Pelé",
        "clues": [
            "I was named after the American inventor Thomas Edison.",
            "I made my international debut at just 16 years and 9 months old.",
            "I am the youngest player to score a hat-trick in a World Cup.",
            "I spent almost my entire professional career playing for Santos.",
            "I briefly stopped a war in Nigeria in 1969 so opposing factions could watch me play.",
            "I scored over 1,000 career goals, though the exact number of official goals is heavily debated.",
            "I later played for the New York Cosmos, popularizing soccer in the US.",
            "I am the only player in history to win three FIFA World Cups.",
            "My nickname translates to 'The King' in Portuguese.",
            "I am widely considered the greatest football player of the 20th century."
        ]
    }
]

PLAYER_DISTRACTORS = [
    "Neymar Jr", "Andrés Iniesta", "Xavi Hernandez", "Ronaldo Nazário", "Ronaldinho",
    "Johan Cruyff", "Michel Platini", "Franz Beckenbauer", "Thierry Henry", "Paolo Maldini",
    "Gianluigi Buffon", "Luka Modrić", "Sergio Ramos", "Wayne Rooney", "Robert Lewandowski",
    "Karim Benzema", "Kylian Mbappé", "Erling Haaland", "Kevin De Bruyne", "Mohamed Salah",
    "Gareth Bale", "Luis Suárez", "Sergio Agüero", "Steven Gerrard", "Frank Lampard"
]


# --- Data: Coaches ---
COACHES_WITH_CLUES = [
    {
        "name": "Pep Guardiola",
        "clues": [
            "I tested positive for nandrolone during my playing career in Italy, serving a four-month ban.",
            "I won an Olympic Gold Medal as a player in 1992.",
            "My managerial career began with the B-team of the club I spent most of my playing career at.",
            "In my first season as a first-team manager, I won the sextuple (six trophies in a calendar year).",
            "I am known for a tactical style heavily focused on positional play ('Juego de Posición').",
            "I managed Bayern Munich for three seasons, winning the Bundesliga each time.",
            "I famously utilized a 'false 9' system to great effect with Lionel Messi.",
            "I became the first manager to win the domestic treble in England.",
            "I led Manchester City to their first-ever Champions League title in 2023.",
            "I am widely considered the most influential tactician of the modern era."
        ]
    },
    {
        "name": "Sir Alex Ferguson",
        "clues": [
            "I played as a forward and was the top goalscorer in the Scottish league in the 1965-66 season.",
            "I began my managerial career at East Stirlingshire at the age of 32.",
            "I managed Aberdeen, famously defeating Real Madrid in a European final.",
            "I was appointed manager of a massive English club in 1986 but didn't win the league for seven years.",
            "I was known for my 'hairdryer treatment' when criticizing players in the dressing room.",
            "I famously stated my greatest challenge was 'knocking Liverpool right off their f***ing perch.'",
            "I won the historic treble (Premier League, FA Cup, Champions League) in 1999.",
            "My teams were famous for scoring late goals in what became known as 'Fergie Time'.",
            "I won 13 Premier League titles before retiring in 2013.",
            "I am the most successful manager in the history of Manchester United."
        ]
    },
    {
        "name": "Jose Mourinho",
        "clues": [
            "My playing career was entirely unremarkable, playing in the lower leagues of my home country.",
            "I worked as an interpreter for Sir Bobby Robson at Sporting CP, Porto, and Barcelona.",
            "I won the UEFA Cup and Champions League in consecutive seasons with Porto.",
            "Upon arriving in England, I famously declared myself 'The Special One' in my first press conference.",
            "I set a Premier League record of 15 goals conceded in a single season.",
            "I am known for my pragmatic, defensive tactical setups, dark arts, and mind games.",
            "I won the historic treble with Inter Milan in 2010.",
            "I managed Real Madrid, winning La Liga with a record 100 points.",
            "I have won the Champions League with two different clubs.",
            "I managed AS Roma to the inaugural UEFA Europa Conference League title."
        ]
    },
    {
        "name": "Jurgen Klopp",
        "clues": [
            "I spent my entire playing career and began my managerial career at Mainz 05.",
            "I brought Borussia Dortmund back to the top of German football, winning back-to-back league titles.",
            "I led Dortmund to the Champions League final in 2013.",
            "I am synonymous with the tactical philosophy of 'Gegenpressing'.",
            "I refer to my preferred style of play as 'heavy metal football'.",
            "I joined Liverpool in 2015, famously calling myself 'The Normal One'.",
            "I led Liverpool to their sixth Champions League title in 2019.",
            "I ended Liverpool's 30-year wait for a top-flight league title in 2020.",
            "I am known for my passionate touchline celebrations and connection with the fans.",
            "I announced I would leave Liverpool at the end of the 2023-24 season."
        ]
    },
    {
        "name": "Carlo Ancelotti",
        "clues": [
            "I was a highly successful player, winning European Cups with AC Milan.",
            "I managed Juventus before taking over at AC Milan.",
            "I won the Champions League twice as manager of AC Milan.",
            "I am known for my calm demeanor and excellent man-management skills.",
            "I managed Chelsea to a Premier League and FA Cup double.",
            "I won 'La Decima' (the 10th European Cup) for Real Madrid in my first spell.",
            "I am the first manager to win league titles in all of Europe's top five leagues.",
            "I am the most successful manager in Champions League history with 4 titles.",
            "I returned to Real Madrid in 2021 and won another Champions League.",
            "I am fondly nicknamed 'Don Carlo'."
        ]
    }
]

COACH_DISTRACTORS = [
    "Diego Simeone", "Arsène Wenger", "Zinedine Zidane", "Antonio Conte", "Mikel Arteta",
    "Massimiliano Allegri", "Thomas Tuchel", "Mauricio Pochettino", "Luis Enrique", "Xavi Hernandez",
    "Roberto Mancini", "Claudio Ranieri", "Marcelo Bielsa", "Louis van Gaal", "Vicente del Bosque",
    "Joachim Löw", "Didier Deschamps", "Gareth Southgate", "Unai Emery", "Erik ten Hag",
    "Xabi Alonso", "Roberto De Zerbi", "Julian Nagelsmann", "Carlo Ancelotti", "Hansi Flick"
]


# --- Data: Stadiums ---
STADIUMS_WITH_CLUES = [
    {
        "name": "Camp Nou",
        "clues": [
            "Construction began in 1954 and it opened in 1957.",
            "It hosted the opening match of the 1982 World Cup.",
            "It was the venue for the 1992 Olympic football final.",
            "It hosted the dramatic 1999 Champions League final where Manchester United won late.",
            "It has a capacity of over 99,000, making it the largest stadium in Europe.",
            "The stadium's name translates simply to 'New Field'.",
            "Its motto 'Més que un club' is displayed in the stands.",
            "It is currently undergoing massive renovations.",
            "It is located in Catalonia.",
            "It is the iconic home of FC Barcelona."
        ]
    },
    {
        "name": "Santiago Bernabéu",
        "clues": [
            "It was inaugurated in 1947.",
            "It is named after a former player and legendary president of the club.",
            "It hosted the 1982 FIFA World Cup final.",
            "It has hosted the European Cup/Champions League final four times.",
            "It is located in the Chamartín district of the Spanish capital.",
            "It underwent a massive, futuristic renovation that included a retractable roof.",
            "It was the venue for the 2018 Copa Libertadores final.",
            "It is one of the most famous football venues in the world.",
            "It is the home of the most successful club in European Cup history.",
            "It is the fortress of Real Madrid."
        ]
    },
    {
        "name": "Old Trafford",
        "clues": [
            "It opened in 1910 and suffered heavy bomb damage during WWII.",
            "It hosted matches during the 1966 World Cup and Euro 96.",
            "It was the venue for the 2003 Champions League final.",
            "It has a capacity of around 74,000, the largest club stadium in England.",
            "The ends are known as the Stretford End and the Scoreboard End.",
            "Sir Bobby Charlton famously nicknamed it 'The Theatre of Dreams'.",
            "A statue of the 'United Trinity' stands outside the ground.",
            "It is located in Greater Manchester.",
            "It has been home to legendary managers like Matt Busby and Alex Ferguson.",
            "It is the iconic home of Manchester United."
        ]
    },
    {
        "name": "Anfield",
        "clues": [
            "It opened in 1884 and was originally home to a different club before 1892.",
            "It has four stands: the Main Stand, the Sir Kenny Dalglish Stand, the Anfield Road End, and its most famous end.",
            "It hosted matches during Euro 96.",
            "The stadium is known for having one of the most intimidating atmospheres in Europe.",
            "A sign reading 'This is...' sits above the tunnel, touched by players before entering the pitch.",
            "The gates outside are named after former managers Bill Shankly and Bob Paisley.",
            "Its most famous stand is a steep, single-tier terrace.",
            "That stand is known as 'The Kop'.",
            "The fans famously sing 'You'll Never Walk Alone' before matches.",
            "It is the legendary home of Liverpool FC."
        ]
    },
    {
        "name": "Wembley Stadium",
        "clues": [
            "The original stadium on this site was built in 1923 and featured iconic Twin Towers.",
            "The original stadium hosted the 1966 World Cup final.",
            "The new stadium opened in 2007 on the same site.",
            "It has a capacity of 90,000.",
            "It features a massive, 134-meter-high arch that supports the roof.",
            "It hosts the FA Cup semi-finals and final.",
            "It hosted the Champions League finals in 2011 and 2013.",
            "It hosted the final of Euro 2020.",
            "It serves as the national stadium for its country.",
            "It is the home of the England national football team."
        ]
    }
]

STADIUM_DISTRACTORS = [
    "San Siro", "Allianz Arena", "Signal Iduna Park", "Emirates Stadium", "Stamford Bridge",
    "Etihad Stadium", "Tottenham Hotspur Stadium", "Maracanã", "Estadio Azteca", "La Bombonera",
    "Monumental", "Parc des Princes", "Stade de France", "Olympiastadion", "Wanda Metropolitano",
    "Mestalla", "Johan Cruyff Arena", "Celtic Park", "Ibrox Stadium", "Boca Juniors Stadium"
]


# --- Data: Iconic Matches ---
MATCHES_WITH_CLUES = [
    {
        "name": "The Miracle of Istanbul (2005)",
        "clues": [
            "This match was the final of the UEFA Champions League.",
            "It took place at the Atatürk Olympic Stadium.",
            "One team scored in the first minute of the match.",
            "That same team led 3-0 at half-time.",
            "The other team scored three goals in a frantic six-minute spell in the second half.",
            "The captain of the trailing team scored a header to start the comeback.",
            "The match went to penalties after a stunning double-save in extra time.",
            "The winning goalkeeper was famously 'spaghetti legs' during the shootout.",
            "The match was played between AC Milan and Liverpool.",
            "It is widely considered the greatest comeback in Champions League final history."
        ]
    },
    {
        "name": "The 7-1 (2014)",
        "clues": [
            "This was a semi-final match of the FIFA World Cup.",
            "It was played at the Mineirão stadium.",
            "The host nation was playing without their star attacker due to injury.",
            "The away team scored five goals in the first 29 minutes.",
            "The host nation's defense completely collapsed in a historic humiliation.",
            "A striker broke the all-time World Cup goalscoring record during this match.",
            "The final scoreline shocked the entire football world.",
            "The host nation managed a late consolation goal in the 90th minute.",
            "The match was between Germany and Brazil.",
            "It is often referred to as the 'Mineirazo'."
        ]
    },
    {
        "name": "Agüeroooooo (2012)",
        "clues": [
            "This match took place on the final day of the league season.",
            "The home team needed a win to secure their first league title in 44 years.",
            "The home team fell behind 2-1 against 10 men in the second half.",
            "The home team's bitter rivals had already won their match and were waiting to celebrate.",
            "An equalizer was scored in the 92nd minute by Edin Dzeko.",
            "The winning goal was scored in the 94th minute.",
            "The commentator famously screamed the goalscorer's name, extending the vowels.",
            "The result meant the title was won on goal difference.",
            "The match was Manchester City vs Queens Park Rangers.",
            "It remains the most dramatic finish to a Premier League season."
        ]
    },
    {
        "name": "La Remontada (2017)",
        "clues": [
            "This was a UEFA Champions League round of 16 second-leg tie.",
            "The home team had lost the first leg 4-0.",
            "No team had ever overturned a four-goal first-leg deficit in the competition's history.",
            "The home team took a 3-0 lead by the 50th minute.",
            "The away team scored a crucial away goal, meaning the home team now needed three more.",
            "Neymar scored a stunning free-kick in the 88th minute.",
            "Neymar scored a penalty in the 91st minute.",
            "Sergi Roberto scored the decisive goal in the 95th minute.",
            "The final score on the night was 6-1.",
            "The match was between Barcelona and Paris Saint-Germain."
        ]
    },
    {
        "name": "The Hand of God Match (1986)",
        "clues": [
            "This was a FIFA World Cup quarter-final.",
            "It was played at the Estadio Azteca in Mexico City.",
            "The match carried heavy geopolitical significance due to a recent conflict between the nations.",
            "The first goal was highly controversial, scored with a hand.",
            "The referee allowed the goal, believing it was a header.",
            "The second goal is widely considered the greatest individual goal in World Cup history.",
            "The scorer of the second goal dribbled past five players starting from his own half.",
            "Both iconic goals were scored by the same player.",
            "That player was Diego Maradona.",
            "The match was Argentina vs England."
        ]
    }
]

MATCH_DISTRACTORS = [
    "The 1999 UCL Final", "The 1966 World Cup Final", "The Battle of Nuremberg", "The Maracanazo",
    "Real Madrid 4-1 Atletico Madrid (2014)", "Barcelona 5-0 Real Madrid (2010)", "Manchester United 8-2 Arsenal",
    "Liverpool 4-0 Barcelona (2019)", "Ajax 2-3 Tottenham (2019)", "Germany 1-0 Argentina (2014)",
    "France 4-2 Croatia (2018)", "Italy 1-1 France (2006)", "Spain 1-0 Netherlands (2010)",
    "Chelsea 1-1 Bayern Munich (2012)", "Arsenal 'Invincibles' Final Match"
]


def generate_challenge(category: str) -> Dict[str, Any]:
    """Generates a random challenge for the specified category."""
    if category == "player":
        source = PLAYERS_WITH_CLUES
        distractors = PLAYER_DISTRACTORS
    elif category == "coach":
        source = COACHES_WITH_CLUES
        distractors = COACH_DISTRACTORS
    elif category == "stadium":
        source = STADIUMS_WITH_CLUES
        distractors = STADIUM_DISTRACTORS
    elif category == "match":
        source = MATCHES_WITH_CLUES
        distractors = MATCH_DISTRACTORS
    else:
        raise ValueError(f"Unknown category: {category}")

    # Pick a random entry
    entry = random.choice(source)
    correct_answer = entry["name"]
    clues = entry["clues"]

    # Generate MCQ options (4 total)
    # Ensure distractors don't include the correct answer
    available_distractors = [d for d in distractors if d != correct_answer]
    selected_distractors = random.sample(available_distractors, 3)
    options = [correct_answer] + selected_distractors
    random.shuffle(options)

    return {
        "category": category,
        "clues": clues,
        "options": options,
        "answer": correct_answer
    }

def start_fan_game() -> Dict[str, Any]:
    """Starts a new Fan Mode game returning 4 challenges."""
    return {
        "challenges": [
            generate_challenge("player"),
            generate_challenge("coach"),
            generate_challenge("stadium"),
            generate_challenge("match")
        ]
    }
