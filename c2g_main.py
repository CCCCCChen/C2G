# locate by row, col
# add an attribute called suitfor, to record a list of suitable characters.
# priority would be [pure, mess]

def pureOrNot():
    


import json

dict_0 = ["flower","feather","sand","cup","head"]
dict_1 = ["setName","position","mainTag","normalTags","omit","level","star","equip"]
typeName = []
typeNameSet = []
with open("Z:/Software/GenshinTools/mona.json","r",encoding="utf-8") as f:
    content = json.load(f)
    
    for i in dict_0:
        cur_dict = content[i]
        for cur_one in cur_dict:
            for cur_two in cur_one["normalTags"]:
                typeNameSet.append(cur_two["name"])
    typeName = set(typeNameSet)
    print(typeName)
