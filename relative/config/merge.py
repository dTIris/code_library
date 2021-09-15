import json
import codecs
fw = codecs.open("./stopwords.json","a+","utf-8")
lines = codecs.open("./stopwords.txt","r","utf-8")
lexcion = {}

for line in lines:
    line = line.strip().replace("\r\n","").replace("\n", "")
    lexcion[line] = 0

fw.write("%s" % (json.dumps(lexcion, ensure_ascii=False)))
fw.close()
