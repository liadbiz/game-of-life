#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import random
import time
import pickle
import pathlib
import os
import tkinter as tk

class mainFrame(tk.Tk):
    '''环境类（GUI）'''
    def __init__(self, unit_size=20, row_num=41, col_num=61, life_type="empty"):
        '''初始化'''
        super().__init__()
        self.MAZE_R = row_num
        self.MAZE_C = col_num
        self.STATES = [[0] * self.MAZE_C for _ in range(self.MAZE_R)]
        if life_type == "empty":
            self.LIFES = []
        elif life_type == "sample":
            self.LIFES = [(0,0), (1, 0), (1, 1), (1, 2), (2, 2), (3, 2), (3, 3)]
        self.UNIT = unit_size
        self._initUI()
    
    def _initUI(self):
        self.title('Game Of Life')
        h = self.MAZE_R * self.UNIT
        w = self.MAZE_C * self.UNIT
        # self.geometry('{0}x{1}'.format(h + 2 * padding, w + 2 * padding)) #窗口大小
        # 视图区
        padding = 5

        self.viewFrame = tk.Frame(self, height=h+padding, width=w+padding, bg='red')
        self.viewFrame.pack(side=tk.LEFT, padx=10, pady=10)
        self.canvas = tk.Canvas(self.viewFrame, height=h + padding , width=w + padding)

        # 画网格
        # 先画竖线
        for c in range(self.MAZE_C + 1):
            self.canvas.create_line(c * self.UNIT + padding,padding, c * self.UNIT + padding, h + padding)

        # 再画横线
        for r in range(self.MAZE_R + 1):
            self.canvas.create_line(padding, r * self.UNIT + padding, w + padding, r * self.UNIT + padding)

        # 画生命所在的地方
        for l in self.LIFES:
            self._draw_rect(l[0] + self.MAZE_C  // 2, l[1] + self.MAZE_R // 2, 'black')
         
        self.canvas.pack() 
        # 控制区域
        self.controlFrame = tk.Frame(self, width=30, height=30)
        self.controlFrame.pack(side=tk.TOP)

        self.controlTopFrame1 = tk.Frame(self.controlFrame)
        self.controlTopFrame1.pack(side=tk.TOP)
        # 开始暂停按钮
        self.startStopButton = tk.Button(self.controlTopFrame1, text='start', width=5)
        self.startStopButton.pack(padx=5, pady=10, side=tk.LEFT)

        # 更新按钮， 只有开始暂停按钮为暂停状态时才显示更新按钮，此时为手动更新
        self.updateButton = tk.Button(self.controlTopFrame1, text='update', width=5)
        self.updateButton.pack(padx=5, pady=10, side=tk.LEFT)

        self.controlTopFrame2 = tk.Frame(self.controlFrame)
        self.controlTopFrame2.pack(side=tk.TOP)
        # 初始状态选择框
        initStates = ['10-cell-row', 'exploder', 'glider', 'gosper-glider-gun', 'lightweight-spaceship', 'small-exploder', 'tumbler']
        self.initStatesSelectBox = tk.Listbox(self.controlTopFrame2, bd=0, height=len(initStates))
        for i, s in enumerate(initStates):
            self.initStatesSelectBox.insert(i, s)
        self.initStatesSelectBox.pack(side=tk.TOP, padx=15, pady=10)

        # 更新速度选择
        initSpeed = ['1px', '2px', '3px', '4px']
        self.initSpeedsSelectBox = tk.Listbox(self.controlTopFrame2, bd=0, height=len(initSpeed))
        for i, s in enumerate(initSpeed):
            self.initSpeedsSelectBox.insert(i, s)
        self.initSpeedsSelectBox.pack(side=tk.TOP, padx=15, pady=10)

        # 格子密度选择
        initDensity = ['1px', '2px', '3px']
        self.initDensitySelectBox = tk.Listbox(self.controlTopFrame2, bd=0, height=len(initDensity))
        for i, s in enumerate(initSpeed):
            self.initDensitySelectBox.insert(i, s)
        self.initDensitySelectBox.pack(side=tk.TOP, padx=15, pady=10)

    def _draw_rect(self, x, y, color):
        '''画矩形，  x,y表示横,竖第几个格子'''
        padding = 5
        coor = [self.UNIT * x + padding , self.UNIT * y + padding , self.UNIT * (x+1) + padding , self.UNIT * (y+1) + padding]
        return self.canvas.create_rectangle(*coor, fill = color)

    def move_agent_to(self, state, step_time=0.01):
        '''移动玩家到新位置，根据传入的状态'''
        coor_old = self.canvas.coords(self.rect) # 形如[5.0, 5.0, 35.0, 35.0]（第一个格子左上、右下坐标）
        x, y = state % 6, state // 6 #横竖第几个格子
        padding = 5 # 内边距5px，参见CSS
        coor_new = [self.UNIT * x + padding, self.UNIT * y + padding, self.UNIT * (x+1) - padding, self.UNIT * (y+1) - padding]
        dx_pixels, dy_pixels = coor_new[0] - coor_old[0], coor_new[1] - coor_old[1] # 左上角顶点坐标之差
        self.canvas.move(self.rect, dx_pixels, dy_pixels)
        self.update() # tkinter内置的update!
        time.sleep(step_time)

if __name__ == "__main__":
    grid = mainFrame(life_type = 'sample')
    grid.mainloop()
