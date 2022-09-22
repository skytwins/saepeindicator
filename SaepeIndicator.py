from tkinter import END, Tk, Frame, Button, Text, Label
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import requests as r 
import pandas as pd
from scipy.signal import find_peaks
from scipy import stats
import time

interval = '1m'
symbol='BTCUSDT'
baseurl = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}"
tail = 200
rango = 0.009
npeaks = 10

ventana = Tk()
ventana.geometry('900x750')
ventana.wm_title('Alquimia Saepe Indicator')
ventana.minsize(width=642, height=535)
background = '#F0F0F0'
foreground = 'black'
frame = Frame(ventana,  bg=background, bd=3)
frame.pack(expand=1, fill='both')
fig, ax = plt.subplots(2, facecolor=background)
plt.style.use(['Solarize_Light2']) 
plt.subplots_adjust(top=0.9, wspace=0.3, hspace=0.3)
canvas = FigureCanvasTkAgg(fig, master = frame)  
canvas.get_tk_widget().pack(padx=5, pady=5 , expand=1, fill='both') 

def data():
    global df
    geturl = baseurl
    salir = False
    while not salir:
        try:
            resp = r.get(url = geturl)
            salir = True
        except:
            time.sleep(2)

    df = pd.DataFrame( eval(resp.text) , columns = ['dateTime','open','high','low','close','','','','','','',''])
    df.set_index('dateTime')
    df.dateTime = pd.to_datetime(df.dateTime, unit='ms')
    df.close = pd.to_numeric(df.close)
    df['lema'] = df.close.ewm(span=14).mean()
    df['sema'] = df.close.ewm(span=7).mean()
    df.lema = pd.to_numeric(df.lema)
    df.sema = pd.to_numeric(df.sema)
    #RSI
    rsi_period = 14
    chg = df['close'].diff(1)
    gain = chg.mask(chg<0,0)
    df['gain'] = gain
    loss = chg.mask(chg>0,0)
    df['loss'] = loss
    avg_gain = gain.ewm(com = rsi_period-1,min_periods=rsi_period).mean()
    avg_loss = loss.ewm(com = rsi_period-1,min_periods=rsi_period).mean()
    df['avg_gain'] = avg_gain
    df['avg_loss'] = avg_loss
    rsi = abs(avg_gain/avg_loss)
    rsi = -((1/(1+rsi))-0.5)
    rsi_peaks = 1/ (1 + rsi)
    rsi= rsi.rolling(2).mean()
    df['rsi'] = pd.to_numeric( rsi)
    dfpeaks = df.rsi.mask( df.rsi<rango)
    dfpeaksb = df.rsi.mask( df.rsi>-rango)
    global peaks 
    global bypeaks
    peaks, _ = find_peaks(dfpeaks)
    bypeaks, _ = find_peaks(-dfpeaksb)
    peaks = peaks[-npeaks:]
    bypeaks = bypeaks[-npeaks:]
    
def dibujar():	
    data()
    yb = df.close[bypeaks].values
    xb = bypeaks
    reg = stats.linregress(xb,yb)
    ys = df.close[peaks].values
    xs = peaks
    regs = stats.linregress(xs,ys)
    ax[0].clear()
    ax[0].set_facecolor("#FEFDEB")
    ax[0].grid(axis = 'y', color = '#FED999', linestyle = 'dashed')
    ax[1].clear()
    ax[1].set_facecolor("#FEFDEB")
    ax[1].grid(axis = 'y', color = '#FED999', linestyle = 'dashed')
    ax[0].set_title(f"PRECIO {symbol} en {interval}")
    ax[0].plot(df.close.tail(tail))
    ax[0].plot(df.close[peaks],'v', color = 'r')
    ax[0].plot(df.close[bypeaks],'^', color = 'g')
    ax[0].plot(xb, reg.intercept + reg.slope*xb, 'g', label='fitted line')
    ax[0].plot(xs, regs.intercept + regs.slope*xs, 'r', label='fitted line')
    
    yb = df.rsi[bypeaks].values
    xb = bypeaks
    reg = stats.linregress(xb,yb)
    ys = df.rsi[peaks].values
    xs = peaks
    regs = stats.linregress(xs,ys)
    ax[1].set_title("Alquimia Saepe Indicator (ASI)")
    ax[1].plot(df.rsi.tail(tail))
    ax[1].plot(df.rsi[peaks],'v', color = 'r')
    ax[1].plot(df.rsi[bypeaks],'^', color = 'g')
    ax[1].plot(xb, reg.intercept + reg.slope*xb, 'g', label='fitted line')
    ax[1].plot(xs, regs.intercept + regs.slope*xs, 'r', label='fitted line')
    fig.canvas.draw()
    fig.canvas.flush_events()
    ventana.after(1000,  dibujar)
    
def update():
    global symbol, interval, rango, npeaks, tail, baseurl
    symbol = symbol if inputtxt1.get("1.0", "end-1c") == "" else inputtxt1.get("1.0", "end-1c")
    interval = interval if inputtxt2.get("1.0", "end-1c") == "" else inputtxt2.get("1.0", "end-1c")
    rango = rango if inputtxt3.get("1.0", "end-1c") == "" else inputtxt3.get("1.0", "end-1c")
    npeaks = npeaks if inputtxt4.get("1.0", "end-1c") == "" else inputtxt4.get("1.0", "end-1c")
    tail = tail if inputtxt5.get("1.0", "end-1c") == "" else inputtxt5.get("1.0", "end-1c")
    symbol = symbol.upper()
    rango = float(rango)
    npeaks = int(npeaks)
    tail = int(tail)
    baseurl = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}"

def salir():
    exit()

if __name__ == "__main__":
    lb1 = Label(frame, text = "Symbol: ", bg = background, fg=foreground)
    inputtxt1 = Text(frame, height = 1, width = 15, bg = "light yellow") 
    inputtxt1.insert(END, symbol)
    lb2 = Label(frame, text = "Interval: ", bg = background, fg=foreground) 
    inputtxt2 = Text(frame, height = 1, width = 5, bg = "light yellow") 
    inputtxt2.insert(END, interval)
    lb3 = Label(frame, text = "Range: ", bg = background, fg=foreground) 
    inputtxt3 = Text(frame, height = 1, width = 5, bg = "light yellow") 
    inputtxt3.insert(END, rango)
    lb4 = Label(frame, text = "Npeaks: ", bg = background, fg=foreground) 
    inputtxt4 = Text(frame, height = 1, width = 5, bg = "light yellow") 
    inputtxt4.insert(END, npeaks)
    lb5 = Label(frame, text = "Tail: ", bg = background, fg=foreground) 
    inputtxt5 = Text(frame, height = 1, width = 5, bg = "light yellow") 
    inputtxt5.insert(END, tail)
    lb1.pack(side='left',expand=1)
    inputtxt1.pack(side='left',expand=1)
    lb2.pack(side='left',expand=1)
    inputtxt2.pack(side='left',expand=1)
    lb3.pack(side='left',expand=1)
    inputtxt3.pack(side='left',expand=1)
    lb4.pack(side='left',expand=1)
    inputtxt4.pack(side='left',expand=1)
    lb5.pack(side='left',expand=1)
    inputtxt5.pack(side='left',expand=1)
    Button(frame, text='Actualizar', width = 15, bg='green',fg='white', command=update).pack(pady =5,side='left',expand=1)
    Button(frame, text='Salir', width = 15, bg='green',fg='white', command=salir).pack(pady =5,side='left',expand=1)
    dibujar()
    #ventana.after(1000,  dibujar)
    ventana.mainloop()