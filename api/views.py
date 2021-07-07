import requests
import stanza
from django.http import JsonResponse
from flask import Flask
from quantulum3 import parser


app = Flask(__name__)


@app.route("/", methods=['POST', 'GETS'])
def index(request):
    # This sets up a default neural pipeline in Lang
    seed = request.GET.get('seed')
    lang = request.GET.get('lang')
    if ',' in seed:
        seed = seed.replace(',', ' , ')
    nlp = stanza.Pipeline(str(lang), use_gpu=False,
                          processors='tokenize,pos,lemma')
    doc = nlp(seed)
    res = {'data': []}
    translated_text = ""
    for sent in doc.sentences:
        if lang != 'en':
            temp = sent.text.replace(',', 'and')
            url = "https://translated-mymemory---translation-memory.p.rapidapi.com/api/get"

            querystring = {"q": temp, "langpair": lang + "|en", "de": "a@b.c", "onlyprivate": "0", "mt": "1"}

            headers = {
                'x-rapidapi-key': "fedcecb517msh4b38401fd4b1c46p102514jsnf278bf4c4523",
                'x-rapidapi-host': "translated-mymemory---translation-memory.p.rapidapi.com"
            }

            response = requests.request("GET", url, headers=headers, params=querystring)
            translated_text = response.json()['responseData']['translatedText']
            print(translated_text)

        else:
            translated_text = sent.text

        quants = parser.parse(translated_text)
        for q in quants:
            if q.unit.entity.name == 'length':
                res['data'].append([float(q.surface.split()[0]), q.surface.split()[1]])
    if len(res['data']) > 0:
        print(res)
        del doc
        return res

    else:
        res['type'] = 'entity'
    if ',' in seed:
        seed = seed.replace(',', ' , ')
    nlp = stanza.Pipeline(str('en'), use_gpu=False,
                          processors='tokenize,pos,lemma')
    doc = nlp(translated_text)
    for sent in doc.sentences:
        for word in sent.words:
            res['data'].append([word.lemma, word.upos, word.text])
    i = 0
    for w in res['data']:
        w.append(i)
        i = 0
        if w[1] == 'NUM':
            i = int(w[0])
    for i, w in enumerate(res['data']):
        if w[1] == 'NOUN':
            if i < len(res['data']) - 1:
                if res['data'][i + 1][1] == 'NOUN':
                    w[0] = w[0] + ' ' + res['data'][i + 1][0]
                    w[2] = w[2] + ' ' + res['data'][i + 1][2]
                    del res['data'][i + 1]
                    del res['data'][i]

    for w in res['data']:
        if w[1] == 'NOUN':
            translated_word = w[0]

            url = "https://bing-image-search1.p.rapidapi.com/images/search/"

            querystring = {"q": str(translated_word) + " clipart png"}

            headers = {
                'x-rapidapi-key': "fedcecb517msh4b38401fd4b1c46p102514jsnf278bf4c4523",
                'x-rapidapi-host': "bing-image-search1.p.rapidapi.com"
            }

            response = requests.request("GET", url, headers=headers, params=querystring)
            if response.json()['value']:

                w[0] = response.json()['value'][0]['contentUrl']
                print(w[0])
            else:
                w[1] = 'NOUN_'
        if w[1] == 'PROPN':
            r2 = requests.get("https://api.genderize.io?name=" + w[0])
            gender = r2.json()['gender']
            if gender == 'female':
                w[0] = 'https://i.pinimg.com/originals/10/1b/28/101b28570197baeba5b390faf3304d07.png'
            else:
                w[
                    0] = 'https://w7.pngwing.com/pngs/96/861/png-transparent-boy-cartoon-child-hat-boy-painted-hand' \
                         '-toddler-thumbnail.png '

    print(res)
    del doc
    return JsonResponse(res)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port= 5000)