class item:
    "物体基本类"
    url = '  qweq'
    def __setitem__(self, key, value):
        self.__dict__[key]=value
    def __getitem__(self, item):
        return self.__dict__[item]
    def SaveAsStr(self):
        keylist = self.__dir__()
        text = ""
        for key in keylist:
            if '__' not in key and key != 'SaveAsStr':
                text += str(getattr(self, key))
        return text

class file(item):
    path = ""

if __name__ == '__main__':
    i = item()
    f= file()

    print(i.SaveAsStr())
