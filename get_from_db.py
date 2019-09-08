import psycopg2
from config import config

#-- utils

#-- from `[('mod',), ...]` to `['mod', ...]`
def get_flat_list(data):
  flat_list = [l[0] for l in data]
  return flat_list

# + + +

#-- get `article.mod` && `article.url` from `scraper`
def get_mod(publisher):
  conn = None
  try:
    params = config()
    print('connecting to db...')
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT url FROM scraper WHERE publisher = %s;", (publisher,))
    urls = cur.fetchall()
    urls = get_flat_list(urls)

    # set timezone to UTC `+00` when fetching from db
    # so it matches w/ ciso8601 default settings `+00`
    # http://initd.org/psycopg/docs/usage.html#time-zones-handling
    cur.execute("SET TIME ZONE 'UTC';")

    cur.execute("SELECT DISTINCT mod FROM scraper WHERE publisher = %s;", (publisher,))
    tss = cur.fetchall()
    tss = get_flat_list(tss)
    tss = [ts.isoformat() for ts in tss]

    mod = dict(zip(tss, urls))

    cur.close()
    return mod

  except (Exception, psycopg2.DatabaseError) as error:
    print('db error:', error)
  finally:
    if conn is not None:
      conn.close()
      print('db connection closed')


#-- get `article.body` data from `scraper`
def get_body(publisher):
  conn = None
  try:
    params = config()
    print('connecting to db...')
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    #-- labels
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'scraper';")
    labels = cur.fetchall()
    labels = get_flat_list(labels)

    #-- values
    cur.execute("SET TIME ZONE 'UTC';")
    cur.execute("SELECT DISTINCT %s FROM scraper WHERE publisher = '%s';" % (', '.join(labels), publisher))
    values = cur.fetchall()

    index = []
    for article in values:

      # convert type objects into string
      art = []
      for item in article:
        try:
          art.append(item.isoformat())
        except Exception:
          art.append(item)

      article = dict(zip(labels, art))
      index.append(article)

    cur.close()
    return index

  except (Exception, psycopg2.DatabaseError) as error:
    print('db error:', error)
  finally:
    if conn is not None:
      conn.close()
      print('db connection closed')