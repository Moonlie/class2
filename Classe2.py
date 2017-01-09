# -*- coding: utf-8 -*-
import tushare as ts
import numpy as np


#获取最近工作日日期
def stocktoday():
    import datetime as dt
    today = dt.datetime.now()
    def Monday(today):
        return today.strftime("%Y-%m-%d")
    def Tuesday(today):
        return today.strftime("%Y-%m-%d")
    def Wednesday(today):
        return today.strftime("%Y-%m-%d")
    def Thursday(today):
        return today.strftime("%Y-%m-%d")
    def Friday(today):
        return today.strftime("%Y-%m-%d")
    def Saturday(today):
        return (today - dt.timedelta(days=1)).strftime("%Y-%m-%d")
    def Sunday(today):
        return (today - dt.timedelta(days=2)).strftime("%Y-%m-%d")
    Weekday={0:Monday,1:Tuesday,2:Wednesday,3:Thursday,4:Friday,5:Saturday,6:Sunday}
    stocktoday=Weekday.get(dt.datetime.weekday(today))(today)
    return stocktoday


def startday(interval):
    import datetime as dt
    today=dt.datetime.now()
    return (today - dt.timedelta(days=interval)).strftime("%Y-%m-%d")


def allcodes():
    return list(ts.get_today_all()['code'].sort_values())


def ma20(close):
    ma20=[]
    for i in range(0,20):
        ma20.append(np.mean(close[0:i+1]))
    for i in range(1,len(close)-19):
        ma20.append(np.mean(close[i:i+20]))
    return ma20


def macd(close):
    emafastperiod=12
    emaslowperiod=26
    difperiod=9
    emafast=[close[0]]
    emaslow=[close[0]]
    dif=[0]
    dea=[0]
    macd=[0]
    for i in range(1,len(close)):
        emafast.append(emafast[i-1]*(emafastperiod-1)/(emafastperiod+1)+close[i]*2/(emafastperiod+1))
        emaslow.append(emaslow[i-1]*(emaslowperiod-1)/(emaslowperiod+1)+close[i]*2/(emaslowperiod+1))
        dif.append(emafast[i]-emaslow[i])
        dea.append(dea[i-1]*(difperiod-1)/(difperiod+1)+dif[i]*2/(difperiod+1))
        macd.append(2*(dif[i]-dea[i]))
    return [dif,dea,macd]


#返回值：turnpoints列表的第一个元素为顶底位置列表；第二元素为顶底，0表示底，1表示顶
def maturnpoints(ma):
#判断移动平均线ma的方向，向下为0，向上为1，生成列表direction
    tmp=2*ma[0]-ma[1]
    if ma[0]==ma[1]:
        tmp=ma[0]+0.1
    direction=[]
    for i in range(len(ma)):
        if ma[i]>tmp:
            direction.append(1)
        elif ma[i]<tmp:
            direction.append(0)
        else:
            direction.append(direction[i-1])
        tmp=ma[i]
        
#通过direction找到ma的转折点，生成turnpoints，turnpoints列表的第一个元素为顶底位置列表；第二元素为顶底，0表示底，1表示顶
    turnpoints=[]
    topbottom=[]
    for i in range(1,len(direction)):
        if direction[i]<direction[i-1]:
            turnpoints.append(i-1)
            topbottom.append(1)
        elif direction[i]>direction[i-1]:
            turnpoints.append(i-1)
            topbottom.append(0)
        else:
            pass
        
#寻找时间间隔小于5的转折点：
    madel=[]
    skip=0
    for i in range(1,(len(turnpoints))):
        if skip:
            skip=0
        else:
            if (turnpoints[i]-turnpoints[i-1])<=5:
                madel.append(i-1)
                madel.append(i)
                skip=1
            else:
                skip=0
#删除时间间隔小于5的转折点：    
    for i in range(len(madel)-1,0,-1):
        del turnpoints[madel[i]]
        del topbottom[madel[i]]    

#计算斜率:
    maslope=[]
    for i in range(1,(len(turnpoints))):
        maslope.append((ma[turnpoints[i]]-ma[turnpoints[i-1]])/(turnpoints[i]-turnpoints[i-1]))
#通过斜率过滤次级别干扰的错误转折点
    delslope=[]
    for i in range(1,len(maslope)):
        if abs(maslope[i])<=0.3*abs(maslope[i-1]):
            delslope.append(i)
            delslope.append(i+1)
        else:
            pass
