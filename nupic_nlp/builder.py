import os
import sys
import json
from reader import find_nouns
from reader import texts as input_texts
import pycept


def plural(word):
  if word.endswith('y'):
    return word[:-1] + 'ies'
  elif word[-1] in 'sx' or word[-2:] in ['sh', 'ch']:
    return word + 'es'
  elif word.endswith('an'):
    return word[:-2] + 'en'
  else:
    return word + 's'


def nouns_from_text(text, cache_dir):
  name = input_texts[text]
  word_cache = os.path.join(cache_dir, 'text')
  nouns = find_nouns(text, word_cache)
  return nouns


def write_sdr_cache(cache, path):
  with open(path, 'w') as f:
    f.write(json.dumps(cache))


def is_valid(sdr, min_sparcity):
  return sdr['sparcity'] > min_sparcity


# def get_sdr(term, cept_client, cache_dir):
#   # Create a cache location for each term, where it will either be read in from
#   # or cached within if we have to go to the CEPT API to get the SDR.
#   cache_file = os.path.join(cache_dir, term + '.json')
#   # Get it from the cache if it's there.
#   if os.path.exists(cache_file):
#     cached_sdr = json.loads(open(cache_file).read())
#   # Get it from CEPT API if it's not cached.
#   else:
#     print '\tfetching %s from CEPT API' % term
#     cached_sdr = cept_client.getBitmap(term)
#     if 'sparcity' not in cached_sdr:
#       # attach the sparcity for reference
#       total = float(cached_sdr['width']) * float(cached_sdr['height'])
#       on = len(cached_sdr['positions'])
#       sparcity = round((on / total) * 100)
#       cached_sdr['sparcity'] = sparcity
#     # write to cache
#     with open(cache_file, 'w') as f:
#       f.write(json.dumps(cached_sdr))
#   return cached_sdr


def build_nouns(max_terms, min_sparcity, cache_dir, cept_app_id, cept_app_key):
  
  cept_client = pycept.Cept(cept_app_id, cept_app_key, cache_dir=cache_dir)
  progress_at = int(max_terms / 10)

  # Get the nouns from some of the text corpora included with the NLTK.
  all_nouns = []
  for i in range(1,9):
    all_nouns += nouns_from_text('text' + str(i), cache_dir)

  # Remove duplicate nouns.
  all_nouns = set(all_nouns)

  # We're only processing the least amount of terms, either of the total number
  # of nouns available, or the number the user specified.
  max_terms = min(len(all_nouns), max_terms)

  print 'processing %i nouns...' % max_terms

  # Convert nouns into pairs of singular / plural nouns.
  term_pair = [ (n, plural(n)) for n in all_nouns ]

  # Some won't be adequate, so we'll only keep the good ones.
  valid_nouns = []
  # Just to track how many we've processed.
  terms_processed = 0
  terms_skipped = []

  for item in term_pair:
    # Singular term.
    sterm = item[0]
    # Plural term.
    pterm = item[1]
    # sys.stdout.write('%s, ' % (sterm,))
    sbm = cept_client.getBitmap(sterm) # get_sdr(sterm, cept_client, cache_dir)
    pbm = cept_client.getBitmap(pterm) # get_sdr(pterm, cept_client, cache_dir)

    # Only gather the ones we deem as 'valid'.
    if is_valid(sbm, min_sparcity) and is_valid(pbm, min_sparcity):
      valid_nouns.append({'term': sterm, 'bitmap': sbm})
      valid_nouns.append({'term': pterm, 'bitmap': pbm})
      terms_processed += 1
    else:
      # print '\tsdrs for %s and %s are too sparce, skipping!' % item
      terms_skipped.append(sterm)

    count = terms_processed + len(terms_skipped)
    if count >= max_terms:
      break

    # Print progress
    if count % progress_at == 0:
      print '\n%.0f%% done...' % (float(count) / float(max_terms) * 100)
      print '%i total terms reviewed, %i terms skipped' % (count, len(terms_skipped))

  skipped_out = os.path.join(cache_dir, 'skipped.txt')
  with open(skipped_out, 'w') as f:
    f.write(', '.join(terms_skipped))

  print '\nProcessing complete!'
  print '===================='
  print '* %i nouns and their plural forms were converted to SDRs within the %s directory' \
    % (len(valid_nouns)/2, cache_dir)
  print '* %i terms skipped because of %.1f%% sparcity requirement. These can be reviewed in %s' \
    % (len(terms_skipped), min_sparcity, skipped_out)

  return valid_nouns
