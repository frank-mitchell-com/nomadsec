Programs to generate sector data for the RPG _Faster Than Light: Nomad_,
available from DriveThruRPG.com.

## Dependencies

`nomadsec.py` depends on the `namemaker` library, which you can install like
so:

```
pip install namemaker
```


## `nomadsec.py`

### Usage

```
usage: nomadsec.py [-h] [-n NAMELIST] [-x EXCLUDE_LIST] [-W WIDTH] [-H HEIGHT]
                   [-X START_WIDTH] [-Y START_HEIGHT] [-d {1,2,3,4,5}]
                   [-s {core,settled,conflict,frontier,unexplored}]
                   [-t {ep,lp,em,lm,ea,la,es,ls,ei,li,eg,lg}] [-D] [-o OUTPUT]
                   [-a] [-j] [--separator SEPARATOR] [--csv] [--tsv]

Generate a sector for the _FTL: Nomad_ RPG

options:
  -h, --help            show this help message and exit
  -n NAMELIST, --namelist NAMELIST
                        text file providing example names
  -x EXCLUDE_LIST, --exclude-list EXCLUDE_LIST
                        text file providing names NOT to use
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
  -a, --abbreviate      abbreviate common strings in default format
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


## `csv2trav.py`

This script converts CSV data created by **`nomadsec.py`** into the
GEnie format used by _Traveller_-based sector mapping applications such as
<https://travellermap.com/make/poster>.

```
usage: csv2trav.py [-h] [-j] inputfile outputfile

Parse `nomadsec.py` data into _Traveller_ GEnie format

positional arguments:
  inputfile   file containing `nomadsec.py` data
  outputfile  file to contain _Traveller_ GEnie data

options:
  -h, --help  show this help message and exit
  -j, --json  read as JSON data
```

Despite the name it can also read tab-separated values, pipe-separated values,
or (with the `-j` flag) JSON data.  (It can't read the default format yet.)
The output file can be dragged and dropped directly into Poster Maker's
"sector data" text box, and you can make an accurate if boring map.

The script translates _Nomad_ parameters into passable numbers for the GEnie
format: the Universal Planet Profile (UPP), trade codes, and PBG (population,
bases, gas giants).  It also generates zone restrictions based on certain
_Nomad_ World Tags.  The translation is far from perfect: _Nomad_ has no
equivalent to "Scout Bases" or "Naval Bases", for example.  Still, it should
make a map from <https://travellermap.com/make/poster> more interesting than
plain dots and names.


## `text2csv.py`

This script converts the default text format (or permutations thereof) into
a CSV suitable for `csv2trav.py`:

```
usage: text2csv.py [-h] inputfile outputfile

Parse `nomadsec.py` plain text data into a CSV

positional arguments:
  inputfile   file containing `nomadsec.py` default text
  outputfile  file to contain CSV data

options:
  -h, --help  show this help message and exit
```

It cleans up most permutations of the pipe-delimited text file, but it still
has some data it cannot clean up.


## TODO

- Add docstrings.

- Make installable.