#找到重复元素，若有重复元素，其前一个元素不删除
    sloperepeat = []
    slipe=1
    for i in delslope:
        if delslope.count(i)>1 and slipe:
            sloperepeat.append(i)
            slipe=0
        else:
            slipe=1
    for i in sloperepeat:
        delslope.remove(i-1)
    delslope=list(set(delslope)) #去掉重复元素 
    if len(delslope):
        delslope.sort(reverse=True)#降序
        for i in delslope:
            del turnpoints[i]
            del topbottom[i]
    else:
        pass       
#只需要最后四段，留5个点\/\/
    del turnpoints[0:len(turnpoints)-5]
    del topbottom[0:len(topbottom)-5]
    turnpoints=[turnpoints,topbottom]            
    return turnpoints



#线段振幅    
def amplitude(code,khigh,klow,turnpoints):
    if len(turnpoints[0])==5:#数量达到5个
        if (turnpoints[1][0]):#且第一段为上涨
            peaks=[]
            for i in range(0,len(turnpoints[0])-1):
                if (turnpoints[1][i]):
                    peaks.append(min(klow[turnpoints[0][i]:turnpoints[0][i+1]]))
                else:
                    peaks.append(max(khigh[turnpoints[0][i]:turnpoints[0][i+1]]))
            lenths=[]
            for i in range(0,len(peaks)-1):
                lenths.append(abs(peaks[i]-peaks[i+1]))
            return lenths
        else:
            return [1,2,3]
    else:
        return [1,2,3]

    
def filter1(ktype='D',interval=250):
    codes=allcodes()
    firstfilt=[]
    for code in codes:
        result=filter1_1(code,ktype,interval)
        if result:
            firstfilt.append(result)
        else:
            pass
    print firstfilt
    return firstfilt

    
def filter1_1(code,ktype='D',interval=250):
    data=ts.get_k_data(code,ktype=ktype)[:interval]#ts.get_hist_data(code,ktype=ktype,start=startday(interval))返回的数量有问题
    ma=ma20(data['close'])
    khigh=(list(data['high']))
    klow=(list(data['low']))
    turnpoints=maturnpoints(ma)
    #找出振幅最大的一段：
    lenth123=amplitude(code,khigh,klow,turnpoints)
    longest_index=lenth123.index(max(lenth123))
    #进入5段判断
    line1_satisfy=filter1_2(turnpoints,klow,lenth123[0],longest_index)
    line2_satisfy=filter1_3(line1_satisfy,lenth123[0],lenth123[1])
    line3_satisfy=filter1_4(line2_satisfy,lenth123[1],lenth123[2])
    if line3_satisfy==1:
        return code
    else:
        pass
    
    
def filter1_4(line2_satisfy,lenth2,lenth3):
    if line2_satisfy==1:
        if lenth3/lenth2>0.7 and lenth3/lenth2<1.2:
            return 1
        else:
            return 0
    else:
        return 0


def filter1_3(line1_satisfy,lenth1,lenth2):
    if line1_satisfy==1:
        if lenth2/lenth1>0.35 and lenth2/lenth1<0.7:
            return 1
        else:
            return 0
    else:
        return 0
    
#第一步，判断振幅最大的一段是否符合    
def filter1_2(turnpoints,klow,lenth1,longest_index):
    if longest_index==0 and turnpoints[1][longest_index]==1: #最长的一段是第一段且为上涨段
        if (lenth1/klow[turnpoints[0][0]])>0.2:
            return 1
        else:
            return 0
    else:
        return 0


def bottomtype(khigh,klow):
    result,start,middle,end,khigh_tmp,klow_tmp,direction = [],0,0,0,khigh[0],klow[0],0
    for i in range(1,len(khigh)):
        if khigh_tmp>khigh[i] and klow_tmp>klow[i]:
            start=i-1
            direction=-1
            khigh_tmp=khigh[i]
            klow_tmp=klow[i]
        elif khigh_tmp<khigh[i] and klow_tmp<klow[i]:
            if direction<0:
                direction=1
                end=i
                middle=start+list(klow[start:end]).index(min(klow[start:end]))
                result.append([start,middle,end])
            else:
                direction=1
                khigh_tmp=khigh[i]
                klow_tmp=klow[i]
        else:
            if direction<1:
                khigh_tmp=min(khigh_tmp,khigh[i])
                klow_tmp=min(klow_tmp,klow[i])
            else:
                khigh_tmp=max(khigh_tmp,khigh[i])
                klow_tmp=max(klow_tmp,klow[i])
    return result


