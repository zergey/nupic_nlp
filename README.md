# NuPIC NLP Experiments

Just stuff I'm messing around with.

### Requirements

You'll need an app ID and app key from [CEPT](https://cept.3scale.net/) for the usage of their API to get word SDRs and decode SDRs back into words. 

You'll also need about 35MB of space to store the text corpus from the NLTK and SDRs from CEPT.

#### Python Modules

- https://github.com/numenta/pycept
- pyyaml
- nltk

## Installation

Set up the following environment variables to contain your CEPT API app id and key:

    export CEPT_APP_ID=<your_id>
    export CEPT_APP_KEY=<your_key>

## Usage

Just run the script, which will kick off a long process on the first time it's run:

    python run.py

After this initial run, a bunch of stuff is cached in the `./cache` directory, so subsequent runs will be much faster.

## Texts and Terms

The texts this program uses are:

- text1: Moby Dick by Herman Melville 1851
- text2: Sense and Sensibility by Jane Austen 1811
- text3: The Book of Genesis
- text4: Inaugural Address Corpus
- text5: Chat Corpus
- text6: Monty Python and the Holy Grail
- text7: Wall Street Journal
- text8: Personals Corpus
- text9: The Man Who Was Thursday by G . K . Chesterton 1908

All the nouns from this corpus of text are extracted using NLTK's `pos_tag` function, looking for words tagged with `NN`. Resulting terms seem to be sometimes mis-categorized, so they are also passed through Wordnet and confirmed to be nouns before sent to CEPT for SDR conversion.