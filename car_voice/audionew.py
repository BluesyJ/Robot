import pyaudio
import wave
import time
import numpy as np
from scipy.io import wavfile as wav
# import noisereduce as nr
import librosa
import soundfile as sf
import serial
import subprocess
import re
import yaml
import os
os.environ["interaput_event"] = '0'


class Audio(object):
    def __init__(self, channels=1, rate=48000):
        """
        参数:
        - channels: 音频通道数，默认为1
        - rate: 音频采样率，默认为48000
        - output: 输出音频文件路径，默认为"wavfiles/output.wav"
        """
        with open(r'D:\UserFiles\文件\研究生\工作项目\机器人框架v2\config.yaml', 'r', encoding='utf-8') as config_file:
            config = yaml.safe_load(config_file)

        self.init_wav_path = config['car_voice']['init_wav_path']
        self.change_wav_path = config['car_voice']['change_wav_path']
        self.THRESHOLD = config['car_voice']['threshold']
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self.audio = pyaudio.PyAudio()
        self.output = config['car_voice']['output_wav_path']
        self.recording = False
        self.save_flag = False
        self.end_flag = False
        self.device_name = config['car_voice']['mic_name']

    def record(self,  signore = False, listen_event = False):
        """
        录制音频的方法

        参数:
        - THRESHOLD: 声音阈值，默认为3000
        - device_name: 音频设备名称，默认为'USB_MIC: Audio (hw:1,0)'

        返回值:
        无
        """

        # start Recording
        self.recording = False
        self.save_flag = False
        self.end_flag = False
        self.audio = pyaudio.PyAudio()
        input_index = self.get_info(self.device_name)
        stream = self.audio.open(format=self.FORMAT,
                                 channels=self.CHANNELS,
                                 rate=self.RATE,
                                 input=True,
                                 input_device_index=input_index,
                                 frames_per_buffer=self.CHUNK)
        
        # print("recording...")
        
        before_frames = []
        frames = []
        temp = []
        silent_frames = 0
        record_frames = 0
        unmanned_frames = 0
        voice_frames = 0
        while True:
            print(os.environ["interaput_event"])
            if os.environ["interaput_event"] == '0':#环境变量没被修改就没有中断
                # 读取音频数据
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                #提前存20帧数据
                if len(before_frames) >= 20:
                    before_frames.pop(0)
                    before_frames.append(data)
                else:
                    before_frames.append(data)
                audio_data = np.frombuffer(data, dtype=np.int16)
                volume = np.max(np.abs(audio_data))
                # print(volume)

                if volume > self.THRESHOLD and not self.recording:
                    # voice_frames += 1
                    # temp.append(data)

                    # if voice_frames >= 3:
                    print("检测到声音！开始录音...")

                    self.recording = True
                    #将20帧数据加到最开始
                    before_frames.pop(-1)
                    frames.extend(before_frames)

                        # output = subprocess.check_output(['pactl', 'list'], text=True)
                        # print(output)
                        # frames.extend(temp)
                # elif volume <= THRESHOLD and not self.recording:
                #     temp = []
                #     voice_frames = 0

                if not self.recording: #长时间没有声音就关闭

                    #unmanned_frames += 1 #注释这一行取消自动关闭
                    if unmanned_frames >= int(self.RATE / self.CHUNK * 60) or signore:
                        self.end_flag = True
                        break
                elif self.recording:

                    record_frames += 1
                    frames.append(data)
                    if volume <= self.THRESHOLD: # 如果音量小于阈值，则判断为无声音状态

                        silent_frames += 1
                        # 当连续检测到一定数量的无声音帧时，停止录制

                        if silent_frames >= int(1.0 * self.RATE / self.CHUNK) or record_frames >= int(self.RATE / self.CHUNK * 10):
                            print("声音停止，录音结束.")
                            print(len(frames))
                            self.recording = False
                            break


                    else:

                        silent_frames = 0
                    
        if not self.end_flag:    
            print("finished recording")
            # stop Recording
            stream.stop_stream()
            stream.close()
            self.audio.terminate()
            wavefile = wave.open(self.init_wav_path, 'wb')
            wavefile.setnchannels(self.CHANNELS)
            wavefile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wavefile.setframerate(self.RATE)
            wavefile.writeframes(b''.join(frames))
            wavefile.close()
            self.resample_wav(self.init_wav_path, self.change_wav_path, 48000, 16000)
            # data = self.reduce_noise('wavfiles/init.wav', 'wavfiles/noise.wav')
            # self.increase_volume(data, self.output)
            print('finished saved')
            self.save_flag = True
       

    def stop(self):
        self.recording = False
        self.save_flag = False
        self.end_flag = False

    def play(self, filename):
        wf = wave.open(filename, 'rb')

        # open stream
        stream = self.audio.open(format=self.audio.get_format_from_width(wf.getsampwidth()),
                                 channels=wf.getnchannels(),
                                 rate=wf.getframerate(),
                                 output=True)

        # read data
        data = wf.readframes(self.CHUNK)

        # play stream
        while data:
            stream.write(data)
            data = wf.readframes(self.CHUNK)

        # stop stream
        stream.stop_stream()
        stream.close()

        # close PyAudio
        #self.audio.terminate()
        wf.close()

    def save_wav(self, filename, frames):
        wavefile = wave.open(filename, 'wb')
        wavefile.setnchannels(self.CHANNELS)
        wavefile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wavefile.setframerate(self.RATE)
        wavefile.writeframes(frames)
        wavefile.close()

    def reduce_noise(self, src_wav, noise_wav):
        t = time.time()

        rate, data = wav.read(src_wav)
        _,noisy_part =  wav.read(noise_wav)
        
        reduced_noise = nr.reduce_noise(y=data, y_noise=noisy_part, sr=self.RATE)
        print(time.time()-t)
        return reduced_noise
       
        # with wave.open(result_wav, 'wb') as wf:
        #     wf.setnchannels(self.CHANNELS)
        #     wf.setsampwidth(2)
        #     wf.setframerate(self.RATE)
        #     wf.writeframes(b''.join(reduced_noise))

    def increase_volume(self, src_wav, result_wav, gain=3):
        t = time.time()
        # sample_rate, audio_data = wav.read(src_wav)
        audio_data = src_wav
        adjusted_audio = audio_data.astype(np.float64) * gain
        adjusted_audio = np.clip(adjusted_audio, -32768, 32767)   # 防止溢出
        adjusted_audio = adjusted_audio.astype(np.int16)
        wav.write(result_wav, self.RATE, adjusted_audio)
        print(time.time()-t)

    def resample_wav(self, input_file, output_file, input_sample_rate, target_sample_rate):
        # 读取输入文件
        data, samplerate = sf.read(input_file)

        # 计算采样率比例
        ratio = input_sample_rate / target_sample_rate

        # 使用插值方法进行重采样
        resampled_data = np.interp(np.arange(0, len(data), ratio), np.arange(len(data)), data)

        # 将重采样后的数据写入输出文件
        sf.write(output_file, resampled_data, target_sample_rate)

    def change_rate(self, src_wav, out_wav, target_sample_rate):
        print(1)
        src_sig, sr = sf.read(src_wav)  
        #resample 入参三个 音频数据 原采样频率 和目标采样频率
        print(2)
        
        try:


            print(src_sig, sr, target_sample_rate)
            dst_sig = librosa.resample(y=src_sig, orig_sr=sr, target_sr=target_sample_rate)  
        #写出数据  参数三个 ：  目标地址  更改后的音频数据  目标采样数据
        except Exception as e:
            print(str(e))
        else:
            print(3)
            sf.write(out_wav, dst_sig, target_sample_rate) 
    def get_info(self, name):
        # get device count
        device_count = self.audio.get_device_count()
        # print(f"device count: {device_count}")
        device_index = None
        # get device info
        for i in range(device_count):
            device_info = self.audio.get_device_info_by_index(i)
            # print(f"device {i}: {device_info}")
            if device_info["name"] == name:
                device_index = i
        return device_index
    
    def release_microphone(self):
        p = pyaudio.PyAudio()
        device_index = self.get_info(self.device_name)
       
        device_info = p.get_device_info_by_index(device_index)
    
    
        print(f"Releasing microphone: {device_info['name']}")
        p.terminate()

if __name__ == '__main__':
    audio = Audio()
    x = audio.get_info('UACDemoV1.0: USB Audio (hw:2,0)')
    print(x)
    audio.record()
    # audio.change_rate('wavfiles/init.wav', 'wavfiles/change.wav', 16000)
    # audio.reduce_noise('wavfiles/init.wav', 'wavfiles/noise.wav')
    # audio.increase_volume('result.wav', 'new.wav')
    # saudio.play('wavfiles/noise.wav')
