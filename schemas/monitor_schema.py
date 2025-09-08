"""Schema for validating API request."""

from marshmallow import Schema, fields


class MonitorSchema(Schema):
    conn1 = fields.String(required=True)
    conn2 = fields.String(required=True)
    hthresh = fields.Float(required=False, load_default=15.0)
    vthresh = fields.Float(required=False, load_default=5.0)
