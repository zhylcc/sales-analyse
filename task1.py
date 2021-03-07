import matplotlib
import numpy as np
import pandas as pd
import matplotlib.pyplot  as plt

class Task1():
    '''
    分别爬取京东和淘宝，在手机频道中，找出累积销量（所有商家销售同一型号手机的销 量之和）最高的 20 款手机。
    按照销量，以直方图的形式展示手机型号及其销量，按照销量倒排序。图中的手机型号 请尽量简化，能够区分即可。
    一个 figure 中有 2 个子图，2 个子图分别展示京东和淘宝中，手机销量直方图。
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
        #处理销量
        #jd/千人
        df1['sale'] = df1['sale'].str.replace('\+','')
        df1.loc[df1['sale'].str.contains('万'), 'sale'] = df1['sale'].str.replace('万','').astype(np.float) * 10000
        df1['sale'] = df1['sale'].astype(np.float)
        df1['sale'] = df1['sale'] / 1000
        #tb/人
        df2['sale'] = df2['sale'].str.replace('\+','')
        df2.loc[df2['sale'].str.contains('万'), 'sale'] = df2['sale'].str.replace('万','').astype(np.float) * 10000
        df2['sale'] = df2['sale'].astype(np.float)
        #按型号合并销量后按销量降序排列
        df1.groupby('model')['sale'].sum()
        df1.sort_values('sale',ascending=False,inplace=True)
        df2.groupby('model')['sale'].sum()
        df2.sort_values('sale',ascending=False,inplace=True)
        #保存处理结果
        df1.to_csv('./source/jd_task1.csv', encoding='utf-8')
        df2.to_csv('./source/tb_task1.csv', encoding='utf-8')

    def data_visiable(self):
        fig = plt.figure()
        #子图1：京东型号-销量
        #1.1 获取销量前20的手机型号和销量
        jd = pd.read_csv('./source/jd_task1.csv', encoding='utf-8')
        model_list = jd['model'][:20]
        sale_list = jd['sale'][:20].astype(np.float)[:20]
        #1.2 设置直方图参数
        ax1 = fig.add_subplot(121)
        ax1.set_title('JingDong') #标题
        ax1.set_ylim(0, 2300) #轴刻度范围
        ax1.set_xlabel('手机型号') #轴标签
        ax1.set_ylabel('销量/千人')
        ax1.set_xticklabels(model_list, rotation=90) #轴刻度
        plt.bar(model_list,sale_list,color='red')
        #子图2：淘宝型号-销量
        #2.1 获取销量前20的手机型号和销量
        tb = pd.read_csv('./source/tb_task1.csv', encoding='utf-8')
        model_list = tb['model'][:20]
        sale_list = tb['sale'][:20].astype(np.float)[:20]
        #2.2 设置直方图参数
        ax2 = fig.add_subplot(122)
        ax2.set_title('TaoBao') #标题
        ax2.set_ylim(8000, 31000) #轴刻度范围
        ax2.set_xlabel('手机型号') #轴标签
        ax2.set_ylabel('销量/人')
        ax2.set_xticklabels(model_list, rotation=90) #轴刻度
        plt.bar(model_list,sale_list,color='blue')
        plt.show()

if __name__ == '__main__':
    matplotlib.rcParams['font.sans-serif'] = ['SimHei'] #显示中文
    task1 = Task1()
    task1.data_process() #数据预处理
    task1.data_visiable() #数据可视化

