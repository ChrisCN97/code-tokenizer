python language-modeling/run_mlm.py \
    --config_name roberta-base \
    --tokenizer_name roberta-base \
    --train_file data/java_custom/train.txt \
    --validation_file data/java_custom/valid.txt \
    --per_device_train_batch_size 12 \
    --per_device_eval_batch_size 12 \
    --do_train \
    --do_eval \
    --line_by_line \
    --output_dir model/roberta_java_custom_fz \
    --seed 123456 \
    --num_train_epochs 10 \
    --overwrite_output_dir