import pandas as pd
import tushare as ts
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.animation as animation
from IPython.display import HTML

#画图显示中文
plt.rcParams['font.sans-serif'] = [u'SimHei']
plt.rcParams['axes.unicode_minus'] = False

#加载锂电池板块股票的数据(爬虫来自东方财富网板块数据)
list_data=pd.read_excel('D:\pycharm\pythonProject\Reptile\锂电池板块的股票.xlsx')
list_code=list_data['股票代码'].astype('str').apply(lambda x:x.zfill(6)).tolist()#因为深成的票有00几开头，用Zfill在左填充0
dic=dict(zip(list_code,list_data['股票名称']))#将股票代码与股票名称封装为字典

#通过Tushare获取股票数据
def get_Data(code):
    data=ts.get_hist_data(code,start='2021-01-01')
    return data

#获取每只票成交量的函数
def creat_data(code):
    p_change_list=get_Data(code)['volume']
    D = pd.DataFrame(p_change_list).reset_index().sort_values(by='date')
    D['Code'] = code
    #循环以实现累加的目的
    i = 0
    while i < D.shape[0] - 1:
        D.iloc[i + 1, 1] += D.iloc[i, 1]
        i += 1
    return D

#执行函数，获取想要的数据框，由时间，成交量，股票代码，股票名称几个维度组成
def get():
    #建立空表来装数据框
    XX=[]
    #遍历需要的股票代码
    for i in list_code:
        XX.append(creat_data(i))#调用封装函数组成数据框
    ALL=pd.concat(XX,axis=0)#按行进行合并

    #通过字典匹配股票代码对应的股票名称
    list_all=[dic[x]for x in ALL['Code']]
    ALL['股票名称']=list_all
    return ALL

#获取数据
df=get()
print(df)
#将字典写入,前面有个dic，现在需要弄个反向字典
dic_2=dict(zip(list_data['股票名称'],list_code))#将股票代码与股票名称封装为字典

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~Begins~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#为了得到今年所有股市开市日期，用以下方法
want_date_list=ts.get_hist_data('601899',start='2021-01-01').reset_index().sort_values(by='date')#任意股票的历史数据，只要时间项
Dict_date=dict(zip(range(0,want_date_list.shape[0]),want_date_list['date']))#得到需要的字典，这样就能以该字典去索引日期赋值于函数

#获取指定颜色
Colors=('#adb0ff', '#ffb3ff', '#90d595', '#e48381',
     '#aafbff', '#f7bb5f', '#eafb50')

#指定绘图布局
fig, ax = plt.subplots(figsize=(15, 8))

#画图函数，单独运行即可成为图片
def draw_barchart(n):
    Date=Dict_date[n]
    dff = df[df['date'].eq(Date)].sort_values(by='volume', ascending=True).tail(10)
    ax.clear()
    ax.barh(dff['股票名称'], dff['volume'], color=Colors)
    dx = dff['volume'].max() / 200
    for i, (value, name) in enumerate(zip(dff['volume'], dff['股票名称'])):
        ax.text(value - dx, i, name, size=14, weight=600, ha='right', va='bottom')
        ax.text(value - dx, i - .25, dic_2[name], size=10, color='#444444', ha='right', va='baseline')
        ax.text(value + dx, i, f'{value:,.0f}', size=14, ha='left', va='center')
    # ... polished styles
    ax.text(1, 0.4, Date, transform=ax.transAxes, color='#777777', size=46, ha='right', weight=800)
    ax.text(0, 1.06, 'Volume (成交量:手)', transform=ax.transAxes, size=12, color='#777777')
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))#定制化刻度标签形式
    ax.xaxis.set_ticks_position('top')#设置该格式位置
    ax.tick_params(axis='x', colors='#777777', labelsize=12)#设置轴的格式
    ax.set_yticks([])#将y标签设为空值
    ax.margins(0, 0.01)#缩放坐标轴
    ax.grid(which='major', axis='x', linestyle='-')#表框格式
    ax.set_axisbelow(True)
    ax.text(0, 1.12, '锂电池板块累计成交量',
            transform=ax.transAxes, size=20, weight=600, ha='left')#设置标题
    plt.box(False)
    plt.show()

#使用animation动态画图工具，生成gif文件
animator = animation.FuncAnimation(fig, draw_barchart,frames=range(0,4))#调用连续作图工具，frame为绘图函数的取值范围
HTML(animator.to_jshtml())#生成HTML文件

animator.save("test3.gif",writer='pillow')#保存为GIF