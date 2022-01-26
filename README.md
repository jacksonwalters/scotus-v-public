#scotus-v-public-opinion

This is the capstone project I did for a data science fellowship with The Data Incubator
in Oakland, CA beginning in 2018.

The idea is to compare supreme court opinions and public opinion on arbitrary issues over time.

Public opinion questions and responses are pulled from the ANES time series, 1948-2016.
Supreme Court opinions are publicly available, and text of those opinions were gathered
using an API from Free Law Project and the help of Michael Lissner. In the intervening
years, it has become easier to obtain this data as a bulk download from CourtListener.

The SCOTUS opinion text data is labeled as being decided in a liberal or conservative direction, and the magnitude is given by the vote ratio for each case. We normalize to a [-1,+1] scale corresponding to the [CONSERVATIVE,LIBERAL] spectrum, one of many axes.

The public opinion questions have answers which are over a range of values, e.g. yes/no,
strongly agree - strongly disagree, a temperature 0-100, etc. We'd like to map a
(question, answer) pair to a statement whose sentiment can be analyzed. For example,
Q: "Do you support government subsidized health care?" A: "Yes." should be interpreted
as a liberal sentiment, +1.

Rather than trying to combine the questions and answers into statement sentences and
map directly to a [-1,+1] scale, it is cleaner to perform a binary classification on
the questions themselves to determine liberal/conservative direction {-1,+1}, and then
use the responses to gauge the magnitude. The subtlety is you must pick an orientation,
i.e. the classification is telling you that an *affirmative/yes/agree/warm feeling*
response to the question at hand indicates a liberal sentiment, and should be
classified as +1. In mathematics, orientation is an element of Z/2Z.

To perform this classification, I use a neural network with a 1d CNN layer trained
using the Tensorflow/Keras framework. This performs well on text data as it is
able to pick out short distance correlations between words. I hand classify a
subset of the 1,000 or so public opinion questions and train the network using
this dataset. Ideally, all questions would be labeled.

The interface is a Flask webapp. The user inputs a set of keywords, and a TF-IDF search of
SCOTUS cases by opinion text and public opinion questions by question text yields a set of relevant cases and questions. The liberal/conservative direction of SCOTUS opinion and public opinion are computed resulting in a plot of ideological polarity for both over time. One can then perform regressions and try to determine when opinion might cross a threshold, etc.

Of course, with more data the resulting plots will be more informative, and likely become
rather jagged, like a stock market tracker. These data could be filled in with relevant
state and local case data, and supplemented with more public opinion questions.

- SCOTUS Case & Justice Data: http://scdb.wustl.edu/
- SCOTUS Opinions, Free Law Project: https://www.courtlistener.com/api/bulk-info/
- Public Opinion Data, ANES: https://electionstudies.org/data-center/
- SCOTUS v. American Public Opinion (July 2020): https://www.hks.harvard.edu/faculty-research/policy-topics/democracy-governance/us-supreme-court-v-american-public-opinion
