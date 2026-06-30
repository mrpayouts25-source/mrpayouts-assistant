from core.database import initialise_database
from gui.home import Home

initialise_database()

app = Home()

app.mainloop()