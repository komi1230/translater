# Backend of Translater

A small sample app of real-time translater.

# Usage

First of all, instlal dependencies:

```bash
$ pipenv install
```

Note: If this install command fails, try following commands:

```bash
$ brew install portaudio
$ pipenv shell

(backend) $ export LDFLAGS="-L/usr/local/lib" 
(backend) $ export CPPFLAGS="-I/usr/local/include"
(backend) $ pipenv install pyaudio
```

