from libraries import chardet, pd, dd
class dataloader:
    def __init__(self, data):
        self.data = data

    def check_encoding(self): # check the encoding method as not all files can be read using 'UTF-8'
        with open(self.data,'rb') as file:
                result = chardet.detect(file.read(15000))
                return result['encoding']
    def pdloader(self):
        encoder = self.check_encoding()
        try:
            loading = pd.read_csv(self.data, encoding=encoder)
            return loading
        except:
            loading =pd.read_csv(self.data, encoding='utf-8')
            return loading             

    def ddloader(self):
        encoder = self.check_encoding()
        try:
            loading = dd.read_csv(self.data, encoding=encoder)
            return loading
        except:
            loading = dd.read_csv(self.data, encoding='utf-8')
            return loading