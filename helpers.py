def get_text(txt):
    f = open('data\\'+ str(txt)+'.txt', 'r', encoding="utf8")
    return f.read()

def fun1(txt):
    txt = txt.replace('“', '"')
    txt = txt.replace('”', '"')
    txt = txt.replace('’', '\'')
    i = 0
    while i < len(txt):
        if txt[i] == ',':
            txt = txt[0:i+1] + '\n' + txt[i+2:]
        i = i + 1
    return txt


