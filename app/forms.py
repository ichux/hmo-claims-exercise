from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    FieldList,
    FormField,
    IntegerField,
    RadioField,
    SelectField,
    StringField,
    TextAreaField,
    validators,
)


class AddUser(FlaskForm):
    name = StringField(
        "name",
        validators=[validators.length(min=3, max=100), validators.DataRequired()],
    )
    gender = RadioField("gender", choices=["male", "female"])
    salary = IntegerField(
        validators=[validators.NumberRange(min=0), validators.DataRequired()]
    )
    date_of_birth = DateField(format="%Y-%m-%d", validators=[validators.DataRequired()])


class ServiceForm(FlaskForm):
    service_date = StringField("Service Date", validators=[validators.DataRequired()])
    service_name = StringField("Service Name", validators=[validators.DataRequired()])
    service_type = SelectField(
        "Service Type",
        choices=[
            "Hematology",
            "Microbiology",
            "Chemical Pathology",
            "Histopathology",
            "Immunology",
        ],
        validators=[validators.DataRequired()],
    )
    provider_name = StringField("Provider Name", validators=[validators.DataRequired()])
    source = StringField("Source", validators=[validators.DataRequired()])
    cost = IntegerField("Cost of Service", validators=[validators.DataRequired()])


class ClaimForm(FlaskForm):
    patient = SelectField("Patient", coerce=int, validators=[validators.DataRequired()])
    age = IntegerField(
        "Age",
        validators=[validators.NumberRange(min=0, max=150), validators.DataRequired()],
    )
    gender = RadioField(
        "Gender",
        choices=[(1, "Male"), (0, "Female")],
        coerce=int,
        validators=[validators.DataRequired()],
    )
    diagnosis = TextAreaField("Diagnosis", validators=[validators.DataRequired()])
    hmo = SelectField(
        "HMO Provider",
        choices=["HMO1", "HMO2", "HMO3", "HMO4"],
        validators=[validators.DataRequired()],
    )
    services = FieldList(FormField(ServiceForm), min_entries=1)
