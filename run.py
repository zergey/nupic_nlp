#!/usr/bin/env python
import os
import sys
from optparse import OptionParser
from nupic_nlp import SDR_Builder, Nupic_Word_Client


if 'CEPT_APP_ID' not in os.environ or 'CEPT_APP_KEY' not in os.environ:
  print 'Missing CEPT_APP_ID and CEPT_APP_KEY environment variables.'
  print 'You can retrieve these by registering for the CEPT API at '
  print 'https://cept.3scale.net/'
  quit(-1)

cept_app_id = os.environ['CEPT_APP_ID']
cept_app_key = os.environ['CEPT_APP_KEY']

DEFAULT_MAX_TERMS = '2000'
DEFAULT_MIN_SPARCITY = 2.0 # percent
DEFAULT_PREDICTION_START = 1000
cache_dir = './cache'

parser = OptionParser(usage="%prog [options]")

parser.add_option('-t', '--max-terms',
  default=DEFAULT_MAX_TERMS,
  dest='max_terms',
  help='Maximum terms to process. Specify "all" for to process all available \
terms.')

parser.add_option('-s', '--min-sparcity',
  default=DEFAULT_MIN_SPARCITY,
  dest='min_sparcity',
  help='Minimum SDR sparcity threshold. Any words processed with sparcity lower \
than this value will be ignored.')

parser.add_option('-p', '--prediction-start',
  default=DEFAULT_PREDICTION_START,
  dest='prediction_start',
  help='Start converting predicted values into words using the CEPT API after \
this many values have been seen.')


def convert_nupic_sdr_to_bitmap(sdr):
  out = {'width': 128, 'height': 128, 'positions': []}
  for i, v in enumerate(sdr):
    if int(v) is 1:
      out['positions'].append(i)
  return out


def main(*args, **kwargs):
  """ NuPIC NLP main entry point. """
  (options, args) = parser.parse_args()
  if options.max_terms.lower() == 'all':
    max_terms = sys.maxint
  else:
    max_terms = int(options.max_terms)
  min_sparcity = float(options.min_sparcity)
  prediction_start = int(options.prediction_start)

  builder = SDR_Builder(cept_app_id, cept_app_key, cache_dir)

  noun_bitmaps = builder.build_nouns(max_terms, min_sparcity)

  print '\nPushing %i nouns through NuPIC, predictions will be converted to words \
after %i iterations.' % (len(noun_bitmaps), prediction_start)
  nupic = Nupic_Word_Client()
  count = 1
  last_singular = ''
  output = []
  header_written = False
  for noun in noun_bitmaps:
    noun_sdr = builder.convert_bitmap_to_sdr(noun['bitmap'])
    raw_prediction = nupic.feed(noun_sdr)
    if count < prediction_start and count % 50 is 0:
      print 'nupic has processed %i terms so far...' % count
    if count >= prediction_start:
      if not header_written:
        print 'Starting prediction conversion!'
        print '\n%20s%20s |%20s' % ('SINGULAR', 'PLURAL', 'PREDICTED PLURAL')
        print '------------------------------------------------------------------'
        header_written = True
      prediction_sdr = convert_nupic_sdr_to_bitmap(raw_prediction)
      predicted_word = builder.closest_term(prediction_sdr)
      if not predicted_word: predicted_word = '?'
      if count % 2 is 0:
        # Just processed plural form, so reset
        nupic.reset()
        print '%20s%20s |%20s' \
          % (last_singular, noun['term'], predicted_word)
        output.append({
          'singular': last_singular, 
          'plural': noun['term'], 
          'prediction': predicted_word
        })
      else:
        last_singular = noun['term']

    count += 1

  # print output

if __name__ == "__main__":
  main()
