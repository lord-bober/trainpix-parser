import requests
import bs4


def get_stats(loco_list):
    roads = dict()
    cnt = 0
    cnt_worked = 0
    for loco in loco_list:
        state_select = loco['class'][0]
        worked = 0
        if state_select in ['s1', 's11']:
            worked = 1
        assign = loco.find_all('td', {'class': 'cs'})
        if len(assign) > 2:
            assign = assign[-2:]
        if len(assign) == 2:
            cnt += 1
            if worked:
                cnt_worked += 1
            if assign[0].text in roads:
                if assign[1].text in roads[assign[0].text]:
                    roads[assign[0].text][assign[1].text][1] += 1
                    if worked:
                        roads[assign[0].text][assign[1].text][0] += 1
                else:
                    roads[assign[0].text][assign[1].text] = [0, 1]
                    if worked:
                        roads[assign[0].text][assign[1].text][0] += 1
            else:
                if worked:
                    roads[assign[0].text] = {assign[1].text: [1, 1]}
                else:
                    roads[assign[0].text] = {assign[1].text: [0, 1]}
    return roads, cnt, cnt_worked


def get_models():
    url = "https://trainpix.org/models.php"
    r = requests.get(url)
    soup = bs4.BeautifulSoup(r.text, 'lxml')
    models_list = soup.find_all('tr', {'class': ['s1', 's11']})
    models = {}
    for model in models_list:
        model_link = model.find('a').get('href')
        model_desc = model.find('a').text
        models[model_desc] = model_link
    return models


def get_array(serie, cnt):
    url = "https://trainpix.org"+serie+"&st=%d" % (cnt)
    s = requests.Session()
    r = s.get(url, cookies={'divide': '1'})
    soup = bs4.BeautifulSoup(r.text, 'lxml')
    title = soup.h2.text
    loco_list = soup.find_all('tr', {'class': ['s1', 's11', 's2', 's12', 's3', 's13']})
    return title, loco_list


def output_stats(title, stats):
    print(title)
    roads_all = stats[0]
    cnt_all = stats[1]
    cnt_worked = stats[2]
    for road, value in roads_all.items():
        print("{0}:".format(road))
        cnt_road_worked = 0
        cnt_road_all = 0
        for depot, cnt in value.items():
            cnt_road_worked += cnt[0]
            cnt_road_all += cnt[1]
            print("    {0}: {1}/{2}".format(depot, cnt[0], cnt[1]))
        print("  Всего по дороге: {0}/{1}".format(cnt_road_worked, cnt_road_all))
    print("Всего: {0}/{1}".format(cnt_worked, cnt_all))


def search_model_link(models, model_str):
    res = dict()
    for key, val in models.items():
        if key.find(model_str) != -1:
            res[key] = val
    if len(res) == 0:
        return None
    if len(res) == 1:
        return list(res.items())[0][1]
    else:
        id = 1
        for key in res:
            print(id, key)
            id += 1
        print("Введите номер нужной модели из списка выше: ")
        choice = int(input())
        return list(res.items())[choice-1][1]


if __name__ == '__main__':
    models = get_models()
    print("Введите модель:")
    model = input()
    model_link = search_model_link(models, model)
    if model_link:
        cnt = 0
        loco_list = []
        title, new_list = get_array(model_link, cnt)
        loco_list += new_list
        while len(new_list) - 3 == 500:
            cnt += 500
            _, new_list = get_array(model_link, cnt)
            loco_list += new_list

        output_stats(title, get_stats(loco_list))
    else:
        print("Модель не найдена")
