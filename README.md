Programs to generate sector data for the RPG _Faster Than Light: Nomad_,
available from DriveThruRPG.com or Lulu.com.

## Dependencies

`nomadsec.py` depends on the `namemaker` library, which you can install like
so:

```
pip install namemaker
```


## `nomadsec.py`

### Usage

```
usage: nomadsec.py [-h] [-n NAMELIST] [-W WIDTH] [-H HEIGHT] [-X START_WIDTH]
                   [-Y START_HEIGHT] [-d {1,2,3,4,5}]
                   [-s {core,settled,conflict,frontier,unexplored}]
                   [-t {ep,lp,em,lm,ea,la,es,ls,ei,li,eg,lg}] [-D] [-o OUTPUT]
                   [-j] [--separator SEPARATOR] [--csv] [--tsv]

Generate a sector for the _FTL: Nomad_ RPG

options:
  -h, --help            show this help message and exit
  -n NAMELIST, --namelist NAMELIST
                        text file providing example names
  -W WIDTH, --width WIDTH
                        number of hexes/parsecs across
  -H HEIGHT, --height HEIGHT
                        number of hexes/parsecs down
  -X START_WIDTH, --start-width START_WIDTH
                        first index across
  -Y START_HEIGHT, --start-height START_HEIGHT
                        first index down
  -d {1,2,3,4,5}, --density {1,2,3,4,5}
                        density of stars (n in 6)
  -s {core,settled,conflict,frontier,unexplored}, --settlement {core,settled,conflict,frontier,unexplored}
                        settlement level of sector
  -t {ep,lp,em,lm,ea,la,es,ls,ei,li,eg,lg}, --tech {ep,lp,em,lm,ea,la,es,ls,ei,li,eg,lg}
                        technology age of sector
  -D, --debug           write debugging info to error stream
  -o OUTPUT, --output OUTPUT
                        output file
  -j, --json            write output as JSON
  --separator SEPARATOR
                        write with the given character as a separator
  --csv                 write as comma-separated values
  --tsv                 write as tab-separated values
```

`NAMELIST` is a simple UTF-8 text file with one sample name per line.
You can use **`namegen.py`** below to generate one, or just get a list of
names from the real-life language of your choice.  If no list is given,
the name generator defaults to an internal list of Greek mythology names.

`-X`, `-Y`, `-W`, and `-H` allow you to start your map indexes at any hex,
and make them any size.  For example, you might want to create a full
*Traveller*-style sector map, in which case you'd set `HEIGHT` to 40 and 
`WIDTH` to 32.  Or maybe you want to do one "subsector" at a time, in which
case you'd leave HEIGHT and WIDTH at their defaults (10 and 8 respectively)
and set -X and -Y to combinations of (1, 9, 17, 22) &times; (1, 11, 21, 31).

The default output conforms to the default format for tables in some dialects
of Markdown, but you can format the file as CSV, TSV (tab-separated values),
pipe-separated values (with `--separator "|"`), any other separator,
*or* as a pretty-printed JSON document for easy consumption by some other
program.  (For example, a program that turns the JSON into a *Traveller*
format that could be fed to <https://travellermap.com/make/poster> ...?)


## `namegen.py`

This helper program generates a list of words to feed into **`nomadsec.py`**.

### Usage

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

### Random Name Generator Grammar Format

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

See the `grammar/*-grammar.json` files in this directory.


## TODO

- Add docstrings.

- Make installable.

- Generate "condensed" sector listing, using abbreviations for:
  - Trade Class
  - Characteristic (maybe)
  - Population (in hundreds, thousands, millions, or billions)
  - Technology Age

- Generate _Traveller_-compatible data files.
