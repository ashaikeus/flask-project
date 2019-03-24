from flask import *
from urllib.parse import unquote

app = Flask(__name__)

@app.route('/characters')
@app.route('/characters/')
def characters():
    with open("news.json", "rt", encoding="utf8") as f:
        news_list = json.loads(f.read())
    print(news_list)
    return render_template('characters.html', characters=news_list)

@app.route('/characters/<name>')
def char_page(name):
    with open("news.json", "rt", encoding="utf8") as f:
        value = json.loads(f.read())
        name = unquote(name)[:-1]
        data = 0
    for j in value:
        for i in value[j]:
            if i['name'] == name:
                data = i
                break
    print(data)
    if not data['image']:
        data['image'] = 'static/img/nophoto.png'
    return render_template('character_page.html', char_info=data)

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
