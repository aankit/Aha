def datetimeformat(value, format='%I:%M %p'):
    return value.strftime(format)

def dayformat(value):
	day_dict = {0:'Monday',
		1:'Tuesday',
		2:'Wednesday',
		3:'Thursday',
		4:'Friday'}
	return day_dict[value]
