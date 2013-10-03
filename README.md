# NuPIC NLP Experiments

This repo contains my experiments with the using CEPT word SDRs as input into the NuPIC temporal pooler, bypassing the spacial pooler. 

## Requirements

You'll need an app ID and app key from [CEPT](https://cept.3scale.net/) for the usage of their API to get word SDRs and decode SDRs back into words. 

You'll also need about 35MB of space to store the text corpus from the NLTK and SDRs from CEPT.

## Installation

### Python Modules

    pip install git+git://github.com/numenta/pycept.git
    pip install pyyaml
    pip install nltk

### NLTK Download

Before you have the NLTK text corpus available for local processing, you need to download it. See [Installing NLTK Data](http://nltk.org/data.html) for details, but here is the gist:

    >$ python
    >>> import nltk
    >>> nltk.download()

This will bring up a GUI window for you to choose what texts to download. Choose them all and proceed. This will take a few minutes.

### Environment

Set up the following environment variables to contain your CEPT API app id and key:

    export CEPT_APP_ID=<your_id>
    export CEPT_APP_KEY=<your_key>

## Caching

All word SDRs from CEPT are cached by default within a `./cache` directory for easy access later, so the CEPT API is not burdened with repeat calls, and script run times don't get overwhelming. You delete this entire directory, or individually cached files within this directory. Additionally, all of the nouns within the NLTK texts are also cached within `/.cache/texts` so the NLTK texts to not need to be reaccessed.

## Experiments

### Singular and Plural Nouns

The `run_plural_noun_experiment.py` script contains code to extract all the nouns from the corpus contained within the [Python NLTK](http://nltk.org/) and attempt to construct each plural form. It then passes each word pair into the CEPT API to retrieve a [Sparce Distributed Representation (SDR)](https://github.com/numenta/nupic/wiki/Sparse-Distributed-Representations) of it. If this word or its derived plural for is below a sparcity threshold (default 2.0%), it both words are ignored. This means that the either the word(s) are quite uncommon in the English language, or that the derived plural form is malformed (ex: cactus -> cactuses). Each SDR retrieved is cached within a local `./cache` directory within a JSON file. 

After extraction of nouns and conversion into SDRs, each noun will be pushed through NuPIC's temporal pooler as a raw SDR. Singular forms are followed by plural forms, and between each pair, a temporal pooler reset() occurs. After `--prediction-start` terms have been fed into NuPIC's TP (default 1000), predictions from the TP will be sent to the CEPT API to calculate the closest term from SDR.

#### Usage

Just run the script, which will kick off a long process on the first time it's runs. This long process will import all the NLTK texts, extract all the nouns from them, and cache them locally within `./cache/texts`. It will then start looping through them and calling the CEPT API to get their SDRs.

    python run_plural_noun_experiment.py

This will take a very long time, so you might want to try it out by specifying the maximum amount of terms to process:

    python run_plural_noun_experiment.py --max-terms=10

You can also specify the minimun sparcity threshold:

    python run_plural_noun_experiment.py --max-terms=10 --min-sparcity=1.0
   
The NLTK corpus contains somewhere around 6,300 nouns to process, which means over 12K API calls to CEPT for SDRs. The results of each call are cached in the `./cache` directory, so subsequent runs will be much faster, but if you want to run it all in one go, I would suggest you run it overnight and specify `--max-terms=all`.

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


## Things to try:

    ./run_association_experiment.py resources/animals.txt resources/vegetables.txt -p 0 -t 1000

Randomly chooses one term from the animal list, and one from the veggie list. Sends that pair through NuPIC, printing NUPIC's prediction for the second term. Should generally choose plant-based objects for the second term after some training.

    ./run_association_experiment.py resources/associations/x-in-y.csv -p 0 -t 300

Reads an input file of country --> capital associations, and passes them into NuPIC in the same way. Doesn't predict very well until it's seen the entire list once, then it is pretty decent.