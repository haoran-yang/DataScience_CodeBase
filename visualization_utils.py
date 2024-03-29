import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import graphviz
from sklearn import tree
from matplotlib import gridspec
mpl.rcParams['font.family']='DFKai-SB'#修改了全局变量,seaborn显示中文

def dist_numb_target(data,x,y,bins=None,hist=True,xlim=None):
    '''单个连续特征分布图(二分类),y取值类型需为int型0,1'''
    plt.figure(figsize=(24,6))
    plt.suptitle("Frequency of "+x, fontsize=22)
    plt.subplot(131)
    g = sns.distplot(data[data[x].notnull()][x].apply(float),bins=bins,hist=hist)
    if xlim is not None:
        plt.xlim(xlim[0],xlim[1])
    g.set_title("frequency", fontsize=22)
    g.set_xlabel(x+" values", fontsize=18)
    g.set_ylabel("Density", fontsize=18)
    plt.subplot(132)
    sns.distplot(data[(data[x].notnull())&(data[y]==1)][x].apply(float), bins=bins,hist=False,label='Yes')
    g2 = sns.distplot(data[(data[x].notnull())&(data[y]==0)][x].apply(float), bins=bins,hist=False,label='No')
    plt.legend(title=y,loc='best')
    if xlim is not None:
        plt.xlim(xlim[0],xlim[1])
    g2.set_ylabel("Density", fontsize=18)
    g2.set_title(x+' by Target({})'.format(y), fontsize=22)
    g2.set_xlabel(x+" values", fontsize=18)
    plt.subplot(133)
    g3 = sns.boxenplot(x=y, y=x, data=data)
    if xlim is not None:
        plt.ylim(xlim[0],xlim[1])
    g3.set_title(x+" Boxenplot by "+y, fontsize=20)
    g3.set_xlabel(y, fontsize=17)
    g3.set_ylabel(x+" Values", fontsize=17)
    plt.subplots_adjust(hspace = 0.6, top = 0.85)

def dist_cate_target(data,x,y,rename={0:'good', 1:'bad'},return_tmp=False):
    '''单个类别特征分布绘图(二分类)'''
    if str(data[x].dtype) != 'category':
        data[x] = data[x].astype(str)
    data[y] = data[y].apply(lambda x:int(float(x)))
    tmp = pd.crosstab(data[x], data[y], normalize='index') * 100
    tmp = tmp.reset_index()
    tmp.rename(columns=rename, inplace=True)

    plt.figure(figsize=(16,6))
    plt.suptitle(x+' Distributions', fontsize=22)

    plt.subplot(121)
    g = sns.countplot(x=x, data=data)
    g.set_title(x+" Distribution", fontsize=19)
    g.set_xlabel(x+" Name", fontsize=17)
    g.set_ylabel("Count", fontsize=17)
    g.set_ylim(0,max([p.get_height() for p in g.patches])*1.2)
    for p in g.patches:
        height = p.get_height()
        g.text(p.get_x()+p.get_width()/2.,
                height + 3,
                '{:1.2f}%\n{}'.format(height/data.shape[0]*100,height),
                ha="center", fontsize=14) 
    plt.subplot(122)
    g1 = sns.countplot(x=x, hue=y, data=data)
    plt.legend(title=y, loc='best', labels=['No', 'Yes'])
    gt = g1.twinx()
    order = [i.get_text() for i in g1.get_xticklabels()] # get_text将类别值转换成了字符串
    if str(data[x].dtype) == 'category': 
        for x_val in range(len(order)):
            if order[x_val] != str(tmp.iloc[:,0].tolist()[x_val]):
                print('Feature Order Wrong!')
                break
        order = None
    gt = sns.pointplot(x=x, y=rename[1], data=tmp, color='black',order=order,legend=False) # 按主轴排序
    gt.set_ylabel("% {} of Total".format(rename[1]), fontsize=16)
    gt.set_ylim(0) # round(tmp[rename[1]].max()+1)
    g1.set_title(x+" by Target({})".format(y), fontsize=19)
    g1.set_xlabel(x+" Name", fontsize=17)
    g1.set_ylabel("Count", fontsize=17)
    if return_tmp:
        return tmp

