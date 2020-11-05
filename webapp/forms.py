from wtforms import StringField, SubmitField, FileField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired


class SourceUploadForm(FlaskForm):
	# sourceLanguage = SelectField('Selected Averaging Period', choices=[('one', "One"), ('two, "Two"),('three', "Three"), ('four, "Four"),('five',"Five")], [validators.Required()])
	sourceLanguage = StringField('Source Language', validators=[DataRequired(), Length(min=3, max =50)])
	sourceDomain = StringField('Source Domain', validators=[DataRequired(), Length(min=4, max =50)])
	file = FileField('Select File', validators=[FileRequired(), FileAllowed(['doc', 'docx', 'pdf'], 'doc or pdf only!')])
	submit = SubmitField('Upload Source')
