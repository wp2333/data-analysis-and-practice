import os

CUR_PATH = r'D:\data analysis and pratice\covers'
def del_file(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        os.remove(c_path)
 
# del_file(CUR_PATH)
# open("result.json", "w").close()
