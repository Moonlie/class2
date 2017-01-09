# -*- coding: UTF-8 -*-
def sendmail(codes,ktype='D',receiver='13559358220@126.com'):
    candlesticks(codes,ktype)#先生成蜡烛图文件 
    import smtplib
    from email.mime.image import MIMEImage
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.header import Header

# 第三方 SMTP 服务
    mail_host="smtp.126.com"  #设置服务器
    mail_user="xmq1989@126.com"    #用户名
    mail_pass="******"   #口令 

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
sendmail(codes,'30','13559358220@126.com')
codes= filt('60')
sendmail(codes,'60','13559358220@126.com')
codes= filt('D')
sendmail(codes,'D','13559358220@126.com')
