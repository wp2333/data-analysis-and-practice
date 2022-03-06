import json
dict1={'片名': '傲慢与偏见 Pride & Prejudice', '导演': '乔·赖特', '编剧': ['简·奥斯汀', '黛博拉·莫盖茨'], '主演': ['凯拉·奈特莉', '马修·麦克费登', '唐纳德·萨瑟兰', '布兰达·布莱斯', '凯瑞·穆里根'], '类型': ['剧情', '爱情'], '制片国家/地区': '法国 / 英国 / 美国', '语言': ['英语'], '上映日期': ['2005-09-16(英国)'], '片长': ['129 分钟', '135 分钟(加拿大)'], '评分': 8.7}
# print(dict1)
with open("result.json","a",encoding='utf-8') as fp:
    json.dump(dict1,fp, ensure_ascii=False, indent=4)
    fp.write('\n')
# print(jsonStr)