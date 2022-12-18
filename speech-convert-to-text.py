#!/usr/bin/env python3
# 
# Copyright(C) 2022 Francesco Murdaca
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""This is the main script to convert audio to text.

# WARNING: drivers for ffmpeg are required on the OS to run this script!

"""

import logging
import os
import time

from pathlib import Path

import speech_recognition as sr

from pydub import AudioSegment
from pydub.silence import split_on_silence
from tqdm import tqdm

logging.basicConfig(level=logging.DEBUG)

_LOGGER = logging.getLogger(__name__)

 

def process_audio_registration(path):
    """Process audio registration."""
  
    output_file_name = path.stem

    # open the audio file stored in
    # the local system as a wav file.
    if path.as_posix().endswith(".wav"):
        # open the audio file using pydub
        sound = AudioSegment.from_wav(path)
    elif path.as_posix().endswith(".aac"):
        sound = AudioSegment.from_file(path, format="aac")
    else:
        raise NameError("Currently only .wav and .aac files are supported.")
    
    min_silence_len = 500
    dBFS = 16
    # split track where silence is 0.5 seconds 
    # or more and get chunks
    chunks = split_on_silence(sound,
        # must be silent for at least 0.5 seconds
        # or 500 ms. adjust this value based on user
        # requirement. if the speaker stays silent for 
        # longer, increase this value. else, decrease it.
        min_silence_len=min_silence_len,
  
        # consider it silent if quieter than -14 dBFS
        # adjust this per requirement
        silence_thresh=sound.dBFS-dBFS,
    )

    # create a directory to store the audio chunks.
    directory_name = f"audio_chunks_{output_file_name}"
    try:
        os.mkdir(directory_name)
    except(FileExistsError):
        pass
  
    # move into the directory to
    # store the audio files.
    os.chdir(directory_name)

    # open a file where we will concatenate  
    # and store the recognized text
    fh = open(f"{output_file_name}-{min_silence_len}silence-{dBFS}db.txt", "w+")

    i = 0
    # process each chunk
    for i, chunk in enumerate(tqdm(chunks), start=1):
              
        # Create 0.5 seconds silence chunk
        chunk_silent = AudioSegment.silent(duration = 10)
  
        # add 0.5 sec silence to beginning and 
        # end of audio chunk. This is done so that
        # it doesn't seem abruptly sliced.
        audio_chunk = chunk_silent + chunk + chunk_silent
  
        # export audio chunk and save it in 
        # the current directory.
        print("+++++++++++++++++++++++")
        print()
        print("saving chunk{0}.wav".format(i))
        # specify the bitrate to be 192 k (check what your mobile phone uses to record audio)
        audio_chunk.export("./chunk{0}.wav".format(i), bitrate ='192k', format ="wav")
        # audio_chunk.export("./chunk{0}.wav".format(i), format ="wav")
  
        # the name of the newly created chunk
        filename = 'chunk'+str(i)+'.wav'
  
        print("Processing chunk "+str(i))
  
        # get the name of the newly created chunk
        # in the AUDIO_FILE variable for later use.
        file = filename
  
        # create a speech recognition object
        r = sr.Recognizer()
  
        # recognize the chunk
        with sr.AudioFile(file) as source:
            # remove this if it is not working
            # correctly.
            # r.adjust_for_ambient_noise(source)  # not working
            audio_listened = r.listen(source)
  
        try:
            # try converting it to text
            rec = r.recognize_google(audio_listened, language="it-IT")
            print(f"Text converted: {rec}")
            # write the output to the file.
            fh.write(f"chunk{str(i):10s}: " + rec +".\n")
  
        # catch any errors.
        except sr.UnknownValueError:
            print(f"Could not understand audio, so removing chunk {filename}")
            os.remove(file)
  
        except sr.RequestError as e:
            print("Could not request results. check your internet connection")
  
        i += 1
    
    fh.close()
    os.chdir('..')


def main():
    """Main method."""
    audio_file_name = "registration-28-10-2022-15-09.aac"
    # audio_file_name = "test_samples/Sample_BeeMoved_48kHz16bit.aac" # test file
    _LOGGER.info(f"Considering file... {audio_file_name}")
    current_path = Path.cwd()
    file_path = current_path.joinpath(Path(audio_file_name))
    print("File path: ", file_path)

    # get the start time
    st = time.time()
    process_audio_registration(path=file_path)

    # get the end time
    et = time.time()

    # get the execution time
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')


if __name__ == "__main__":
    main()
