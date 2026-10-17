# data

- raw/       : untouched downloads (put source corpora here)
- processed/ : symlinks to working inputs (corpus_real.txt, tokens.bin)
               plus generated JSONL (real_train.jsonl)

If you want the Chinese path, put a UTF-8 Chinese corpus at
data/raw/chinese_corpus.txt and symlink it into processed/.
