#!/usr/bin/env python
import os
import sys
import string
from random import choice
from optparse import OptionParser
from nupic_nlp import Noun_Reader, SDR_Builder, Nupic_Word_Client


if 'CEPT_APP_ID' not in os.environ or 'CEPT_APP_KEY' not in os.environ:
  print 'Missing CEPT_APP_ID and CEPT_APP_KEY environment variables.'
  print 'You can retrieve these by registering for the CEPT API at '
  print 'https://cept.3scale.net/'
  quit(-1)

cept_app_id = os.environ['CEPT_APP_ID']
cept_app_key = os.environ['CEPT_APP_KEY']

DEFAULT_MAX_TERMS = '100'
DEFAULT_MIN_sparsity = 2.0 # percent
DEFAULT_PREDICTION_START = 1000
cache_dir = './cache'

parser = OptionParser(usage="%prog input_file [options]")

parser.add_option('-t', '--max-terms',
  default=DEFAULT_MAX_TERMS,
  dest='max_terms',
  help='Maximum terms to process. Specify "all" for to process all available \
terms.')

parser.add_option('-s', '--min-sparsity',
  default=DEFAULT_MIN_sparsity,
  dest='min_sparsity',
  help='Minimum SDR sparsity threshold. Any words processed with sparsity lower \
than this value will be ignored.')

parser.add_option('-p', '--prediction-start',
  default=DEFAULT_PREDICTION_START,
  dest='prediction_start',
  help='Start converting predicted values into words using the CEPT API after \
this many values have been seen.')


def read_words_from(file):
  lines = open(file).read().strip().split('\n')
  return [tuple(line.split(',')) for line in lines]


def feed_term(sdr_builder, nupic_client, term, get_predicted_word=False):
  raw_sdr = sdr_builder.term_to_sdr(term)
  sdr_array = sdr_builder.convert_bitmap_to_sdr(raw_sdr)
  predicted_bitmap = nupic_client.feed(sdr_array)
  output_sparsity = float(len(predicted_bitmap)) / (float(raw_sdr['width']) * float(raw_sdr['height'])) * 100.0
  # print 'Sparcity %s:prediction ==> %.2f%%: %.2f%%' % (term, raw_sdr['sparsity'], output_sparsity)
  if get_predicted_word:
    if len(predicted_bitmap) is 0:
      predicted_word = 'Unknown'
    else:
      predicted_word = sdr_builder.closest_term(predicted_bitmap)
    return predicted_word


def strip_punctuation(s):
  return s.translate(string.maketrans("",""), string.punctuation)


def main(*args, **kwargs):
  """ NuPIC NLP main entry point. """
  (options, args) = parser.parse_args()
  if options.max_terms.lower() == 'all':
    max_terms = sys.maxint
  else:
    max_terms = int(options.max_terms)
  min_sparsity = float(options.min_sparsity)
  prediction_start = int(options.prediction_start)

  if len(args) is 0:
    print 'no input file provided!'
    exit(1)

  input_file = args[0]

  # Create the cache directory if necessary.
  if not os.path.exists(cache_dir):
    os.mkdir(cache_dir)

  associations = read_words_from(input_file)

  builder = SDR_Builder(cept_app_id, cept_app_key, cache_dir)
  nupic = Nupic_Word_Client()


  for count in range(0, max_terms):
    # Loops over association list until max_terms is met
    if count >= len(associations):
      associations += associations
    term1 = strip_punctuation(associations[count][0])
    term2 = strip_punctuation(associations[count][1])
    show_predicted_word = (count >= prediction_start)
    term2_prediction = feed_term(builder, nupic, term1, show_predicted_word)
    feed_term(builder, nupic, term2)
    if show_predicted_word:
      if term2_prediction is not 'Unknown':
        print u'#%i: %s - > %s (%s)' % (count, term1, term2, term2_prediction)
    else:
      print count
    nupic.reset()



if __name__ == "__main__":
  main()
