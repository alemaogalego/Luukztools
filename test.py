import keyboard
import pyautogui as py


center = (956, 346)

def revive():
    pos_poke = (32, 59)
    py.moveTo(pos_poke)
    py.click(button='right')
    keyboard.press_and_release('r')
    py.moveTo(pos_poke)
    py.click(button='right')

while True:
    keyboard.wait('h')
    print(py.position())