import os
import sys
import json
import pandas as pd

import requests
from requests.exceptions import HTTPError

from oxford import setOxfordKey, getLemmas, formatEntry

KEY_FIELD = 0  # already contains word and must append audio
DEFINITION_FIELD = 1

WHAT_TO_INSERT = "pronunciation"
PRIMARY_SHORTCUT = "ctrl+alt+d"


def insertDefinition():
    # update config

    # Get the word
    word = ""
    try:
        # word = editor.note.fields[0]
        word = "hello"
        if word == "" or word.isspace():
            raise KeyError()  # Purely to jump to the tooltip here
    except (AttributeError, KeyError) as e:
        print("OxfordDefine: No text found in note fields.")
        return

    try:
        wordInfos = formatEntry(word)
        if not wordInfos:
            raise HTTPError()  # jump to exception handling
    except HTTPError as e:
        try:
            lemmas = getLemmas(word)
            wordInfos = formatEntry(lemmas[0])
        except (HTTPError, KeyError) as e:
            print(f"OxfordDefine: Could not root words for {word}.")
            return

    # Format word
    definition = ""
    soundURLs = set()
    for result in wordInfos['results']:
        for lexical in result:
            ########## Definition format ##########
            definition += '<hr>'
            definition += '<b>' + lexical['lexicalCategory'] + '.</b><br>'
            for entry in lexical['entries']:
                if "pronunciations" in entry:  # sounds saved for later
                    soundURLs.update(entry["pronunciations"])

                for sense in entry['senses']:
                    definition += '<p>'
                    definition += '<br>'.join(sense['definitions']) + '<br>'
                    if 'example' in sense:
                        definition += '<b>e.g.</b> ' + '"' + sense['example'] + '"' + '<br>'
                    if 'notes' in entry:
                        definition += '<b>notes:</b> ' + '<br>'.join(entry['notes']) + '<br>'
                    definition += '</p>'

                if 'etymologies' in entry:
                    definition += '<h5>Origins:</h5> '
                    definition += '<br>'.join(entry['etymologies']) + '<br>'
                if 'notes' in entry:
                    definition += '<h5>Notes:</h5> '
                    definition += '<br>'.join(entry['notes']) + '<br>'
            if 'derivatives' in lexical:
                definition += '<h5>Derivatives:</h5> '
                definition += '<br>'.join(lexical['derivatives']) + '<br>'

    ############# Output ##############
    sounds = [url.strip() for url in soundURLs]

    for sound_url in sounds:
        response = requests.get(sound_url)
        with open(f'{word}.mp3', 'wb') as file:
            file.write(response.content)


def csvOperations():
    # read csv file
    df = pd.read_csv("blabla.csv", delimiter='\t')
    # print(df)

    words = list(df["Word"][3:])
    print(words[0])

    # sounds = list(df["Unnamed: 11"][3:])
    # print(sounds[0])

    df.loc[3, "Audio"] = "[bla bla]"
    print(df["Audio"][3])
    df.to_csv("blabla.csv", sep='\t', index=False)

# setting header names
# headers = ['', 'ID', 'Word', 'Definition', 'Class', 'Register', 'CEFR Level', 'IPA', 'Image', 'Example', 'Cambridge Examples', 'Audio', 'Definition Audio', 'Example Audio', 'Explanation', 'Morphology', 'Etymology', 'Connected Words', 'Hint', 'Tags']
# df.to_csv("blabla.csv", header=headers, sep='\t', index=False)

# insertDefinition()
csvOperations()
