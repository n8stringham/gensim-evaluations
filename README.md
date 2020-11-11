# gensim-evaluations
This library provides methods for evaluating word embedding models loaded with `gensim`. Currently, it implements two methods designed specifically for the evaluation of low-resource models. The code allows users to automatically create custom test sets in any of the 581 languages supported by [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page) and then to evaluate on them using the `OddOneOut` and `Topk` methods proposed in this [paper](https://www.aclweb.org/anthology/2020.eval4nlp-1.17/).

## Basic Usage

### Installation

Install from [PyPI](https://pypi.org/)
    
    $ pip install gensim-evaluations

### Loading a model 
These methods have been designed for evaluation of embedding models loaded through Gensim.
As an example, we'll first load the famous pre-trained word2vec model from [Mikolov et. al](https://research.google/pubs/pub41224/).

    import gensim.downloader as api
    from gensim.models import Word2Vec

    model = api.load('word2vec-google-news-300')

A complete list of pre-trained models available through gensim can be found [here](https://github.com/RaRe-Technologies/gensim-data). Of course, you can always use `gensim` to train and load your own model.

### Generating custom language-specific test sets
In addition to a model, `OddOneOut` and `Topk` require a custom test set of categories. Each category contains a list of words belonging to it.
We can easily generate a custom test set by selecting a few relevant items from [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page).
Here are just a few of the many items we could choose from:

* Capital - Q5119
* Country - Q6256
* Emotion - Q9415
* Human Biblical Figure - Q20643955
* Mythical Character - Q4271324
* Negative Emotion - Q60539481
* News Agency - Q192283
* Tibetan Buddhist Monastery - Q54074585

Each of these `items` has an associated code in Wikidata. They are related to other `items` in the knowledgebase through certain `properties`. One of the most important of these is the `instance of` property `P31` which finds specific examples of some `item`. 

> For example, `Wikinews` is an `instance of` `News Agency` `(Q192283)` and `abhorrence` is an `instance of` `Negative Emotion` `(Q60539481)` 

Following this basic idea, we can generate test set(s) for any of these categories in any language(s) supported by Wikidata. Below we create test sets for the negative emotions category in both English and Latin.

    from gensim_evaluations import wikiqueries

    categories = ['Q60539481']
    langs = ['en','la']
    wikiqueries.generate_test_set(items=categories,languages=langs,filename='neg_emotion')

For simplicity, we create test sets for only a single category and two languages, but in fact the `generate_test_set` function takes as many categories and language codes as you want. The test set(s) will be saved as `.txt` file(s) at location specified by the `filename` parameter. The appropriate language code is automatically appended to the corresponding `filename`.

Here are some useful links
* List of languages supported by Wikidata - https://www.wikidata.org/wiki/Help:Wikimedia_language_codes/lists/all
* SQID Browser for all items in Wikidata containing the `Instance of (P31)` property - https://sqid.toolforge.org/#/browse?type=classes

It should also be noted that category sizes will vary. In particular a broad category such as `human (Q5)`, contains 8,255,736 instances which is too large to work with as a single category. It is advised that you either use SQID to filter down to categories that have a reasonable number of entries or test your query on the [Wikidata Query Service](https://query.wikidata.org/) to make sure it runs before using it as a category.

### Evaluation Using Topk and OddOneOut
We can now evaluate the word2vec model (loaded previously) on the newly generated test set using `OddOneOut`.  
    
    from gensim_evaluations import methods

    odd_out_result = methods.OddOneOut(cat_file='neg_emotion_en.txt',model=model, k_in=3, allow_oov=True, sample_size=1000)
    print('odd_out_result=', odd_out_result)

Output

    OddOneOut Evaluation
    0 categories have fewer than k_in entries and will be skipped
    2 words have been identified as out out of vocabulary
    words_in_test= 43
    out of vocab ratio is  0.05
    Will calculate the 3 th order OddOneOut score for 1 categories
    odd_out_result= (0.832, {':instance of negative emotion (en)': 0.832}, [], 832, {':instance of negative emotion (en)': 832})

and `Topk`

    topk_result = methods.Topk(cat_file='neg_emotion_en.txt',model=model, k=3, allow_oov=True)
    print('topk_result=', topk_result)

Output  

    Performing Topk Evaluataion
    0 categories do not have enough words and will be skipped
    2 words have been identified as out out of vocabulary
    43 total words in test set
    out of vocab ratio is  0.05
    topk_result= (0.1937984496124031, {':instance of negative emotion (en)': 0.1937984496124031}, [], 25, {':instance of negative emotion (en)': 25})

The `Topk` and `OddOneOut` functions both return a 5-tuple containing:
1. overall accuracy
2. category accuracy (float accuracy for each category)
3. list of skipped categories
4. overall raw score (total number of correct comparisons)
5. category raw score (number of correct comparisons for each category)

