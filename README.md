#scvpo

This is a partially completed capstone project I did for a data science fellowship
with The Data Incubator in Oakland, CA.

The idea is to compare supreme court opinions and public opinion on issues.

Public opinion data is pulled from ANES data from 1948-2016. Supreme Court opinions
are publicly available, and text of those opinions were gathered using an API from
Free Law Project and the help of Michael Lissner.

The method is to take a set of keyword inputs from the user, and filter relevant
public opinion questions and supreme court opinions.

The SCOTUS opinion data is labeled as being decided in a liberal or conservative direction,
and the magnitude is given by the vote ratio for each case. We normalize to a [-1,+1]
scale corresponding to the [LIBERAL,CONSERVATIVE] spectrum, one of many axes.

The public opinion questions have answers which are over a range of values. Typically
binary, 1-5, or 0-100. The strategy is to take the question and answer and put them
together to form a statement, which is easier to analyze for LIBERAL vs. CONSERVATIVE
sentiment, e.g. Do you support medicare-for-all? 1) Strong Yes 2) Yes ... 5) Strong No.
maps to 1) I strongly support medicare-for-all which, on a scale of [-1,+1] with -1 being
LIBERAL, this question/answer pair would map close to a value of -1.

Putting a question and answer together can be performed by a neural network which is trained
on a large set of Q/A pairs. An RNN or CNN would be best suited to this task. Further, there
currently exist trained networks to perform political sentiment analysis on text. I trained
one using tweet data from Donald Trump and AOC from 2018 using [Denny Britz's classifier]
(https://github.com/dennybritz/cnn-text-classification-tf), and it performed okay. In the
intervening years TensorFlow upgraded to v2.0+ and deprecated tf.contrib. TensorFlow is
encouraging people to use [Keras](https://www.tensorflow.org/tutorials/keras/text_classification_with_hub),
a higher level toolkit, and use pre-existing datasets or upload their own in a specific format.

In the end, a user puts in a set of keywords to specify an issue, and a plot of public sentiment
vs. supreme court sentiment over time appears. One can perform regressions and try to determine when
opinion might cross a threshold.

- SCOTUS Case & Justice Data: http://scdb.wustl.edu/
- SCOTUS Opinions, Free Law Project: https://www.courtlistener.com/api/bulk-info/
- PO Data, ANES: https://electionstudies.org/data-center/