def btype_halt(khigh,klow):
    btype=bottomtype(khigh,klow)
    if btype:
        if btype[len(btype)-1][2]<len(khigh):
            index=btype[len(btype)-1][2]
            khigh_tmp,klow_tmp=khigh[index],klow[index]
            for i in range(index+1,len(khigh)):
                if khigh_tmp<khigh[i] and klow_tmp<klow[i]:
                    return i
                elif khigh_tmp>khigh[i] and klow_tmp>klow[i]:
                    break
                else:
                    khigh_tmp=max(khigh_tmp,khigh[i])
                    klow_tmp=max(klow_tmp,klow[i])                   
        else:
            pass            
    else:
        pass

    
def toptype(khigh,klow):
    result,start,middle,end,khigh_tmp,klow_tmp,direction = [],0,0,0,khigh[0],klow[0],0
    for i in range(1,len(khigh)):
        if khigh_tmp<khigh[i] and klow_tmp<klow[i]:
            start=i-1
            direction=1
            khigh_tmp=khigh[i]
            klow_tmp=klow[i]
        elif khigh_tmp>khigh[i] and klow_tmp>klow[i]:
            if direction>0:
                direction=-1
                end=i
                middle=start+list(khigh[start:end]).index(max(khigh[start:end]))
                result.append([start,middle,end])
            else:
                direction=-1
                khigh_tmp=khigh[i]
                klow_tmp=klow[i]
        else:
            if direction<1:
                khigh_tmp=min(khigh_tmp,khigh[i])
                klow_tmp=min(klow_tmp,klow[i])
            else:
                khigh_tmp=max(khigh_tmp,khigh[i])
                klow_tmp=max(klow_tmp,klow[i])
    return result


def ttype_halt(khigh,klow):
    ttype=toptype(khigh,klow)
    if ttype:
        if ttype[len(ttype)-1][2]<len(khigh):
            index=ttype[len(ttype)-1][2]
            khigh_tmp,klow_tmp=khigh[index],klow[index]
            for i in range(index+1,len(khigh)):
                if khigh_tmp>khigh[i] and klow_tmp>klow[i]:
                    return i
                elif khigh_tmp<khigh[i] and klow_tmp<klow[i]:
                    break
                else:
                    khigh_tmp=min(khigh_tmp,khigh[i])
                    klow_tmp=min(klow_tmp,klow[i])                   
        else:
            pass            
    else:
        pass
    

def filter2_1(code,ktype='D',interval=250):
    data=ts.get_k_data(code,ktype=ktype)[:interval]   
    ma=ma20(list(data['close']))
    turnpoints=maturnpoints(ma)
    minklow1=0.6*min((list(data['low']))[turnpoints[0][2]:turnpoints[0][3]])+0.4*max((list(data['high']))[turnpoints[0][3]:turnpoints[0][4]])#第三段降60%的点，做比较用
    index1=turnpoints[0][len(turnpoints[0])-1]
    khigh=(list(data['high']))[index1:]
    klow=(list(data['low']))[index1:]
    ma=ma[index1:]
    minklow2=0 #从ma开始下降到ma与khigh接触的最低点
#确保ma20 >khigh:
    index2=0
    for i in range(0,len(khigh)):
        if khigh[i]<ma[i]:
            index2=i
            break
        else:
            pass
    khigh=khigh[index2:]
    klow=klow[index2:]
    ma=ma[index2:]
#ma20与khigh相交:
    index3,index3_flag=0,0
    for i in range(0,len(khigh)):
        if khigh[i]>=ma[i]:
            index3=i
            index3_flag=1
            tmp=(list(data['high'])).index(max((list(data['high']))[turnpoints[0][3]:turnpoints[0][4]]))
            minklow2=min((list(data['low']))[tmp:turnpoints[0][4]+index2+index3])
            khigh=khigh[index3:]
            klow=klow[index3:]
            ma=ma[index3:]
            break
        else:
            pass
#klow降到比minklow2还低：
    index4,index4_flag=0,0
    for i in range(0,len(klow)):
        if klow[i]<minklow2 and index3_flag==1:
            index4=i
            index4_flag=1
            khigh=khigh[index4:]
            klow=klow[index4:]
            ma=ma[index4:]
            break
        else:
            pass
