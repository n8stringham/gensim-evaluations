# gensim-evaluations
This library provides methods for evaluating word embedding models loaded with `gensim`. Currently, it implements two methods designed specifically for the evaluation of low-resource models. The code allows users to automatically create custom test sets in any of the 581 languages supported by [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page) and then to evaluate on them using the `OddOneOut` and `Topk` methods proposed in this [paper]().

## Basic Usage

### Installation

Install from [PyPi](https://pypi.org/)
    
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
For example we might choose

* Tibetan Buddhist Monastery - Q54074585
* News Agency - Q192283
* Algorithm - Q8366
* Theorem - Q65943
* Mathematical Concept - Q24034552
* Human Biblical Figure - Q20643955
* Capital - Q5119
* Country - Q6256
* Mythical Character - Q4271324
* Emotion - Q9415
* Negative Emotion - Q60539481

As you can see, each of these `classes` has an associated code in the Wikidata Knowledgebase. These classes are related to other `items` in the knowledgebase through certain `properties`. One of the most important of these is the `instance of` property `P31` which links items that are a particular example of a class to that class.

> For example, `Wikinews` is an `instance of Q192283` and `Chuzang` is an `instance of Q54074585` 

Following this basic idea, we can generate test set(s) composed of all words in Wikidata belonging to these categories in any language(s) supported by the project.

    from gensim_evaluations import wikiqueries

    categories = ['Q54074585','Q192283','Q8366','Q65943','Q24034552','Q20643955',
               'Q5119','Q6256','Q4271324','Q9415','Q60539481']

    langs = ['en','la']
    wikiqueries.generate_test_set(items=categories,languages=langs,filename='test_set')

All that is required for the `generate_test_set` function is a list of Wikidata items to be used as categories and a list of language codes. The test set(s) will be saved as `.txt` file(s) at location specified by the `filename` parameter. The appropriate language code is automatically appended to the corresponding `filename`.

Here are some useful links to help determine the languages and categories available.
* List of languages supported by Wikidata - https://www.wikidata.org/wiki/Help:Wikimedia_language_codes/lists/all
* SQID Browser for all items in Wikidata containing the `Instance of (P31)` property - https://sqid.toolforge.org/#/browse?type=classes

It should also be noted that category sizes will vary. In particular a broad category such as `human (Q5)`, contains 8,255,736 instances which is too large to work with as a single category. It is advised that you either use SQID to filter down to categories that have a reasonable number of entries or test your query on the [Wikidata Query Service](https://query.wikidata.org/) to make sure it runs before using it as a category.

### Evaluation Using Topk and OddOneOut
We can now evaluate the word2vec model (which we loaded earlier) on these newly generated test sets using both `Topk` and `OddOneOut`
    
    from gensim_evaluations import methods

    topk_result = methods.Topk(cat_file='test_set_en.txt',model=model, k=3, allow_oov=True)
    odd_out_result = methods.OddOneOut(cat_file='test_set_en.txt',model=model, k_in=3, allow_oov=True, sample_size=1000)
    
    print('topk_result=', topk_result)
    print('odd_out_result=', odd_out_result)
    

The `Topk` and `OddOneOut` functions both return a 5-tuple containing:
1. overall accuracy
2. category accuracy (float accuracy for each category)
3. list of skipped categories
4. overall raw score (total number of correct comparisons)
5. category raw score (number of correct comparisons for each category)

## Contact
Feel free to reach out to `n8stringham@gmail.com` with any questions.
