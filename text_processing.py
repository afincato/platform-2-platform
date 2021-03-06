from collections import defaultdict
import contractions
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk import ngrams, FreqDist
from nltk import pos_tag
import re
import hashlib
from slugify import slugify

#-- text-clean-up
def text_cu(text):
  # take out punctuation
  text = re.sub(r'[^\w\s]', '', text)
  text = text.lower()

  # expand to contraction form
  text = contractions.fix(text)

  return text

#-- stop-words
def stop_words(text, article):
  sw = set(stopwords.words('english'))

  stop_words = []
  wordsclean = []
  for w in text:
    if w in sw:
      stop_words.append(w)
    else:
      wordsclean.append(w)

  return wordsclean

def unique_words(text, article):
  frequency = defaultdict(int)
  for token in text:
    frequency[token] += 1

  tokens = [key for key, value in frequency.items() if value > 1]
  return tokens

def pos(corpus, article):
  tk = pos_tag(corpus)
  words = []
  # take out adverbs, but why?
  for word, code in tk:
    # if (code != 'RB'):
      words.append(word)

  return words

def tags_filter(tags, flag):
  #-- `online-open` tag conversion
  if flag is True:
    oo_tags = {"commons": "commons",
               "labour": "labour",
               "money": "finance and money",
               "": "commodification",
               "capitalism": "capitalism",
               "memory": "archive-memory",
               "": "anti-disciplinarity",
               "open! academy": "learning",
               "public domain": "public domain",
               "image": "image-representation",
               "art discourse": "image-representation",
               "architecture": "architecture",
               "critical theory": "theory-reflection",
               "philosophy": "theory-reflection",
               "media society": "media",
               "": "technology",
               "": "mobility",
               "urban space": "citizenship",
               "biopolitics": "control",
               "control": "control",
               "discrimination": "inequity",
               "discrimination": "colonization",
               "activism": "alternatives",
               "": "futures",
               "activism": "activism",
               "": "wicked problems",
               "public space": "public space",
               "conflict": "conflict",
               "research": "methods",
               "ecology": "ecologies",
               "": "care"}

    tags_oo = []
    for tag in tags['tags']:
      try:
        tags_oo.append(oo_tags[tag.lower()])
        print(tag.lower(), '=>', oo_tags[tag.lower()])
      except Exception as e:
        print('tag not in list', e)

    tags = tags_oo

  tags_master = ['commons',
                 'labour',
                 'finance and money',
                 'commodification',
                 'capitalism',
                 'archive-memory',
                 'anti-disciplinarity',
                 'learning',
                 'public domain',
                 'image-representation',
                 'architecture',
                 'theory-reflection',
                 'media',
                 'technology',
                 'mobility',
                 'citizenship',
                 'control',
                 'inequity',
                 'colonization',
                 'alternatives',
                 'futures',
                 'activism',
                 'wicked problems',
                 'public space',
                 'conflict',
                 'methods',
                 'ecologies',
                 'care']

  taglist = []
  for tag in tags:
    if tag.lower() in tags_master:
      taglist.append(tag.lower())

  # print('TAGLIST', taglist)
  return taglist

#-- word-frequency
def word_freq(corpus, article):
  wordfreq = []
  wf = FreqDist(corpus)

  for word, freq in wf.most_common():
    # (word-frequency / body-tokens-length ) * 100
    rel = (freq / len(corpus)) * 100
    wwf = word, freq, rel

    wordfreq.append(wwf)

  return wordfreq

#-- n-word phrases frequency
def phrases_freq(text, size, article):
  pf = dict()
  pf = FreqDist(ngrams(text, size))
  nwf = pf.most_common()

  index = []
  for item in nwf:
    x = {'ngram': list(item[0]),
         'frequency': item[1]}
    index.append(x)

  return index

# def relevancy(word_freq, article):
  # relevancy = 0
  # addup = 0
  # for word in word_freq:
  #   addup += word[2]
  #   relevancy = addup / len(word_freq)

  # article['relevancy'] = relevancy

def process_metadata(input, article, publisher):
  print(publisher)
  article = {"mod": input['mod'],
             "url": input['url'],
             "title": input['title'],
             "publisher": input['publisher'],
             "abstract": input['abstract'],
             "author": input['author'],
             "images": input['images'],
             "links": input['links'],
             "refs": input['refs']}

  article['title'] = input['title'].replace('&nbsp', ' ').replace('\n', '').strip()
  article['abstract'] = input['abstract'].replace('&nbsp', ' ').replace('\n', '')

  authors = []
  for item in input['author']:
    item = item.replace('&nbsp', ' ').replace(' ;', ' ').strip()
    authors.append(item)

  article['author'] = authors

  tags = []
  if publisher == 'online-open':
    oo = {'title': input['title'],
          'url': input['url'],
          'tags': input['tags']}
    tags = tags_filter(oo, True)
  else:
    tags = tags_filter(input['tags'], False)

  article['tags'] = tags

  body = re.sub(r'&nbsp', ' ', input['body'])
  article['body'] = body

  links = [url for url in input['links'] if url.startswith('#') is False]

  article['slug'] = slugify(article['title'])
  article['hash'] = hashlib.sha256(str.encode(article['slug'] + article['publisher'])).hexdigest()

  article['links'] = links

  print('text processing done')
  return article

def process_tokens(input, article):
  try:
    tags = tags_filter(input['tags'], False)
    article['tags'] = tags
  except Exception as e:
      print('TAGS parser', e)

  def tokenize(input, flag):
    if flag is True:
      tokens = re.sub(r'\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave$', '', input)

    tokens = text_cu(input)
    tokens = word_tokenize(tokens)
    tokens = stop_words(tokens, article)

    if flag is True:
      tokens = unique_words(tokens, article)

    return tokens

  try:
    article['title'] = tokenize(input['title'], False)
  except Exception as e:
    print('TITLE parser', e)

  try:
    article['body'] = tokenize(input['body'], True)
    corpus = tokenize(input['body'], False)
    article['word_freq'] = word_freq(corpus, article)
    article['2-word_freq'] = phrases_freq(corpus, 2, article)
    article['3-word_freq'] = phrases_freq(corpus, 3, article)
  except Exception as e:
    print('BODY parser', e)

  print('text processing done')
  return article

def vector_tokenize(input, article):
  def tokenize(input, flag):
    if flag is True:
      tokens = re.sub(r'\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave\n\n\n\nSaveSave$', '', input)

    tokens = text_cu(input)
    tokens = word_tokenize(tokens)
    tokens = stop_words(tokens, article)

    if flag is True:
      tokens = unique_words(tokens, article)

    return tokens

  try:
    article['title'] = tokenize(input['title'], False)
  except Exception as e:
    print('TITLE parser', e)

  try:
    authors = []
    for item in input['author']:
      authors.append(item)
    article['author'] = authors
  except Exception as e:
    print('AUTHOR parser', e)

  try:
    tags = tags_filter(input['tags'], False)
    article['tags'] = tags
  except Exception as e:
      print('TAGS parser', e)

  try:
    article['body'] = tokenize(input['body'], True)
  except Exception as e:
    print('BODY parser', e)

  print('text processing done')
  return article

#-- end
