#scotus-v-public

This is the capstone project I did for a data science fellowship with The Data Incubator 
in Oakland, CA beginning in 2018.

The idea is to compare supreme court opinions and public opinion on arbitrary issues. 

Public opinion questions and responses are pulled from the ANES time series, 1948-2016. 
Supreme Court opinions are publicly available, and text of those opinions were gathered 
using an API from Free Law Project and the help of Michael Lissner. In the intervening 
years, it has become easier to obtain this data as a bulk download from CourtListener.

The SCOTUS opinion data is labeled as being decided in a liberal or conservative direction,
and the magnitude is given by the vote ratio for each case. We normalize to a [-1,+1]
scale corresponding to the [LIBERAL,CONSERVATIVE] spectrum, one of many axes.

The public opinion questions have answers which are over a range of values. Typically
binary, 1-5, or 0-100. One strategy is to take the question and answer and put them
together to form a statement, which is easier to analyze for LIBERAL vs. CONSERVATIVE
sentiment, e.g. Do you support medicare-for-all? 1) Strong Yes 2) Yes ... 5) Strong No.
maps to 1) I strongly support medicare-for-all which, on a scale of [-1,+1] with -1 being
LIBERAL, this question/answer pair would map close to a value of -1. Putting a question and
answer together can be performed by a neural network which is trained on a large set of Q/A pairs.
An RNN or CNN would be best suited to this task.

There currently exist trainable networks to perform political sentiment analysis on text. I trained
one using tweet data from Donald Trump and AOC from 2018 using [Denny Britz's classifier](https://github.com/jacksonwalters/cnn-text-political-bias-tf),
and it performed okay. In the intervening years TensorFlow upgraded to v2.0+ and deprecated tf.contrib, which broke this with no easy ability
to downgrade to TF 1.14. They're encouraging people to use [Keras](https://www.tensorflow.org/tutorials/keras/text_classification_with_hub),
a higher level toolkit, and use pre-existing datasets or upload their own in a specific format.

Rather than combining response text with questions to form statements to analyze, it is easier
and likely less noisy to simply classify the questions depending on whether an affirmative response
would be considered liberal. This gives a question orientation. The responses can be scaled directly
to get the magnitude, and then these are multiplied together to get polarity.

The user inputs a set of keywords, a search of SCOTUS cases by opinion text and 
public opinion questions by question text yields a set of relevant cases and questions,
and the liberal/conservative direction of the decisions and public responses are computed
resulting in a plot of political polarity for both over time. One can then perform regressions 
and try to determine when opinion might cross a threshold, etc.

- SCOTUS Case & Justice Data: http://scdb.wustl.edu/
- SCOTUS Opinions, Free Law Project: https://www.courtlistener.com/api/bulk-info/
- PO Data, ANES: https://electionstudies.org/data-center/
