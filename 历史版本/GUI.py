import tkinter as tk
from  tkinter  import ttk

class windows():
    def __init__(self):
        self.year = '2020'
        self.month = '01'
        self.day = '01'
        self.new_year = '2020'
        self.new_month = '02'
        self.new_day = '01'
        self.win=tk.Tk() #构造窗体
        self.win.title('Sankaku') # 给窗口的可视化起名字
        self.win.geometry('400x120')  # 设定窗口的大小(长 * 宽)

        var=tk.StringVar()
        self.comboxlist_year = ttk.Combobox(self.win,textvariable=var,width=4,height=2)
        self.comboxlist_year["values"]=("2020","2019","2018","2017","2016","2015")
        self.comboxlist_year.current(0)
        self.comboxlist_year.bind("<<ComboboxSelected>>",self.get_year)
        self.comboxlist_year.place(x=50,y=60,anchor='s')

        var4=tk.StringVar()
        self.comboxlist_new_year = ttk.Combobox(self.win,textvariable=var4,width=4,height=2)
        self.comboxlist_new_year["values"]=("2020","2019","2018","2017","2016","2015")
        self.comboxlist_new_year.current(0)
        self.comboxlist_new_year.bind("<<ComboboxSelected>>",self.get_new_year)
        self.comboxlist_new_year.place(x=250,y=60,anchor='s')

        var2=tk.StringVar()
        self.comboxlist_month = ttk.Combobox(self.win,textvariable=var2,width=4,height=2)
        self.comboxlist_month["values"]=("01","02","03","04","05","06","07","08","09","10","11","12")
        self.comboxlist_month.current(0)
        self.comboxlist_month.bind("<<ComboboxSelected>>",self.get_month)
        self.comboxlist_month.place(x=100,y=60,anchor='s')

        var5=tk.StringVar()
        self.comboxlist_new_month = ttk.Combobox(self.win,textvariable=var5,width=4,height=2)
        self.comboxlist_new_month["values"]=("01","02","03","04","05","06","07","08","09","10","11","12")
        self.comboxlist_new_month.current(1)
        self.comboxlist_new_month.bind("<<ComboboxSelected>>",self.get_new_month)
        self.comboxlist_new_month.place(x=300,y=60,anchor='s')

        var3=tk.StringVar()
        self.comboxlist_day = ttk.Combobox(self.win,textvariable=var3,width=4,height=2)
        self.comboxlist_day["values"]=("01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31")
        self.comboxlist_day.current(0)
        self.comboxlist_day.bind("<<ComboboxSelected>>",self.get_day)
        self.comboxlist_day.place(x=350,y=60,anchor='s')

        var6=tk.StringVar()
        self.comboxlist_new_day = ttk.Combobox(self.win,textvariable=var6,width=4,height=2)
        self.comboxlist_new_day["values"]=("01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31")
        self.comboxlist_new_day.current(0)
        self.comboxlist_new_day.bind("<<ComboboxSelected>>",self.get_new_day)
        self.comboxlist_new_day.place(x=150,y=60,anchor='s')

        l = tk.Label(self.win, text='开始日期：',font=('pingfang', 12))
        l.place(x=66,y=30,anchor='s')

        n = tk.Label(self.win, text='结束日期：',font=('pingfang', 12))
        n.place(x=266,y=30,anchor='s')

        d = tk.Button(self.win, text='运行', font=('pingfang', 12), width=12, height=2, command=self.main)
        d.place(x=200,y=120,anchor='s')

        self.win.mainloop() #进入消息循环
        
    def get_year(self, *args):
        self.year = self.comboxlist_year.get()
    def get_month(self, *args):
        self.month = self.comboxlist_month.get()
    def get_day(self, *args):
        self.day = self.comboxlist_day.get()
    def get_new_year(self, *args):
        self.new_year = self.comboxlist_new_year.get()
    def get_new_month(self, *args):
        self.new_month = self.comboxlist_new_month.get()
    def get_new_day(self, *args):
        self.new_day = self.comboxlist_new_day.get()

    def main(self):
        start_date = f'{self.year}-{self.month}-{self.day}'
        end_Date = f'{self.new_year}-{self.new_month}-{self.new_day}'
        try:
            self.win.destroy()
        except:
            pass
        return f'{start_date}..{end_Date}'

if __name__ == "__main__":
    windows()