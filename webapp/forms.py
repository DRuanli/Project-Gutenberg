# ---- webapp/forms.py ----

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField, IntegerField, SelectField, BooleanField
from wtforms.validators import DataRequired, Optional, NumberRange

class GutenbergIdForm(FlaskForm):
    """Form for entering Project Gutenberg book IDs"""
    book_ids = StringField('Book IDs (comma-separated)', validators=[DataRequired()])
    submit = SubmitField('Analyze Books')

class FileUploadForm(FlaskForm):
    """Form for uploading text files"""
    file = FileField('Upload Text File', validators=[
        FileRequired(),
        FileAllowed(['txt'], 'Text files only!')
    ])
    submit = SubmitField('Upload and Analyze')

class AnalysisOptionsForm(FlaskForm):
    """Form for configuring analysis options"""
    remove_stopwords = BooleanField('Remove Stop Words', default=True)
    lemmatize = BooleanField('Lemmatize Words', default=True)
    top_words = IntegerField('Number of Top Words', default=50, 
                           validators=[NumberRange(min=5, max=500)])
    generate_wordcloud = BooleanField('Generate Word Cloud', default=True)
    generate_charts = BooleanField('Generate Charts', default=True)
    analyze_themes = BooleanField('Analyze Themes', default=True)
    num_topics = IntegerField('Number of Topics', default=5, 
                            validators=[NumberRange(min=2, max=20)])
    submit = SubmitField('Run Analysis')

class ComparisonForm(FlaskForm):
    """Form for comparing two books"""
    book1 = SelectField('First Book', validators=[DataRequired()])
    book2 = SelectField('Second Book', validators=[DataRequired()])
    submit = SubmitField('Compare Books')