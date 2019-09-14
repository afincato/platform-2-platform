import sys
import get_from_db
from gensim import corpora
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
import text_processing

def ask(title, publisher, article_id, labels):
    # -- get article metadata from all pubs except the one passed as `arg`
    metadata = get_from_db.get_metadata(publisher)
    # print(metadata)

    # -- get corpuses from all pubs except the one passed as `arg`
    input_corpus = get_from_db.get_corpus(publisher, **labels)
    # print(input_corpus['index'], len(input_corpus['data']))
    # print(input_corpus['data'])

    dictionary = corpora.Dictionary(input_corpus['data'])
    # print(dictionary)

    corpus = [dictionary.doc2bow(text) for text in input_corpus['data']]
    # print(corpus)

    documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(input_corpus['data'])]
    # print(documents)

    pubs = ['amateur-cities', 'online-open', 'open-set-reader']
    pubs.remove(publisher)
    fn_model = '_'.join(pubs)

    # setup model
    def model_setup(documents, fname):
      model = Doc2Vec(documents, dm=1, vector_size=50, window=2, min_count=2, workers=4, epochs=40)
      # model.build_vocab(documents)
      print('model initialized', model)

      # save model to disk
      model.save(fname)
      return model

    #-- check if having to build new model again
    # by loading model saved to disk, if it fails
    # build model anew
    try:
      model = Doc2Vec.load(fn_model)
      # model.build_vocab(documents)
    except Exception as e:
      print('model could not be loaded', e)
      model = model_setup(documents, fn_model)

    def model_training(model, documents):
      model.train(documents, total_examples=model.corpus_count, epochs=model.epochs)
      return model

    try:
      if (sys.argv[3] == 'train'):
        model = model_training(model, documents)
    except Exception as e:
      print('no `train` flag', e)

    article = {}
    words = get_from_db.get_specific_article(article_id, labels)

    if bool(words) is False:
      return {'error': 'article with id %s not found' % article_id}
    else:
      tokens = text_processing.process_tokens(words, article)
      article['tokens'] = tokens

      td = TaggedDocument(article['tokens'], 1)

      inferred_vector = model.infer_vector(td[0])
      sims = model.docvecs.most_similar([inferred_vector])

      results = []
      for label, index in [('MOST', 0), ('SECOND-MOST', 1), ('THIRD-MOST', 2)]:
        title = metadata[documents[index].tags[0]]['title']
        url = metadata[documents[index].tags[0]]['url']
        publisher = metadata[documents[index].tags[0]]['publisher']
        abstract = metadata[documents[index].tags[0]]['abstract']

        article = {
          "title": title,
          "url": url,
          "publisher": publisher,
          "abstract": abstract,
          "score": sims[index][1]
        }
        results.append(article)

      return results
