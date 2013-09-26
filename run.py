#!/usr/bin/env python
import os
import sys
from optparse import OptionParser
from nupic_nlp import build_nouns


if 'CEPT_APP_ID' not in os.environ or 'CEPT_APP_KEY' not in os.environ:
  print 'Missing CEPT_APP_ID and CEPT_APP_KEY environment variables.'
  print 'You can retrieve these by registering for the CEPT API at '
  print 'https://cept.3scale.net/'
  quit(-1)

cept_app_id = os.environ['CEPT_APP_ID']
cept_app_key = os.environ['CEPT_APP_KEY']

DEFAULT_MAX_TERMS = 50
DEFAULT_MIN_SPARCITY = 2.0 # percent
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


def main(*args, **kwargs):
  """ NuPIC NLP main entry point. """
  (options, args) = parser.parse_args()
  if options.max_terms.lower() == 'all':
    max_terms = sys.maxint
  else:
    max_terms = int(options.max_terms)
  min_sparcity = float(options.min_sparcity)

  noun_sdrs = build_nouns(max_terms, min_sparcity, cache_dir, 
    cept_app_id, cept_app_key)


if __name__ == "__main__":
  main()
