"""
羊了个羊解法
"""

import random
import time
import cv2 as cv
import win32gui
import pyautogui as gui
import numpy as np
import os

# only 7 slots max, over 7 will be game over
MAX_SLOTS = 7
# if there are 3 connected, then they will be erased
CONNECTION = 3

# there are 15 different types
# grass
# wood
# veggi
# fork
# brush
# fire
# scissor
# carrot
# corn
# glove
# wool
# pink
# bell
# milk
# bucket
icon_list = ['bell.png', 'bucket.png', 'carrot.png', 'corn.png', 'fire.png', 'fork.png', 'grass.png', 'glove.png',
             'milk.png', 'pink.png', 'scissor.png', 'veggi.png', 'wood.png', 'wool.png', 'brush.png']

# validate all names
for icon in icon_list:
    if not os.path.exists('../icon/' + icon):
        print(f'"{icon}" not found, please make sure the icon file is in the same folder as this script')
        exit(1)

class SheepSolver:

    def __init__(self):
        self.slots = {}
        for icon in icon_list:
            self.slots[icon] = 0

        # find the location of program scrcpy
        def enumHandler(hwnd, lParam):
            window_name = win32gui.GetWindowText(hwnd).lower()
            # my device name
            if 'sm-f916b' in window_name:
                rect = win32gui.GetWindowRect(hwnd)
                x = rect[0]
                y = rect[1]
                w = rect[2] - x
                h = rect[3] - y
                # ignore (1, 1)
                if (w > 100 or h > 100):
                    self.location = [x, y, w, h]
        win32gui.EnumWindows(enumHandler, None)
        print(self.location)

    def _slotCount(self):
        """
        Count the number of slots
        """
        counter = 0
        for slot in self.slots:
            counter += self.slots[slot]
        return counter

    def _gamescreen(self):
        """
        take a screenshot based on self.location
        """
        # take a screenshot
        img = gui.screenshot(region=self.location)
        # opencv format
        img = cv.cvtColor(np.array(img), cv.COLOR_RGB2BGR)
        return img

    def _find(self, name: str) -> bool:
        """
        find the img in the board using opencv, return the location
        """
        img = '../icon/' + name
        if not os.path.exists(img):
            raise FileNotFoundError('{} not found'.format(img))

        # read the image
        img = cv.imread(img)
        # convert to gray
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        game = self._gamescreen()
        # convert to gray
        game = cv.cvtColor(game, cv.COLOR_BGR2GRAY)
        
        # find the image
        res = cv.matchTemplate(game, img, cv.TM_CCOEFF_NORMED)
        # get the location
        loc = np.where(res >= 0.9)
        # remove very close matches
        matches = []
        # sort the matches
        for pt in sorted(zip(*loc[::-1])):
            if len(matches) == 0:
                matches.append(pt)
            else:
                # make sure it is too close to any points in matches
                if not any([abs(pt[0] - x[0]) < 10 and abs(pt[1] - x[1]) < 10 for x in matches]):
                    matches.append(pt)
        
        # draw the matches
        for pt in matches:
            cv.rectangle(game, pt, (pt[0] + 50, pt[1] + 50), (0, 0, 255), 2)
        print("There are {} matches of {}".format(len(matches), name))
        return matches

    def _tap(self, name: str):
        """
        Tap the first match
        """
        matches = self._find(name)
        if len(matches) == 0:
            return
        pt = matches[0]
        self._select(name, pt)

    def _select(self, icon: str, loc):
        img = cv.imread('../icon/' + icon)
        # get the size
        h, w, _ = img.shape
        # get the center
        x = loc[0] + w // 2
        y = loc[1] + h // 2

        # tap the center
        gui.moveTo(self.location[0] + x, self.location[1] + y, duration=0.1)
        gui.click(clicks=2)

    def solve(self):
        while True:
            print(self.slots)
            game_over = self._find('revive.png')
            if len(game_over) > 0:
                print('Game Over')
                self._tap('nothanks.png')
                time.sleep(1)
                self._tap('retry.png')
                time.sleep(3)
                continue

            retry = self._find('retry.png')
            if len(retry) > 0:
                print('Retry')
                self._tap('retry.png')
                time.sleep(3)
                continue

            nothanks2 = self._find('nothanks2.png')
            if len(nothanks2) > 0:
                print('No Thanks')
                self._tap('nothanks2.png')
                time.sleep(3)
                continue

            # analyze the board
            info = {}
            for icon in icon_list:
                info[icon] = self._find(icon)

            # if there are 3 connected, erase them
            did_something = False
            for icon in info:
                curr_icon = info[icon]
                count = len(curr_icon)
                # also check the slots
                count += self.slots[icon]
                if count < CONNECTION:
                    continue
                
                did_something = True
                # take random first two
                points = random.sample(curr_icon, 3)
                print(points)
                for pt in points:
                    self._select(icon, pt)
                    self.slots[icon] += 1
                    # erase if there are three connected
                    if self.slots[icon] >= 3:
                        self.slots[icon] -= 3
                        print('Erase {}'.format(icon))

            if not did_something:
                # get all options
                options = []
                for icon in info:
                    curr_icon = info[icon]
                    if len(curr_icon) > 0:
                        options.append(icon)
                
                choice = random.choice(options)
                print('Randomly choose {}'.format(choice))

                for icon in info:
                    curr_icon = info[icon]
                    if icon == choice:
                        self._select(icon, random.choice(curr_icon))
                        break
            time.sleep(2)
if __name__ == "__main__":
    solver = SheepSolver()
    solver.solve()