def ploting_cat_fets(data, cols, target='target', vis_row=5, vis_col=2,figsize=(14, 6)):
    '''多特征目标target正类比例,y取值类型需为int型0,1'''
    grid = gridspec.GridSpec(vis_row,vis_col) # The grid of chart
    plt.figure(figsize=figsize) # size of figure

    # loop to get column and the count of plots
    for n, col in enumerate(data[cols]): 
        tmp = pd.crosstab(data[col], data[target], normalize='index') * 100
        tmp = tmp.reset_index()
        tmp.rename(columns={0:'No',1:'Yes'}, inplace=True)

        ax = plt.subplot(grid[n]) # feeding the figure of grid
        sns.countplot(x=col, data=data, order=list(tmp[col].values) , color='green') 
        ax.set_ylabel('Count', fontsize=15) # y axis label
        ax.set_title(f'{col} Distribution by Target', fontsize=18) # title label
        ax.set_xlabel(f'{col} values', fontsize=15) # x axis label

        # twinX - to build a second yaxis
        gt = ax.twinx()
        gt = sns.pointplot(x=col, y='Yes', data=tmp,
                           order=list(tmp[col].values),
                           color='black', legend=False)
        gt.set_ylim(tmp['Yes'].min()-5,tmp['Yes'].max()*1.1)
        gt.set_ylabel("Target %True(1)", fontsize=16)
        sizes=[] # Get highest values in y
        for p in ax.patches: # loop to all objects
            height = p.get_height()
            sizes.append(height)
            ax.text(p.get_x()+p.get_width()/2.,
                    height + 3,
                    '{:1.2f}%'.format(height/data.shape[0]*100),
                    ha="center", fontsize=14) 
        ax.set_ylim(0, max(sizes) * 1.15) # set y limit based on highest heights
    plt.subplots_adjust(hspace = 0.5, wspace=.3)

def ploting_numb_fets(data, cols, target='target', vis_row=5, vis_col=2, draw_type='dist_y',figsize=(14, 6),bins=50):
    '''多连续特征分布,参数draw_type:绘图类型,取值：dist_y(按y分布图),dist(分布图),box_y(按y增强箱形图),box(增强箱形图)'''
    grid = gridspec.GridSpec(vis_row,vis_col) # The grid of chart
    plt.figure(figsize=figsize) # size of figure
    suptitle = "Frequency" if draw_type=='dist' else f"Frequency by {target}" if draw_type=='dist_y' else f"Boxenplot by {target}" if draw_type=='box_y' \
                else 'Boxenplot'
    plt.suptitle(suptitle, fontsize=22)
    # loop to get column and the count of plots
    for n, col in enumerate(data[cols]): 
        ax = plt.subplot(grid[n]) # feeding the figure of grid
        if draw_type=='dist_y':
            sns.distplot(data[(data[col].notnull())&(data[target]==1)][col].apply(float), bins=bins,hist=False,label='Yes')
            sns.distplot(data[(data[col].notnull())&(data[target]==0)][col].apply(float), bins=bins,hist=False,label='No')
            ax.set_ylabel('Density', fontsize=13) 
        elif draw_type == 'dist':
            sns.distplot(data[data[col].notnull()][col].apply(float),bins=bins,hist=False)
        elif draw_type == 'box_y':
            sns.boxenplot(x=target, y=col, data=data)
        elif draw_type == 'box':
            sns.boxenplot(y=col, data=data)
        else:
            print('Wrong draw type!')
            break
        ax.set_title(col, fontsize=16)
        ax.set_ylabel(f"{col}" if draw_type in ['box_y','box'] else "Density", fontsize=13)
        ax.set_xlabel(f'{target}' if draw_type in ['box_y','box'] else '',fontsize=12)
    plt.subplots_adjust(hspace = 0.5, wspace=.3) # 图间间隔

