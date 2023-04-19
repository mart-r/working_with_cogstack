from medcat.cat import MetaCAT
import os
import pandas as pd
import json

import logging
medcat_logger = logging.getLogger('medcat')
fh = logging.FileHandler('medcat.log')
medcat_logger.addHandler(fh)

import sys
sys.path.append('../../')
from credentials import *
from cogstack import CogStack

# Initialise search
cs = CogStack(hosts=hosts, username=username, password=password api=True)

cogsatck_indices = [''] # Enter your list of relevant cogstack indices here

# log size of indices
df = cs.DataFrame(index=cogsatck_indices, columns=['body_analysed'])
medcat_logger.warning(f'The index size is {df.shape[0]}!')
del df

# Initialise the model
model_dir = '../../models/modelpack/'

modelpack = '' # enter your model here. Should be the output of trained 'output_modelpack' from step 2.
model_pack_path = os.path.join(model_dir, modelpack)

snomed_filter_path = None

data_dir = '../../data/'
ann_folder_path = os.path.join(data_dir, f'annotated_docs')
if not os.path.exisits(ann_folder_path):
    os.makedirs(ann_folder_path)

medcat_logger.warning(f'Anntotations will be saved here: {ann_folder_path}')

# Load CAT - the main class from medcat used fro concept annotation
cat = CAT.load_model_pack(model_pack_path)

# Set snomed filter if needed
# This is a white list filter of concepts
if snomed_filter_path:
    snomed_filter = set(json.load(open(snomed_filter_path)))
else:
    snomed_filter = set(cat.cdb.cui2preferred_name.keys())

cat.config.linking['filters']['cuis'] = snomed_filter
del snomed_filter

# build query, change as appropriate
query = {
    "query": {
    "match_all": {}
    },
    "_source":["_id", "body_analysed"]
}

search_gen = cs.get_docs_generator(index=cogsatck_indices, query=query, request_timeout=None)

def relevant_text_gen(generator, doc_id = '_id', text_col='body_analysed'):
    for i in generator:
        try:
            yield (i[doc_id], i['_source'][text_col])
        except KeyError:
            # medcat_logger.warning(f'KeyError {text_col} not found')
            continue

batch_char_size = 500000  # Batch size (BS) in number of characters
cat.multiprocessing(relevant_text_gen(search_gen),
                    batch_char_size=batch_char_size,
                    only_cui=False,
                    nproc=8, # Number of processors
                    save_dir_path=ann_folder_path,
                    )

medcat_logger.warning(f'Annotation process complete!')

