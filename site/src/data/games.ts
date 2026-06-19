export type GameEntry = {
  slug: string;
  title: string;
  teamCode: string;
  track: "Pygame" | "Unity";
  category: "ranked" | "special";
  awards: string[];
  team: string;
  summary: string;
  cover: string;
  writeup: string;
  links: Array<{ label: string; href: string }>;
  playNote: string;
};

const w = "/winners";

export const games: GameEntry[] = [
  {
    slug: "p6",
    title: "ALARM CLOCK: Tick's Timebomb",
    teamCode: "P6",
    track: "Pygame",
    category: "ranked",
    awards: ["Pygame Winner"],
    team: "Gan Xuan En Claire, Peh Hng Hao Lucas, Yong Tian Ci Braden",
    summary:
      "A psychological horror adventure where an alarm clock comes to life, grows stranger over ten days, and changes its ending through player choices.",
    cover: "/assets/images/p6-cover.png",
    writeup: "A psychological horror adventure where your alarm clock comes to life and grows more frightening each day — until, halfway through, you unexpectedly start to develop feelings for it. The choices you make across the ten-day story shape the boss fight and which ending you reach.",
    links: [
      {
        label: "Slides PDF",
        href: `${w}/P6 - Pygame Winner - ALARM CLOCK Ticks Timebomb/slides/pygame second - p15 - Canva/GAME JAM BUILDINGBLOCS 2026.pdf`,
      },
    ],
    playNote:
      "This entry has a confirmed browser export from the submitted Pygame source.",
  },
  {
    slug: "p15",
    title: "Finding the Way Home",
    teamCode: "P15",
    track: "Pygame",
    category: "ranked",
    awards: ["Pygame Runner-up"],
    team: "Liew Jia Yan Anne, Su Myat Thiri, Jonas Phua Yong Bin, Isaac Thian Junjie",
    summary:
      "A visual novel concept about memory loss, wayfinding, and how an ordinary walk home can become emotionally difficult.",
    cover: "/assets/images/p15-cover.svg",
    writeup: "A visual novel about memory loss and finding your way home, drawn from a real encounter with an elderly woman lost at a void deck. It puts you in the shoes of someone for whom an ordinary walk home becomes a genuine struggle, told through a quiet, emotional story.",
    links: [
      {
        label: "Submission note",
        href: `${w}/P15 - Pygame Runner-up - Finding the Way Home/README.md`,
      },
    ],
    playNote:
      "This entry has a confirmed browser export built from the recovered submitted Pygame source.",
  },
  {
    slug: "p26",
    title: "Homebound",
    teamCode: "P26",
    track: "Pygame",
    category: "ranked",
    awards: ["Pygame Second Runner-up"],
    team: "Cyrus Tng Jia Zhe, Chye Kai Ru Jolin, Lee Jia Hui",
    summary:
      "A running and fighting game where household problems become interactive enemies and relatable daily obstacles.",
    cover: "/assets/images/p26-cover.png",
    writeup: "A running-and-fighting game built around the small challenges of daily life — like ants swarming a grain of rice dropped on the floor. You and the enemies stand in for these everyday nuisances, with interactive, relatable encounters rather than a passive screen.",
    links: [
      {
        label: "Writeup DOCX",
        href: `${w}/P26 - Pygame Second Runner-up - Homebound/slides/Writeup.docx`,
      },
    ],
    playNote:
      "This entry has a confirmed browser export from the submitted Pygame source.",
  },
  {
    slug: "u8",
    title: "The Trash Won't Take Itself Out!",
    teamCode: "U8",
    track: "Unity",
    category: "ranked",
    awards: ["Unity Winner"],
    team: "Ng Wei Le Dylan, Chelsea Diane Balane Paquibot, Ian Then Kai Xiang, Jose Matthew Abram Mendoza",
    summary:
      "A Unity game about taking out the trash, scoped around clear mechanics, compact level design, and a new perspective on routine.",
    cover: "/assets/images/u8-cover.png",
    writeup: "A Unity game about the everyday routine of taking out the trash, seen from a fresh angle. A tightly-paced level introduces its mechanics with good flow as you work your way through a compact, polished layout.",
    links: [
      {
        label: "Slides PDF",
        href: `${w}/U8 - Unity Winner - The Trash Wont Take Itself Out/slides/unity 1st - u8 - Canva/JuneJam U8.pdf`,
      },
    ],
    playNote:
      "This entry has a confirmed Unity WebGL export from the submitted project.",
  },
  {
    slug: "u4",
    title: "5 More Minutes",
    teamCode: "U4",
    track: "Unity",
    category: "ranked",
    awards: ["Unity Runner-up"],
team: "Pan Yinchen, Elliott Huang, Lian Shengzhe, Ricardo Delario",
    summary:
      "A walking simulator about the student commute, using narration and player choice to turn a mundane journey into comedy.",
    cover: "/assets/images/u4-cover.png",
    writeup: "A Stanley Parable-style walking simulator about the student commute to a BuildingBloCS workshop. The core is simply walking and clicking, with the heart of the game in its branching narration, humour, and the little world you explore.",
    links: [
    ],
    playNote:
      "This entry has a confirmed Unity WebGL export from the submitted project.",
  },
  {
    slug: "u2",
    title: "Taking OUT the Trash",
    teamCode: "U2",
    track: "Unity",
    category: "ranked",
    awards: ["Unity Second Runner-up", "Best Art"],
    team: "Chew Keng Kai Enson, Fang Xinzhuo, Kouta Alexander Ono-Wong, Jayden Tan Yu Zhe",
    summary:
      "A roguelike-inspired Unity game that asks players to think twice before throwing something away.",
    cover: "/assets/images/u2-cover.png",
    writeup: "A Brotato-inspired roguelike that puts you in the perspective of an item about to be discarded. Survive time-based waves of enemies with obstacles, walls, and enemy pathfinding — a wave system that rewards skilled play while staying accessible to newcomers.",
    links: [
    ],
    playNote:
      "This entry has a confirmed Unity WebGL export from the submitted project.",
  },
  {
    slug: "p17",
    title: "BREACH",
    teamCode: "P17",
    track: "Pygame",
    category: "special",
    awards: ["CSIT Prize"],
    team: "Khambhati Moiz Huzefa, Kendrick Slamat, Jerome Loke, Agne Rudhresh Ravichandran",
    summary:
      "A cybersecurity social-deduction game where attackers and defenders race to save or destroy a compromised research lab.",
    cover: "/assets/images/p17-cover.png",
    writeup: "An Among Us-style social-deduction game that teaches cybersecurity. Attackers and defenders play as the imposters and crewmates, racing the clock around a compromised research lab to either save or destroy it — with real-time multiplayer over WebSockets.",
    links: [
      {
        label: "Slides PDF",
        href: `${w}/P17 - CSIT Prize - BREACH/slides/csit prize - p17 - Canva/Breach.pdf`,
      },
    ],
    playNote:
      "Single-player browser build: BREACH is normally real-time multiplayer over a server, so this build runs the same game logic locally in the browser and fills the other two seats with bots (AVA and NOVA). You play one role against the AI \u2014 no server or other players needed.",
  },
  {
    slug: "u16",
    title: "A Day in the Life of a Blind Person",
    teamCode: "U16",
    track: "Unity",
    category: "special",
    awards: ["Most Original Concept"],
    team: "Mao Yuxi, Sara Tan Jia Ning, Maddula Geethika, Cheng Ruitao",
    summary:
      "A 2D platformer RPG about navigating ordinary life from the perspective of someone who is blind.",
    cover: "/assets/images/u16-cover.png",
    writeup: "A 2D platformer RPG that conveys parts of everyday life for someone who is blind. A cane-tap mechanic briefly lights a small circle around you, so you navigate by sound and limited sight through its puzzle-like spaces.",
    links: [
    ],
    playNote:
      "This entry has a confirmed Unity WebGL export from the submitted project.",
  },
  {
    slug: "p14",
    title: "Daily Life Reimagined",
    teamCode: "P14",
    track: "Pygame",
    category: "special",
    awards: ["Most Lines of Code"],
    team: "Va Ramaswami, Mohammad Adnan Khilji, Ng Yek Tiek, Li Chang Wei Eben",
    summary:
      "A collection of minigames that turns waking up, brushing teeth, eating, homework, and sleeping into playful challenges.",
    cover: "/assets/images/p14-cover.png",
    writeup: "A collection of mini-games that turns a normal day — waking up, brushing teeth, eating lunch, doing homework, going to bed — into playful levels, each with a twist like toothpaste monsters or things that come alive in the dark, all tied together by one story.",
    links: [
      {
        label: "Slides PDF",
href: `${w}/P14 - Most Lines of Code - Daily Life Reimagined/slides/most lines of code - p14 - Canva/Building Blocs Game Presentation slides.pdf`,
      },
    ],
    playNote:
      "This entry has a confirmed browser export from the submitted Pygame source.",
  },
  {
    slug: "p1",
    title: "School Subway Surfers",
    teamCode: "P1",
    track: "Pygame",
    category: "special",
    awards: ["Sensory Overload"],
    team: "Aditya Jain, Tsai Rui Jie, Nguyen Ngoc Minh Khang Hamilton, Krish Vishwa Muthia",
    summary:
      "A student-teacher endless runner inspired by Subway Surfers and Mario, changing as the player survives longer.",
    cover: "/assets/images/p1-cover.png",
    writeup: "An endless runner that turns the addictive Subway Surfers / Mario loop into a funny student-teacher chase that escalates the longer you survive, with varied obstacles, a level-progression system, and a magnet power-up.",
    links: [
      {
        label: "Slides PDF",
        href: `${w}/P1 - Sensory Overload - School Subway Surfers/slides/sensory overload - p1 - Canva/Our Pygame Journey with Krish, Hamilton, Rui Jie, and Aditya.pdf`,
      },
      {
        label: "Source README",
        href: `${w}/P1 - Sensory Overload - School Subway Surfers/src/sensory overload - p1 - Drive/README FILE.md`,
      },
    ],
    playNote:
      "This entry has a confirmed browser export from the submitted Pygame source.",
  },
  {
    slug: "p8",
    title: "Bleach Rush",
    teamCode: "P8",
    track: "Pygame",
    category: "special",
    awards: ["Most Silly"],
    team: "Guo Renjun, Kee Heng Jun, Salman Farsi, Hayyan",
    summary:
      "A deliberately unexpected Pygame entry shaped by task ownership, deadlines, and remote coordination.",
    cover: "/assets/images/p8-cover.png",
    writeup: "A deliberately silly Pygame entry: a character navigates a mall to buy bleach for a shirt stain while salespeople block the way. Fight through them in a short, self-aware, retro-styled romp.",
    links: [
      {
        label: "Slides PDF",
        href: `${w}/P8 - Most Silly - Bleach Rush/slides/most silly - p8 - Canva/Pygame_P8.pdf`,
      },
    ],
    playNote:
      "This entry has a confirmed browser export from the submitted Pygame source.",
  },
  {
    slug: "u13",
    title: "TinyExplorer",
    teamCode: "U13",
    track: "Unity",
    category: "special",
    awards: ["Most Overengineered"],
    team: "Chong Sin Yan, Cheah Kai Qian Lucius, Quick Rui Ern, Khoo Hui Ning",
    summary:
      "A plushie-scale Unity adventure through a giant house, inspired by toys coming to life.",
    cover: "/assets/images/u13-cover.png",
    writeup: "A Toy Story-inspired adventure where you play a tiny plushie navigating giant furniture and obstacles to escape the house, testing your critical-thinking and observation skills as you find the path to freedom.",
    links: [
    ],
    playNote:
      "This entry has a confirmed Unity WebGL export from the submitted project.",
  },
];

export const rankedGames = games.filter((game) => game.category === "ranked");
export const specialGames = games.filter((game) => game.category === "special");
