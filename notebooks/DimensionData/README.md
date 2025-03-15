# README
The list of selected journals can be found in journal\_selection\_05\_11\_five.csv.

### publishers.csv
is the result of the query:

```
q = f"""
search publications
where year>=2021 and
year <=2023 and
document_type="RESEARCH_ARTICLE" and
category_for.id in [80071, 80067, 80066, 80069, 80070, 80124, 80126, 80221, 80223]
return publisher[id+title]
    aggregate citations_avg, citations_total, citations_median, rcr_avg sort by count
    limit 1000
for_results = dsl.query(q, verbose=True)
df_publishers = for_results.as_dataframe()
df_publishers.to_csv('publishers.csv')
```
the ids correspond to the Fields of Research (ANZSRC 2020):
- 3407 Theoretical and Computational Chemistry
- 3403 Macromolecular and Materials Chemistry
- 3402 Inorganic Chemistry
- 3405 Organic Chemistry
- 3406 Physical Chemistry
- 4016 Materials Engineering
- 4018 Nanotechnology
- 5102 Atomic, Molecular and Optical Physics
- 5104 Condensed Matter Physics

### publisher_data
is the result of the following queries (querying for the aggregated journal data of the most popular 50 publishers in terms of number of articles):

```python
for el in df_publishers['id'][0:50]:
    query = f"""search publications
    where year>=2021 and
    year <=2023 and
    document_type="RESEARCH_ARTICLE" and
    category_for.id in [80071, 80067, 80066, 80069, 80070, 80124, 80126, 80221, 80223] and
    publisher="{el}"
    return journal[id+title]
        aggregate citations_avg, citations_total, citations_median, rcr_avg sort by count
        limit 1000
    """
res = dsl.query(query)
df = res.as_dataframe()
publisher_dict[el] = df.copy()
```

### journal_selection.csv 
contains a selection of journals from the publisher_data. For each publisher only journals with at least 50 articles in the "Material Science" categories were chosen. The selection criterion is noted in the column "choice" as top 5 according to citation median, citation average, number of articles or random. In case where less than 5 journals were left for a publisher the column was set to all.

Fields in the csv:
- id
- count (Number of articles published in the respective categories and time range in the journal)
- title (Journal name)
- citations_avg (average citations of the selected articles)
- citations_median (median citations of the selected articles)
- citations_total (total number of citations of the selected articles)
- rcr_avg (average citation_ratio relative by field)
- publisher (publisher name)
