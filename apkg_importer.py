#!/usr/bin/python3

import sys
sys.path.append("/usr/share/anki")
import anki, aqt
from anki.exporting import AnkiPackageExporter
from anki.importing import AnkiPackageImporter
import csv
import pathlib
import random
import re
import requests

DOCS_PATH = '/home/cowley/Documents/'
TMP_PATH = '/tmp/'
APKG_PATH = DOCS_PATH + 'accelerated_spanish_empty.apkg'
CSV_PATH = DOCS_PATH + 'spanish5.csv'
TMP_COL_PATH = TMP_PATH
DECK_NAME = 'accelerated spanish'
DECK_ID = None #1518389138178
MODEL_NAME = 'Basic'
QUESTION_FIELD = 'Front'
ANSWER_FIELD = 'Back'
MEDIA_PATH = '/home/cowley/.local/share/Anki2/User 1/collection.media/'

with open(CSV_PATH) as f:
    reader = csv.reader(f, delimiter='\t')

    collection = anki.Collection(TMP_COL_PATH + str(random.randint(10**9, 10**10)) + '.anki2')
    api = AnkiPackageImporter(collection, APKG_PATH)
    api.run()

    collection = api.col

    # get deck
    try:
        deck_id = collection.decks.id(DECK_NAME)
    except:
        print('invalid deck name')
        raise
    collection.decks.select(deck_id)

    # get model to use
    try:
        model = collection.models.byName(MODEL_NAME)
    except:
        print('invalid model name', model_name_to_model.keys())
        raise

    # set deck id
    model['did'] = deck_id
    if DECK_ID:
        model['did'] = DECK_ID
    collection.models.setCurrent(model)
    collection.models.save(model)

    for row in reader:
        try:
            a, q = row[0], row[1]
            if not q:
                q = row[2]
        except:
            print('unable to print row:', row)
            continue

        # do we need additional media?
        # if so, download it to the media directory
        if q.startswith('http'):
            url = q
            q = re.search('[^/]*$', q)[0]
            # no need to download if file already exists
            if not pathlib.Path(MEDIA_PATH + q).is_file():
                q_f = open(MEDIA_PATH + q, 'wb')
                print("Downloading", url)
                q_f.write(requests.get(url).content)
                q_f.close()

        if (q.endswith('.jpg') or q.endswith('.jpeg') or
            q.endswith('.png') or q.endswith('.gif')):
            q = '<img src="' + q + '">'

        if q.endswith('.mp3'):
            q = '[sound:' + q + ']'

        note = anki.notes.Note(collection, model)

        note[QUESTION_FIELD] = q
        note[ANSWER_FIELD] = a
        note.guid = abs(hash(q))

        collection.addNote(note)

    export = AnkiPackageExporter(collection)
    export.exportInto(DOCS_PATH + 'out.apkg')
