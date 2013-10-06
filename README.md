# NuPIC NLP Experiments

This repo contains my Natural Language Processing (NLP) experiments with [NuPIC](http://numenta.org/nupic.html). Some of them are using CEPT word SDRs as input into the NuPIC temporal pooler, bypassing the spacial pooler. Others are simply using the Python Natural Language Tool Kit (NLTK) and parts of speech tagging.

## Requirements

For some experiments, you'll need an app ID and app key from [CEPT](https://cept.3scale.net/) for the usage of their API to get word SDRs and decode SDRs back into words. 

You'll also need 35MB (or more depending on what individual experiments you run) of space to store the text corpus from the NLTK and SDRs from CEPT.

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

### Word Association

The `run_association_experiment.py` script is a generic script to read input files with word associations and pass them into NuPIC one after the other in an attempt to see if NuPIC will properly associate the semantics encoded with their SDRs.

#### Usage

    ./run_association_experiment.py [input file(s)] [options]

If one input file is specified, it's assumed that there is a hard-coded association on each line of the file, in this format:

    term-a1,term-b1
    term-a2,term-b2
    <etc>

See an example in `resources/animal_food.csv`.

If two input files are specified, a it's assumed that each file has a topical grouping, and associations will be randomly passed into NuPIC from each file. For example, take a look at `resources/animals.txt` and `resources/vegetables.txt`.

    ./run_association_experiment.py resources/animals.txt resources/vegetables.txt -p 100 -t 1000

In the example above, a random term from the animals text is associated with another random term in the vegetables text, and this pair is passed into NuPIC 1000 times. NuPIC's predicted SDRs are passed back into the CEPT API and printed to the screen after 100 iterations. (See options below for details on the `-p` and `-t` options.)

Here is an example of the output you'll get from running the above command:

    $ ./run_association_experiment.py resources/animals.txt resources/vegetables.txt -p 100 -t 1000
    Prediction output for 1000 pairs of terms

    #COUNT        TERM ONE        TERM TWO | TERM TWO PREDICTION
    --------------------------------------------------------------------
    #  100          salmon          endive |              lentil
    #  101       crocodile          borage |
    #  102            wolf        turmeric |            amaranth
    #  103         termite       chickweed |
    #  104           quail            poke |
    #  105      woodpecker         shallot |
    #  106         echidna           caper |              tomato
    #  107         panther            guar |
    #  108             ape       tomatillo |       chrysanthemum
    #  109             bee         cabbage |
    #  110        seahorse          sorrel |
    #  111           camel       tomatillo |          lemongrass
    #  112             rat          chives |
    #  113            crab             yam |              turnip

If the word association is understood by NuPIC, the predictions should be within the same topical category of the second file. NuPIC should even predict words that are not within the original term listing.

##### Options

    --verbose
    -v

Prints details about CEPT API calls and minimum sparsity errors.

    --max-terms=<int>
    -t <int>

How many total terms to run. Stops after reaching this limit. If `all` is specified instead of an integer value, it will run indefinitely.

    --min-sparsity=<float>
    -s <float>

Required SDR sparsity, in percent, for terms to be included. This omits uncommon words from the process. The lower the sparsity, the less words get processed. CEPT will return anywhere from 1.0% to 5.0% sparse representations. The default for this value is 0.0%.

    --prediction-start=<int>
    -p <int>

When to start sending the predicted SDRs from NuPIC back to the CEPT API to translate back into English words. This adds overhead because of the HTTP calls, and initial results will probably be bad. So setting this a bit into your term list is a good idea if you want to time-box the process.

### Singular and Plural Nouns

> This really doesn't work at all. NuPIC doesn't predict anything. It was my first experiment, and I made the assumption that singular and plural semantic information was inherent in the CEPT SDRs, but it seems they are not. I am leaving it as an example of how you might extract text from the NLTK corpus and push through NuPIC.

The `run_plural_noun_experiment.py` script contains code to extract all the nouns from the corpus contained within the [Python NLTK](http://nltk.org/) and attempt to construct each plural form. It then passes each word pair into the CEPT API to retrieve a [Sparce Distributed Representation (SDR)](https://github.com/numenta/nupic/wiki/Sparse-Distributed-Representations) of it. If this word or its derived plural for is below a sparsity threshold (default 2.0%), it both words are ignored. This means that the either the word(s) are quite uncommon in the English language, or that the derived plural form is malformed (ex: cactus -> cactuses). Each SDR retrieved is cached within a local `./cache` directory within a JSON file. 

After extraction of nouns and conversion into SDRs, each noun will be pushed through NuPIC's temporal pooler as a raw SDR. Singular forms are followed by plural forms, and between each pair, a temporal pooler reset() occurs. After `--prediction-start` terms have been fed into NuPIC's TP (default 1000), predictions from the TP will be sent to the CEPT API to calculate the closest term from SDR.

#### Usage

Just run the script, which will kick off a long process on the first time it's runs. This long process will import all the NLTK texts, extract all the nouns from them, and cache them locally within `./cache/texts`. It will then start looping through them and calling the CEPT API to get their SDRs.

    ./run_plural_noun_experiment.py [options]

##### Options

    --verbose
    -v

Prints details about CEPT API calls and minimum sparsity errors.

    --max-terms=<int>
    -t <int>

How many total terms to run. Stops after reaching this limit. If `all` is specified instead of an integer value, it will run indefinitely.

    --min-sparsity=<float>
    -s <float>

Required SDR sparsity, in percent, for terms to be included. This omits uncommon words from the process. The lower the sparsity, the less words get processed. CEPT will return anywhere from 1.0% to 5.0% sparse representations. The default for this value is 0.0%.

    --prediction-start=<int>
    -p <int>

When to start sending the predicted SDRs from NuPIC back to the CEPT API to translate back into English words. This adds overhead because of the HTTP calls, and initial results will probably be bad. So setting this a bit into your term list is a good idea if you want to time-box the process.

##### Examples

Running without any options will take a very long time, so you might want to try it out by specifying the maximum amount of terms to process:

    python run_plural_noun_experiment.py --max-terms=10

You can also specify the minimun sparsity threshold:

    python run_plural_noun_experiment.py --max-terms=10 --min-sparsity=1.0
   
The NLTK corpus contains somewhere around 6,300 nouns to process, which means over 12K API calls to CEPT for SDRs. The results of each call are cached in the `./cache` directory, so subsequent runs will be much faster, but if you want to run it all in one go, I would suggest you run it overnight and specify `--max-terms=all`.

### Parts of Speech

This script does not use CEPT. It parses the input text(s) specified inside the script and breaks each sentence into POS (Parts of Speech) tags. These tags are fed into NuPIC using a [category encoder](https://github.com/numenta/nupic/wiki/Encoders), and each next POS is predicted. Output is written to the console as well as an output file in the `output` directory.

#### Usage

    ./run_pos_experiment.py

#### Example Output

Here is some example output for Thor's Hammer (`06_how_thor_got_the_hammer`):

        The (          determiner              pronoun)
        fly (              adverb                 noun)
        bit (                noun          proper noun)
         me (             pronoun                    .)
         so (              adverb                 noun)
       hard (              adverb          proper noun)
       that (         preposition          proper noun)
          I (             pronoun           determiner)
        had (          past tense                 noun)
         to (         the word to          preposition)
       stop (                verb                 verb)
    blowing (                noun               adverb)
          . (                   .                    .)

As you can see from this sample output, there are problems with NLTK's POS tagging. For example, `bit` is mis-categorized as a noun, when it is used as a past-tense verb. When the input is incorrect, it is harder for NuPIC to predict correctly. You might also note, however, that NuPIC does predict the end of the sentence correctly. 

Grammar trees are difficult to predict, even for humans. At any point in the tree, the sentence could branch into multiple directions. Turning this experiment into an anomaly detection problem could provide more valuable results.

## Texts and Terms

All the nouns processed from this corpus of text by the `run_plural_noun_experiment.py` experiment are extracted using NLTK's `pos_tag` function, looking for words tagged with `NN`. Resulting terms seem to be sometimes mis-categorized, so they are also passed through Wordnet and confirmed to be nouns before sent to CEPT for SDR conversion.

## Things to try:

    ./run_association_experiment.py resources/animals.txt resources/vegetables.txt -p 0 -t 1000

Randomly chooses one term from the animal list, and one from the veggie list. Sends that pair through NuPIC, printing NUPIC's prediction for the second term. Should generally choose plant-based objects for the second term after some training.

    ./run_association_experiment.py resources/associations/x-in-y.csv -p 0 -t 300

Reads an input file of country --> capital associations, and passes them into NuPIC in the same way. Doesn't predict very well until it's seen the entire list once, then it is pretty decent.
