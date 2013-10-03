#!/usr/bin/env python
import os
import sys
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

parser = OptionParser(usage="%prog [options]")

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
  return open(file).read().strip().split('\n')


def feed_term(sdr_builder, nupic_client, term):
  # print term
  raw_sdr = sdr_builder.term_to_sdr(term)
  # print raw_sdr
  # print raw_sdr
  sdr_array = sdr_builder.convert_bitmap_to_sdr(raw_sdr)
  # print sdr_array
  predicted_bitmap = nupic_client.feed(sdr_array)
  output_sparsity = float(len(predicted_bitmap)) / (float(raw_sdr['width']) * float(raw_sdr['height'])) * 100.0
  # print predicted_sdr
  # print ''.join([str(int(x)) for x in predicted_sdr])
  # predicted_bitmap = sdr_builder.convert_sdr_to_bitmap(predicted_sdr)
  print 'Sparcity %s:prediction ==> %.2f%%: %.2f%%' % (term, raw_sdr['sparsity'], output_sparsity)
  # print predicted_bitmap
  if len(predicted_bitmap) is 0:
    predicted_word = 'Unknown'
  else:
    predicted_word = sdr_builder.closest_term(predicted_bitmap)
  # print predicted_word
  # print '%s ==> %s' % (term, predicted_word)
  return predicted_word



def main(*args, **kwargs):
  """ NuPIC NLP main entry point. """
  (options, args) = parser.parse_args()
  if options.max_terms.lower() == 'all':
    max_terms = sys.maxint
  else:
    max_terms = int(options.max_terms)
  min_sparsity = float(options.min_sparsity)
  prediction_start = int(options.prediction_start)

  # Create the cache directory if necessary.
  if not os.path.exists(cache_dir):
    os.mkdir(cache_dir)

  animals = read_words_from('./resources/animals.txt')
  vegs = read_words_from('./resources/vegetables.txt')

  builder = SDR_Builder(cept_app_id, cept_app_key, cache_dir)
  nupic = Nupic_Word_Client()

  for count in range(0, int(max_terms / 2)):
    animal = choice(animals)
    veg = choice(vegs)
    after_animal = feed_term(builder, nupic, animal)
    after_veg = feed_term(builder, nupic, veg)
    if after_animal is not 'Unknown':
      print u'#%i: %s - > %s (%s)' % (count, animal, veg, after_animal)
    nupic.reset()



if __name__ == "__main__":
  main()