def target_dist_plot(data,target='target'):
    '''二分类目标分布图,默认列名为target'''
    plt.figure(figsize=(12,6))
    g = sns.countplot(x=target, data=data)
    g.set_title("TARGET DISTRIBUTION", fontsize = 20)
    g.set_xlabel("Target Vaues", fontsize = 15)
    g.set_ylabel("Count", fontsize = 15)
    sizes=[] # Get highest values in y
    for p in g.patches:
        height = p.get_height()
        sizes.append(height)
        g.text(p.get_x()+p.get_width()/2.,
                height + 3,
                '{}, {:1.2f}%'.format(height,height/data.shape[0]*100),
                ha="center", fontsize=16) 
    g.set_ylim(0, max(sizes) * 1.15) # set y limit based on highest heights

def dist_target_detail(data,x,target,xlim=[]):
    '''单个特征分布图，手动分箱可用'''
    a = sns.FacetGrid(data, hue = target, aspect=4)
    a.map(sns.kdeplot, x, shade=True)  # sns.countplot
    if not xlim:
        xlim = [data[x].min(),data[x].max()]
    a.set(xlim=(xlim[0],xlim[1]))
    a.add_legend()

def correlation_heatmap(df,figsize=(10, 8)):
    '''相关性热力图'''
    _ , ax = plt.subplots(figsize =figsize)
    colormap = sns.diverging_palette(220, 10, as_cmap = True)
    _ = sns.heatmap(
        df.corr(), 
        cmap = colormap,
        square=True, 
        cbar_kws={'shrink':.9 }, 
        ax=ax,
        annot=True, 
        linewidths=0.1,vmax=1.0, linecolor='white',
        annot_kws={'fontsize':12 }
    )
    plt.title('Pearson Correlation of Features', y=1.05, size=15)

