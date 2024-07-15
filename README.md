Programs to generate sector data for the RPG _Faster Than Light: Nomad_,
available from DriveThruRPG.com or Lulu.com.

As of this writing, the format is somewhat idiosyncratic.
Conversion to <https://travellermap.com/make/poster> formats are for the
future.

## Dependencies

`nomadsec.py` depends on the `namemaker` library, which you can install like
so:

```
pip install namemaker
```

## Usage

```
usage: nomadsec.py [-h] [-n NAMELIST] [-x WIDTH] [-y HEIGHT] [-d {1,2,3,4,5}]
                   [-l LENGTH]

Generate a sector for the _FTL: Nomad_ RPG

options:
  -h, --help            show this help message and exit
  -n NAMELIST, --namelist NAMELIST
                        text file providing example names
  -x WIDTH, --width WIDTH
                        number of hexes/parsecs across
  -y HEIGHT, --height HEIGHT
                        number of hexes/parsecs down
  -d {1,2,3,4,5}, --density {1,2,3,4,5}
                        density of stars (n in 6)
  -l LENGTH, --length LENGTH
                        maximum length of star names
```

The helper program `namegen` has the following syntax.

```
usage: namegen.py [-h] [-n NUMBER] [-o OUTPUT] namefile

Generate a list of names based on a grammar

positional arguments:
  namefile              JSON file specifying random name generator

options:
  -h, --help            show this help message and exit
  -n NUMBER, --number NUMBER
                        number of names to generate
  -o OUTPUT, --output OUTPUT
                        output file
```

### Random Name Generator Format

The grammars for `namegen.py` constructs a name as a sequence of *syllables*.
Each grammar specification is a single JSON Object with the following keys:

`min_syllables`:
: The minimum number of syllables in a name.

`max_syllables`:
: The maximum number of syllables in a name.

`initial`:
: A List of Strings containing zero or more letters, ideally consonants.

`vowels`
: A List of Strings containing zero or more letters, ideally vowels.

`medial` (optional):
: A List of Strings containing zero or more letters that occur *between*
  `vowels`.  If not given, the code will use the product of 
  `initial` &times; `final`.

`final` (optional):
: A List of Strings containing zero or more letters that occur at the end
  of a name (or a syllable, if `medial` is not given). If `final` is not
  given, it is assumed to be equal to `[""]` (a List of the empty string).

See the `*-names.json` files in this directory.


## TODO

- Add docstrings.

- Package as a wheel.

- Generate _Nomad_ planets?
  - Distinguish stars and planets?
  - Inputs:
    - Settlement Level (if not random)
    - Prevailing Technology Age
  - Outputs:
    - Trade Class (random, modified by Settlement Level)
    - Physical Characteristic (fn of Trade Class & random roll)
    - Population (fn of Trade Class and random roll)
    - Technology Age (fn of Prevailing if given & random roll)
    - World Tag 1 (random)
    - World Tag 2 (random)

- Generate _Traveller_-compatible data files.
