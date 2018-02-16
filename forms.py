from flask_wtf import Form
from wtforms import TextField, SubmitField, validators, ValidationError

class SearchForm(Form):
    searchValue = TextField("Enter Search Term", [validators.Required("Please enter a search term.")])
    submit = SubmitField("Search")

class CourseSearch(Form):
    searchValue = TextField("Search Courses", [validators.Required("Please enter a search term.")])
    submit = SubmitField("Search")