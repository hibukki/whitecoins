from wtforms import Form, StringField, PasswordField, validators, SubmitField, TextField, IntegerField, SelectField, BooleanField, TextAreaField
from country_codes import COUNTRY_CODE_MAP
    
                                        
class Form_SystemConfig_FrontEnd(Form): 
    FRONTEND_LISTEN_IP = StringField('FRONTEND_LISTEN_IP', validators=[validators.DataRequired(),
                                        validators.IPAddress(message='IPv4 address')])
    FRONTEND_LISTEN_PORT = IntegerField('FRONTEND_LISTEN_PORT', validators=[validators.DataRequired(),
                                        validators.NumberRange(min=1, max=65535, message='Invalid port number')])
    fe_save = SubmitField("Save")                                        
                                        
class Form_SystemConfig_BridgeServer(Form):
    BRIDGE_SERVER_IP = StringField('BRIDGE_SERVER_IP', validators=[validators.DataRequired(),
                                        validators.IPAddress(message='Invalid IPv4 address')])
    BRIDGE_SERVER_PORT = IntegerField('BRIDGE_SERVER_PORT', validators=[validators.DataRequired(),
                                        validators.NumberRange(min=1, max=65535, message='Invalid port number')])
    bs_save = SubmitField("Save")
    
class Form_SystemConfig_Filtering(Form):
    BRIDGE_BY_DNS_LIST = TextAreaField('BRIDGE_BY_DNS_LIST', validators=[validators.Optional()])
    BRIDGE_BY_IP_LIST = TextAreaField('BRIDGE_BY_IP_LIST', validators=[validators.Optional()])
    SSL_STRIP_BY_DNS_LIST = TextAreaField('SSL_STRIP_BY_DNS_LIST', validators=[validators.Optional()])
    SSL_STRIP_BY_IP_LIST = TextAreaField('SSL_STRIP_BY_IP_LIST', validators=[validators.Optional()])
    
    fl_save = SubmitField("Save")
    

class Form_SystemConfig_Luminati(Form):
    LUMINATI_ENABLED = BooleanField('LUMINATI_ENABLED', validators=[validators.Optional()])

    LUMINATI_HOST = StringField('LUMINATI_HOST', validators=[validators.DataRequired(),
                                             validators.Length(min=2, max=30, message='2-30 characters')])
    LUMINATI_PORT = IntegerField('LUMINATI_PORT', validators=[validators.DataRequired(),
                                        validators.NumberRange(min=1, max=65535, message='Invalid port number')])
    LUMINATI_ACCOUNT_ID = StringField('LUMINATI_ACCOUNT_ID', validators=[validators.DataRequired(),
                                             validators.Length(min=2, max=30, message='2-30 characters')])
    LUMINATI_ZONE_ID = StringField('LUMINATI_ZONE_ID', validators=[validators.DataRequired(),
                                             validators.Length(min=2, max=30, message='2-30 characters')])
    LUMINATI_ZONE_PASSWORD = PasswordField('LUMINATI_ZONE_PASSWORD', validators=[validators.Optional(),
                                             validators.Length(min=2, max=30, message='2-30 characters')])
    choices = COUNTRY_CODE_MAP.items()
    choices.sort(key=lambda x:x[1])
    choices.insert(0, ("none", "Random"))
    LUMINATI_COUNTRY_CODE = SelectField('LUMINATI_COUNTRY_CODE', choices=choices)
    lum_save = SubmitField("Save")