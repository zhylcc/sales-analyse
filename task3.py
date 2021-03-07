import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot  as plt

class Task3():
    '''
    找出在两个平台上都有售卖的 5 款手机（找销量较大的） ，由于两个平台上都有不同的 卖家都销售这些手机，价格也不同，需要将这些卖家销售这款手机的价格，做出箱型图，比 较不同平台上的价格情况。
    一个 figure 中有 5 个子图，每个子图里面有两个平台上售卖的同一型号手机的 2 个价 格箱型图。
    '''
    def data_process(self):
        #读取数据
        df1 = pd.read_csv('./source/jd.csv',encoding='utf-8',dtype=str)
        df2 = pd.read_csv('./source/tb.csv',encoding='utf-8',dtype=str)
        #删除包含空值的行
        df1.dropna(inplace=True)
        df2.dropna(inplace=True)
        #处理型号
        #jd
        df1['model'] = df1['model'].str.replace('s.*$','S',case=False)
        df1['model'] = df1['model'].str.replace('pro.*$','Pro',case=False)
        df1['model'] = df1['model'].str.replace('\s|苹果|双.*$|手机|【.*?】','')
        df1['model'] = df1['model'].str.replace('xr','XR')
        df1['model'] = df1['model'].str.replace('华为（HUAWEI）','华为')
        df1['model'] = df1['model'].str.replace('华为.*华为','华为')
        df1['model'] = df1['model'].str.replace('华为.*荣耀','荣耀')
        df1['model'] = df1['model'].str.replace('小米.*小米','小米')
        df1['model'] = df1['model'].str.replace('小米.*Redmi','红米')
        df1['model'] = df1['model'].str.replace('AppleiPhone','iPhone')
        #tb
        df2['model'] = df2['model'].str.replace('.*?/|\s|苹果','')
        df2['model'] = df2['model'].str.replace('荣耀.*?荣耀','荣耀')
        df2['model'] = df2['model'].str.replace('HUAWEI.*?HUAWEI','华为')
        df2['model'] = df2['model'].str.replace('HUAWEI.*?华为','华为')
        df2['model'] = df2['model'].str.replace('HUAWEI','华为')
        df2['model'] = df2['model'].str.replace('小米.*小米','小米')
        df2['model'] = df2['model'].str.replace('小米.*Redmi','红米')
        df2['model'] = df2['model'].str.replace('AppleiPhone','iPhone')
        #处理版本——{存储容量:价格}键值对，按存储容量分行
        #jd
        df1['versions'] = df1['versions'].str.replace('\'|\s|{|}|【.*?】|全网通|（|）|3D感光','')
        df1['versions'] = df1['versions'].str.replace('\+','GB')
        df1['versions'] = df1['versions'].str.replace('GBGB','GB')
        df1 = df1.drop('versions',axis=1).join(
            df1['versions'].str.split(',',expand=True).stack().reset_index(level=1,drop=True).rename('vp')
        )
        df1['version'] = df1['vp'].str.split(':',expand=True)[0]
        df1['price'] = df1['vp'].str.split(':',expand=True)[1].astype(np.float)
        df1.drop('vp', axis=1, inplace=True)
        #tb
        df2['versions'] = df2['versions'].str.replace('\'|\s|{|}|-.*','')
        df2['versions'] = df2['versions'].str.replace('\+','GB')
        df2['versions'] = df2['versions'].str.replace('GBGB','GB')
        df2 = df2.drop('versions',axis=1).join(
            df2['versions'].str.split(',',expand=True).stack().reset_index(level=1,drop=True).rename('vp')
        )
        df2['version'] = df2['vp'].str.split(':',expand=True)[0]
        df2['price'] = df2['vp'].str.split(':',expand=True)[1].astype(np.float)
        df2.drop('vp', axis=1, inplace=True)
        #合并型号+版本
        df1['model'] = df1['model'] + '_' + df1['version']
        df2['model'] = df2['model'] + '_' + df2['version']
        #保存处理结果
        df1.to_csv('./source/jd_task3.csv', encoding='utf-8')
        df2.to_csv('./source/tb_task3.csv', encoding='utf-8')
        #找到在两个平台都有售卖的手机型号
        models = []
        df1_model, df1_price = df1.model.tolist(), df1.price.tolist()
        df2_model, df2_price = df2.model.tolist(), df2.price.tolist()
        for i in range(len(df1_model)):
            for j in range(len(df2_model)):
                if df1_model[i] == df2_model[j] and df1_model[i] not in models:
                    models.append(df1_model[i])
                    break
        #找到对应型号的售卖价格
        mp_jd, mp_tb = dict(), dict()
        for i in range(len(models)):
            mp_jd[i], mp_tb[i] = list(), list()
        for i in range(len(models)):
            for j in range(len(df1_model)):
                if df1_model[j] == models[i]:
                    mp_jd[i].append(df1_price[j])
            for j in range(len(df2_model)):
                if df2_model[j] == models[i]:
                    mp_tb[i].append(df2_price[j])
        #筛选出在两平台出售店铺数均大于4的手机
        for i in range(len(models)):
            if not (len(mp_jd[i]) > 4 and len(mp_tb[i]) > 4):
                del mp_jd[i]
                del mp_tb[i]
        #筛选出在淘宝出售店家最多的5款手机
        self.res_jd = sorted(mp_jd.items(), key=lambda x:len(x[1]), reverse=True)[:5]
        self.res_tb = list()
        for i in range(5):
            index = self.res_jd[i][0]
            self.res_jd[i] = (models[index], mp_jd[index])
            self.res_tb.append((models[index], mp_tb[index]))

    def data_visiable(self):
        fig = plt.figure()
        for i in range(5):
            #1. 获取两个平台上型号i的销售价格信息
            price_list1 = self.res_jd[i][1]
            price_list2 = self.res_tb[i][1]
            #2. 子图i
            plt.subplot(1,5,i+1)
            plt.title(f'{self.res_jd[i][0]}')
            plt.boxplot([price_list1,price_list2],labels=['JingDong','TaoBao'],meanline=True,showmeans=True)
        plt.show()

if __name__ == '__main__':
    matplotlib.rcParams['font.sans-serif'] = ['SimHei'] #显示中文
    task3= Task3()
    task3.data_process() #数据预处理
    task3.data_visiable() #数据可视化

