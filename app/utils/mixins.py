class Upmodel():
    """
    Class used to add the to-dict functionality/method to db model classes - it allows the user to get only
    specific data out of the queried item, by passing a list of attributes the user wants to get, which are
    then parsed from the object and returned as a dictionary.
    This functionality is used to get back the columns/attributes the user wants to display in the table of
    queried results.
    """
    def to_dict(self, list):
        return {k: (getattr(self, k) if k!='date' else getattr(self, k).strftime('%Y-%m-%d')) for k in list}