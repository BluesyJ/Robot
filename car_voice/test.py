import pygame
import time

def play_wav(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)

if __name__ == "__main__":
    file_path = "xiaoaixiaoai.wav"  # 替换成您的.wav文件路径
    play_wav(file_path)
