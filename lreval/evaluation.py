"""Implementation of the Topk and OddOneOut methods for evaluating word embeddings"""

# dependencies
from gensim.models import Word2Vec
import re
from itertools import combinations
import random
import warnings

def Topk(cat_file, model, k=3, allow_oov=False, ft=False):
    """Performs Topk Evaluation on an embedding model

    Parameters
    ----------
    cat_file : str 
        location of the .txt file of categories to evaluate on
    model : 
        embedding model loaded via gensim
    k : int 
        number of words to return from similarity query
    allow_oov : bool, optional
        whether to skip or mark wrong comparisons with oov words (default False)
    ft : bool, optional
        set to True if using fastText embedding models (default False)

    Returns
    -------
    float
        overall accuracy
    dict
        category accuracy (float accuracy for each category)
    list
        list of skipped categories
    int
        overall raw score (total number of correct comparisons)
    dict
        category raw score (number of correct comparisons for each category)

    """
    cats = {}
    skipped_cats = []
    # convert test set file into dictionary where each category is a key
    # and the corresponding value is the list of words belonging to it.
    with open(cat_file, 'r') as f:
        for line in f:
            if re.search('^:',line):
                key = line.rstrip()
            # can't do topk comparisons when category has fewer than 2 words
            elif not len(line.strip().split()) < 2:
                cats.update({key: line.strip().split()})
            else:
                skipped_cats.append(key)

    model_vocab = model.wv.vocab
    # fast text uses n-grams, so checking for oov is different
    if ft:
        model_vocab = model.wv
        print('using ft n-grams')
    oov_list = []
    words_in_test = 0
    # verify that all words are in the vocabulary
    for value in cats.values():
        for word in value:
            words_in_test += 1
            # keep track of oov words
            if allow_oov and word not in model_vocab:
                oov_list.append(word)
            elif not allow_oov and word not in model_vocab:
                raise KeyError('word '+word+' is not in vocabulary')
    
    # test set info
    print('Performing Topk Evaluataion')
    print(' %d categories do not have enough words and will be skipped' % len(skipped_cats))
    print(' %d words have been identified as out out of vocabulary' % len(oov_list))
    print(' %d total words in test set' % words_in_test)
    ratio = len(oov_list)/words_in_test
    print('out of vocab ratio is ','{0:.2f}'.format(ratio))

    # for tracking scores for each category
    category_acc = {}
    category_raw = {}
    # total raw number of correct answers
    raw_correct = 0
    # total number of categories
    m = len(cats.items())

    # find the topk most similar for each word in all categories
    for cat, words in cats.items():
        # zero out for each new category
        cat_score = 0

        for word in words:
            # number of the words 
            n = len(words)
            category = words
            ignore_comparison=False
            # if word isn't in vocab, then ignore comparison altogether
            if word in oov_list:
                ignore_comparison = True
            # Evaluating Comparisons
            if not ignore_comparison:
                # find top_k similar words for a given entry
                topk = model.wv.most_similar(positive=word, topn=k)
                # items in each category
                for x in topk:
                    # x is a tuple and we want first element
                    cat_score += x[0] in category

        # Update category score
        category_acc.update({cat: cat_score/(n*k)})
        category_raw.update({cat: cat_score})
        # update total raw number correct
        raw_correct += cat_score
    
    # Total Score
    accuracy = sum(category_acc.values())/m

    return accuracy, category_acc, skipped_cats, raw_correct, category_raw


