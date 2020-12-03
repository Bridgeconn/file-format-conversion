from wtforms import StringField, SubmitField, FileField,SelectField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired


class SourceUploadForm(FlaskForm):
	# sourceLanguage = SelectField('Selected Averaging Period', choices=[('one', "One"), ('two, "Two"),('three', "Three"), ('four, "Four"),('five',"Five")], [validators.Required()])
	# targetType = StringField('Targettype', validators=[DataRequired(), Length(min=4, max =50)])
	targetType = SelectField('Target Type', choices = [('csv', 'CSV'),('usfm','USFM'),('txt','TXT')])
	file = FileField('Select File', validators=[FileRequired(), FileAllowed(['doc', 'docx', 'pdf'], 'doc or pdf only!')])
	submit = SubmitField('Convert File')
 
