from typing import Dict, List

import requests
from requests.exceptions import HTTPError

APP_ID = "add your id"
APP_KEY = "add your key"

base_url = "https://od-api.oxforddictionaries.com/api/v2"

# for british accent. <https://developer.oxforddictionaries.com/documentation/languages>
language = 'en-gb'


def setOxfordKey(app_id, app_key) -> None:
    global APP_ID
    global APP_KEY
    APP_ID = app_id
    APP_KEY = app_key
    # print("setOxfordKey", APP_ID, APP_KEY, file=sys.stderr)


def getLemmas(word, app_id=None, app_key=None, language=language) -> List[str]:
    """gets a list of valid headwords"""
    if app_id is None or app_key is None:
        app_id = APP_ID
        app_key = APP_KEY

    # print("getLemmas", file=sys.stderr)

    url = base_url + "/lemmas/" + language + '/' + word
    r = requests.get(url, headers={"app_id": app_id, "app_key": app_key})

    res: List[str] = []
    if not r.ok:
        raise requests.exceptions.HTTPError(response=r)

    for result in r.json()["results"]:
        for lexicalEntry in result["lexicalEntries"]:
            for inflection in lexicalEntry["inflectionOf"]:
                res.append(inflection["id"])
    return res


def getEntry(word, app_id=None, app_key=None, language=language):
    if app_id is None or app_key is None:
        app_id = APP_ID
        app_key = APP_KEY

    url = base_url + "/entries/" + language + '/' + word
    r = requests.get(url, headers={"app_id": app_id, "app_key": app_key})

    if not r.ok:
        raise requests.exceptions.HTTPError(response=r)

    return r.json()


def formatEntry(word, app_id=None, app_key=None, language=language) -> object:
    try:
        """returns an empty dict if the entry can't be found
            returning: {
                word: str,
                results: List[
                    List[{
                        lexicalCategory: str,
                        derivatives: List[str],
                        entries: List[{
                            pronunciation: List[str],
                            senses: List[{
                                definitions: List[str],
                                example: str,
                                notes: List[str]
                            ]}
                            etymologies: List[str],
                            notes: List[str]
                        }]
                    }]
                }]
            }"""
        r = getEntry(word, app_id, app_key, language)

        returning: Dict = {}
        returning["word"] = r["word"]
        returning["results"] = []
        results = r["results"]

        for result in results:

            myResult: List[object] = []
            for lexicalEntry in result["lexicalEntries"]:
                myLexical: Dict = {}
                myLexical["lexicalCategory"] = lexicalEntry["lexicalCategory"]["text"]
                if "derivatives" in lexicalEntry:
                    myLexical["derivatives"] = [d["text"] for d in lexicalEntry["derivatives"]]

                myLexical["entries"] = []
                for entry in lexicalEntry["entries"]:
                    myEntry: Dict = {}
                    myEntry["pronunciations"] = [pronunciation["audioFile"] \
                                                 for pronunciation in entry["pronunciations"] \
                                                 if "audioFile" in pronunciation]

                    myEntry["senses"] = []
                    for sense in entry["senses"]:
                        mySense: Dict = {}
                        if "definitions" not in sense:
                            continue
                        mySense["definitions"] = sense["definitions"]
                        if "examples" in sense:
                            mySense["example"] = sense["examples"][0]["text"]
                        if "notes" in sense:
                            mySense["notes"] = [note["text"] for note in sense["notes"]]
                        myEntry["senses"].append(mySense)

                    if "etymologies" in entry:
                        myEntry["etymologies"] = entry["etymologies"]
                    if "notes" in entry:
                        myEntry["notes"] = [note["text"] for note in entry["notes"]]

                    myLexical["entries"].append(myEntry)
                myResult.append(myLexical)
            returning["results"].append(myResult)

        return returning

    except:
        raise HTTPError()