def OddOneOut(cat_file, model, k_in, sample_size=1000, restrict_vocab=None, allow_oov=False, ft=False, debug=False):
    """Performs Topk Evaluation on an embedding model

    Parameters
    ----------
    cat_file : str 
        location of the .txt file of categories to evaluate on
    model : 
        embedding model loaded via gensim
    k_in : int 
        size of group of words from the same category
    sample_size : int
        number of OddOneOut comparisons to evaluate for each category (default=1000)
    restrict_vocab : int, optional
        the size of the model vocabulary to sample the out-word from (default None)
    allow_oov : bool, optional
        whether to skip or mark wrong comparisons with oov words (default False)
    ft : bool, optional
        set to True if using fastText embedding models (default False)
    debug : bool, optional
        print out the comparisons being made for debugging purposes (default False)

    Returns
    -------
    float
        overall accuracy
    dict
        category accuracy (float accuracy for each category)
    list
        list of skipped categories
    int
        overall raw score (total number of correct comparisons)
    dict
        category raw score (number of correct comparisons for each category)

    """
    original_state = random.getstate()
    random.seed(0)
    cats = {}
    skipped_cats = []
    # create category dictionary with key as category and value = list of words from that category
    with open(cat_file, 'r') as f:
        for line in f:
            if re.search('^:',line):
                key = line.rstrip()
            # check category contains enough values
            elif len(line.strip().split()) < k_in:
                skipped_cats.append(key)
            else:
                cats.update({key: line.split()})
  
    # Verify all words are in the vocabulary
    model_vocab = model.wv.vocab
    # fast text uses n-grams, so checking for oov is different
    if ft:
        model_vocab = model.wv
        print('using ft n-grams')
    oov_list = []
    words_in_test = 0
    for value in cats.values():
        for word in value:
            words_in_test += 1
            if allow_oov and word not in model_vocab:
                oov_list.append(word)
            elif not allow_oov and word not in model_vocab:
                raise KeyError('word '+word+' is not in vocabulary')
    
    # test set info
    print('OddOneOut Evaluation')
    print(' %d categories have fewer than k_in entries and will be skipped' % len(skipped_cats))
    print(' %d words have been identified as out out of vocabulary' % len(oov_list))
    print('words_in_test=',words_in_test)    
    ratio = len(oov_list)/words_in_test
    print('out of vocab ratio is ','{0:.2f}'.format(ratio))


    # for storing accuracies
    category_acc = {}
    category_raw = {}
    
    # to return raw # correct preds instead of accuracy
    raw_correct = 0

    # total number of categories
    m = len(cats.items())
    print('Will calculate the %d th order OddOneOut score for %d categories' %(k_in,m))
    not_skipped = 0
    for cat in cats.keys():     
        s = list(combinations(cats[cat],k_in))
        c_i = cats[cat]
        # sample k-combos
        s_sampled = random.choices(s, k=sample_size)
        # print(s_sampled)

        # sample OddOneOut from model vocabulary
        w_sampled = []
        while len(w_sampled) < sample_size:
            word = random.choice(model.wv.index2word[:restrict_vocab])
            # don't add word if it's a dupe
            if word not in c_i:
                w_sampled.append(word)
        # kth order OddOneOut score for category i
        cat_score = 0
        # compute OddOneOut for each comparison
        for in_words, odd_one_out in zip(s_sampled,w_sampled):
            comparison = in_words + (odd_one_out,)

            # By default don't ignore any comparisons
            ignore_comparison = False
            if allow_oov:
                # check for oov word
                for w in comparison:
                    if w in oov_list:
                        ignore_comparison = True
            if not ignore_comparison:
                cat_score += int(model.wv.doesnt_match(comparison)==odd_one_out)
                if debug:
                    not_skipped +=1
                    print('comparison count=',not_skipped)
                    print('comparison=',comparison)
                    print('predicted OddOneOut=',model.wv.doesnt_match(comparison))
                    print('actual OddOneOut=',odd_one_out)
                # print('cat_score=',cat_score)
        category_acc.update({cat: cat_score/sample_size})
        category_raw.update({cat:cat_score})
        # update total raw number correct answers
        raw_correct += cat_score
    # Calculate Total Score
    accuracy = sum(category_acc.values())/m
    random.setstate(original_state)

    return accuracy, category_acc, skipped_cats, raw_correct, category_raw
