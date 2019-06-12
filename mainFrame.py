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
    def __init__(self, unit_size=20, row_num=30, col_num=30, life_type="empty"):
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
        padding = 5
        self.geometry('{0}x{1}'.format(h +2 * padding, w + 2 * padding)) #窗口大小
        self.canvas = tk.Canvas(self, bg='white', height= h + 2 * padding, width=w +2 * padding)

        # 画网格
        # 先画竖线
        for c in range(self.MAZE_C + 1):
            self.canvas.create_line(c * self.UNIT + padding, padding, c * self.UNIT + padding, h + padding)

        # 再画横线
        for r in range(self.MAZE_R + 1):
            self.canvas.create_line(padding, r * self.UNIT + padding, w + padding, r * self.UNIT + padding)

        # 画生命所在的地方
        for l in self.LIFES:
            self._draw_rect(l[0], l[1], 'black')
            self.canvas.pack() # 显示画作！

    def _draw_rect(self, x, y, color):
        '''画矩形，  x,y表示横,竖第几个格子'''
        padding = 5 # 内边距5px，参见CSS
        coor = [self.UNIT * x + padding, self.UNIT * y + padding, self.UNIT * (x+1) + padding, self.UNIT * (y+1) + padding]
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
