from nativ import nlp

tagDict = {
    'n': '名词', 'nr': '人名', 'ns': '地名', 'nt': '组织机构名', 'nz': '专有名字', 'nl': '惯用名词',
    't': '时间词', 's': '处所词', 'f': '方位词',
    'v': '动词', 'vd': '副动词', 'vi': '不及物动词', 'vn': '名动词', 'vl': '惯用动词', 'vyou': '动词', 'vshi': '动词',
    'a': '形容词', 'ad': '副动词', 'an': '名形容词', 'al': '惯用形容词',
    'b': '区别词', 'bl': '惯用区别词', 'z': '状态词', 'r': '代词', 'm': '数词', 'q': '量词',
    'd': '副词', 'dl': '惯用副词', 'p': '介词', 'c': '连词', 'u': '助词', 'y': '语气词',
    'o': '拟声词', 'h': '前缀', 'k': '后缀', 'nx': '字符串', 'w': '标点符号',
    'em': '电子邮件', 'tel': '电话号码', 'id': '身份证号', 'ip': 'ip地址', 'url': '链接'
}

nerDict = {
    'time': '时间', 'location': '地点', 'person_name': '人名', 'org_name': '组织名',
    'company_name': '公司名', 'product_name': '产品名', 'job_title': '职位'
}


def tagWrapper(source):
    tagSource = nlp.tag(source)
    tagColor = tagSource[0]['tag']
    tagWord = tagSource[0]['word']
    tag = []
    tagSet = set()
    i = 0
    length = len(tagColor)
    while i < length:
        if tagColor[i].startswith('nr'):
            tagColor[i] = 'nr'
        elif tagColor[i].startswith('u') and tagColor != 'url':
            tagColor[i] = 'u'
        tag.append([tagColor[i], tagWord[i]])
        if tagColor[i][0] in ['t', 'v', 'a', 'b', 'm', 'q', 'd', 'p',
                              'c', 'u', 'x', 'w']:
            tagSet.add((tagColor[i][0], tagDict.get(tagColor[i][0])))
        else:
            tagSet.add((tagColor[i], tagDict.get(tagColor[i])))
        i += 1
    return tag, tagSet

def nerWrapper(source):
    nerSource = nlp.ner(source)
    nerEntity = nerSource[0]['entity']
    nerWord = nerSource[0]['word']
    ner = []
    nerSet = set()
    start = 0
    for e in nerEntity:
        head = e[0]
        tail = e[1]
        name = e[2]
        nerSet.add((name, nerDict.get(name)))

        ner.extend(nerWord[start:head])
        ner.append({'word': ''.join(nerWord[head:tail]), 'css': name})
        start = tail
    ner.extend(nerWord[start:])
    return ner, nerSet


def nersWrapper(source):
    splitSource = [s for s in source.split('\r\n') if s.strip() !='']
    ners = {
        'time': {},
        'location': {},
        'person_name': {},
        'org_name': {},
        'company_name': {},
        'product_name': {},
        'job_title': {}
    }
    for s in nlp.ner(splitSource):
        nerEntity = s['entity']
        nerWord = s['word']
        for e in nerEntity:
            head = e[0]
            tail = e[1]
            name = e[2] #类型 project_name
            entity = ''.join(nerWord[head:tail]) # 实体名 商人
            if ners[name].get(entity):
                ners[name][entity] += 1
            else:
                ners[name][entity] = 1

    for r in ners:
        ners[r] = sorted(ners[r].items(), key=lambda x: x[1], reverse=True)[:7]

    nersSet = set()
    for r in ners:
        if ners[r]:
            nersSet.add((r, nerDict[r]))
    return ners, nersSet


def sentimentWrapper(source):
    sentimentSource = nlp.sentiment(source)[0]
    sentiment = ["%.2f" % sentimentSource[0], "%.2f" % sentimentSource[1]]
    return sentiment

def keywordsWrapper(source):
    keywordsSource = nlp.extract_keywords(source, top_k=15)
    keywordsList = list(map(lambda i: [int(i[0] * 100), i[1]], keywordsSource))
    i = 0
    count = 0
    length = len(keywordsList)
    keywords = []
    tmp = []
    while i < length:
        tmp.append(keywordsList[i])
        count += 1
        if(count == 5):
            keywords.append(tmp)
            count = 0
            tmp = []
        i += 1
    if count != 0:
        keywords.append(tmp)
    return keywords, keywordsList

def suggestWrapper(keywordsList):
    suggest = []
    for k in keywordsList:
        if len(suggest) == 3:
            break
        suggestSource = nlp.suggest(k[1], top_k=5)
        suggestList = []
        if suggestSource:
            for s in suggestSource:
                suggestList.append(['%.2f' % s[0], s[1].split('/')[0]])
            suggest.append(suggestList)
    return suggest