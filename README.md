# knownledge-gop

The code runs on Kaldi-5.5 and primarily utilizes "computer-gop".

Once you have prepared the data( Aishell, Thchs30, UY/Child ), you simply need to back up ["kaldi/egs/gop_speechocean"](https://github.com/kaldi-asr/kaldi/tree/master/egs/gop_speechocean76) and use this project to overwrite it. Then, run "aug_run.sh" to proceed.

The data will be stored in a separate repository.

The code implements random data augment SVM, knowledge data augment SVM, and compares their plotting with GOP.

## How to Run

```
mv gop_speechocean762 gop_chinese
cd gop_chinese/s5
./aug_run.sh
```