class SeabornPlot():
    def __init__(self):
        pass

    def box_violin_sns(self,data=None, x=None, y=None, hue=None,figsize=(10, 6),exampleShow=False,violin=False,violin_split=True):
        '''箱线图/琴音图 
        data:DataFrame, array 数据源
        x,y,hue:变量名
        exampleShow:是否显示示例'''
        # sns.set(style="ticks", palette="pastel")
        f, ax = plt.subplots(figsize= figsize)
        if not violin:
            if exampleShow:
                x,y,hue,data = "day","total_bill","smoker",sns.load_dataset("tips")
            sns.boxplot(x=x, y=y, hue=hue, data=data, ax=ax)
            # sns.despine(offset=10, trim=True)
        else:
            sns.violinplot(x=x, y=y, hue=hue,split=violin_split, inner="quartile",data=data)        
        plt.show()

    def scatter_sns(self,data=None,x=None,y=None,hue=None,hue_order=None,size=None,kind='scatter',jointplot=False,figsize=(8,8),exampleShow=False):
        '''散点图 
        data:DataFrame, array 数据源
        x,y,hue,size:变量名
        hue_order:hue排列
        exampleShow:是否显示示例
        kind:'''
        sns.set(style="whitegrid")
        if not jointplot:
            f, ax = plt.subplots(figsize=figsize)
            if exampleShow:
                hue_order=["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"]
                x,y,hue,size,data = "carat","price","clarity","depth",sns.load_dataset("diamonds")
            sns.despine(f, left=True, bottom=True)
            sns.scatterplot(x=x, y=y,
                            hue=hue, size=size,
                            hue_order=hue_order,
                            sizes=(1, 8), linewidth=0,
                            data=data, ax=ax)
        else:
            sns.jointplot(x=x, y=y, data=data, kind=kind,height=7)        
        plt.show()

    def bar_plot(self,data,x,hue=None,figsize=(10,6),ax=None):
        '''分组条形图。量。hue 仅支持0、1二分类'''
        sns.set(style="whitegrid")
        if hue is None:
            Ser = data[x].value_counts()
            Ser.plot(kind='bar',figsize=figsize)
        else:
            positives = data[data[hue]==1][x].value_counts()
            negatives = data[data[hue]==0][x].value_counts()
            df = pd.DataFrame([positives,negatives])
            df.index = [hue+'_1',hue+'_0']
            df.T.plot(kind='bar',stacked=True,figsize=figsize,ax=ax)
            ax.set_title(x)

    def distribute_numeric(self,data,x,hue,xlim):
        '''数值变量分布图'''
        facet = sns.FacetGrid(data, hue=hue,aspect=4)
        facet.map(sns.kdeplot,x,shade= True)
        facet.set(xlim=(0, data[x].max()))
        facet.add_legend()
        plt.xlim(xlim[0],xlim[1])

    def catplot_sns(self,data=None, x=None, y=None, hue=None,exampleShow=False):
        '''分组条形图 
        data:DataFrame, array 数据源
        x,y,hue:变量名
        exampleShow:是否显示示例'''
        sns.set(style="whitegrid")
        if exampleShow:
            x,y,hue,data = "class","survived","sex", sns.load_dataset("titanic")
            
        g = sns.catplot(x=x, y=y, hue=hue, data=data,
                        height=6, kind="bar",palette="muted") 
        g.despine(left=True)
        g.set_ylabels(y+" probability")
        plt.show()

    def pairplot_sns(self,data=None, hue=None,figsize=(10, 10),exampleShow=False):
        '''配对图 
        data:DataFrame, array 数据源
        hue:分类变量名
        exampleShow:是否显示示例'''
        sns.set(style="ticks")
        if exampleShow:
            hue,data ="species",sns.load_dataset("iris")
        sns.pairplot(data, hue=hue)    
        plt.show()

    def Andrews_plot(self,data=None,class_column=None,figsize=(10, 6),exampleShow=False):
        '''Andrews曲线
        将每个样本的属性值转化为傅里叶序列的系数来创建曲线,
        通过将每一类曲线标成不同颜色可以可视化聚类数据,
        属于相同类别的样本的曲线通常更加接近并构成了更大的结构。
        data:DataFrame 数据源
        class_column:类别变量名'''
        from pandas.plotting import andrews_curves
        if exampleShow:
            data,class_column = sns.load_dataset("iris"),'species'
        sns.set(style='whitegrid')
        f, ax = plt.subplots(figsize=figsize)
        andrews_curves(data, class_column, ax=ax)
        plt.show()

    def parallel_plot(self,data=None,class_column=None,figsize=(10, 6),exampleShow=False):
        '''平行坐标线
        可以看到数据中的类别以及从视觉上估计其他的统计量。
        使用平行坐标时，每个点用线段联接，每个垂直的线代表一个属性，一组联接的线段表示一个数据点。
        可能是一类的数据点会更加接近。
        data:DataFrame 数据源
        class_column:类别变量名'''
        from pandas.plotting import parallel_coordinates
        if exampleShow:
            data,class_column = sns.load_dataset("iris"),'species'
        sns.set(style='whitegrid')
        f, ax = plt.subplots(figsize=figsize)
        parallel_coordinates(data, class_column, ax=ax)
        plt.show()

    def radviz_plot(self,data=None,class_column=None,figsize=(10, 6),exampleShow=False):
        '''RadViz图
        基于基本的弹簧压力最小化算法（在复杂网络分析中也会经常应用）。
        简单来说，将一组点放在一个平面上，每一个点代表一个属性。
        iris案例中有四个点，被放在一个单位圆上，设想每个数据集通过一个弹簧联接到每个点上，
        弹力和他们属性值成正比（属性值已经标准化），数据集在平面上的位置是弹簧的均衡位置。
        不同类的样本用不同颜色表示。
        data:DataFrame 数据源
        class_column:类别变量名'''
        from pandas.plotting import radviz
        if exampleShow:
            data,class_column = sns.load_dataset("iris"),'species'
        sns.set(style='whitegrid')
        f, ax = plt.subplots(figsize=figsize)
        radviz(data, class_column, ax=ax)
        plt.show()


def tree_visualization(dt,x_list):
    '''决策树可视化'''
    dot_data = tree.export_graphviz(dt, out_file=None, feature_names = x_list, class_names = True, filled = True, rounded = True)
    return graphviz.Source(dot_data)