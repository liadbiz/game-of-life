#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import random
import time
import pickle
import pathlib
import os
import tkinter as tk
import itertools
import threading

status = 0

class mainFrame(tk.Tk):
    '''环境类（GUI）'''
    def __init__(self, unit_size=20, row_num=41, col_num=61, life_type="empty"):
        '''初始化'''
        super().__init__()
        self.MAZE_R = row_num
        self.MAZE_C = col_num
        self.padding = 5
        self.stepTime  = 1
        if life_type == "empty":
            self.LIFES = []
        elif life_type == "Glider":
            self.LIFES = [(-1,1), (0,-1), (0,1), (1,0), (1,1)]
            self.LIFES = [(c[0] + self.MAZE_C // 2, c[1] + self.MAZE_R // 2) for c in self.LIFES]
        self.UNIT = unit_size
        self._initUI()
    
    def _initUI(self):
        self.title('Game Of Life')
        h = self.MAZE_R * self.UNIT
        w = self.MAZE_C * self.UNIT
        # self.geometry('{0}x{1}'.format(h + 2 * self.padding, w + 2 * self.padding)) #窗口大小
        # 视图区
        self.padding = 5

        self.viewFrame = tk.Frame(self, height=h+self.padding, width=w+self.padding, bg='red')
        self.viewFrame.pack(side=tk.LEFT, padx=10, pady=10)
        self.canvas = tk.Canvas(self.viewFrame, height=h + self.padding , width=w + self.padding)

        # 画网格
        # 先画竖线
        for c in range(self.MAZE_C + 1):
            self.canvas.create_line(c * self.UNIT + self.padding,self.padding, c * self.UNIT + self.padding, h + self.padding)

        # 再画横线
        for r in range(self.MAZE_R + 1):
            self.canvas.create_line(self.padding, r * self.UNIT + self.padding, w + self.padding, r * self.UNIT + self.padding)

        # 画生命所在的地方
        self.life_controller = []
        for l in self.LIFES:
            rect = self._draw_rect(l[0], l[1], 'black')
            self.life_controller.append(rect)
            
         
        self.canvas.pack() 
        # 控制区域
        self.controlFrame = tk.Frame(self, width=30, height=30)
        self.controlFrame.pack(side=tk.TOP)

        self.controlTopFrame1 = tk.Frame(self.controlFrame)
        self.controlTopFrame1.pack(side=tk.TOP)
        # 开始暂停按钮
        self.startStopButton = tk.Button(self.controlTopFrame1, text='start', width=5)
        self.startStopButton.pack(padx=5, pady=10, side=tk.LEFT)
        self.startStopButton.bind('<Button>', self.startOrStop)

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
        self.padding = 5
        coor = [self.UNIT * x  + self.padding , self.UNIT * y  + self.padding , self.UNIT * (x+1) + self.padding , self.UNIT * (y+1) + self.padding]
        return self.canvas.create_rectangle(*coor, fill = color)
    

    def get_neighbors(self, l):
        x, y = l[0], l[1]
        r = [-1, 0, 1]
        x_ = [x+_ for _ in r]
        y_ = [y+_ for _ in r]
        neighbors = list(itertools.product(x_, y_))
        neighbors = [c for c in neighbors if c[0] >= 0 and c[0] <= self.MAZE_C and c[1] >=0 and c[1] <= self.MAZE_R ]
        return neighbors
         
        
    def  update_lifes(self):
        new_lifes = []
        to_be_updated = set()
        # print(self.LIFES)
        for l in self.LIFES:
            for n in self.get_neighbors(l):
                to_be_updated.add(n)
        for l in to_be_updated:
            # print(l)
            neighbors = self.get_neighbors(l)
            # print(neighbors)
            live_neighbors = sum(1 for n in neighbors if n in self.LIFES and (n[0] != l[0] or n[1] != l[1]))
            # print(live_neighbors)
            if (l in self.LIFES and (live_neighbors == 2 or live_neighbors == 3)) or (l not in self.LIFES and (live_neighbors == 3)):
                new_lifes.append(l)
        # print(new_lifes) 
        return new_lifes 

    def update_ui(self):
        # old_coords = []
        print('in update ui')
        for l in self.life_controller:
            # old_coords.append(self.canvas.coords(l))
            self.canvas.delete(l)
        
        self.life_controller.clear()
        new_lifes = self.update_lifes()
        for c in new_lifes:
            self.life_controller.append(self._draw_rect(c[0], c[1], 'black'))
        
        self.LIFES = new_lifes

    def startOrStop(self, event):
        print('in event ')
        global status
        if status == 1:
            self.startStopButton.config(text='start')
            status = 0
        elif status == 0:
            self.startStopButton.config(text='stop')
            status = 1

    def play(self):
        # 开始进化
        # 在这里写更新状态的逻辑，实际上是得到下一轮为活着的格子的坐标，然后调用更新的函数，这个过程每一个进化周期执行一次
        print('in play')
        global staus
        if status == 1:
            self.update_ui()
            self.update()

        self.after(1000, self.play)

    def _update_lifes(self):
        # destroy lifes last time
        pass
                
                

    def move_agent_to(self, state, step_time=0.01):
        '''移动玩家到新位置，根据传入的状态'''
        coor_old = self.canvas.coords(self.rect) # 形如[5.0, 5.0, 35.0, 35.0]（第一个格子左上、右下坐标）
        x, y = state % 6, state // 6 #横竖第几个格子
        self.padding = 5 # 内边距5px，参见CSS
        coor_new = [self.UNIT * x + self.padding, self.UNIT * y + self.padding, self.UNIT * (x+1) - self.padding, self.UNIT * (y+1) - self.padding]
        dx_pixels, dy_pixels = coor_new[0] - coor_old[0], coor_new[1] - coor_old[1] # 左上角顶点坐标之差
        self.canvas.move(self.rect, dx_pixels, dy_pixels)
        self.update() # tkinter内置的update!
        time.sleep(step_time)


if __name__ == "__main__":
    grid = mainFrame(life_type = 'Glider')
    grid.play()
    grid.mainloop()

