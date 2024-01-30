import wave
import pygame


def pcm_to_wav(pcm_file, wav_file, channels=1, sample_width=2, frame_rate=16000):
    try:
        pcm_data = open(pcm_file, 'rb').read()

        wav = wave.open(wav_file, 'wb')
        wav.setnchannels(channels)
        wav.setsampwidth(sample_width)
        wav.setframerate(frame_rate)
        wav.writeframes(pcm_data)
        wav.close()
        print("Conversion successful: {} -> {}".format(pcm_file, wav_file))
    except Exception as e:
        print("An error occurred:", e)


def play_wav_file(wav_file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(wav_file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass


if __name__ == "__main__":
    pcm_file_path = "/home/xd/syj_workspace/aNewCar/car_voice/demo.pcm"  # Replace with the path to your PCM file
    wav_file_path = "/home/xd/syj_workspace/aNewCar/car_voice/demo.wav"  # Replace with the desired output WAV file path

    pcm_to_wav(pcm_file_path, wav_file_path)