#寻找底分型：
    btype=bottomtype(khigh,klow)
    index5,index5_flag=0,0
    if index4_flag and btype:
        index5_flag=1
    else:
        pass
#底分型位置符合：
    if index5_flag and min(klow)<=minklow1:
        return code
    else:
        pass

    
def filter2(codes,ktype='D',interval=250):
    secondfilt=[]
    for code in codes:
        result=filter2_1(code,ktype,interval)
        if result:
            secondfilt.append(result)
        else:
            pass
    return secondfilt


#codes=['000422','000712','002068','002092','002142','002538','002602','002604','002685','300320','300450','600050','600293','600531','600613','600992','600993']
def filt(ktype='60',interval=250):
    return filter2(filter1(ktype,interval),ktype,interval)

def sendmail(codes,ktype='D',receiver='13559358220@126.com'):
    candlesticks(codes,ktype)#先生成蜡烛图文件 
    import smtplib
    from email.mime.image import MIMEImage
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.header import Header

# 第三方 SMTP 服务
    mail_host="smtp.163.com"  #设置服务器
    mail_user="stock_auto@163.com"    #用户名
    mail_pass="xsw2zaq1"   #口令 

    sender = '13559358220@126.com'
    receivers = receiver  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

    msgRoot = MIMEMultipart('related')
    msgRoot['From'] = '13559358220@126.com'
    msgRoot['To'] =  receiver
    msgRoot['Subject'] = Header("Class 2 auto", 'utf-8')

    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)


    mail_msg = """
<p>Class 2 auto with picture</p>
<p>图片演示：</p>
"""
#<p><img src="cid:image1"></p>

    for i in codes:
        mail_msg+="<p><img src=cid:"+str(i)+"-"+ktype+'F'+"></p>"+'\n'
        
    msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))

    for i in codes:
# 指定图片为当前目录
        fp = open(i+"-"+ktype+'F'+'.png', 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()

# 定义图片 ID，在 HTML 文本中引用
        msgImage.add_header('Content-ID', '<'+str(i)+"-"+ktype+'F'+'>')
        msgRoot.attach(msgImage)

    try:
        smtpObj = smtplib.SMTP() 
        smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(sender, receivers, msgRoot.as_string())
        smtpObj.quit()
        print "邮件发送成功"
    except smtplib.SMTPException:
        print "Error: 无法发送邮件"

        
#画图，生成png图片
def candlesticks(codes,ktype='D'):
    for i in codes:
        candlestick(i,ktype=ktype)


def candlestick(code,ktype='D'):
    import matplotlib.pyplot as plt
    import matplotlib.finance as mpf
    import pandas as pd
    data=ts.get_k_data(code,ktype=ktype)
    data['date_fake']=pd.Series(range(1,len(data)+2))
    if len(data)>230:
        ldata=len(data)-230
        data=data[ldata:]
    else:
        pass
    #pd.rolling_mean(data['close'], window=10, min_periods=1).plot(label = "10-day moving averages", ax=ax)
    tuple1 = [tuple(x) for x in data[['date_fake','open','high','low','close']].values]
    tuple2 = [tuple(x) for x in data[['date_fake','open','high','low','close','volume']].values]
    
    #开始画图ax1为k线，ax2为成交量
    fig = plt.figure()  
    fig.set_size_inches(11,5)
    fig.set_dpi(500)
    ax1 = plt.subplot2grid((4,4),(0,0),rowspan=4,colspan=4)
    #ax2 = plt.subplot2grid((4,4),(3,0),rowspan=1,colspan=4) 
    ax1.set_title(code+' '+ktype+'F')
    pd.rolling_mean(data['close'], window=20, min_periods=1).plot(label = "ma20", ax=ax1)#均线
    mpf.candlestick_ohlc(ax1, tuple1, width=0.5, colorup='r', colordown='g', alpha=1)#K线
    #mpf.volume_overlay3(ax2, tuple2, colorup='r', colordown='g', width=0.5, alpha=1.0)
    ##plt.setp(ax1.get_xticklables(),visible=False)
    plt.tick_params()
    plt.grid(True)
    ax1.autoscale()
    #ax2.autoscale()
    #plt.show()
    fig.savefig(code+'-'+ktype+'F'+'.png',dpi=100)

codes= filt('30')
sendmail(codes,'30','xmq1989@126.com')
codes= filt('60')
sendmail(codes,'60','xmq1989@126.com')
codes= filt('D')
sendmail(codes,'D','xmq1989@126.com')
