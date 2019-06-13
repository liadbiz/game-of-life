#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
    def __init__(self, unit_size=10, row_num=81, col_num=121, life_type="empty"):
        '''初始化'''
        super().__init__()
        self.MAZE_R = row_num
        self.MAZE_C = col_num
        self.padding = 5
        self.stepTime  = 1
        self.life_type = life_type
        self.UNIT = unit_size
        self.speed = 1000
        # self.density = 1
        self.set_lifes()
        self._initUI()
    
    def set_lifes(self):
        self.LIFES = []
        if self.life_type == "empty":
            self.LIFES = []
        elif self.life_type == "glider":
            self.LIFES = [(-1,1), (0,-1), (0,1), (1,0), (1,1)]
        elif self.life_type == "exploder":
            self.LIFES = [(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(0,-2),(0,2),(2,-2),(2,-1),(2,0),(2,1),(2,2)]
        elif self.life_type == "10-cell-row":
            self.LIFES = [(-5,0),(-4,0),(-3,0),(-2,0),(-1,0),(0,0),(1,0),(2,0),(3,0),(4,0)]
        elif self.life_type == "gosper-glider-gun":
            self.LIFES = [(-18,-5),(-18,-4),(-17,-5),(-17,-4),(-11,-4),(-11,-3),(-10,-5),(-10,-3),(-9,-5),
                    (-9,-4),(-2,-3),(-2,-2),(-2,-1),(-1,-3),(0,-2),(4,-6),(4,-5),(5,-7),(5,-5),(6,-7),(6,-6),
                    (6,5),(6,6),(7,5),(7,7),(8,5),(17,-7),(17,-6),(18,-7),(18,-6),(18,0),(18,1),(18,2),(19,0),(20,1)]
        elif self.life_type == "lightweight-spaceship":
            self.LIFES = [(-2,-1),(-2,1),(-1,-2),(0,-2),(1,-2),(1,1),(2,-2),(2,-1),(2,0)]
        elif self.life_type == "small-exploder":
            self.LIFES = [(-1,-1),(-1,0),(0,-2),(0,-1),(0,1),(1,-1),(1,0)]
        elif self.life_type == "tumbler":
            self.LIFES = [(-3,0),(-3,1),(-3,2),(-2,-3),(-2,-2),(-2,2),(-1,-3),(-1,-2),(-1,-1),(-1,0),(-1,1),
                    (1,-3),(1,-2),(1,-1),(1,0),(1,1),(2,-3),(2,-2),(2,2),(3,0),(3,1),(3,2)]
        if self.life_type != "empty":
            self.LIFES = [(c[0] + self.MAZE_C // 2, c[1] + self.MAZE_R // 2) for c in self.LIFES]

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
        self.resetButton= tk.Button(self.controlTopFrame1, text='reset', width=5)
        self.resetButton.pack(padx=5, pady=10, side=tk.LEFT)
        self.resetButton.bind('<Button>', self.reset)

        self.controlTopFrame2 = tk.Frame(self.controlFrame)
        self.controlTopFrame2.pack(side=tk.TOP)
        # 初始状态选择框
        initStates = ['10-cell-row', 'exploder', 'glider', 'gosper-glider-gun', 'lightweight-spaceship', 'small-exploder', 'tumbler']
        self.initStatesSelectBox = tk.Listbox(self.controlTopFrame2, bd=0, height=len(initStates))
        self.initStatesSelectBox.bind('<<ListboxSelect>>', self.resetInitStatus)
        for i, s in enumerate(initStates):
            self.initStatesSelectBox.insert(i, s)
        self.initStatesSelectBox.pack(side=tk.TOP, padx=15, pady=10)

        # 更新速度选择
        initSpeed = ['1px', '2px', '4px', '8px']
        self.initSpeedsSelectBox = tk.Listbox(self.controlTopFrame2, bd=0, height=len(initSpeed))
        for i, s in enumerate(initSpeed):
            self.initSpeedsSelectBox.insert(i, s)
        self.initSpeedsSelectBox.pack(side=tk.TOP, padx=15, pady=10)
        self.initSpeedsSelectBox.bind('<<ListboxSelect>>', self.setSpeed)

        # 格子密度选择
        # initDensity = ['1px', '2px', '4px', '8px']
        # self.initDensitySelectBox = tk.Listbox(self.controlTopFrame2, bd=0, height=len(initDensity))
        # for i, s in enumerate(initSpeed):
        #     self.initDensitySelectBox.insert(i, s)
        # self.initDensitySelectBox.pack(side=tk.TOP, padx=15, pady=10)
        # self.initSpeedsSelectBox.bind('<<ListboxSelect>>', self.changeDensity)
        
    def setSpeed(self, event):
        print("in envet setSpeed")
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        if value == "1px":
            self.speed = 1000
        elif value == "2px":
            self.speed = 500
        elif value == "4px":
            self.speed = 250
        elif value == "8px":
            self.speed = 125

    # def changeDensity(self, event):
    #     w = event.widget
    #     index = int(w.curselection()[0])
    #     value = w.get(index)
    #     if value == "1px":
    #         self.density= 1
    #     elif value == "2px":
    #         self.density= 2
    #     elif value == "4px":
    #         self.density= 4
    #     elif value == "8px":
    #         self.density= 8

    def resetInitStatus(self, event):
        print('in event resetInitStatus')
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        print(value)
        status = 0
        self.startStopButton.config(text="start")
        self.life_type = value
        self.set_lifes()
        self.update_ui()

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
        self.LIFES = new_lifes

    def update_ui(self):
        # old_coords = []
        print('in update ui')
        for l in self.life_controller:
            # old_coords.append(self.canvas.coords(l))
            self.canvas.delete(l)
        
        for c in self.LIFES:
            self.life_controller.append(self._draw_rect(c[0], c[1], 'black'))
        
        # self.LIFES = new_lifes

    def startOrStop(self, event):
        print('in event startorstop')
        global status
        if status == 1:
            self.startStopButton.config(text='start')
            status = 0
        elif status == 0:
            self.startStopButton.config(text='stop')
            status = 1

    def reset(self, event):
        print("in event reset")
        global status
        status = 0 # stop
        self.startStopButton.config(text='start')
        # reset lifes
        self.set_lifes()
        self.update_ui()
        
        
    def play(self):
        # 开始进化
        # 在这里写更新状态的逻辑，实际上是得到下一轮为活着的格子的坐标，然后调用更新的函数，这个过程每一个进化周期执行一次
        # print('in play')
        global staus
        if status == 1:
            self.update_lifes()
            self.update_ui()
            self.update()

        self.after(self.speed, self.play)



if __name__ == "__main__":
    grid = mainFrame(life_type = 'glider')
    grid.play()
    grid.mainloop()

