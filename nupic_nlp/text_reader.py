import os
import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus.reader import NOUN
from nltk.tag import pos_tag


def is_noun(word):
  return len(wn.synsets(word, NOUN)) > 0


def filter_nouns(nouns):
  return [ n for n in nouns 
            if len(n) > 3 and len(wn.synsets(n, NOUN)) > 0 ]


def write_cache(path, nouns):
  with open(path, 'w') as f:
    f.write(','.join(nouns))


class Noun_Reader(object):

  def __init__(self, cache_dir):
    self.cache_dir = cache_dir

  TEXTS = {
    'text1': 'Moby Dick by Herman Melville 1851',
    'text2': 'Sense and Sensibility by Jane Austen 1811',
    'text3': 'The Book of Genesis',
    'text4': 'Inaugural Address Corpus',
    'text5': 'Chat Corpus',
    'text6': 'Monty Python and the Holy Grail',
    'text7': 'Wall Street Journal',
    'text8': 'Personals Corpus',
    'text9': 'The Man Who Was Thursday by G . K . Chesterton 1908'
  }



  def get_nouns_from_all_texts(self):
    """Retrieves all nouns from the NLTK corpus of texts."""
    all_nouns = []
    for i in range(1,9):
        all_nouns += self._get_nouns_from_text('text' + str(i))
    # Remove duplicate nouns.
    return list(set(all_nouns))



  def _get_nouns_from_text(self, text):
    name = self.TEXTS[text]
    word_cache = os.path.join(self.cache_dir, 'text')
    nouns = self._find_nouns(text, word_cache)
    return nouns



  def _find_nouns(self, text_name, word_cache):
    cache_dir = word_cache
    cache_file = os.path.join(cache_dir, text_name);
    
    try:
      os.mkdir(cache_dir)
    except Exception:
      pass

    # print 'looking for %s cache' % text_name
    if (os.path.exists(cache_file)):
      nouns = open(cache_file, 'r').read().split(',')
    else:
      # print 'no cache for %s, reading book input from nltk' % text_name
      _tmp = __import__('nltk.book', globals(), locals(), [text_name], -1)
      txt = getattr(_tmp, text_name)
      words = pos_tag(txt.vocab().keys())
      nouns = [ word for word, pos in words 
                if len(word) > 2 and pos == 'NN' and is_noun(word) ]
      write_cache(cache_file, nouns)

    return nouns

