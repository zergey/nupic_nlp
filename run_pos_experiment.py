#!/usr/bin/python

import os

from nupic_nlp import NLTK_Reader
from nupic.frameworks.opf.modelfactory import ModelFactory
import run_pos_model_params

reader = NLTK_Reader(
  input='./resources/text',
  cache_dir='./cache/text', verbosity=NLTK_Reader.INFO
)
moby_dick = 'melville-moby_dick.txt'
paradise_lost = 'milton-paradise.txt'
bible = 'bible-kjv.txt'
poems = 'blake-poems.txt'
ugly = '01_the_ugly_duckling.txt'
thor_hammer = '06_how_thor_got_the_hammer.txt'

target_text = thor_hammer
simple_tags = True
output_dir = 'output'

if not os.path.exists(output_dir):
  os.mkdir(output_dir)

output_file_path = os.path.join(output_dir, 'pos_out_' + target_text)

# reader.text_report()
# print reader.get_parts_of_speech(target_text, simplify_tags=simple_tags)
# print reader.get_tag_decriptions()

model = ModelFactory.create(run_pos_model_params.MODEL_PARAMS)
model.enableInference({'predictedField': 'pos'})

def report(output):
  print '%15s (%20s %20s)' % tuple(output)

# Clear the output file with a header.
with open(output_file_path, 'w') as output_file:
  output_file.write('input pos predicted_pos\n')

# Append each result to output file.
with open(output_file_path, 'a') as output_file:
  last_prediction = None
  for sentence in reader.get_tagged_sentences(target_text, simplify_tags=simple_tags):
    for tag in sentence:
      word = tag[0]
      pos = tag[1]
      model_input = { 'pos': pos }
      result = model.run(model_input)
      line_out = (word, reader.describe_tag(pos)[0], last_prediction)
      output_file.write('%s|%s|%s\n' % line_out)
      report(line_out)
      best_prediciton = result.inferences['multiStepBestPredictions'][1]
      last_prediction = reader.describe_tag(best_prediciton)[0]



