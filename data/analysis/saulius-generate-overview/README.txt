This directory contains information extracted from the YAML encoded
files, regularised, summarised and presented as a set of TSV and CSV
[1-3] outputs.

In the "outputs/" directory, the CSV and TSV files conatain the first
line with a time stamp. Below the first line, a regular TSV or CSV
stream follows as specified in the correspinding format descriptions
[1-3]. Strictly speaking, these files should have '.ttsv' and 'tcsv'
extensions, for "time-stamped TSV" and "time-stamped CSV",
correspondingly.

The "all-answers.{csv,tsv}" files contain variable number of columns;
the number of columns, and the position of the selected "correct"
column can be derived from values in "NAnsw" and "IdxCorrect" columns,
respectively. The more detailed explanation of this is provided in the
"doc/column-descriptions/all-answers_columns.tsv" file.

References
----------

1. RFC 4180. Common Format and MIME Type for Comma-Separated Values
   (CSV) Files. https://www.ietf.org/rfc/rfc4180.txt [accessed:
   2022-04-05T11:49+03:00]

2. Library of Congress. CSV, Comma Separated Values (RFC
   4180). https://www.loc.gov/preservation/digital/formats/fdd/fdd000323.shtml
   [accessed: 2022-04-05T11:50+03:00]

3. Library of Congress. TSV, Tab-Separated
   Values. https://www.loc.gov/preservation/digital/formats/fdd/fdd000533.shtml
   [accessed: 2022-04-05T11:51+03:00]

