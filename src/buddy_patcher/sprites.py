"""ASCII sprite data for companion preview — ported from buddy/sprites.ts."""

from buddy_patcher.types import Eyes, Hat, Species

# Each sprite is 5 lines tall, 12 wide (after {E}->1char substitution).
# Multiple frames per species for idle fidget animation.
# Line 0 is the hat slot — must be blank in frames 0-1; frame 2 may use it.
BODIES: dict[Species, list[list[str]]] = {
    Species.DUCK: [
        [
            "            ",
            "    __      ",
            "  <({E} )___  ",
            "   (  ._>   ",
            "    `--´    ",
        ],
        [
            "            ",
            "    __      ",
            "  <({E} )___  ",
            "   (  ._>   ",
            "    `--´~   ",
        ],
        [
            "            ",
            "    __      ",
            "  <({E} )___  ",
            "   (  .__>  ",
            "    `--´    ",
        ],
    ],
    Species.GOOSE: [
        [
            "            ",
            "     ({E}>    ",
            "     ||     ",
            "   _(__)_   ",
            "    ^^^^    ",
        ],
        [
            "            ",
            "    ({E}>     ",
            "     ||     ",
            "   _(__)_   ",
            "    ^^^^    ",
        ],
        [
            "            ",
            "     ({E}>>   ",
            "     ||     ",
            "   _(__)_   ",
            "    ^^^^    ",
        ],
    ],
    Species.BLOB: [
        [
            "            ",
            "   .----.   ",
            "  ( {E}  {E} )  ",
            "  (      )  ",
            "   `----´   ",
        ],
        [
            "            ",
            "  .------.  ",
            " (  {E}  {E}  ) ",
            " (        ) ",
            "  `------´  ",
        ],
        [
            "            ",
            "    .--.    ",
            "   ({E}  {E})   ",
            "   (    )   ",
            "    `--´    ",
        ],
    ],
    Species.CAT: [
        [
            "            ",
            "   /\\_/\\    ",
            "  ( {E}   {E})  ",
            "  (  ω  )   ",
            '  (")_(")   ',
        ],
        [
            "            ",
            "   /\\_/\\    ",
            "  ( {E}   {E})  ",
            "  (  ω  )   ",
            '  (")_(")~  ',
        ],
        [
            "            ",
            "   /\\-/\\    ",
            "  ( {E}   {E})  ",
            "  (  ω  )   ",
            '  (")_(")   ',
        ],
    ],
    Species.DRAGON: [
        [
            "            ",
            "  /^\\  /^\\  ",
            " <  {E}  {E}  > ",
            " (   ~~   ) ",
            "  `-vvvv-´  ",
        ],
        [
            "            ",
            "  /^\\  /^\\  ",
            " <  {E}  {E}  > ",
            " (        ) ",
            "  `-vvvv-´  ",
        ],
        [
            "   ~    ~   ",
            "  /^\\  /^\\  ",
            " <  {E}  {E}  > ",
            " (   ~~   ) ",
            "  `-vvvv-´  ",
        ],
    ],
    Species.OCTOPUS: [
        [
            "            ",
            "   .----.   ",
            "  ( {E}  {E} )  ",
            "  (______)  ",
            "  /\\/\\/\\/\\  ",
        ],
        [
            "            ",
            "   .----.   ",
            "  ( {E}  {E} )  ",
            "  (______)  ",
            "  \\/\\/\\/\\/  ",
        ],
        [
            "     o      ",
            "   .----.   ",
            "  ( {E}  {E} )  ",
            "  (______)  ",
            "  /\\/\\/\\/\\  ",
        ],
    ],
    Species.OWL: [
        [
            "            ",
            "   /\\  /\\   ",
            "  (({E})({E}))  ",
            "  (  ><  )  ",
            "   `----´   ",
        ],
        [
            "            ",
            "   /\\  /\\   ",
            "  (({E})({E}))  ",
            "  (  ><  )  ",
            "   .----.   ",
        ],
        [
            "            ",
            "   /\\  /\\   ",
            "  (({E})(-))  ",
            "  (  ><  )  ",
            "   `----´   ",
        ],
    ],
    Species.PENGUIN: [
        [
            "            ",
            "  .---.     ",
            "  ({E}>{E})     ",
            " /(   )\\    ",
            "  `---´     ",
        ],
        [
            "            ",
            "  .---.     ",
            "  ({E}>{E})     ",
            " |(   )|    ",
            "  `---´     ",
        ],
        [
            "  .---.     ",
            "  ({E}>{E})     ",
            " /(   )\\    ",
            "  `---´     ",
            "   ~ ~      ",
        ],
    ],
    Species.TURTLE: [
        [
            "            ",
            "   _,--._   ",
            "  ( {E}  {E} )  ",
            " /[______]\\ ",
            "  ``    ``  ",
        ],
        [
            "            ",
            "   _,--._   ",
            "  ( {E}  {E} )  ",
            " /[______]\\ ",
            "   ``  ``   ",
        ],
        [
            "            ",
            "   _,--._   ",
            "  ( {E}  {E} )  ",
            " /[======]\\ ",
            "  ``    ``  ",
        ],
    ],
    Species.SNAIL: [
        [
            "            ",
            " {E}    .--.  ",
            "  \\  ( @ )  ",
            "   \\_`--´   ",
            "  ~~~~~~~   ",
        ],
        [
            "            ",
            "  {E}   .--.  ",
            "  |  ( @ )  ",
            "   \\_`--´   ",
            "  ~~~~~~~   ",
        ],
        [
            "            ",
            " {E}    .--.  ",
            "  \\  ( @  ) ",
            "   \\_`--´   ",
            "   ~~~~~~   ",
        ],
    ],
    Species.GHOST: [
        [
            "            ",
            "   .----.   ",
            "  / {E}  {E} \\  ",
            "  |      |  ",
            "  ~`~``~`~  ",
        ],
        [
            "            ",
            "   .----.   ",
            "  / {E}  {E} \\  ",
            "  |      |  ",
            "  `~`~~`~`  ",
        ],
        [
            "    ~  ~    ",
            "   .----.   ",
            "  / {E}  {E} \\  ",
            "  |      |  ",
            "  ~~`~~`~~  ",
        ],
    ],
    Species.AXOLOTL: [
        [
            "            ",
            "}~(______)~{",
            "}~({E} .. {E})~{",
            "  ( .--. )  ",
            "  (_/  \\_)  ",
        ],
        [
            "            ",
            "~}(______){~",
            "~}({E} .. {E}){~",
            "  ( .--. )  ",
            "  (_/  \\_)  ",
        ],
        [
            "            ",
            "}~(______)~{",
            "}~({E} .. {E})~{",
            "  (  --  )  ",
            "  ~_/  \\_~  ",
        ],
    ],
    Species.CAPYBARA: [
        [
            "            ",
            "  n______n  ",
            " ( {E}    {E} ) ",
            " (   oo   ) ",
            "  `------´  ",
        ],
        [
            "            ",
            "  n______n  ",
            " ( {E}    {E} ) ",
            " (   Oo   ) ",
            "  `------´  ",
        ],
        [
            "    ~  ~    ",
            "  u______n  ",
            " ( {E}    {E} ) ",
            " (   oo   ) ",
            "  `------´  ",
        ],
    ],
    Species.CACTUS: [
        [
            "            ",
            " n  ____  n ",
            " | |{E}  {E}| | ",
            " |_|    |_| ",
            "   |    |   ",
        ],
        [
            "            ",
            "    ____    ",
            " n |{E}  {E}| n ",
            " |_|    |_| ",
            "   |    |   ",
        ],
        [
            " n        n ",
            " |  ____  | ",
            " | |{E}  {E}| | ",
            " |_|    |_| ",
            "   |    |   ",
        ],
    ],
    Species.ROBOT: [
        [
            "            ",
            "   .[||].   ",
            "  [ {E}  {E} ]  ",
            "  [ ==== ]  ",
            "  `------´  ",
        ],
        [
            "            ",
            "   .[||].   ",
            "  [ {E}  {E} ]  ",
            "  [ -==- ]  ",
            "  `------´  ",
        ],
        [
            "     *      ",
            "   .[||].   ",
            "  [ {E}  {E} ]  ",
            "  [ ==== ]  ",
            "  `------´  ",
        ],
    ],
    Species.RABBIT: [
        [
            "            ",
            "   (\\__/)   ",
            "  ( {E}  {E} )  ",
            " =(  ..  )= ",
            '  (")__(")  ',
        ],
        [
            "            ",
            "   (|__/)   ",
            "  ( {E}  {E} )  ",
            " =(  ..  )= ",
            '  (")__(")  ',
        ],
        [
            "            ",
            "   (\\__/)   ",
            "  ( {E}  {E} )  ",
            " =( .  . )= ",
            '  (")__(")  ',
        ],
    ],
    Species.MUSHROOM: [
        [
            "            ",
            " .-o-OO-o-. ",
            "(__________)",
            "   |{E}  {E}|   ",
            "   |____|   ",
        ],
        [
            "            ",
            " .-O-oo-O-. ",
            "(__________)",
            "   |{E}  {E}|   ",
            "   |____|   ",
        ],
        [
            "   . o  .   ",
            " .-o-OO-o-. ",
            "(__________)",
            "   |{E}  {E}|   ",
            "   |____|   ",
        ],
    ],
    Species.CHONK: [
        [
            "            ",
            "  /\\    /\\  ",
            " ( {E}    {E} ) ",
            " (   ..   ) ",
            "  `------´  ",
        ],
        [
            "            ",
            "  /\\    /|  ",
            " ( {E}    {E} ) ",
            " (   ..   ) ",
            "  `------´  ",
        ],
        [
            "            ",
            "  /\\    /\\  ",
            " ( {E}    {E} ) ",
            " (   ..   ) ",
            "  `------´~ ",
        ],
    ],
}

HAT_LINES: dict[Hat, str] = {
    Hat.NONE: "",
    Hat.CROWN: "   \\^^^/    ",
    Hat.TOPHAT: "   [___]    ",
    Hat.PROPELLER: "    -+-     ",
    Hat.HALO: "   (   )    ",
    Hat.WIZARD: "    /^\\     ",
    Hat.BEANIE: "   (___)    ",
    Hat.TINYDUCK: "    ,>      ",
}


def render_sprite(species: Species, eye: Eyes, hat: Hat = Hat.NONE, frame: int = 0) -> list[str]:
    """Return rendered ASCII art lines with eye and hat substitutions applied."""
    frames = BODIES[species]
    body = frames[frame % len(frames)]
    lines = [line.replace("{E}", eye.value) for line in body]

    # Replace line 0 with hat if applicable
    if hat != Hat.NONE and not lines[0].strip():
        lines[0] = HAT_LINES[hat]

    # Drop blank hat slot when no hat and all frames have blank line 0
    if not lines[0].strip() and all(not f[0].strip() for f in frames):
        lines = lines[1:]

    return lines
