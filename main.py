import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Menu
from tkinter import filedialog
from tkinter import Entry
from tkinter import messagebox as msg

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from scipy import stats

import os
os.system('pause')
from pprint import pprint

# --------------------------------------------------------------
# Create instance
mainWindow = tk.Tk()
mainWindow.title("Target-Baseline(Impedance)")
mainWindow.geometry("700x400")
mainWindow.resizable(False, False)

# --------------------------------------------------------------
# Create a menu bar
menu_bar = Menu(mainWindow)
mainWindow.config(menu=menu_bar)
# 메뉴를 생성하고 메뉴 아이템 추가하기
file_menu = Menu(menu_bar, tearoff=0)  # 점선이 보이지 않음.


# file_menu.add_command(label="Exit")


def _quit():  # ******* 메인 이벤트 루프를 끝내기 위해 권장하는 파이썬다운 방식이다.
    mainWindow.quit()
    mainWindow.destroy()
    exit()


file_menu.add_command(label="Exit", command=_quit)
menu_bar.add_cascade(label="File", menu=file_menu)  # 중요

help_menu = Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About")
menu_bar.add_cascade(label="Help", menu=help_menu)  # 중요

# --------------------------------------------------------------
# ------------------- ImportFile 칸 ----------------------------
# --------------------------------------------------------------
ImportFile = ttk.LabelFrame(mainWindow, text="Import File: ")
ImportFile.grid(column=0, row=0, padx=8, pady=4)

# [Baseline 파일용] 다른 위젯을 한데 붙들어 모으기 위해서 Container frame 만들기
# 컨테이너 안에 라벨 넣기
baseline = ttk.Label(ImportFile, text="Baseline: ")
baseline.grid(column=0, row=0, padx=4, sticky=tk.W)

baseline_path = tk.StringVar()


def basefile_select():
    path = filedialog.askopenfilename(initialdir='',
                                      title='Select File',
                                      filetypes=(('csv files', '*.csv'),
                                                 ('all files', '*.*')))
    if path != '':
        baselineintro = ttk.Label(ImportFile, text="File load: complete.")
        baselineintro.grid(column=1, row=2, padx=4, sticky=tk.W)
    baseline_path.set(path)


baseline_path_result = Entry(ImportFile, width=50, textvariable=baseline_path)
baseline_path_result.grid(column=1, row=0, padx=8)

baseFileImport = ttk.Button(ImportFile, text="Get File", command=basefile_select)
baseFileImport.grid(column=2, row=0, padx=4)

baselineintro = ttk.Label(ImportFile, text="File check......")
baselineintro.grid(column=1, row=2, padx=4, sticky=tk.W)

# [Target 파일용]
target = ttk.Label(ImportFile, text="Target: ")
target.grid(column=0, row=1, padx=4, sticky=tk.W)

target_path = tk.StringVar()


def targetfile_select():
    path = filedialog.askopenfilename(initialdir='',
                                      title='Select File',
                                      filetypes=(('csv files', '*.csv'),
                                                 ('all files', '*.*')))
    target_path.set(path)
    if path != '':
        targetintro = ttk.Label(ImportFile, text="File load: complete.")
        targetintro.grid(column=1, row=3, padx=4, sticky=tk.W)


target_path_result = Entry(ImportFile, width=50, textvariable=target_path)
target_path_result.grid(column=1, row=1, padx=8)

targetFileImport = ttk.Button(ImportFile, text="Get File", command=targetfile_select)
targetFileImport.grid(column=2, row=1, padx=4)

targetintro = ttk.Label(ImportFile, text="File check......")
targetintro.grid(column=1, row=3, padx=4, sticky=tk.W)

# ---------------------------------------------------------
# ------------------- Analyse 칸 ----------------------------
# --------------------------------------------------------------
# 결과값을 보여주는 부분 구현하기
Analyse = ttk.LabelFrame(mainWindow, text="Result: ")
Analyse.grid(column=0, row=1, padx=8, pady=4, sticky=tk.W)

# ----------------------- Trimmed mean을 보여주는 표 제작 ----------------------------------------
trimmeanTable = ttk.Treeview(Analyse,
                             columns=['receptor?', 'Solution', 'Trimmed mean(30%)'],
                             displaycolumns=['receptor?', 'Solution', 'Trimmed mean(30%)']
                             )
trimmeanTable.grid(column=0, row=0, padx=4, pady=4, sticky=tk.W)

trimmeanTable.column('#0', width=0, stretch=False)
trimmeanTable.column('#1', width=100, minwidth=100, anchor='center', stretch=False)
trimmeanTable.heading('#1', text='receptor?', anchor='center')
trimmeanTable.column('#2', width=100, minwidth=100, anchor='center', stretch=False)
trimmeanTable.heading('#2', text='Solution', anchor='center')
trimmeanTable.column('#3', width=150, minwidth=150, anchor='center', stretch=False)
trimmeanTable.heading('#3', text='Trimmed mean (30%)', anchor='center')


# ----------------------- 최종 결과값을 보여주는 표 제작 ----------------------------------------
resultTable = ttk.Treeview(Analyse,
                           columns=['Trop-I 차이값', 'center point', 'Result'],
                           displaycolumns=['Trop-I 차이값', 'center point', 'Result']
                           )
resultTable.grid(column=1, row=0, padx=4, pady=4, sticky=tk.E)

