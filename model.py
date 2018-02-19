from wtforms import Form, FloatField, validators, StringField
import numpy as np


class InitForm(Form):
    e_min = FloatField(
        label='Energy min. (eV)', default=1,
        validators=[validators.InputRequired()])
    e_max = FloatField(
        label='Energy max. (eV)', default=100,
        validators=[validators.InputRequired()])
    e_step = FloatField(
        label='Energy step (eV)', default=0.01,
        validators=[validators.InputRequired()])


class SampleForm(Form):
    formula = StringField(
        label='Chemical formula', default='Ag',
        validators=[validators.InputRequired()])
    thickness = FloatField(
        label='Thickness (mm)', default=0.5,
        validators=[validators.InputRequired()])
    density = FloatField(
        label='Density (g/cm3)', default=np.NaN,
        validators=[validators.Optional()])

