from main import app
import user


app.add_url_rule("/",view_func=user.login,methods=["GET","POST"])
app.add_url_rule("/register",view_func=user.register,methods=["GET","POST"])
app.add_url_rule("/homepage",view_func=user.homepage)
app.add_url_rule("/login",view_func=user.login,methods=["GET","POST"])
app.add_url_rule("/addExpense",view_func=user.addExpense,methods=["GET","POST"])
app.add_url_rule("/editExpense/<expense_id>",view_func=user.editExpense,methods=["GET","POST"])
app.add_url_rule("/deleteExpense/<expense_id>",view_func=user.deleteExpense,methods=["GET","POST"])
app.add_url_rule("/showAllExp",view_func=user.showAllExp)
app.add_url_rule("/logout",view_func=user.logout)