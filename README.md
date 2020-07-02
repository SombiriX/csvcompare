# csvcompare
Had a need to hastily compare some csv files. These scripts implement progressivly more refined methods for making text comparisons from brute force to simple and even context-aware natural language processing.

- `script.py` - Brute force, simple string comparison
- `script_nlp.py` - tf-idf, Using Spacy for tokenization and similarity calculation
- `script_tf.py` - Uses tensorflow hub universal sentence encoder https://tfhub.dev/google/universal-sentence-encoder/4
