import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot  as plt

class Task2():
    '''
    用你爬取下来的数据制作散点图，横轴为手机价格，纵轴为该价格对应的商家个数。
    一个 figure 中有 2 个子图，2 个子图分别展示京东和淘宝中，手机价格的分布情况。
    '''
    def data_process(self):
        #读取数据
        df1 = pd.read_csv('./source/jd.csv',encoding='utf-8',dtype=str)
        df2 = pd.read_csv('./source/tb.csv',encoding='utf-8',dtype=str)
        #删除包含空值的行
        df1.dropna(inplace=True)
        df2.dropna(inplace=True)
        #处理版本——{存储容量:价格}键值对，按存储容量分行
        #jd
        df1['versions'] = df1['versions'].str.replace('\'|\s|{|}','')
        df1 = df1.drop('versions',axis=1).join(
            df1['versions'].str.split(',',expand=True).stack().reset_index(level=1,drop=True).rename('vp')
        )
        df1['version'] = df1['vp'].str.split(':',expand=True)[0]
        df1['price'] = df1['vp'].str.split(':',expand=True)[1].astype(np.float)
        df1.drop('vp', axis=1, inplace=True)
        #tb
        df2['versions'] = df2['versions'].str.replace('\'|\s|{|}|-.*','')
        df2 = df2.drop('versions',axis=1).join(
            df2['versions'].str.split(',',expand=True).stack().reset_index(level=1,drop=True).rename('vp')
        )
        df2['version'] = df2['vp'].str.split(':',expand=True)[0]
        df2['price'] = df2['vp'].str.split(':',expand=True)[1].astype(np.float)
        df2.drop('vp', axis=1, inplace=True)
        #按价格合并商家个数
        price1 = df1.groupby('price')['store'].count().reset_index()
        price1.rename(columns={'store':'count'}, inplace=True)
        price2 = df2.groupby('price')['store'].count().reset_index()
        price2.rename(columns={'store':'count'}, inplace=True)
        #保存处理结果
        price1.to_csv('./source/jd_task2.csv', encoding='utf-8')
        price2.to_csv('./source/tb_task2.csv', encoding='utf-8')

    def data_visiable(self):
        fig = plt.figure()
        #子图1：京东价格-商家数目
        #1.1 获取价格和对应商家个数
        jd = pd.read_csv('./source/jd_task2.csv', encoding='utf-8')
        price_list = jd['price'].astype(np.float)
        count_list = jd['count'].astype(np.int)
        #1.2 设置散点图图参数
        ax1 = fig.add_subplot(121)
        ax1.set_title('JingDong') #标题
        ax1.set_xlabel('手机价格') #轴标签
        ax1.set_ylabel('商家数')
        plt.scatter(price_list, count_list, 1, 'red')
        #子图2：淘宝价格-商家数目
        #2.1 获取价格和对应商家个数
        tb = pd.read_csv('./source/tb_task2.csv', encoding='utf-8')
        price_list = tb['price'].astype(np.float)
        count_list = tb['count'].astype(np.int)
        #2.2 设置散点图图参数
        ax2 = fig.add_subplot(122)
        ax2.set_title('TaoBao') #标题
        ax2.set_xlabel('手机价格') #轴标签
        ax2.set_ylabel('商家数')
        plt.scatter(price_list, count_list, 1, 'blue')
        plt.show()

if __name__ == '__main__':
    matplotlib.rcParams['font.sans-serif'] = ['SimHei'] #显示中文
    task2 = Task2()
    task2.data_process() #数据预处理
    task2.data_visiable() #数据可视化

