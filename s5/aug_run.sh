#!/usr/bin/env bash
# 2023/8/30 
# gop for chinese
# gop_speeechocean762 + my edits
# https://github.com/kaldi-asr/kaldi/tree/master/egs/gop_speechocean762
# Copyright     2019  Junbo Zhang
#               2020-2021  Xiaomi Corporation (Author: Junbo Zhang, Yongqing Wang)

# This script shows how to calculate Goodness of Pronunciation (GOP) in chinese and
# use the data augmentation of GOP-based features to do phone-level  zero-shot mispronunciations detection.

data=/home/shiyinglocal/kaldi/egs/gop_chinese/s5/raw_data

stage=0
nj=40

set -e

. ./cmd.sh
. ./path.sh
. parse_options.sh

#ASR model
asr_eg=/home/shiyinglocal/Documents/model_from_shiying
model=$asr_eg/AM
lang=$asr_eg/language/lang/lang

for d in $model $lang; do
  [ ! -d $d ] && echo "$0: no such path $d" && exit 1;
done


# if [ $stage -le 1 ]; then
#   # Download data and untar
#   local/download_and_untar.sh $data_url $data
# fi

if [ $stage -le 2 ]; then
  # Prepare data
  for part in train test; do
    local/data_prep.sh $data/$part data/$part
  done

  mkdir -p data/local
  cp $data/resource/* data/local
fi

if [ $stage -le 3 ]; then
  # Fbank features
  for part in train test; do
    steps/make_fbank.sh --nj $nj --fbank-config conf/fbank.conf \
      --cmd "$cmd" data/$part || exit 1;
    steps/compute_cmvn_stats.sh data/$part || exit 1;
    utils/fix_data_dir.sh data/$part
  done
fi


if [ $stage -le 4 ]; then
  # ASR Compute Log-likelihoods
  for part in train test; do
    steps/nnet3/compute_output.sh --cmd "$cmd" --nj $nj \
      data/$part $model exp/probs_$part
  done
fi

# if [ $stage -le 5 ]; then
#   # Prepare lang
#   local/prepare_dict.sh data/local/lexicon.txt data/local/dict_nosp

#   utils/prepare_lang.sh --phone-symbol-table $lang/phones.txt \
#     data/local/dict_nosp "<SPOKEN_NOISY>" data/local/lang_tmp_nosp data/lang_nosp
# fi

if [ $stage -le 6 ]; then
  # Split data and make phone-level transcripts
  for part in train test; do
    utils/split_data.sh data/$part $nj
    for i in `seq 1 $nj`; do
      utils/sym2int.pl -f 2- $lang/words.txt \
        data/$part/split${nj}/$i/text \
        > data/$part/split${nj}/$i/text.int
    done

    utils/sym2int.pl -f 2- $lang/phones.txt \
      data/local/text-phone > data/local/text-phone.int
  done
fi

if [ $stage -le 7 ]; then
  # Make align graphs
  for part in train test; do
    $cmd JOB=1:$nj exp/ali_$part/log/mk_align_graph.JOB.log \
      compile-train-graphs-without-lexicon \
        --read-disambig-syms=$lang/phones/disambig.int \
        $model/tree $model/final.mdl \
        "ark,t:data/$part/split${nj}/JOB/text.int" \
        "ark,t:data/local/text-phone.int" \
        "ark:|gzip -c > exp/ali_$part/fsts.JOB.gz"   || exit 1;
    echo $nj > exp/ali_$part/num_jobs
  done
fi

if [ $stage -le 8 ]; then
  # Align
  for part in train test; do
    steps/align_mapped.sh --cmd "$cmd" --nj $nj --graphs exp/ali_$part \
      data/$part exp/probs_$part $lang $model exp/ali_$part
  done
fi

if [ $stage -le 9 ]; then
  # Convert transition-id to phone-id
  echo "transition-id to phone-id"
  for part in train test; do
    $cmd JOB=1:$nj exp/ali_$part/log/ali_to_phones.JOB.log \
      ali-to-phones --per-frame=true $model/final.mdl \
        "ark,t:gunzip -c exp/ali_$part/ali.JOB.gz|" \
        "ark,t:|gzip -c >exp/ali_$part/ali-phone.JOB.gz"   || exit 1;
  done
fi

# knowledge random ali_scores 
if [ $stage -le 10 ]; then

  echo "knowledge ali_scores"

  gunzip exp/ali_train/ali-phone*
  python3 ali_change.py exp/ali_train \
                        exp/ali_train_know_random 
  python3 err_phone_data_aug.py  exp/ali_train_know_random \
                         exp/ali_train_know \
                         exp/ali_train_know_random/pos_scores.txt \
                         $lang/phones-pure.txt \
                         data/local/trans_ini.json \
                         data/local/trans_vow.json \
                         data/local/error_rates.json\
                         data/local/count_ph.json
  python3 err2scores.py exp/ali_train_know_random/pos_scores.txt \
                        data/local/scores.json \ 
                        exp/ali_train_know_random/ \
                        $lang/phones-pure.txt  || exit 1;
  gzip  exp/ali_train_know/ali-phone*
  echo " finish know ali-phone err "
fi
# random ali_scores 
if [ $stage -le 11 ]; then
  echo "random ali_scores"

  python3 ali_change.py exp/ali_train/ \
                        exp/ali_train_random_random 
  python3 err_phone.py  exp/ali_train_random_random \
                         exp/ali_train_random \
                         exp/ali_train_random_random/pos_scores.txt \
                         $lang/phones-pure.txt 
  python3 err2scores.py exp/ali_train_random_random/pos_scores.txt \
                        data/local/scores.json \
                        exp/ali_train_random_random/ \
                        $lang/phones-pure.txt  || exit 1;
  gzip  exp/ali_train_random/ali-phone*

  echo " finish random ali-phone err "
fi

# compute gop & gop features
if [ $stage -le 12 ]; then
  for part in train_know train_random; do
  echo "compute $part gop"
    $cmd JOB=1:$nj exp/gop_$part/log/compute_gop.JOB.log \
      compute-gop --phone-map=$lang/phone-to-pure-phone.int \
        --skip-phones-string=0:1:2\
        $model/final.mdl \
        "ark,t:gunzip -c exp/ali_$part/ali-phone.JOB.gz|" \
        "ark:exp/probs_train/output.JOB.ark" \
        "ark,scp:exp/gop_$part/gop.JOB.ark,exp/gop_$part/gop.JOB.scp" \
        "ark,scp:exp/gop_$part/feat.JOB.ark,exp/gop_$part/feat.JOB.scp"   || exit 1;
      cat exp/gop_$part/feat.*.scp > exp/gop_$part/feat.scp
      cat exp/gop_$part/gop.*.scp > exp/gop_$part/gop.scp
  done

  for part in test; do
  echo "compute $part gop"
    $cmd JOB=1:$nj exp/gop_$part/log/compute_gop.JOB.log \
      compute-gop --phone-map=$lang/phone-to-pure-phone.int \
        --skip-phones-string=0:1:2\
        $model/final.mdl \
        "ark,t:gunzip -c exp/ali_$part/ali-phone.JOB.gz|" \
        "ark:exp/probs_$part/output.JOB.ark" \
        "ark,scp:exp/gop_$part/gop.JOB.ark,exp/gop_$part/gop.JOB.scp" \
        "ark,scp:exp/gop_$part/feat.JOB.ark,exp/gop_$part/feat.JOB.scp"   || exit 1;
      cat exp/gop_$part/feat.*.scp > exp/gop_$part/feat.scp
      cat exp/gop_$part/gop.*.scp > exp/gop_$part/gop.scp
  done
fi

local/check_dependencies.sh   || exit 1;


# train and test
if [ $stage -le 16 ]; then

  for input in feat; do
    echo "training" 
    python3 local/feat_to_score_train.py \
              --phone_symbol_table $lang/phones-pure.txt \
              --nj $nj \
              exp/gop_train_know/feat.scp \
              exp/ali_train_know_random/ali_err_scores.json \
              exp/gop_train_know/model_feat

    python3 local/feat_to_score_train.py \
              --phone_symbol_table $lang/phones-pure.txt \
              --nj $nj \
              exp/gop_train_random/feat.scp \
              exp/ali_train_random_random/ali_err_scores.json \
              exp/gop_train_random/model_feat

    echo "testing"  
    python3 local/feat_to_score_eval.py \
              exp/gop_train_random/model_feat \
              --phone_symbol_table $lang/phones-pure.txt \
              exp/gop_test/feat.scp \
              exp/gop_test/predicted_feat.txt

    echo "Random SVM" 
    python3 local/print_predicted_result.py \
              --phone_symbol_table $lang/phones-pure.txt \
              --write exp/gop_test/result_feat.int \
              exp/ali_train_random_random/ali_err_scores.json\
              exp/gop_test/predicted_feat.txt  
              
    echo "Knowledge SVM" 
    python3 local/feat_to_score_eval.py \
              exp/gop_train_know/model_feat \
              --phone_symbol_table $lang/phones-pure.txt \
              exp/gop_test/feat.scp \
              exp/gop_test/predicted_feat.txt   
    
    python3 local/print_predicted_result.py \
              --phone_symbol_table $lang/phones-pure.txt \
              --write exp/gop_test/result_feat.int \
              exp/ali_train_know_random/ali_err_scores.json\
              exp/gop_test/predicted_feat.txt                    
  done
fi

# # delete fuzzy information
# if [ $stage -le 17 ]; then

#   for input in feat; do
#     echo "Modified Knowledge SVM" 
#     python3 re_save.py 
#     python3 local/print_predicted_result.py \
#               --phone_symbol_table $lang/phones-pure.txt \
#               --write exp/gop_test/result_feat.int \
#               data/local/scores_modified.json\
#               exp/gop_test/predicted_feat.txt  

#   done
# fi

# PR curve and SVM point
if [ $stage -le 18 ]; then

  echo "draw PR" 
  for part in test; do
    python3 local/ph_gop_draw.py \
            --phone_symbol_table $lang/phones-pure.txt \
            --nj $nj \
            exp/gop_$part/gop.scp \
            exp/ali_train_random_random/ali_err_scores.json \
            ph_gop_$part \
            
    python3 local/roc_gop.py \
            ph_gop_$part     
  done
fi


