from __future__ import division

import sys
import itertools

from google.cloud import mediatranslation as media
import pyaudio

from microphone import MicrophoneStream
from send_zoom import send_zoom

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
SpeechEventType = media.StreamingTranslateSpeechResponse.SpeechEventType

API_KEY = sys.argv[1]

def listen_print_loop(responses, seq):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.
    """
    translation = ''
    source = ''
    
    for response in responses:
        # Once the transcription settles, the response contains the
        # END_OF_SINGLE_UTTERANCE event.
        if (response.speech_event_type ==
                SpeechEventType.END_OF_SINGLE_UTTERANCE):

            print(u'\nFinal translation: {0}'.format(translation))
            print(u'Final recognition result: {0}'.format(source))

            print("Zoom response: ", send_zoom(API_KEY, translation, seq))
            
            return 0

        result = response.result
        translation = result.text_translation_result.translation
        source = result.recognition_result

        #print(u'\nPartial translation: {0}'.format(translation))
        #print(u'Partial recognition result: {0}'.format(source))

        
def do_translation_loop(seq):
    print('Begin speaking...')

    client = media.SpeechTranslationServiceClient()

    speech_config = media.TranslateSpeechConfig(
        audio_encoding='linear16',
        source_language_code='en-US',
        target_language_code='ja-JP')

    config = media.StreamingTranslateSpeechConfig(
        audio_config=speech_config, single_utterance=True)

    # The first request contains the configuration.
    # Note that audio_content is explicitly set to None.
    first_request = media.StreamingTranslateSpeechRequest(
        streaming_config=config, audio_content=None)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        mic_requests = (media.StreamingTranslateSpeechRequest(
            audio_content=content,
            streaming_config=config)
            for content in audio_generator)

        requests = itertools.chain(iter([first_request]), mic_requests)

        responses = client.streaming_translate_speech(requests)

        # Print the translation responses as they arrive
        result = listen_print_loop(responses, seq)
        if result == 0:
            stream.exit()

            
def main():
    seq = 0
    while True:
        print()
        option = input('Press any key to translate or \'q\' to quit: ')

        if option.lower() == 'q':
            break

        while True:
            do_translation_loop(seq)
            seq += 1

        
if __name__ == '__main__':
    main()
