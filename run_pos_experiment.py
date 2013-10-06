#!/usr/bin/python

from nupic_nlp import NLTK_Reader
from nupic.frameworks.opf.modelfactory import ModelFactory
import run_pos_model_params

max_sents = 1000

reader = NLTK_Reader(cache_dir='./cache/text', verbosity=NLTK_Reader.INFO)
moby_dick = 'melville-moby_dick.txt'
paradise_lost = 'milton-paradise.txt'
bible = 'bible-kjv.txt'
poems = 'blake-poems.txt'

target_text = paradise_lost

# reader.text_report()
# print reader.get_parts_of_speech(target_text)

model = ModelFactory.create(run_pos_model_params.MODEL_PARAMS)
model.enableInference({'predictedField': 'pos'})

max_output = 5
output = []
for x in range(0, max_output):
  output.append(('','',''))

def report(output):
  format = '%15s (%5s %5s)' * len(output)
  fmt_out = []
  for w in output:
    fmt_out += list(w)
  print format % tuple(fmt_out)

with open('pos_out_' + target_text, 'w') as output_file:
  output_file.write('input,pos,predicted_pos\n')

with open('pos_out_' + target_text, 'a') as output_file:
  output_file.write('input,pos,predicted_pos\n')
  last_prediction = None
  for sentence in reader.get_tagged_sentences(target_text, exclude_punctuation=False):
    for tag in sentence:
      word = tag[0]
      pos = tag[1]
      output.append((word, pos, last_prediction))
      if len(output) > max_output:
        output.pop(0)
      model_input = { 'pos': pos }
      result = model.run(model_input)
      output_file.write('%s %s %s\n' % (word, pos, last_prediction))
      best_prediciton = result.inferences['multiStepBestPredictions'][1]
      last_prediction = best_prediciton
      report(output)



