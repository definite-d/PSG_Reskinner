from psg_reskinner.exception import ReskinnerException
from psg_reskinner.version import __deprecation_condition__


def deprecation_trigger():
    if __deprecation_condition__:
        m = "Hello! Annoying little reminder to remove the deprecated functions, and this message."
        raise ReskinnerException(m)
