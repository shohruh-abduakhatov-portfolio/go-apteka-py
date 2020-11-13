from datetime import datetime
import locale
import pandas as pd


def validate_date2(value):

    if type(value) is float:
        return None
    formats = [
        '%d.%m.%y', '%d.%m.%Y', '%m.%y', '%m/%y', '%m/%Y', '%Y.%m', '%Y',
        '%m.%Y', '%m,%Y', '%Y', '%m/%d/%y %I:%M:%S %p', '%m/%Yг.', '%m/%Yг',
        '%m/%d/%Y %I:%M:%S %p', '%b %Y']
    print("??")
    for format in formats:
        try:
            # val = pendulum.from_format(value, format)
            val = pd.to_datetime(value, format=format)
            return val
        except Exception:
            pass
    value = value.replace("Январь", "January")\
        .replace("Февраль", "February")\
        .replace("Март", "March")\
        .replace("Апрель", "April")\
        .replace("Май", "May")\
        .replace("Июнь", "June")\
        .replace("Июль", "July")\
        .replace("Август", "August")\
        .replace("Сентябрь", "September")\
        .replace("Октябрь", "October")\
        .replace("Ноябрь", "November")\
        .replace("Декабрь", "December")

    try:
            # val = pendulum.from_format(value, format)
        val = pd.to_datetime(value, format='%B %y г.')
        return val
    except Exception:
        pass

    try:
            # val = pendulum.from_format(value, format)
        val = pd.to_datetime(value, format='%B %Y г.')
        return val
    except Exception:
        pass

    value = value.replace("янв.", "January ")\
        .replace("фев.", "February ")\
        .replace("мар.", "March ")\
        .replace("апр.", "April ")\
        .replace("май.", "May ")\
        .replace("июн.", "June ")\
        .replace("июл.", "July ")\
        .replace("авг.", "August ")\
        .replace("сен.", "September ")\
        .replace("окт.", "October ")\
        .replace("ноя.", "November ")\
        .replace("дек.", "December ")

    try:
            # val = pendulum.from_format(value, format)
        val = pd.to_datetime(value, format='%B %y')
        return val
    except Exception:
        pass

    value = value.replace("янв", "January")\
        .replace("фев", "February")\
        .replace("мар", "March")\
        .replace("апр", "April")\
        .replace("май", "May")\
        .replace("июн", "June")\
        .replace("июл", "July")\
        .replace("авг", "August")\
        .replace("сен", "September")\
        .replace("окт", "October")\
        .replace("ноя", "November")\
        .replace("дек", "December")

    try:
            # val = pendulum.from_format(value, format)
        val = pd.to_datetime(value, format='%B %Y')
        return val
    except Exception:
        pass

    # locale.setlocale(locale.LC_TIME, "ru_RU")
    # n = datetime.now()
    return None


def validate_date(value):
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    locale.setlocale(locale.LC_TIME, "ru_RU")
    n = datetime.now()
    print(n.strftime('%b %Y'))
    print(locale.getlocale())
    val = None
    if type(value) is float:
        return None
    formats = ['%d.%m.%y', '%d.%m.%Y', '%m.%y',
               '%m.%Y', '%m,%Y', '%Y', '%m/%d/%y %I:%M:%S %p',
               '%m/%d/%Y %I:%M:%S %p', '%B %y г.', '%b %Y']
    for format in formats:
        try:
            val = datetime.strptime(value, format)
            return val
        except Exception:
            pass

    if type(value) is str:
        from_month = ["январь", "февраль", "март", "апрель", "май", "июнь",
                      "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]
        to_month = ["января", "февраля", "марта", "апреля", "мая", "июня",
                    "июля", "августа", "сентября", "октября", "ноября", "декабря"]
        for i, m in enumerate(from_month):
            if value.startswith(m):
                value = value.replace(m, to_month[i])
                val = self.validate_date(value)
                break
    return val


# print(validate_date("янв 2021"))
print(validate_date2("Июль 2022"))
