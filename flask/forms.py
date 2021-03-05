from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import Optional, Length

class KeywordForm(FlaskForm):
	word1 = StringField('word1', render_kw={"placeholder": "marriage"}, validators=[Optional(),Length(max=100,message="100 chars max")])
	word2 = StringField('word2', render_kw={"placeholder": "equality"}, validators=[Optional(),Length(max=100,message="100 chars max")])
	word3 = StringField('word3', render_kw={"placeholder": "civil rights"}, validators=[Optional(),Length(max=100,message="100 chars max")])
	submit = SubmitField('Search & Plot')
