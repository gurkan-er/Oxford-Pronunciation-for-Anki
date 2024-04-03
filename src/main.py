import pandas as pd
import requests
from requests.exceptions import HTTPError

from oxford_api import getLemmas, formatEntry

KEY_FIELD = 0  # already contains word and must append audio
DEFINITION_FIELD = 1

WHAT_TO_INSERT = "pronunciation"
PRIMARY_SHORTCUT = "ctrl+alt+d"


def insert_definition(target):
    # update config

    # Get the word
    word = ""
    try:
        # word = editor.note.fields[0]
        word = target
        if word == "" or word.isspace():
            raise KeyError()  # Purely to jump to the tooltip here
    except (AttributeError, KeyError) as e:
        print("OxfordDefine: No text found in note fields.")
        return "OxfordDefine: No text found in note fields."

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
            return f"OxfordDefine: Could not root words for {word}."

    # Format word
    definition = ""
    sound_urls = set()
    for result in wordInfos['results']:
        for lexical in result:
            # Definition format
            definition += '<hr>'
            definition += '<b>' + lexical['lexicalCategory'] + '.</b><br>'
            for entry in lexical['entries']:
                if "pronunciations" in entry:  # sounds saved for later
                    sound_urls.update(entry["pronunciations"])

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

    # Output
    sounds = [url.strip() for url in sound_urls]

    for sound_url in sounds:
        response = requests.get(sound_url)
        with open(f'oxford_{word}.mp3', 'wb') as file:
            file.write(response.content)

    return f"[sound:oxford_{target}.mp3]"


def csv_operations():
    # read csv file
    df = pd.read_csv("../data/input.csv", delimiter='\t')

    for i in range(187, len(df)):
        df.loc[i, "Audio"] = insert_definition(df["Word"][i])

        # write df to a csv file
        df.to_csv("../data/output.csv", sep='\t', index=False)
        print(i)

    select_rows(0, 10, df, "../data/outputFirstRows.csv")

    df.to_csv("../data/output.csv", sep='\t', index=False)


def select_columns(start, end, df, target_file):
    selected_columns = df.iloc[:, start:end]
    selected_columns.to_csv('../data/' + target_file, sep='\t', index=False)


def select_rows(start, end, df, target_file):
    selected_rows = df.iloc[start:end]
    selected_rows.to_csv('../data/' + target_file, sep='\t', index=False)


def move_column(location: int, df, column_name: str):
    """
    If you want to move "ID" column to the location of another column:
    move_column(5, df, "ID")
    """

    # pop the column and paste to the index
    df.insert(location, column_name, df.pop(column_name))


def move_column_with_name(location: str, df, column_name: str):
    """
    If you want to move "ID" column in place of another column named "Hint":
    move_column("Hint", df, "ID")
    """

    # pop the column and paste to the index
    df.insert(df.columns.get_loc(location), column_name, df.pop(column_name))


def insert_column(location: int, df, column_name: str, new_column):
    """
    If you want to insert a column called "this" as 5th column:
    insert_column(5, df, "this", " ")
    column will have empty items

    As 5th column, If you want to insert a column called "this" that contains the values of the "ID" column:
    insert_column(5, df, "this", df["ID"])
    """

    df.insert(location, column_name, new_column)


def insert_column_with_name(location: str, df, column_name: str, new_column):
    """
    If you want to insert a column called "this" in place of another column named "Hint":
    insert_column("Hint", df, "this", " ")
    column will have empty items

    If you want to insert a column called "this" that contains the values of the "ID" column, in place of another
    column named "Hint":
    insert_column("Hint", df, "this", df["ID"])
    """
    df.insert(df.columns.get_loc(location), column_name, new_column)


def define_headers(*args, df):
    # headers = ['', 'ID', 'Word', 'Definition', 'Class', 'Register', 'CEFR Level', 'IPA', 'Image', 'Example',
    # 'Cambridge Examples', 'Audio', 'Definition Audio', 'Example Audio', 'Explanation', 'Morphology', 'Etymology',
    # 'Connected Words', 'Hint', 'Tags']
    headers = []
    for item in args:
        headers += item

    df.to_csv("../data/inputWithHeader.csv", header=headers, sep='\t', index=False)

# csvOperations()
