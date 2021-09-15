import codecs
import json
jk_all = {}

lines = codecs.open("jk.big","r", "utf-8").readlines()
for line in lines:
    data = line.split()
    if len(data) < 1:
        continue
    key = data[0].strip()
    if len(key) <=0:
        continue
    jk_all[key] = 0
   

lines = codecs.open("jk.disease.big","r", "utf-8").readlines()
for line in lines:
    data = line.split()
    if len(data) < 1:
        continue
    key = data[0].strip()
    if len(key) <=0:
        continue
    jk_all[key] = 0

fpw = codecs.open("jk.all.json", "w", "utf-8")
fpw.write("%s" % (json.dumps(jk_all, ensure_ascii=False)))
fpw.close()

fpw = codecs.open("jk.all.big", "w", "utf-8")
count = 0
for _ in jk_all:
    fpw.write("%s 30\n" % (_))
    count += 1
    print count

fpw.close()
