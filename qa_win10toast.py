from win10toast import ToastNotifier as toast
toaster = toast()
def Toast(Title, Text, Icon = None, Duration = 5):
    if not type(Title) is str or not type(Text) is str or type(Duration) is int: raise TypeError("Inavlid datatype")
    toaster.show_toast(Title, Text, icon_path = Icon, duration = Duration)