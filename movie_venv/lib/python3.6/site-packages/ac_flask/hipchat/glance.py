class Glance(object):

    def __init__(self):
        self.data = {}

    def with_label(self, value, glance_type="html"):
        self.data["label"] = {
            "value": value,
            "type": glance_type
        }
        return self

    def with_lozenge(self, label, lozenge_type):
        self.data["status"] = {
            "type": "lozenge",
            "value": {
                "label": label,
                "type": lozenge_type
            }
        }
        return self

    def with_icon(self, url, url2x):
        self.data["status"] = {
            "type": "icon",
            "value": {
                "url": url,
                "url@2x": url2x
            }
        }
        return self