import pyaudiowpatch as pyaudio
import time
import wave
import openai
import whisper
import numpy as np

# Load the Whisper model
model = whisper.load_model("base", download_root="../model/")

DURATION = 10
CHUNK_SIZE = 512

filename = "../Listened/loopback_record.wav"

if __name__ == "__main__":
    with pyaudio.PyAudio() as p:
        try:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            print("Looks like WASAPI is not available on the system. Exiting...")
            exit()

        default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])

        if not default_speakers["isLoopbackDevice"]:
            for loopback in p.get_loopback_device_info_generator():
                if default_speakers["name"] in loopback["name"]:
                    default_speakers = loopback
                    break
            else:
                print(
                    "Default loopback output device not found.\n\nRun `python -m pyaudiowpatch` to check available devices.\nExiting...\n")
                exit()

        print(f"Recording from: ({default_speakers['index']}){default_speakers['name']}")

        wave_file = wave.open(filename, 'wb')
        wave_file.setnchannels(default_speakers["maxInputChannels"])
        wave_file.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
        wave_file.setframerate(int(default_speakers["defaultSampleRate"]))


        def callback(in_data, frame_count, time_info, status):
            wave_file.writeframes(in_data)
            return (in_data, pyaudio.paContinue)


        with p.open(format=pyaudio.paInt16,
                    channels=default_speakers["maxInputChannels"],
                    rate=int(default_speakers["defaultSampleRate"]),
                    frames_per_buffer=CHUNK_SIZE,
                    input=True,
                    input_device_index=default_speakers["index"],
                    stream_callback=callback
                    ) as stream:
            print(f"The next {DURATION} seconds will be written to {filename}")
            time.sleep(DURATION)  # Blocking execution while recording

        wave_file.close()

    # response = model.transcribe(
    #     audio='./'+filename,
    #     language="fr"  # Adjust the language code as needed
    # )
    # print("Transcription results:")
    # print(response['text'])
    # Transcription using OpenAI Whisper

    # Read file to get buffer
    ifile = wave.open(filename)
    samples = ifile.getnframes()
    audio = ifile.readframes(samples)
    # Convert buffer to float32 using NumPy
    audio_as_np_int16 = np.frombuffer(audio, dtype=np.int16)
    print(audio_as_np_int16)
    audio_as_np_float32 = audio_as_np_int16.astype(np.float32)
    print(audio_as_np_float32)

    # Normalise float32 array so that values are between -1.0 and +1.0
    max_int16 = 2 ** 15
    #audio_normalised = audio_as_np_float32 / max_int16
    #audio_data_copy = audio_data.copy()
    response = model.transcribe(
        audio=filename,
        language="en",  # Adjust the language code as needed
        fp16=False
    )
    with open('../Transcripts/transcription.txt', "w", encoding="utf-8") as txt:
        txt.write(response["text"])

    print("Transcription results:")
    print(response['text'])
