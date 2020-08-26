from __future__ import division

import re
import sys

from google.cloud import speech_v1p1beta1
from google.cloud.speech_v1p1beta1 import enums
from google.cloud.speech_v1p1beta1 import types
import pyaudio
import requests

from microphone import MicrophoneStream
from send_zoom import send_zoom
from translate import translate

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
    

def listen_print_loop(URL, responses):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    seq = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Summarize speech
        text = ""

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()

            text += transcript + overwrite_chars

            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)

            text += transcript + overwrite_chars
            
            translated_text = translate(text, target="en")
            print("Translated: ", translated_text)
            print("Zoom response: ", send_zoom(URL, translated_text, seq))
            
            seq += 1

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Exiting..')
                break

            num_chars_printed = 0

def main():
    if len(sys.argv) < 2:
        print("Input some Zoom API TOKEN")
        sys.exit(0)
    
    # Zoom API TOKEN
    URL = sys.argv[1]

    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = 'ja'  # a BCP-47 language tag

    # Alternative language codes
    alternative_language_code_element_0 = "en"
    alternative_language_code_element_1 = "zh-TW"
    alternative_language_codes = [
        alternative_language_code_element_0,
        alternative_language_code_element_1,
    ]

    client = speech_v1p1beta1.SpeechClient()

    dialization_config = types.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
    )
    
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
        alternative_language_codes=alternative_language_codes,
        diarization_config=dialization_config,
    )
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()

        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(URL, responses)

        
if __name__ == '__main__':
    main()
