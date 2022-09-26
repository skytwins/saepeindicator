# ************************************************************************
# *  O   Codigo de la interface grafica desarrollado por:                *
# * <j>  @JotaEle Copyright (c) 2022                                     *
# * / \  Creditos a @LaAlquimia creador de la Alquimia Saepe indicator   *
# ************************************************************************
from tkinter import END, Tk, Frame, Button, Text, Label, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib
import requests as r 
import pandas as pd
from scipy.signal import find_peaks
from scipy import stats
import time

interval = '1m'
symbol='BTCUSDT'
baseurl = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}"
tail = 200
rango = 0.065
npeaks = 5

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
matplotlib.rcParams['timezone'] = 'GMT-5'
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

    df = pd.DataFrame( eval(resp.text) , columns = ['dateTime','open','high','low','close','volume','closeTime','','','','',''])
    df.set_index('closeTime')
    df.closeTime = pd.to_datetime(df.closeTime, unit='ms')
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
    dfpeaks = df.rsi#.mask( df.rsi<rango)
    dfpeaksb = df.rsi#.mask( df.rsi>-rango)
    global peaks 
    global bypeaks
    peaks, _ = find_peaks(dfpeaks,prominence=rango, width=2)
    bypeaks, _ = find_peaks(-dfpeaksb, prominence=rango, width=2)
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
    ax[0].plot(df.closeTime.tail(tail), df.close.tail(tail))
    ax[0].plot(df.closeTime.tail(tail)[peaks],df.close[peaks],'v', color = 'r')
    ax[0].plot(df.closeTime.tail(tail)[bypeaks],df.close[bypeaks],'^', color = 'g')
    ax[0].plot(df.closeTime.tail(tail)[xb], reg.intercept + reg.slope*xb, "--",color='g')
    ax[0].plot(df.closeTime.tail(tail)[xs], regs.intercept + regs.slope*xs, "--",color='r')
    
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
    ax[1].plot(xb, reg.intercept + reg.slope*xb, "--",color='g')
    ax[1].plot(xs, regs.intercept + regs.slope*xs,"--", color = 'r')
    fig.canvas.draw()
    fig.canvas.flush_events()
    ventana.after(1000,  dibujar)
    
def update_graphic(event):
    global symbol, interval, rango, npeaks, tail, baseurl
    symbol = symbol if cbx_symbols.get() == "" else cbx_symbols.get()
    interval = interval if cbx_intervals.get() == "" else cbx_intervals.get()
    rango = rango if inputtxt3.get("1.0", END) == "\n" else inputtxt3.get("1.0", END)
    npeaks = npeaks if cbx_npeaks.get() == "" else cbx_npeaks.get()
    tail = tail if cbx_tails.get() == "" else cbx_tails.get()
    symbol = symbol.upper()
    rango = float(rango)
    npeaks = int(npeaks)
    tail = int(tail)
    baseurl = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}"

def salir():
    exit()

def getSymbolsTradingFutures():
    # Obtiene la lista completa de los simbolos de futuros tradeables en USDT
    symbols = []
    endPoint = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    resp = r.get(endPoint)
    respuesta = resp.json()
    coins = respuesta['symbols']
    for coin in coins:    
        symbol = coin["symbol"]
        status = coin['status']
        if status == "TRADING" and symbol[-4:] == 'USDT':
            symbols.append(symbol)
    return symbols

if __name__ == "__main__":
    list_symbols = getSymbolsTradingFutures()
    list_intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
    list_npeaks = [x for x in range(1,11)]
    list_tails = [100, 200, 300, 400, 500]
    lb1 = Label(frame, text = "Symbol: ", bg = background, fg=foreground)
    cbx_symbols = ttk.Combobox(frame, width=20, state="readonly", values=list_symbols)
    cbx_symbols.set("BTCUSDT")
    lb2 = Label(frame, text = "Interval: ", bg = background, fg=foreground) 
    cbx_intervals = ttk.Combobox(frame, width=6, state="readonly", values=list_intervals)
    cbx_intervals.set("1m")
    lb3 = Label(frame, text = "Range: ", bg = background, fg=foreground) 
    inputtxt3 = Text(frame, height = 1, width = 6, bg = "light yellow") 
    inputtxt3.insert(END, rango)
    lb4 = Label(frame, text = "Npeaks: ", bg = background, fg=foreground) 
    cbx_npeaks = ttk.Combobox(frame, width=6, state="readonly", values=list_npeaks)
    cbx_npeaks.set("5")
    lb5 = Label(frame, text = "Tail: ", bg = background, fg=foreground) 
    cbx_tails = ttk.Combobox(frame, width=6, state="readonly", values=list_tails)
    cbx_tails.set(200)
    lb1.pack(side='left',expand=1)
    cbx_symbols.pack(side='left',expand=1)
    lb2.pack(side='left',expand=1)
    cbx_intervals.pack(side='left',expand=1)
    lb3.pack(side='left',expand=1)
    inputtxt3.pack(side='left',expand=1)
    lb4.pack(side='left',expand=1)
    cbx_npeaks.pack(side='left',expand=1)
    lb5.pack(side='left',expand=1)
    cbx_tails.pack(side='left',expand=1)
    cbx_symbols.bind("<<ComboboxSelected>>", update_graphic)
    cbx_intervals.bind("<<ComboboxSelected>>", update_graphic)
    inputtxt3.bind('<KeyRelease>', update_graphic)
    cbx_npeaks.bind("<<ComboboxSelected>>", update_graphic)
    cbx_tails.bind("<<ComboboxSelected>>", update_graphic)
    Button(frame, text='Salir', width = 15, bg='green',fg='white', command=salir).pack(pady=5,side='left',expand=1)
    dibujar()
    ventana.mainloop()
