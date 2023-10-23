# knownledge-gop

The code runs on Kaldi-5.5 and primarily utilizes "computer-gop".

you can get kaldi form ["here"](https://github.com/kaldi-asr/kaldi)

Once you have prepared the .wav data( ["Aishell"](https://www.openslr.org/33/) , ["Thchs30"](https://www.openslr.org/18/), UY/Child ) to s5/raw_data/WAVE/speakid*, you simply need to back up ["kaldi/egs/gop_speechocean"](https://github.com/kaldi-asr/kaldi/tree/master/egs/gop_speechocean76) and use this project to overwrite it. Then, run "aug_run.sh" to proceed.

The data will be stored in a separate repository.

The code implements random data augment SVM, knowledge data augment SVM, and compares their plotting with GOP.

## How to Run

```
mv gop_speechocean762 gop_chinese
cd gop_chinese/s5
./aug_run.sh
```