resultTable.column('#0', width=0, stretch=False)
resultTable.column('#1', width=100, minwidth=100, anchor='center', stretch=False)
resultTable.heading('#1', text='Trop-I 차이값', anchor='center')
resultTable.column('#2', width=100, minwidth=100, anchor='center', stretch=False)
resultTable.heading('#2', text='center point', anchor='center')
resultTable.column('#3', width=100, minwidth=100, anchor='center', stretch=False)
resultTable.heading('#3', text='Result', anchor='center')


# ------------------------------------------------------------------------------------
# -------------------- .csv 파일을 불러와서 계산할 것들을 계산하기 ------------------------------
# ------------------------------------------------------------------------------------
def loadCSV():
    try:
        baselineCSV = pd.read_csv(baseline_path.get(), names=['Node', 'Tempe', 'Freq', 'Gain', 'Cali',
                                                              'Imp', 'Phase', 'Real', 'Imag', 'Mag', 'ms'])
        baseDF = baselineCSV[['Node', 'Freq', 'Imp', 'Imag']]
        # baseDF.info()

        targetCSV = pd.read_csv(target_path.get(), names=['Node', 'Tempe', 'Freq', 'Gain', 'Cali',
                                                          'Imp', 'Phase', 'Real', 'Imag', 'Mag', 'ms'])
        targetDF = targetCSV[['Node', 'Freq', 'Imp', 'Imag']]
        # targetDF.info()

        baseline_list = []
        for i in range(8):
            # 각 노드별로 돌면서...
            total_baseline_imp_list = []
            total_baseline_imp_list = baseDF.Imp[i * 100 : i * 100 + 100] # e.g. df.Imp[0:100] -> [0]~[99]까지의 값.
            baseline_list.append(list(total_baseline_imp_list[20:])) # 21kHz~100kHz까지의 임피던스만 고려한다.

        # pprint(baseline_list)

        target_list = []
        for i in range(8):
            # 각 노드별로 돌면서...
            total_target_imp_list = []
            total_target_imp_list = targetDF.Imp[i * 100 : i * 100 + 100]
            target_list.append(list(total_target_imp_list[20:])) # 마찬가지로 21kHz~100kHz까지의 임피던스만 고려한다.

        # pprint(target_list)

        final_baseline_no_receptor = []
        final_target_no_receptor = []
        for i in [0, 1, 2, 7]: # NO RECEPTOR: 1번, 2번, 3번, 9번 전극
            temp1 = []
            temp1 = baseline_list[i]
            temp2 = []
            temp2 = target_list[i]
            for j in range(len(temp1)):
                final_baseline_no_receptor.append(temp1[j])
                final_target_no_receptor.append(temp2[j])

        final_baseline_receptor = []
        final_target_receptor = []
        for i in [3, 4, 5, 6]: # RECEPTOR: 4번, 6번, 7번, 8번 전극
            temp1 = []
            temp1 = baseline_list[i]
            temp2 = []
            temp2 = target_list[i]
            for j in range(len(temp1)):
                final_baseline_receptor.append(temp1[j])
                final_target_receptor.append(temp2[j])

        # pprint(final_baseline)
        baseline_no_receptor = round(stats.trim_mean(final_baseline_no_receptor, 0.3), 4) # Trimmed mean(30%)
        # pprint(baseline_no_receptor)

        target_no_receptor = round(stats.trim_mean(final_target_no_receptor, 0.3), 4)
        # pprint(target_no_receptor)

        baseline_receptor = round(stats.trim_mean(final_baseline_receptor, 0.3), 4)
        # pprint(baseline_receptor)

        target_receptor = round(stats.trim_mean(final_target_receptor, 0.3), 4)
        # pprint(target_receptor)

        trimmeanInitial = [('no receptor', 'Target', f'{target_no_receptor}'),
                           ('', 'Baseline', f'{baseline_no_receptor}'),
                           ('receptor', 'Target', f'{target_receptor}'),
                           ('', 'Baseline', f'{baseline_receptor}')]
        for i in range(len(trimmeanInitial)):
            trimmeanTable.insert('', 'end', values=trimmeanInitial[i])

        no_receptor = round((target_no_receptor - baseline_no_receptor) / baseline_no_receptor, 4)
        # print(no_receptor)
        receptor = round((target_receptor - baseline_receptor) / baseline_receptor, 4)
        total_avg = no_receptor - receptor
        # pprint(no_receptor, receptor)

        resultTableInitial = [('Pt-Au\n(ch: 1, 2, 3, 9)', '5', f'{no_receptor}'),
                              ('Pt-Pt\n(ch: 4, 6, 7, 8)', '5', f'{receptor}'),
                              ('total difference\n(receptor-no receptor', 'total avg', f'{total_avg}')
                              ]
        for i in range(len(resultTableInitial)):
            resultTable.insert('', 'end', values=resultTableInitial[i])


    except FileNotFoundError:
        msg.showerror('Select file first.')


Calculate = ttk.Button(Analyse, text="Calculate", command=loadCSV)
Calculate.grid(column=0, row=1, padx=4, pady=4)


Reset = ttk.Button(Analyse, text="Reset")
Reset.grid(column=1, row=1, padx=4, pady=4)

# ===================
# Start GUI
# ===================
mainWindow.mainloop()
