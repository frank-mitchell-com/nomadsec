Programs to generate sector data for _Faster Than Light: Nomad_.
As of this writing, the format is somewhat idiosyncratic.
Conversion to <https://travellermap.com/make/poster> formats are for the
future.

## Usage

```
usage: nomadsec.py [-h] [-x WIDTH] [-y HEIGHT] [-d {1,2,3,4,5}] [-l LENGTH]
                   namefile

Generate a sector for the _FTL: Nomad_ RPG

positional arguments:
  namefile              JSON file specifying random name generator

options:
  -h, --help            show this help message and exit
  -x WIDTH, --width WIDTH
                        number of hexes/parsecs across
  -y HEIGHT, --height HEIGHT
                        number of hexes/parsecs down
  -d {1,2,3,4,5}, --density {1,2,3,4,5}
                        density of stars (n in 6)
  -l LENGTH, --length LENGTH
                        maximum length of star names
```

### Random Name Generator Format

The Random Name Generator constructs a name as a sequence of *syllables*.
Each name generator specification is a single JSON Object with the following
keys:

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

- Generate _Nomad_ planets?
  - Distinguish stars and planets?
  - Inputs:
    - Settlement Level (if not random)
    - Prevailing Technology Age
  - Outputs:
    - Trade Class
    - Physical Characteristic (fn of Trade Class & random roll)
    - Population (fn of Trade Class and random roll)
    - Technology Age (fn of Prevailing if given & random roll)
    - World Tag 1 (random)
    - World Tag 2 (random)